"""FastMCP entrypoint wiring Raindrop.io tools together."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any, Final

from fastmcp import FastMCP

from raindropio_mcp import __version__
from raindropio_mcp.clients.client_factory import build_raindrop_client
from raindropio_mcp.config import get_settings
from raindropio_mcp.tools import register_all_tools

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

logger = logging.getLogger(__name__)

APP_NAME: Final = "raindropio-mcp"
APP_VERSION: Final = __version__


def create_app() -> FastMCP:
    """Create and configure the FastMCP application."""

    settings = get_settings()
    app = FastMCP(name=APP_NAME, version=APP_VERSION)
    client = build_raindrop_client(settings)
    register_all_tools(app, client)

    original_lifespan = app._mcp_server.lifespan

    @asynccontextmanager
    async def lifespan(server: Any) -> AsyncGenerator[dict[str, Any]]:
        async with original_lifespan(server) as state:
            try:
                yield state
            finally:
                await client.close()

    app._mcp_server.lifespan = lifespan
    app._raindrop_client = client  # type: ignore[attr-defined]
    logger.debug("Registered Raindrop.io MCP tools")
    return app


# Initialize app lazily to avoid startup errors in testing environment
def __getattr__(name: str) -> FastMCP:
    if name == "app":
        return create_app()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = ["create_app", "APP_NAME", "APP_VERSION"]
