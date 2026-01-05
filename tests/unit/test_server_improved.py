"""Improved tests for the server module to increase coverage."""

import importlib.util
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from fastmcp import FastMCP

from raindropio_mcp.server import (
    APP_NAME,
    APP_VERSION,
    RATE_LIMITING_AVAILABLE,
    SECURITY_AVAILABLE,
    SERVERPANELS_AVAILABLE,
    __getattr__,
    create_app,
)


def test_server_availability_flags():
    """Test the availability flags for optional features."""
    # These are set at module level based on importlib checks
    assert isinstance(RATE_LIMITING_AVAILABLE, bool)
    assert isinstance(SERVERPANELS_AVAILABLE, bool)
    assert isinstance(SECURITY_AVAILABLE, bool)


@patch("raindropio_mcp.server.create_app")
def test_getattr_app(mock_create_app):
    """Test the __getattr__ function for 'app'."""
    mock_app = MagicMock()
    mock_create_app.return_value = mock_app

    result = __getattr__("app")
    assert result == mock_app
    mock_create_app.assert_called_once()


@patch("raindropio_mcp.server.create_app")
def test_getattr_http_app(mock_create_app):
    """Test the __getattr__ function for 'http_app'."""
    mock_app = MagicMock()
    mock_http_app = MagicMock()
    mock_app.http_app = mock_http_app
    mock_create_app.return_value = mock_app

    result = __getattr__("http_app")
    assert result == mock_http_app
    mock_create_app.assert_called_once()


def test_getattr_invalid_attribute():
    """Test the __getattr__ function with invalid attribute."""
    with pytest.raises(AttributeError, match="module 'raindropio_mcp.server' has no attribute 'invalid_attr'"):
        __getattr__("invalid_attr")


@patch("raindropio_mcp.server.get_settings")
@patch("raindropio_mcp.server.RATE_LIMITING_AVAILABLE", True)
@patch("raindropio_mcp.server.hasattr")
def test_create_app_with_rate_limiting_not_addable(mock_hasattr, mock_get_settings):
    """Test create_app with rate limiting available but not addable to server."""
    # Mock settings
    mock_settings = MagicMock()
    mock_settings.token = "test_token_1234567890abcdefghijklmnopqr"
    mock_get_settings.return_value = mock_settings

    # Mock hasattr to return False so middleware is not added
    mock_hasattr.return_value = False

    # Mock the app's _mcp_server
    with patch("raindropio_mcp.server.FastMCP") as mock_fastmcp_class:
        mock_app = MagicMock()
        mock_server = MagicMock()
        mock_app._mcp_server = mock_server
        mock_fastmcp_class.return_value = mock_app

        # Create the app
        result = create_app()

        # Verify that rate limiting middleware was NOT added
        # (because hasattr returned False)
        mock_server.add_middleware.assert_not_called()


@patch("raindropio_mcp.server.get_settings")
@patch("raindropio_mcp.server.RATE_LIMITING_AVAILABLE", False)  # Rate limiting not available
def test_create_app_without_rate_limiting(mock_get_settings):
    """Test create_app without rate limiting."""
    # Mock settings
    mock_settings = MagicMock()
    mock_settings.token = "test_token_1234567890abcdefghijklmnopqr"
    mock_get_settings.return_value = mock_settings

    # Mock the app's _mcp_server
    with patch("raindropio_mcp.server.FastMCP") as mock_fastmcp_class:
        mock_app = MagicMock()
        mock_server = MagicMock()
        mock_app._mcp_server = mock_server
        mock_fastmcp_class.return_value = mock_app

        # Create the app
        result = create_app()

        # Verify that rate limiting middleware was NOT added
        # (because RATE_LIMITING_AVAILABLE is False)
        mock_server.add_middleware.assert_not_called()


@patch("raindropio_mcp.server.get_settings")
@patch("raindropio_mcp.server.build_raindrop_client")
@patch("raindropio_mcp.server.register_all_tools")
def test_create_app_lifespan_exception(mock_register_tools, mock_build_client, mock_get_settings):
    """Test the lifespan context manager when an exception occurs."""
    # Mock settings and client
    mock_settings = MagicMock()
    mock_settings.token = "test_token_1234567890abcdefghijklmnopqr"
    mock_client = AsyncMock()
    mock_get_settings.return_value = mock_settings
    mock_build_client.return_value = mock_client

    test_app = create_app()

    # Get the lifespan context manager
    lifespan = test_app._mcp_server.lifespan

    # Test the context manager with an exception
    async def test_with_exception():
        try:
            async with lifespan(test_app._mcp_server):
                raise ValueError("Test exception")
        except ValueError:
            pass  # Expected

    # Run the test
    import asyncio
    asyncio.run(test_with_exception())

    # Verify the client close was called when exiting the context (even with exception)
    mock_client.close.assert_called_once()


def test_app_constants():
    """Test the app constants."""
    assert APP_NAME == "raindropio-mcp"
    assert isinstance(APP_VERSION, str)
    assert len(APP_VERSION) > 0
