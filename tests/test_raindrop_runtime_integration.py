"""Runtime integration test for Raindrop.io MCP Server.

This test verifies the Oneiric runtime integration is working correctly.
Tests import paths, configuration loading, and basic lifecycle operations.
"""

import pytest
from unittest.mock import AsyncMock, patch


# Test 1: Verify Oneiric modules can be imported
def test_oneiric_imports():
    """Test that Oneiric runtime modules are accessible."""
    # Core CLI imports
    from oneiric.core.cli import MCPServerCLIFactory
    from oneiric.core.config import OneiricMCPConfig

    # Runtime imports
    from oneiric.runtime.snapshot import RuntimeSnapshotManager
    from oneiric.runtime.cache import RuntimeCacheManager
    from oneiric.runtime.mcp_health import HealthCheckResponse, HealthStatus, HealthMonitor

    # Verify classes exist
    assert MCPServerCLIFactory is not None
    assert OneiricMCPConfig is not None
    assert RuntimeSnapshotManager is not None
    assert RuntimeCacheManager is not None
    assert HealthMonitor is not None
    assert HealthStatus is not None
    assert HealthCheckResponse is not None


# Test 2: Verify RaindropConfig configuration class
def test_raindrop_config():
    """Test that RaindropConfig can be instantiated."""
    from raindropio_mcp.__main__ import RaindropConfig

    # Create configuration with defaults
    config = RaindropConfig()

    # Verify default values
    assert config.http_port == 3034
    assert config.http_host == "127.0.0.1"
    assert config.enable_http_transport is True
    assert config.cache_dir is None or config.cache_dir == ".oneiric_cache"


# Test 3: Verify RaindropMCPServer can be created
@patch('raindropio_mcp.__main__.create_app')
def test_raindrop_server_creation(mock_create_app):
    """Test that RaindropMCPServer can be instantiated."""
    from raindropio_mcp.__main__ import RaindropConfig, RaindropMCPServer

    # Create mock app
    mock_app = AsyncMock()
    mock_app.http_app = AsyncMock()
    mock_create_app.return_value = mock_app

    # Create configuration
    config = RaindropConfig()

    # Create server instance
    server = RaindropMCPServer(config)

    # Verify runtime components are initialized
    assert server.config is not None
    assert server.snapshot_manager is not None
    assert server.cache_manager is not None
    assert server.health_monitor is not None
    assert server.app is not None


# Test 4: Verify health check can be executed
@pytest.mark.asyncio
@patch('raindropio_mcp.__main__.create_app')
@patch('raindropio_mcp.__main__.get_settings')
async def test_raindrop_health_check(mock_get_settings, mock_create_app):
    """Test that health check method works."""
    from raindropio_mcp.__main__ import RaindropConfig, RaindropMCPServer

    # Create mock settings
    mock_settings = AsyncMock()
    mock_settings.token = "x" * 32  # Valid 32-character token
    mock_get_settings.return_value = mock_settings

    # Create mock app
    mock_app = AsyncMock()
    mock_app.http_app = AsyncMock()
    mock_create_app.return_value = mock_app

    # Create server
    config = RaindropConfig()
    server = RaindropMCPServer(config)

    # Execute health check
    health_response = await server.health_check()

    # Verify response structure
    assert health_response is not None
    assert hasattr(health_response, 'status')
    assert hasattr(health_response, 'components')
    assert len(health_response.components) > 0


# Test 5: Verify cache directory can be configured
def test_cache_directory_configuration():
    """Test that custom cache directory can be set."""
    from raindropio_mcp.__main__ import RaindropConfig

    # Create config with custom cache dir
    config = RaindropConfig(cache_dir="/tmp/test_cache")

    # Verify cache directory is set
    assert config.cache_dir == "/tmp/test_cache"


# Test 6: Verify CLI factory can be created
def test_cli_factory_creation():
    """Test that MCPServerCLIFactory can be created for Raindrop.io."""
    from oneiric.core.cli import MCPServerCLIFactory
    from raindropio_mcp.__main__ import RaindropConfig, RaindropMCPServer

    # Create CLI factory
    cli_factory = MCPServerCLIFactory(
        server_class=RaindropMCPServer,
        config_class=RaindropConfig,
        name="raindropio-mcp",
        use_subcommands=True,
        legacy_flags=False,
        description="Raindrop.io MCP Server - Bookmark management via Raindrop.io API"
    )

    # Verify factory configuration
    assert cli_factory.server_class == RaindropMCPServer
    assert cli_factory.config_class == RaindropConfig
    assert cli_factory.name == "raindropio-mcp"
    assert cli_factory.use_subcommands is True
    assert cli_factory.legacy_flags is False


# Test 7: Verify environment prefix configuration
def test_environment_prefix():
    """Test that environment variable prefix is correctly configured."""
    from raindropio_mcp.__main__ import RaindropConfig

    # Check Config class attributes
    assert hasattr(RaindropConfig.Config, 'env_prefix')
    assert RaindropConfig.Config.env_prefix == "RAINDROP_MCP_"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
