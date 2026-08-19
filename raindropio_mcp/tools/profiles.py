"""Tool profile registration groups for raindropio-mcp MCP server.

Maps ``ToolProfile`` levels to specific ``register_<group>_tools()`` call
lists, controlling which tools are exposed at startup based on the
``RAINDROPIO_TOOL_PROFILE`` environment variable.

Profile tiers (Tier-A canonical mapping, per the W4 plan):
    MINIMAL:  Only the MCP ``health_check`` tool + ``/health`` + ``/healthz``
              HTTP routes + the ``discover_tools`` meta-tool.
    STANDARD: All 30 Raindrop.io tools + ``health_check`` + ``discover_tools``.
    FULL:     All 30 Raindrop.io tools + ``health_check`` + ``discover_tools``.

Tier-A trivial mapping: ``MINIMAL=health, STANDARD/FULL=all``.

Architectural notes
-------------------

The pre-W4 entry points in ``raindropio_mcp.tools`` use a custom
``FastMCPToolRegistry`` wrapper (``raindropio_mcp/tools/tool_registry.py``)
which delegates to ``app.tool(name=..., description=...)(func)``. Each
``register_<group>_tools`` fn takes a ``(registry, client)`` pair — they
do NOT match the ``(server, settings)`` contract the W0 dispatch helper
expects. Per the W3.1 backend-lambda lesson, each register fn is wrapped
in an adapter that closes over a caller-supplied ``RaindropClient`` and
constructs a ``FastMCPToolRegistry(server)`` inside the call.

The dispatch surface (``PROFILE_REGISTRATIONS`` + ``_GROUP_REGISTRY`` +
``_build_registration_map`` + ``register_all_tool_groups``) is consumed
by ``raindropio_mcp.server.apply_raindropio_tool_profile`` which
delegates to ``mcp_common.tools.dispatch._apply_tool_profile`` (the
async helper, NOT the sync wrapper — W2b.3 keystone).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from mcp_common.tools import ToolProfile
from mcp_common.tools.dispatch import ALL_TOOLS

from raindropio_mcp.tools.tool_registry import FastMCPToolRegistry

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from fastmcp import FastMCP

    from raindropio_mcp.clients.raindrop_client import RaindropClient


# ---------------------------------------------------------------------------
# _GROUP_REGISTRY — single source of truth for the (group_key, register_fn)
# pairings. The dispatch helper's subset check walks this list, so adding a
# new tool group requires editing this constant + the per-profile lists
# below (the W3.2 lesson).
#
# group_key   — string used in PROFILE_REGISTRATIONS / mandatory_groups
# register_fn — callable(server) -> ``(FastMCPToolRegistry, RaindropClient)``
#               adapter that wraps the legacy ``register_<group>_tools``
#               (registry, client) signature.
# ---------------------------------------------------------------------------
_GROUP_REGISTRY: Final[list[tuple[str, str]]] = [
    ("collection_tools", "register_collection_tools"),
    ("bookmark_tools", "register_bookmark_tools"),
    ("tag_tools", "register_tag_tools"),
    ("highlight_tools", "register_highlight_tools"),
    ("batch_tools", "register_batch_tools"),
    ("filter_tools", "register_filter_tools"),
    ("import_export_tools", "register_import_export_tools"),
    ("account_tools", "register_account_tools"),
    ("system_tools", "register_system_tools"),
]


def _group_keys() -> list[str]:
    """Return the group keys (first element of each ``_GROUP_REGISTRY`` tuple)."""
    return [key for key, _ in _GROUP_REGISTRY]


# ---------------------------------------------------------------------------
# Profile tier definitions
# ---------------------------------------------------------------------------
MINIMAL_REGISTRATIONS: list[str | Callable[[FastMCP], Awaitable[None] | None]] = [
    "health_tools",  # register_health_tool — local health_check MCP tool
]

STANDARD_REGISTRATIONS: list[str | Callable[[FastMCP], Awaitable[None] | None]] = [
    "health_tools",
    *_group_keys(),
]

FULL_REGISTRATIONS: list[str | Callable[[FastMCP], Awaitable[None] | None]] = [
    "health_tools",
    *_group_keys(),
]

PROFILE_REGISTRATIONS: dict[
    ToolProfile,
    list[str | Callable[[FastMCP], Awaitable[None] | None]] | type[ALL_TOOLS],
] = {
    ToolProfile.MINIMAL: MINIMAL_REGISTRATIONS,
    ToolProfile.STANDARD: STANDARD_REGISTRATIONS,
    ToolProfile.FULL: FULL_REGISTRATIONS,
}


# ---------------------------------------------------------------------------
# Registration map — backend-lambda adapters (W3.1 lesson)
#
# Each adapter closes over a caller-supplied ``RaindropClient`` and the
# caller-supplied ``settings`` (W4.1 — never re-load from env) and constructs
# the ``FastMCPToolRegistry(server)`` wrapper inside the call. The
# ``system_tools`` group has no client dependency and registers via
# ``registry`` alone; we still pass the closure-captured client (unused)
# so the W0 dispatch loop can call every adapter with a uniform shape.
# ---------------------------------------------------------------------------
def _build_registration_map(
    client: RaindropClient,
) -> dict[str, Callable[[FastMCP], Awaitable[None] | None]]:
    """Build the ``{group_key: register_fn(server)}`` map.

    Each value is a backend-lambda adapter (W3.1) that constructs a
    ``FastMCPToolRegistry(server)`` and forwards to the legacy
    ``register_<group>_tools(registry, client)`` signature.

    The ``client`` is the SAME instance already attached to
    ``server._raindrop_client`` in ``raindropio_mcp/server.py`` so the
    W4.3 lifespan ``finally: await client.close()`` closes the same
    object the adapters use.
    """
    from raindropio_mcp.tools import (
        register_account_tools,
        register_batch_tools,
        register_bookmark_tools,
        register_collection_tools,
        register_filter_tools,
        register_health_tool,
        register_highlight_tools,
        register_import_export_tools,
        register_system_tools,
        register_tag_tools,
    )

    def _adapter(reg_fn: Callable[..., None]) -> Callable[[FastMCP], None]:
        """Build a (server) -> None adapter that wraps ``reg_fn(registry, client)``."""

        def _adapter_impl(server: FastMCP) -> None:
            registry = FastMCPToolRegistry(server)
            reg_fn(registry, client)

        return _adapter_impl

    def _system_adapter(server: FastMCP) -> None:
        """system_tools takes only ``(registry)`` — no client."""
        registry = FastMCPToolRegistry(server)
        register_system_tools(registry)

    def _health_adapter(server: FastMCP) -> None:
        """health_tools — registers ``health_check`` MCP tool (W4.1 keystone).

        The settings + client are threaded for signature uniformity, but
        neither is needed for the static health payload.
        """
        register_health_tool(server, None, client)  # type: ignore[arg-type]

    return {
        "health_tools": _health_adapter,
        "collection_tools": _adapter(register_collection_tools),
        "bookmark_tools": _adapter(register_bookmark_tools),
        "tag_tools": _adapter(register_tag_tools),
        "highlight_tools": _adapter(register_highlight_tools),
        "batch_tools": _adapter(register_batch_tools),
        "filter_tools": _adapter(register_filter_tools),
        "import_export_tools": _adapter(register_import_export_tools),
        "account_tools": _adapter(register_account_tools),
        "system_tools": _system_adapter,
    }


def register_all_tool_groups(server: FastMCP, client: RaindropClient) -> None:
    """Bulk register every Raindrop.io tool group (called at FULL profile).

    Used as ``register_all_fn`` for the W0 helper. Iterates
    ``_GROUP_REGISTRY`` so adding a new tool group only requires editing
    the SSOT constant (the W3.2 lesson).
    """
    from raindropio_mcp.tools import (
        register_account_tools,
        register_batch_tools,
        register_bookmark_tools,
        register_collection_tools,
        register_filter_tools,
        register_highlight_tools,
        register_import_export_tools,
        register_system_tools,
        register_tag_tools,
    )

    registry = FastMCPToolRegistry(server)
    # All eight client-bound groups
    register_collection_tools(registry, client)
    register_bookmark_tools(registry, client)
    register_tag_tools(registry, client)
    register_highlight_tools(registry, client)
    register_batch_tools(registry, client)
    register_filter_tools(registry, client)
    register_import_export_tools(registry, client)
    register_account_tools(registry, client)
    # system_tools needs no client
    register_system_tools(registry)


__all__ = [
    "FULL_REGISTRATIONS",
    "MINIMAL_REGISTRATIONS",
    "PROFILE_REGISTRATIONS",
    "STANDARD_REGISTRATIONS",
    "_GROUP_REGISTRY",
    "_build_registration_map",
    "register_all_tool_groups",
]