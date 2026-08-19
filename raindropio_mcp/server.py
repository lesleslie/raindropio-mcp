"""FastMCP entrypoint wiring Raindrop.io tools together."""

from __future__ import annotations

import asyncio
import importlib.util
import logging
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any, Final

from fastmcp import FastMCP
from mcp_common.health import register_http_health_route
from mcp_common.tools.dispatch import _apply_tool_profile

from raindropio_mcp import __version__
from raindropio_mcp.clients.client_factory import build_raindrop_client
from raindropio_mcp.config import get_settings
from raindropio_mcp.tools.profiles import (
    PROFILE_REGISTRATIONS,
    _build_registration_map,
    register_all_tool_groups,
)

# Check FastMCP rate limiting middleware availability (Phase 3.3 M2: improved pattern)
RATE_LIMITING_AVAILABLE = (
    importlib.util.find_spec("fastmcp.server.middleware.rate_limiting") is not None
)

# Check ServerPanels availability (Phase 3.3 M2: improved pattern)
SERVERPANELS_AVAILABLE = importlib.util.find_spec("mcp_common.ui") is not None

# Import security availability flag (Phase 3 Security Hardening)
try:
    from mcp_common import security  # noqa: F401 - check availability only

    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from raindropio_mcp.clients.raindrop_client import RaindropClient
    from raindropio_mcp.config.settings import RaindropSettings

logger = logging.getLogger(__name__)

APP_NAME: Final = "raindropio-mcp"
APP_VERSION: Final = __version__


# ---------------------------------------------------------------------------
# W4 apply_tool_profile dispatch surface.
#
# Registers the ``health_tools`` group inside ``mandatory_groups`` so
# ``health_check`` is exposed at EVERY profile (the W4.1 keystone). The
# per-profile lists (``PROFILE_REGISTRATIONS``) add the eight client-bound
# tool groups at STANDARD and FULL — Tier-A trivial mapping
# (``MINIMAL=health, STANDARD/FULL=all``).
#
# Per W2b.3 keystone: production MUST use ``_apply_tool_profile`` (async
# helper). The sync ``apply_tool_profile`` wrapper raises RuntimeError
# inside an event loop. The ``apply_raindropio_tool_profile`` wrapper
# is async and is what ``create_app`` awaits.
# ---------------------------------------------------------------------------
RAINDROPIO_MANDATORY_GROUPS: set[str] = {"health_tools"}


async def apply_raindropio_tool_profile(
    server: FastMCP,
    settings: RaindropSettings,
    client: RaindropClient,
) -> None:
    """Apply ``RAINDROPIO_TOOL_PROFILE`` dispatch to ``server`` at startup.

    Async wrapper around the W0 helper. Caller-supplied ``settings`` and
    ``client`` are threaded through to the registration adapters so
    tests can inject overrides (the W4.1 reviewer fix). The
    ``essential_tool_names={"health_check"}`` subset check enforces the
    W4 spec invariant that the health tool is present at every profile.
    """
    await _apply_tool_profile(
        server,
        profile_env_var="RAINDROPIO_TOOL_PROFILE",
        registrations=PROFILE_REGISTRATIONS,
        registration_map=_build_registration_map(client),
        register_all_fn=lambda srv: register_all_tool_groups(srv, client),
        mandatory_groups=RAINDROPIO_MANDATORY_GROUPS,
        essential_tool_names={"health_check"},
    )


# ---------------------------------------------------------------------------
# Sync-async bridge (W3.4 lesson + W4.6 precedent)
#
# ``create_app`` is async because the W0 tool profile dispatch is async.
# CLI startup, ``__main__.py`` (``RaindropMCPServer.__init__``), and
# ``__getattr__`` lazy access are sync, so we bridge via
# ``_run_async_safely`` — asyncio.run when no loop is running,
# private ThreadPoolExecutor with a fresh asyncio.run when pytest-asyncio
# already has a loop running (the W4 unifi-mcp precedent).
# ---------------------------------------------------------------------------
def _run_async_safely(coro: Any) -> Any:
    """Run an async coroutine from a sync context, tolerating a running loop."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=1) as pool_executor:
        return pool_executor.submit(asyncio.run, coro).result()


async def create_app(
    settings: RaindropSettings | None = None,
) -> FastMCP:
    """Create and configure the FastMCP application (async production path).

    Async because the W0 tool profile dispatch helper is async. Sync
    callers (``__main__.py``, ``__getattr__``) use ``create_app_sync``
    which wraps this coroutine via ``_run_async_safely``.

    Args:
        settings: Optional pre-loaded ``RaindropSettings``. When ``None``,
            falls back to ``get_settings()`` (env-driven loader).
            Pass-through preserves caller-supplied configuration overrides
            (the W4.1 reviewer fix).
    """
    if settings is None:
        settings = get_settings()

    app = FastMCP(name=APP_NAME, version=APP_VERSION)

    # HTTP health endpoint for Claude Code compatibility — always-on,
    # independent of profile dispatch (load-balancer probe).
    register_http_health_route(
        app,
        service_name="raindropio",
        version=APP_VERSION,
    )

    @app.custom_route("/healthz", methods=["GET"])
    async def healthz_check(request: Any) -> Any:
        """Kubernetes-style health check endpoint."""
        from starlette.responses import JSONResponse

        return JSONResponse({"status": "ok"})

    # Add rate limiting middleware (Phase 3 Security Hardening)
    if RATE_LIMITING_AVAILABLE and hasattr(app._mcp_server, "add_middleware"):
        from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware

        rate_limiter = RateLimitingMiddleware(
            max_requests_per_second=8.0,  # Sustainable rate for bookmark API
            burst_capacity=16,  # Allow brief bursts
            global_limit=True,  # Protect the Raindrop.io API globally
        )
        app._mcp_server.add_middleware(rate_limiter)  # ty: ignore[call-non-callable]
        logger.info("Rate limiting enabled: 8 req/sec, burst 16")

    # Construct the RaindropClient ONCE upfront. The W0 dispatch adapters
    # capture the same instance via closure, AND the lifespan ``finally``
    # block holds a closure reference so ``await client.close()`` actually
    # closes the registered client. The W4.3 reviewer lesson: long-running
    # servers leak httpx pools if the close call refers to a different
    # instance.
    client = build_raindrop_client(settings)

    original_lifespan = app._mcp_server.lifespan

    @asynccontextmanager
    async def lifespan(server: Any) -> AsyncGenerator[dict[str, Any]]:
        async with original_lifespan(server) as state:
            try:
                yield state
            finally:
                await client.close()

    app._mcp_server.lifespan = lifespan
    app._raindrop_client = client  # ty: ignore[unresolved-attribute]

    # Apply tool profile dispatch — replaces the pre-W4 direct
    # ``register_all_tools(app, client)`` call. The W0 helper walks
    # ``PROFILE_REGISTRATIONS`` and registers the ``discover_tools``
    # meta-tool. Default (no env var) remains FULL = all 30 Raindrop.io
    # tools — the previous behavior is preserved (the W4.1 reviewer fix).
    await apply_raindropio_tool_profile(app, settings, client)

    logger.debug("Registered Raindrop.io MCP tools")
    return app


def create_app_sync(
    settings: RaindropSettings | None = None,
) -> FastMCP:
    """Sync wrapper around the async ``create_app``.

    Bridges via ``_run_async_safely`` so CLI startup, ``__main__.py``,
    ``__getattr__`` lazy access (``module.app``, ``module.http_app``),
    and pytest-asyncio tests can all call into the same production
    path. Tests that exercise the real async startup should call
    ``await create_app(...)`` directly so any W2b.3-style regression in
    the production dispatch path is caught.
    """
    return _run_async_safely(create_app(settings))


# Initialize app lazily to avoid startup errors in testing environment
def __getattr__(name: str) -> Any:
    if name == "app":
        return create_app_sync()
    if name == "http_app":
        # Export ASGI app for uvicorn (same pattern as mailgun-mcp)
        return create_app_sync().http_app
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
    "APP_NAME",
    "APP_VERSION",
    "RATE_LIMITING_AVAILABLE",
    "SECURITY_AVAILABLE",
    "SERVERPANELS_AVAILABLE",
    "apply_raindropio_tool_profile",
    "create_app",
    "create_app_sync",
    "get_settings",  # Added to fix zuban type error
]