"""Register FastMCP tools for the Raindrop.io server."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from raindropio_mcp import __version__
from raindropio_mcp.tools.account import register_account_tools
from raindropio_mcp.tools.batch import register_batch_tools
from raindropio_mcp.tools.bookmarks import register_bookmark_tools
from raindropio_mcp.tools.collections import register_collection_tools
from raindropio_mcp.tools.filters import register_filter_tools
from raindropio_mcp.tools.highlights import register_highlight_tools
from raindropio_mcp.tools.import_export import register_import_export_tools
from raindropio_mcp.tools.system import register_system_tools
from raindropio_mcp.tools.tags import register_tag_tools
from raindropio_mcp.tools.tool_registry import FastMCPToolRegistry

if TYPE_CHECKING:
    from fastmcp import FastMCP

    from raindropio_mcp.clients.raindrop_client import RaindropClient


def register_health_tool(
    server: FastMCP,
    settings: Any = None,
    client: RaindropClient | None = None,
) -> None:
    """Register only the MCP ``health_check`` tool for the MINIMAL profile.

    Split out from the legacy monolithic flow so the W0 tool profile
    dispatch can expose ``health_check`` independently at MINIMAL
    (the canonical W4.1 mapping: ``MINIMAL=health``).

    The HTTP ``/health`` route and ``/healthz`` route are registered by
    ``server.create_app`` outside the profile dispatch (they're always-on
    load-balancer probes, not profile-dependent).

    The ``settings`` and ``client`` parameters are accepted (but unused
    here) so the W0 dispatch helper can call every group fn with a
    uniform ``(server, settings, client)`` shape. The health probe
    doesn't need either — it returns a static shape that downstream
    load balancers can match.

    Args:
        server: FastMCP server instance.
        settings: Accepted for signature uniformity; unused.
        client: Accepted for signature uniformity; unused.
    """
    _ = (settings, client)  # silence unused-name lint; signature uniformity

    @server.tool()
    async def health_check() -> dict[str, Any]:
        """Return a static health payload (status, version, server name).

        Used by load balancers and orchestrators at the MINIMAL profile.
        The HTTP ``/health`` route (registered in ``server.create_app``)
        carries the same payload via ``register_http_health_route`` for
        non-MCP probe callers.
        """
        return {
            "status": "ok",
            "name": "raindropio-mcp",
            "version": __version__,
        }


def register_all_tools(app: FastMCP, client: RaindropClient) -> FastMCPToolRegistry:
    """Register every MCP tool and return the registry for inspection.

    Pre-W4 entry point retained for backward compatibility with callers
    (tests, examples) that bypass the W0 dispatch. New code should use
    ``apply_raindropio_tool_profile`` from ``raindropio_mcp.server`` so
    the ``RAINDROPIO_TOOL_PROFILE`` env var gates registration.
    """
    registry = FastMCPToolRegistry(app)
    register_collection_tools(registry, client)
    register_bookmark_tools(registry, client)
    register_tag_tools(registry, client)
    register_highlight_tools(registry, client)
    register_batch_tools(registry, client)
    register_filter_tools(registry, client)
    register_import_export_tools(registry, client)
    register_account_tools(registry, client)
    register_system_tools(registry)
    return registry


__all__ = [
    "FastMCPToolRegistry",
    "register_all_tools",
    "register_health_tool",
]
