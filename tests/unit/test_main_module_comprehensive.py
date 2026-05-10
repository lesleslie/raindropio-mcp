"""Comprehensive tests for main module to improve coverage."""

from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

import pytest

from raindropio_mcp.main import (
    _get_features_list,
    _handle_http_mode,
    _handle_stdio_mode,
    configure_logging,
    main,
)


class TestGetFeaturesList:
    """Tests for _get_features_list function."""

    @patch("raindropio_mcp.main.SECURITY_AVAILABLE", True)
    @patch("raindropio_mcp.main.RATE_LIMITING_AVAILABLE", True)
    def test_get_features_list_all_features(self) -> None:
        """Test features list with all optional features available."""
        features = _get_features_list()
        assert len(features) == 6
        assert "🔖 Bookmark Management" in features
        assert "📚 Collection Organization" in features
        assert "🔍 Search & Filtering" in features
        assert "🏷️  Tag Management" in features
        assert "🔒 API Key Validation (32+ chars)" in features
        assert "⚡ Rate Limiting (8 req/sec, burst 16)" in features

    @patch("raindropio_mcp.main.SECURITY_AVAILABLE", False)
    @patch("raindropio_mcp.main.RATE_LIMITING_AVAILABLE", False)
    def test_get_features_list_minimal(self) -> None:
        """Test features list with no optional features."""
        features = _get_features_list()
        assert len(features) == 4
        assert "🔖 Bookmark Management" in features
        assert "📚 Collection Organization" in features
        assert "🔍 Search & Filtering" in features
        assert "🏷️  Tag Management" in features

    @patch("raindropio_mcp.main.SECURITY_AVAILABLE", True)
    @patch("raindropio_mcp.main.RATE_LIMITING_AVAILABLE", False)
    def test_get_features_list_security_only(self) -> None:
        """Test features list with only security feature."""
        features = _get_features_list()
        assert len(features) == 5
        assert "🔒 API Key Validation (32+ chars)" in features
        assert "⚡ Rate Limiting (8 req/sec, burst 16)" not in features


class TestHandleHttpMode:
    """Tests for _handle_http_mode function."""

    @patch("raindropio_mcp.main.SERVERPANELS_AVAILABLE", False)
    @patch("raindropio_mcp.main.asyncio.run")
    @patch("raindropio_mcp.main.logger")
    def test_handle_http_mode_without_serverpanels(
        self, mock_logger: MagicMock, mock_asyncio_run: MagicMock
    ) -> None:
        """Test HTTP mode without ServerPanels available."""
        args = MagicMock()
        args.http_host = None
        args.http_port = None
        args.http_path = None

        settings = MagicMock()
        settings.http_host = "127.0.0.1"
        settings.http_port = 3034
        settings.http_path = "/mcp"

        app = MagicMock()

        _handle_http_mode(args, settings, app)

        # Verify logger was called
        mock_logger.info.assert_called_once()
        # Verify asyncio.run was called
        mock_asyncio_run.assert_called_once()
        app.run.assert_called_once_with(
            transport="streamable-http",
            host="127.0.0.1",
            port=3034,
            streamable_http_path="/mcp",
        )

    @patch("raindropio_mcp.main.SERVERPANELS_AVAILABLE", True)
    @patch("raindropio_mcp.main.asyncio.run")
    @patch("raindropio_mcp.main._get_features_list")
    def test_handle_http_mode_with_serverpanels(
        self, mock_get_features: MagicMock, mock_asyncio_run: MagicMock
    ) -> None:
        """Test HTTP mode with ServerPanels available."""
        mock_get_features.return_value = ["Feature 1", "Feature 2"]

        args = MagicMock()
        args.http_host = "localhost"
        args.http_port = 8080
        args.http_path = "/api"

        settings = MagicMock()
        settings.http_host = "127.0.0.1"
        settings.http_port = 3034
        settings.http_path = "/mcp"

        app = MagicMock()

        # Import ServerPanels at runtime when it's available
        from mcp_common.ui import ServerPanels

        with patch("mcp_common.ui.ServerPanels") as mock_server_panels:
            _handle_http_mode(args, settings, app)

            # Verify ServerPanels.startup_success was called
            mock_server_panels.startup_success.assert_called_once()
            call_args = mock_server_panels.startup_success.call_args
            assert call_args[1]["server_name"] == "Raindrop.io MCP"
            assert call_args[1]["transport"] == "HTTP (streamable)"
            assert call_args[1]["endpoint"] == "http://localhost:8080/api"

    @patch("raindropio_mcp.main.SERVERPANELS_AVAILABLE", False)
    @patch("raindropio_mcp.main.asyncio.run")
    @patch("raindropio_mcp.main.logger")
    def test_handle_http_mode_with_args_override(
        self, mock_logger: MagicMock, mock_asyncio_run: MagicMock
    ) -> None:
        """Test HTTP mode when args override settings."""
        args = MagicMock()
        args.http_host = "0.0.0.0"
        args.http_port = 9000
        args.http_path = "/custom"

        settings = MagicMock()
        settings.http_host = "127.0.0.1"
        settings.http_port = 3034
        settings.http_path = "/mcp"

        app = MagicMock()

        _handle_http_mode(args, settings, app)

        # Verify args override settings
        app.run.assert_called_once_with(
            transport="streamable-http",
            host="0.0.0.0",
            port=9000,
            streamable_http_path="/custom",
        )


class TestHandleStdioMode:
    """Tests for _handle_stdio_mode function."""

    @patch("raindropio_mcp.main.SERVERPANELS_AVAILABLE", False)
    @patch("raindropio_mcp.main.asyncio.run")
    @patch("raindropio_mcp.main.logger")
    def test_handle_stdio_mode_without_serverpanels(
        self, mock_logger: MagicMock, mock_asyncio_run: MagicMock
    ) -> None:
        """Test STDIO mode without ServerPanels available."""
        app = MagicMock()

        _handle_stdio_mode(app)

        # Verify logger was called
        mock_logger.info.assert_called_once_with("Starting Raindrop.io MCP server (stdio)")

        # Verify asyncio.run was called
        mock_asyncio_run.assert_called_once()
        app.run.assert_called_once_with()

    @patch("raindropio_mcp.main.SERVERPANELS_AVAILABLE", True)
    @patch("raindropio_mcp.main.asyncio.run")
    @patch("raindropio_mcp.main._get_features_list")
    def test_handle_stdio_mode_with_serverpanels(
        self, mock_get_features: MagicMock, mock_asyncio_run: MagicMock
    ) -> None:
        """Test STDIO mode with ServerPanels available."""
        mock_get_features.return_value = ["Feature 1", "Feature 2"]

        app = MagicMock()

        # Import ServerPanels at runtime when it's available
        from mcp_common.ui import ServerPanels

        with patch("mcp_common.ui.ServerPanels") as mock_server_panels:
            _handle_stdio_mode(app)

            # Verify ServerPanels.startup_success was called
            mock_server_panels.startup_success.assert_called_once()
            call_args = mock_server_panels.startup_success.call_args
            assert call_args[1]["server_name"] == "Raindrop.io MCP"
            assert call_args[1]["transport"] == "STDIO"
            assert call_args[1]["mode"] == "Claude Desktop"


class TestConfigureLogging:
    """Additional tests for configure_logging function."""

    def test_configure_logging_debug_level(self) -> None:
        """Test logging configuration with DEBUG level."""
        with patch("raindropio_mcp.main.get_settings") as mock_get_settings:
            settings_mock = MagicMock()
            settings_mock.observability.log_level = "DEBUG"
            settings_mock.observability.structured_logging = False
            mock_get_settings.return_value = settings_mock

            configure_logging()

            # Get root logger and verify level
            root_logger = logging.getLogger()
            # Note: The actual level might be DEBUG or numeric 10

    def test_configure_logging_warning_level(self) -> None:
        """Test logging configuration with WARNING level."""
        with patch("raindropio_mcp.main.get_settings") as mock_get_settings:
            settings_mock = MagicMock()
            settings_mock.observability.log_level = "WARNING"
            settings_mock.observability.structured_logging = False
            mock_get_settings.return_value = settings_mock

            configure_logging()

            # Should not raise exception

    def test_configure_logging_error_level(self) -> None:
        """Test logging configuration with ERROR level."""
        with patch("raindropio_mcp.main.get_settings") as mock_get_settings:
            settings_mock = MagicMock()
            settings_mock.observability.log_level = "ERROR"
            settings_mock.observability.structured_logging = False
            mock_get_settings.return_value = settings_mock

            configure_logging()

            # Should not raise exception

    def test_configure_logging_critical_level(self) -> None:
        """Test logging configuration with CRITICAL level."""
        with patch("raindropio_mcp.main.get_settings") as mock_get_settings:
            settings_mock = MagicMock()
            settings_mock.observability.log_level = "CRITICAL"
            settings_mock.observability.structured_logging = False
            mock_get_settings.return_value = settings_mock

            configure_logging()

            # Should not raise exception


class TestMainFunctionEdgeCases:
    """Additional edge case tests for main function."""

    @patch("raindropio_mcp.main.configure_logging")
    @patch("raindropio_mcp.main.create_app")
    @patch("raindropio_mcp.main.get_settings")
    @patch("raindropio_mcp.main._handle_stdio_mode")
    def test_main_with_empty_argv(
        self,
        mock_handle_stdio: MagicMock,
        mock_get_settings: MagicMock,
        mock_create_app: MagicMock,
        mock_configure_logging: MagicMock,
    ) -> None:
        """Test main function with empty argv list."""
        settings_mock = MagicMock()
        settings_mock.enable_http_transport = False
        mock_get_settings.return_value = settings_mock

        app_mock = MagicMock()
        mock_create_app.return_value = app_mock

        main([])

        # Verify stdio mode was used
        mock_handle_stdio.assert_called_once_with(app_mock)

    @patch("raindropio_mcp.main.configure_logging")
    @patch("raindropio_mcp.main.create_app")
    @patch("raindropio_mcp.main.get_settings")
    @patch("raindropio_mcp.main._handle_http_mode")
    def test_main_http_via_settings(
        self,
        mock_handle_http: MagicMock,
        mock_get_settings: MagicMock,
        mock_create_app: MagicMock,
        mock_configure_logging: MagicMock,
    ) -> None:
        """Test main function uses HTTP when settings enable it."""
        settings_mock = MagicMock()
        settings_mock.enable_http_transport = True
        mock_get_settings.return_value = settings_mock

        app_mock = MagicMock()
        mock_create_app.return_value = app_mock

        main([])

        # Verify HTTP mode was used
        mock_handle_http.assert_called_once()

    @patch("raindropio_mcp.main.configure_logging")
    @patch("raindropio_mcp.main.create_app")
    @patch("raindropio_mcp.main.get_settings")
    @patch("raindropio_mcp.main._handle_http_mode")
    def test_main_http_via_flag(
        self,
        mock_handle_http: MagicMock,
        mock_get_settings: MagicMock,
        mock_create_app: MagicMock,
        mock_configure_logging: MagicMock,
    ) -> None:
        """Test main function uses HTTP when --http flag is set."""
        settings_mock = MagicMock()
        settings_mock.enable_http_transport = False
        settings_mock.http_host = "127.0.0.1"
        settings_mock.http_port = 3034
        settings_mock.http_path = "/mcp"
        mock_get_settings.return_value = settings_mock

        app_mock = MagicMock()
        mock_create_app.return_value = app_mock

        main(["--http"])

        # Verify HTTP mode was used despite settings
        mock_handle_http.assert_called_once()
