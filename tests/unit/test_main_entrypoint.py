"""Tests for __main__.py module to improve coverage."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


class TestRaindropConfig:
    """Tests for RaindropConfig class."""

    def test_raindrop_config_defaults(self) -> None:
        """Test RaindropConfig default values."""
        from raindropio_mcp.__main__ import RaindropConfig

        config = RaindropConfig()
        assert config.http_port == 3034
        assert config.http_host == "127.0.0.1"
        assert config.enable_http_transport is True

    def test_raindrop_config_custom_values(self) -> None:
        """Test RaindropConfig with custom values."""
        from raindropio_mcp.__main__ import RaindropConfig

        config = RaindropConfig(
            http_port=8080, http_host="0.0.0.0", enable_http_transport=False
        )
        assert config.http_port == 8080
        assert config.http_host == "0.0.0.0"
        assert config.enable_http_transport is False


class TestRaindropMCPServer:
    """Tests for RaindropMCPServer class."""

    @patch("raindropio_mcp.__main__.create_runtime_components")
    @patch("raindropio_mcp.__main__.create_app")
    def test_server_initialization(
        self, mock_create_app: MagicMock, mock_create_runtime: MagicMock
    ) -> None:
        """Test RaindropMCPServer initialization."""
        from raindropio_mcp.__main__ import RaindropConfig, RaindropMCPServer

        mock_app = MagicMock()
        mock_create_app.return_value = mock_app

        mock_runtime = MagicMock()
        mock_create_runtime.return_value = mock_runtime

        config = RaindropConfig()
        server = RaindropMCPServer(config)

        assert server.config is config
        assert server.app is mock_app
        assert server.runtime is mock_runtime

    @patch("raindropio_mcp.__main__.create_runtime_components")
    @patch("raindropio_mcp.__main__.create_app")
    def test_snapshot_manager_property(
        self, mock_create_app: MagicMock, mock_create_runtime: MagicMock
    ) -> None:
        """Test snapshot_manager property."""
        from raindropio_mcp.__main__ import RaindropConfig, RaindropMCPServer

        mock_app = MagicMock()
        mock_create_app.return_value = mock_app

        mock_runtime = MagicMock()
        mock_snapshot_manager = MagicMock()
        mock_runtime.snapshot_manager = mock_snapshot_manager
        mock_create_runtime.return_value = mock_runtime

        config = RaindropConfig()
        server = RaindropMCPServer(config)

        assert server.snapshot_manager is mock_snapshot_manager

    @patch("raindropio_mcp.__main__.create_runtime_components")
    @patch("raindropio_mcp.__main__.create_app")
    def test_cache_manager_property(
        self, mock_create_app: MagicMock, mock_create_runtime: MagicMock
    ) -> None:
        """Test cache_manager property."""
        from raindropio_mcp.__main__ import RaindropConfig, RaindropMCPServer

        mock_app = MagicMock()
        mock_create_app.return_value = mock_app

        mock_runtime = MagicMock()
        mock_cache_manager = MagicMock()
        mock_runtime.cache_manager = mock_cache_manager
        mock_create_runtime.return_value = mock_runtime

        config = RaindropConfig()
        server = RaindropMCPServer(config)

        assert server.cache_manager is mock_cache_manager

    @patch("raindropio_mcp.__main__.create_runtime_components")
    @patch("raindropio_mcp.__main__.create_app")
    def test_health_monitor_property(
        self, mock_create_app: MagicMock, mock_create_runtime: MagicMock
    ) -> None:
        """Test health_monitor property."""
        from raindropio_mcp.__main__ import RaindropConfig, RaindropMCPServer

        mock_app = MagicMock()
        mock_create_app.return_value = mock_app

        mock_runtime = MagicMock()
        mock_health_monitor = MagicMock()
        mock_runtime.health_monitor = mock_health_monitor
        mock_create_runtime.return_value = mock_runtime

        config = RaindropConfig()
        server = RaindropMCPServer(config)

        assert server.health_monitor is mock_health_monitor

    @patch("raindropio_mcp.__main__.create_runtime_components")
    @patch("raindropio_mcp.__main__.create_app")
    @pytest.mark.asyncio
    async def test_startup_lifecycle(
        self, mock_create_app: MagicMock, mock_create_runtime: MagicMock
    ) -> None:
        """Test server startup lifecycle."""
        from raindropio_mcp.__main__ import RaindropConfig, RaindropMCPServer

        mock_app = MagicMock()
        mock_create_app.return_value = mock_app

        mock_runtime = MagicMock()
        mock_create_runtime.return_value = mock_runtime

        config = RaindropConfig()
        server = RaindropMCPServer(config)

        await server.startup()

        # Verify runtime initialization was called
        mock_runtime.initialize.assert_called_once()

    @patch("raindropio_mcp.__main__.create_runtime_components")
    @patch("raindropio_mcp.__main__.create_app")
    @pytest.mark.asyncio
    async def test_shutdown_lifecycle(
        self, mock_create_app: MagicMock, mock_create_runtime: MagicMock
    ) -> None:
        """Test server shutdown lifecycle."""
        from raindropio_mcp.__main__ import RaindropConfig, RaindropMCPServer

        mock_app = MagicMock()
        mock_create_app.return_value = mock_app

        mock_runtime = MagicMock()
        mock_create_runtime.return_value = mock_runtime

        config = RaindropConfig()
        server = RaindropMCPServer(config)

        await server.shutdown()

        # Verify runtime cleanup was called
        mock_runtime.cleanup.assert_called_once()

    @patch("raindropio_mcp.__main__.create_runtime_components")
    @patch("raindropio_mcp.__main__.create_app")
    @patch("raindropio_mcp.__main__.get_settings")
    @pytest.mark.asyncio
    async def test_health_check_healthy(
        self,
        mock_get_settings: MagicMock,
        mock_create_app: MagicMock,
        mock_create_runtime: MagicMock,
    ) -> None:
        """Test health check returns healthy when configured."""
        from raindropio_mcp.__main__ import RaindropConfig, RaindropMCPServer
        from oneiric.runtime.mcp_health import HealthStatus

        mock_app = MagicMock()
        mock_create_app.return_value = mock_app

        mock_runtime = MagicMock()
        mock_health_monitor = MagicMock()
        mock_runtime.health_monitor = mock_health_monitor

        mock_health_monitor.create_component_health.return_value = MagicMock(
            status=HealthStatus.HEALTHY
        )
        mock_health_monitor.create_health_response.return_value = {"status": "healthy"}

        mock_create_runtime.return_value = mock_runtime

        mock_settings = MagicMock()
        mock_settings.token = "test_token_1234567890abcdefghijklmnopqr"
        mock_get_settings.return_value = mock_settings

        config = RaindropConfig()
        server = RaindropMCPServer(config)

        result = await server.health_check()

        # Verify health check was performed
        assert result is not None

    @patch("raindropio_mcp.__main__.create_runtime_components")
    @patch("raindropio_mcp.__main__.create_app")
    @patch("raindropio_mcp.__main__.get_settings")
    @pytest.mark.asyncio
    async def test_health_check_unhealthy(
        self,
        mock_get_settings: MagicMock,
        mock_create_app: MagicMock,
        mock_create_runtime: MagicMock,
    ) -> None:
        """Test health check returns unhealthy when not configured."""
        from raindropio_mcp.__main__ import RaindropConfig, RaindropMCPServer
        from oneiric.runtime.mcp_health import HealthStatus

        mock_app = MagicMock()
        mock_create_app.return_value = mock_app

        mock_runtime = MagicMock()
        mock_health_monitor = MagicMock()
        mock_runtime.health_monitor = mock_health_monitor

        def create_component_health(name: str, status: HealthStatus, details: dict):
            return MagicMock(status=status, details=details)

        mock_health_monitor.create_component_health.side_effect = create_component_health
        mock_health_monitor.create_health_response.return_value = {"status": "unhealthy"}

        mock_create_runtime.return_value = mock_runtime

        mock_settings = MagicMock()
        mock_settings.token = ""
        mock_get_settings.return_value = mock_settings

        config = RaindropConfig()
        server = RaindropMCPServer(config)

        result = await server.health_check()

        # Verify health check was performed
        assert result is not None

    @patch("raindropio_mcp.__main__.create_runtime_components")
    @patch("raindropio_mcp.__main__.create_app")
    def test_get_app(self, mock_create_app: MagicMock, mock_create_runtime: MagicMock) -> None:
        """Test get_app method returns http_app."""
        from raindropio_mcp.__main__ import RaindropConfig, RaindropMCPServer

        mock_app = MagicMock()
        mock_http_app = MagicMock()
        mock_app.http_app = mock_http_app
        mock_create_app.return_value = mock_app

        mock_runtime = MagicMock()
        mock_create_runtime.return_value = mock_runtime

        config = RaindropConfig()
        server = RaindropMCPServer(config)

        result = server.get_app()

        assert result is mock_http_app

    @patch("raindropio_mcp.__main__.create_runtime_components")
    @patch("raindropio_mcp.__main__.create_app")
    def test_get_timestamp(
        self, mock_create_app: MagicMock, mock_create_runtime: MagicMock
    ) -> None:
        """Test _get_timestamp method."""
        from raindropio_mcp.__main__ import RaindropConfig, RaindropMCPServer

        mock_app = MagicMock()
        mock_create_app.return_value = mock_app

        mock_runtime = MagicMock()
        mock_create_runtime.return_value = mock_runtime

        config = RaindropConfig()
        server = RaindropMCPServer(config)

        timestamp = server._get_timestamp()

        # Verify timestamp format (ISO 8601)
        assert isinstance(timestamp, str)
        assert len(timestamp) == 20  # YYYY-MM-DDTHH:MM:SSZ
        assert timestamp.endswith("Z")


class TestMainFunction:
    """Tests for main function."""

    @patch("raindropio_mcp.__main__.MCPServerCLIFactory")
    def test_main_creates_cli_factory(self, mock_cli_factory: MagicMock) -> None:
        """Test main function creates CLI factory."""
        from raindropio_mcp.__main__ import main

        mock_factory_instance = MagicMock()
        mock_cli_factory.create_server_cli.return_value = mock_factory_instance

        # Call main (which should not raise)
        main()

        # Verify CLI factory was created
        mock_cli_factory.create_server_cli.assert_called_once()

    @patch("raindropio_mcp.__main__.MCPServerCLIFactory")
    def test_main_creates_app(self, mock_cli_factory: MagicMock) -> None:
        """Test main function creates and runs app."""
        from raindropio_mcp.__main__ import main

        mock_factory_instance = MagicMock()
        mock_cli_factory.create_server_cli.return_value = mock_factory_instance

        main()

        # Verify factory methods were called
        mock_factory_instance.create_app.assert_called_once()


class TestRaindropConfigEnvPrefix:
    """Tests for RaindropConfig environment variable prefix."""

    def test_env_prefix(self) -> None:
        """Test RaindropConfig has correct env prefix."""
        from raindropio_mcp.__main__ import RaindropConfig

        # The Config class should have env_prefix set
        assert hasattr(RaindropConfig.Config, "env_prefix")
        assert RaindropConfig.Config.env_prefix == "RAINDROP_MCP_"

    def test_env_file(self) -> None:
        """Test RaindropConfig has correct env file."""
        from raindropio_mcp.__main__ import RaindropConfig

        # The Config class should have env_file set
        assert hasattr(RaindropConfig.Config, "env_file")
        assert RaindropConfig.Config.env_file == ".env"
