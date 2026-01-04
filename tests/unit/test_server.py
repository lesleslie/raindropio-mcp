"""Unit tests for the server module."""

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
    create_app,
    __getattr__,
)


@pytest.mark.asyncio
@patch("raindropio_mcp.server.get_settings")
async def test_create_app(mock_get_settings: object) -> None:
    """Test the create_app function."""
    # Mock settings with a valid token
    mock_settings = MagicMock()
    mock_settings.token = "test_token_1234567890abcdefghijklmnopqr"  # At least 32 chars
    mock_get_settings.return_value = mock_settings

    # Create a test app
    test_app = create_app()

    # Verify the app is created correctly
    assert isinstance(test_app, FastMCP)
    assert test_app.name == APP_NAME
    assert test_app.version == APP_VERSION

    # Check that client is attached to app
    assert hasattr(test_app, "_raindrop_client")

    # Verify lifespan context manager is properly wrapped
    original_lifespan = test_app._mcp_server.lifespan
    assert original_lifespan is not None


@patch("raindropio_mcp.server.build_raindrop_client")
@patch("raindropio_mcp.server.get_settings")
def test_create_app_integration(
    mock_get_settings: object, mock_build_client: object
) -> None:
    """Integration test for create_app."""
    # Mock settings and client
    mock_settings = MagicMock()
    mock_client = AsyncMock()
    mock_get_settings.return_value = mock_settings
    mock_build_client.return_value = mock_client

    # Create app
    test_app = create_app()

    # Verify all steps were called
    mock_get_settings.assert_called_once()
    mock_build_client.assert_called_once_with(mock_settings)

    # Verify client was attached to app
    assert test_app._raindrop_client == mock_client


@pytest.mark.asyncio
@patch("raindropio_mcp.server.get_settings")
async def test_app_lifespan(mock_get_settings: object) -> None:
    """Test the lifespan context manager."""
    # Mock settings with a valid token
    mock_settings = MagicMock()
    mock_settings.token = "test_token_1234567890abcdefghijklmnopqr"  # At least 32 chars
    mock_get_settings.return_value = mock_settings

    test_app = create_app()

    # Get the lifespan context manager
    lifespan = test_app._mcp_server.lifespan

    # Test the context manager
    async with lifespan(test_app._mcp_server):
        # State should be the original state from the server
        pass

    # Verify the client close was called when exiting the context
    await test_app._raindrop_client.close()


@patch("raindropio_mcp.server.importlib.util.find_spec")
def test_server_availability_flags(mock_find_spec: object) -> None:
    """Test the availability flags for optional features."""
    # Test RATE_LIMITING_AVAILABLE
    mock_find_spec.return_value = True
    assert importlib.util.find_spec("fastmcp.server.middleware.rate_limiting") is not None

    # Test SERVERPANELS_AVAILABLE
    mock_find_spec.return_value = True
    assert importlib.util.find_spec("mcp_common.ui") is not None


@patch("raindropio_mcp.server.create_app")
def test_getattr_app(mock_create_app: object) -> None:
    """Test the __getattr__ function for 'app'."""
    mock_app = MagicMock()
    mock_create_app.return_value = mock_app

    result = __getattr__("app")
    assert result == mock_app
    mock_create_app.assert_called_once()


@patch("raindropio_mcp.server.create_app")
def test_getattr_http_app(mock_create_app: object) -> None:
    """Test the __getattr__ function for 'http_app'."""
    mock_app = MagicMock()
    mock_http_app = MagicMock()
    mock_app.http_app = mock_http_app
    mock_create_app.return_value = mock_app

    result = __getattr__("http_app")
    assert result == mock_http_app
    mock_create_app.assert_called_once()


def test_getattr_invalid_attribute() -> None:
    """Test the __getattr__ function with invalid attribute."""
    with pytest.raises(AttributeError):
        __getattr__("invalid_attr")


@patch("raindropio_mcp.server.get_settings")
@patch("raindropio_mcp.server.RATE_LIMITING_AVAILABLE", True)
@patch("raindropio_mcp.server.hasattr")
def test_create_app_with_rate_limiting(
    mock_hasattr: object, mock_get_settings: object
) -> None:
    """Test create_app with rate limiting enabled."""
    # Mock settings
    mock_settings = MagicMock()
    mock_settings.token = "test_token_1234567890abcdefghijklmnopqr"
    mock_get_settings.return_value = mock_settings

    # Mock hasattr to return True so middleware is added
    mock_hasattr.return_value = True

    # Mock the RateLimitingMiddleware from the fastmcp module
    with patch("fastmcp.server.middleware.rate_limiting.RateLimitingMiddleware") as mock_rate_limiter_class:
        mock_rate_limiter_instance = MagicMock()
        mock_rate_limiter_class.return_value = mock_rate_limiter_instance

        # Mock the app's _mcp_server
        with patch("raindropio_mcp.server.FastMCP") as mock_fastmcp_class:
            mock_app = MagicMock()
            mock_server = MagicMock()
            mock_app._mcp_server = mock_server
            mock_fastmcp_class.return_value = mock_app

            # Create the app
            result = create_app()

            # Verify that rate limiting middleware was added
            mock_rate_limiter_class.assert_called_once_with(
                max_requests_per_second=8.0,
                burst_capacity=16,
                global_limit=True,
            )
            mock_server.add_middleware.assert_called_once_with(mock_rate_limiter_instance)
