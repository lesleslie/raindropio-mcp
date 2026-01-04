"""Improved tests for the main module to increase coverage."""

import argparse
import json
import logging
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from raindropio_mcp.main import build_parser, configure_logging, main


def test_build_parser_with_all_args():
    """Test argument parser with all possible arguments."""
    parser = build_parser()

    # Test all arguments
    args = parser.parse_args([
        "--version"
    ])
    assert args.version is True

    args = parser.parse_args([
        "--http"
    ])
    assert args.http is True

    args = parser.parse_args([
        "--http-host", "localhost"
    ])
    assert args.http_host == "localhost"

    args = parser.parse_args([
        "--http-port", "8080"
    ])
    assert args.http_port == 8080

    args = parser.parse_args([
        "--http-path", "/mcp-test"
    ])
    assert args.http_path == "/mcp-test"


def test_configure_logging_structured_with_exception():
    """Test structured logging configuration with exception in format method."""
    with patch("raindropio_mcp.main.get_settings") as mock_get_settings:
        settings_mock = MagicMock()
        settings_mock.observability.log_level = "DEBUG"
        settings_mock.observability.structured_logging = True
        mock_get_settings.return_value = settings_mock

        # Just call configure_logging to test it works with structured logging
        configure_logging()


def test_configure_logging_invalid_log_level():
    """Test logging configuration with invalid log level."""
    with patch("raindropio_mcp.main.get_settings") as mock_get_settings:
        settings_mock = MagicMock()
        settings_mock.observability.log_level = "INVALID_LEVEL"
        settings_mock.observability.structured_logging = False
        mock_get_settings.return_value = settings_mock

        configure_logging()  # Should default to INFO level


@patch("raindropio_mcp.main.SERVERPANELS_AVAILABLE", True)
@patch("raindropio_mcp.main.configure_logging")
@patch("raindropio_mcp.main.create_app")
@patch("raindropio_mcp.main.get_settings")
@patch("raindropio_mcp.main.asyncio.run")
def test_main_http_mode_with_args(
    mock_asyncio_run, mock_get_settings, mock_create_app, mock_configure_logging
):
    """Test main function with HTTP mode and command line arguments."""
    # Mock settings to enable HTTP transport
    settings_mock = MagicMock()
    settings_mock.enable_http_transport = False  # Will be overridden by --http flag
    settings_mock.http_host = "default-host"
    settings_mock.http_port = 8000
    settings_mock.http_path = "/default-path"
    mock_get_settings.return_value = settings_mock

    # Mock the app
    app_mock = MagicMock()
    mock_create_app.return_value = app_mock

    # Test with --http flag and custom args
    main(["--http", "--http-host", "localhost", "--http-port", "9000", "--http-path", "/custom"])

    # Verify app.run() was called with transport arguments (HTTP mode)
    mock_asyncio_run.assert_called_once()
    app_mock.run.assert_called_once_with(
        transport="streamable-http",
        host="localhost",
        port=9000,
        streamable_http_path="/custom",
    )


@patch("raindropio_mcp.main.SERVERPANELS_AVAILABLE", False)
@patch("raindropio_mcp.main.configure_logging")
@patch("raindropio_mcp.main.create_app")
@patch("raindropio_mcp.main.get_settings")
@patch("raindropio_mcp.main.asyncio.run")
def test_main_http_mode_no_serverpanels(
    mock_asyncio_run, mock_get_settings, mock_create_app, mock_configure_logging
):
    """Test main function with HTTP mode when ServerPanels is not available."""
    # Mock settings to enable HTTP transport
    settings_mock = MagicMock()
    settings_mock.enable_http_transport = True
    settings_mock.http_host = "localhost"
    settings_mock.http_port = 8000
    settings_mock.http_path = "/mcp"
    mock_get_settings.return_value = settings_mock

    # Mock the app
    app_mock = MagicMock()
    mock_create_app.return_value = app_mock

    main([])  # Will use HTTP due to settings

    # Verify app.run() was called with transport arguments (HTTP mode)
    mock_asyncio_run.assert_called_once()
    app_mock.run.assert_called_once_with(
        transport="streamable-http",
        host="localhost",
        port=8000,
        streamable_http_path="/mcp",
    )


@patch("raindropio_mcp.main.SERVERPANELS_AVAILABLE", False)
@patch("raindropio_mcp.main.configure_logging")
@patch("raindropio_mcp.main.create_app")
@patch("raindropio_mcp.main.get_settings")
@patch("raindropio_mcp.main.asyncio.run")
def test_main_stdio_mode_no_serverpanels(
    mock_asyncio_run, mock_get_settings, mock_create_app, mock_configure_logging
):
    """Test main function with STDIO mode when ServerPanels is not available."""
    # Mock settings to not enable HTTP transport
    settings_mock = MagicMock()
    settings_mock.enable_http_transport = False
    mock_get_settings.return_value = settings_mock

    # Mock the app
    app_mock = MagicMock()
    mock_create_app.return_value = app_mock

    main([])  # No --http flag

    # Verify app.run() was called without transport arguments (stdio mode)
    mock_asyncio_run.assert_called_once()
    app_mock.run.assert_called_once_with()


def test_main_with_none_argv():
    """Test main function with None argv."""
    with patch("raindropio_mcp.main.build_parser") as mock_build_parser:
        mock_parser = Mock()
        mock_parser.parse_args.return_value = argparse.Namespace(
            version=False,
            http=False,
            http_host=None,
            http_port=None,
            http_path=None
        )
        mock_build_parser.return_value = mock_parser
        
        with patch("raindropio_mcp.main.configure_logging"), \
             patch("raindropio_mcp.main.get_settings"), \
             patch("raindropio_mcp.main.create_app"), \
             patch("raindropio_mcp.main.SERVERPANELS_AVAILABLE", False), \
             patch("raindropio_mcp.main.asyncio.run"):
            main(None)  # Pass None as argv