#!/usr/bin/env python3
"""Raindrop.io MCP Server - Oneiric CLI Entry Point."""

from typing import TYPE_CHECKING

from mcp_common.cli import MCPServerCLIFactory
from mcp_common.server import BaseOneiricServerMixin, create_runtime_components
from oneiric.core.config import OneiricMCPConfig
from oneiric.runtime.mcp_health import HealthStatus

# Import the main server from the existing codebase
from raindropio_mcp.server import create_app, get_settings

# Type annotation to help with type checking
OneiricMCPConfigType = (
    OneiricMCPConfig if not TYPE_CHECKING else "TypedOneiricMCPConfig"
)


class RaindropConfig(OneiricMCPConfig):  # type: ignore[misc]
    """Raindrop.io MCP Server Configuration."""

    http_port: int = 3041
    http_host: str = "127.0.0.1"
    enable_http_transport: bool = True

    class Config:
        env_prefix = "RAINDROP_MCP_"
        env_file = ".env"


class RaindropMCPServer(BaseOneiricServerMixin):
    """Raindrop.io MCP Server with Oneiric integration."""

    def __init__(self, config: RaindropConfig):
        self.config = config
        self.app = create_app()  # Use the existing FastMCP instance

        # Initialize runtime components using mcp-common helper
        self.runtime = create_runtime_components(
            server_name="raindropio-mcp", cache_dir=config.cache_dir or ".oneiric_cache"
        )

    @property
    def snapshot_manager(self) -> object:
        """Convenience property to access snapshot manager from runtime."""
        return self.runtime.snapshot_manager

    @property
    def cache_manager(self) -> object:
        """Convenience property to access cache manager from runtime."""
        return self.runtime.cache_manager

    @property
    def health_monitor(self) -> object:
        """Convenience property to access health monitor from runtime."""
        return self.runtime.health_monitor

    async def startup(self) -> None:
        """Server startup lifecycle hook."""
        # Settings are already validated by get_settings()
        # The validator runs automatically during model initialization
        _ = get_settings()

        # Initialize runtime components
        await self.runtime.initialize()

        # Create startup snapshot with custom components
        await self._create_startup_snapshot(
            custom_components={
                "raindrop": {
                    "status": "initialized",
                    "timestamp": self._get_timestamp(),
                },
            }
        )

    async def shutdown(self) -> None:
        """Server shutdown lifecycle hook."""
        # Create shutdown snapshot
        await self._create_shutdown_snapshot()

        # Clean up runtime components
        await self.runtime.cleanup()

    async def health_check(self) -> object:
        """Perform health check."""
        # Build base health components using mixin helper
        base_components = await self._build_health_components()

        # Check Raindrop configuration
        settings = get_settings()
        raindrop_configured = bool(settings and settings.token)

        # Add raindrop-specific health checks
        base_components.append(
            self.runtime.health_monitor.create_component_health(
                name="raindrop",
                status=HealthStatus.HEALTHY
                if raindrop_configured
                else HealthStatus.UNHEALTHY,
                details={
                    "configured": raindrop_configured,
                    "api_token": bool(settings.token if settings else False),
                },
            )
        )

        # Create health response
        return self.runtime.health_monitor.create_health_response(base_components)

    def get_app(self) -> object:
        """Get the ASGI application."""
        return self.app.http_app

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        import time

        return time.strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> None:
    """Main entry point for Raindrop.io MCP Server."""

    # Create CLI factory using mcp-common's enhanced factory
    cli_factory = MCPServerCLIFactory.create_server_cli(
        server_class=RaindropMCPServer,
        config_class=RaindropConfig,
        name="raindropio-mcp",
        _description="Raindrop.io MCP Server - Bookmark management via Raindrop.io API",
    )

    # Create and run CLI
    cli_factory.create_app()()


if __name__ == "__main__":
    main()
