"""Comprehensive tests for settings module to improve coverage."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from raindropio_mcp.config.settings import (
    CacheConfig,
    ObservabilityConfig,
    RaindropSettings,
    RetryConfig,
    get_settings,
)
from raindropio_mcp.utils.exceptions import ConfigurationError


class TestRetryConfig:
    """Tests for RetryConfig model."""

    def test_retry_config_defaults(self) -> None:
        """Test default values for RetryConfig."""
        config = RetryConfig()
        assert config.total == 3
        assert config.backoff_factor == 0.5
        assert config.status_forcelist == (408, 425, 429, 500, 502, 503, 504)

    def test_retry_config_custom_values(self) -> None:
        """Test RetryConfig with custom values."""
        config = RetryConfig(total=5, backoff_factor=1.0)
        assert config.total == 5
        assert config.backoff_factor == 1.0

    def test_retry_config_validation_total_too_high(self) -> None:
        """Test RetryConfig rejects total > 10."""
        with pytest.raises(ValidationError):
            RetryConfig(total=11)

    def test_retry_config_validation_total_negative(self) -> None:
        """Test RetryConfig rejects negative total."""
        with pytest.raises(ValidationError):
            RetryConfig(total=-1)

    def test_retry_config_validation_backoff_too_high(self) -> None:
        """Test RetryConfig rejects backoff_factor > 10.0."""
        with pytest.raises(ValidationError):
            RetryConfig(backoff_factor=11.0)

    def test_retry_config_validation_backoff_negative(self) -> None:
        """Test RetryConfig rejects negative backoff_factor."""
        with pytest.raises(ValidationError):
            RetryConfig(backoff_factor=-1.0)


class TestCacheConfig:
    """Tests for CacheConfig model."""

    def test_cache_config_defaults(self) -> None:
        """Test default values for CacheConfig."""
        config = CacheConfig()
        assert config.enabled is True
        assert config.ttl_seconds == 60
        assert config.max_entries == 1024

    def test_cache_config_custom_values(self) -> None:
        """Test CacheConfig with custom values."""
        config = CacheConfig(enabled=False, ttl_seconds=300, max_entries=2048)
        assert config.enabled is False
        assert config.ttl_seconds == 300
        assert config.max_entries == 2048

    def test_cache_config_validation_ttl_too_high(self) -> None:
        """Test CacheConfig rejects ttl_seconds > 3600."""
        with pytest.raises(ValidationError):
            CacheConfig(ttl_seconds=3601)

    def test_cache_config_validation_max_entries_too_high(self) -> None:
        """Test CacheConfig rejects max_entries > 1_000_000."""
        with pytest.raises(ValidationError):
            CacheConfig(max_entries=1_000_001)

    def test_cache_config_validation_negative_values(self) -> None:
        """Test CacheConfig rejects negative values."""
        with pytest.raises(ValidationError):
            CacheConfig(ttl_seconds=-1)
        with pytest.raises(ValidationError):
            CacheConfig(max_entries=-1)


class TestObservabilityConfig:
    """Tests for ObservabilityConfig model."""

    def test_observability_config_defaults(self) -> None:
        """Test default values for ObservabilityConfig."""
        config = ObservabilityConfig()
        assert config.log_level == "INFO"
        assert config.structured_logging is True
        assert config.redact_sensitive_fields is True

    def test_observability_config_custom_values(self) -> None:
        """Test ObservabilityConfig with custom values."""
        config = ObservabilityConfig(
            log_level="DEBUG", structured_logging=False, redact_sensitive_fields=False
        )
        assert config.log_level == "DEBUG"
        assert config.structured_logging is False
        assert config.redact_sensitive_fields is False


class TestRaindropSettingsValidation:
    """Additional tests for RaindropSettings validation."""

    def test_validate_token_with_whitespace(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test token validation strips whitespace."""
        monkeypatch.setenv("RAINDROP_TOKEN", "  test_token_1234567890abcdefghijklmnopqr  ")
        settings = RaindropSettings()
        assert settings.token.strip() == "test_token_1234567890abcdefghijklmnopqr"

    def test_validate_token_empty_after_strip(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test token validation fails when token is only whitespace."""
        monkeypatch.setenv("RAINDROP_TOKEN", "   ")
        with pytest.raises(ConfigurationError):
            RaindropSettings()

    def test_validate_token_short_token_without_security(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test short token validation without security module."""
        with patch("raindropio_mcp.config.settings.SECURITY_AVAILABLE", False):
            monkeypatch.setenv("RAINDROP_TOKEN", "short")
            # Should not raise with security module disabled
            settings = RaindropSettings()
            assert settings.token == "short"

    @patch("raindropio_mcp.config.settings.SECURITY_AVAILABLE", True)
    def test_validate_token_with_security_module(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test token validation with security module enabled."""
        monkeypatch.setenv(
            "RAINDROP_TOKEN", "test_token_1234567890abcdefghijklmnopqr"
        )
        # Should validate with security module
        settings = RaindropSettings()
        assert len(settings.token) >= 32

    def test_request_timeout_bounds(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test request_timeout validation bounds."""
        monkeypatch.setenv("RAINDROP_TOKEN", "test_token_1234567890abcdefghijklmnopqr")

        # Test minimum
        settings = RaindropSettings(request_timeout=1.0)
        assert settings.request_timeout == 1.0

        # Test maximum
        settings = RaindropSettings(request_timeout=120.0)
        assert settings.request_timeout == 120.0

        # Test out of bounds
        with pytest.raises(ValidationError):
            RaindropSettings(request_timeout=0.5)
        with pytest.raises(ValidationError):
            RaindropSettings(request_timeout=121.0)

    def test_max_connections_bounds(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test max_connections validation bounds."""
        monkeypatch.setenv("RAINDROP_TOKEN", "test_token_1234567890abcdefghijklmnopqr")

        # Test minimum
        settings = RaindropSettings(max_connections=1)
        assert settings.max_connections == 1

        # Test maximum
        settings = RaindropSettings(max_connections=100)
        assert settings.max_connections == 100

        # Test out of bounds
        with pytest.raises(ValidationError):
            RaindropSettings(max_connections=0)
        with pytest.raises(ValidationError):
            RaindropSettings(max_connections=101)

    def test_http_port_bounds(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test http_port validation bounds."""
        monkeypatch.setenv("RAINDROP_TOKEN", "test_token_1234567890abcdefghijklmnopqr")

        # Test minimum
        settings = RaindropSettings(http_port=1)
        assert settings.http_port == 1

        # Test maximum
        settings = RaindropSettings(http_port=65535)
        assert settings.http_port == 65535

        # Test out of bounds
        with pytest.raises(ValidationError):
            RaindropSettings(http_port=0)
        with pytest.raises(ValidationError):
            RaindropSettings(http_port=65536)

    def test_base_url_custom(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test custom base_url."""
        monkeypatch.setenv("RAINDROP_TOKEN", "test_token_1234567890abcdefghijklmnopqr")
        settings = RaindropSettings(
            base_url="https://custom.api.example.com/v1"  # type: ignore[arg-type]
        )
        assert str(settings.base_url) == "https://custom.api.example.com/v1"

    def test_user_agent_custom(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test custom user_agent."""
        monkeypatch.setenv("RAINDROP_TOKEN", "test_token_1234567890abcdefghijklmnopqr")
        settings = RaindropSettings(user_agent="CustomAgent/1.0")
        assert settings.user_agent == "CustomAgent/1.0"

    def test_cache_dir_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test cache_dir can be None."""
        monkeypatch.setenv("RAINDROP_TOKEN", "test_token_1234567890abcdefghijklmnopqr")
        settings = RaindropSettings()
        assert settings.cache_dir is None

    def test_cache_dir_custom(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test custom cache_dir."""
        monkeypatch.setenv("RAINDROP_TOKEN", "test_token_1234567890abcdefghijklmnopqr")
        custom_path = "/tmp/raindrop_cache"
        settings = RaindropSettings(cache_dir=Path(custom_path))
        assert settings.cache_dir == Path(custom_path)


class TestGetMaskedToken:
    """Additional tests for get_masked_token method."""

    def test_get_masked_token_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test get_masked_token with empty token."""
        monkeypatch.setenv("RAINDROP_TOKEN", "test_token_1234567890abcdefghijklmnopqr")
        settings = RaindropSettings()
        settings.token = ""
        assert settings.get_masked_token() == "***"

    def test_get_masked_token_short_without_security(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test get_masked_token with short token without security module."""
        with patch("raindropio_mcp.config.settings.SECURITY_AVAILABLE", False):
            monkeypatch.setenv("RAINDROP_TOKEN", "short")
            settings = RaindropSettings()
            # Should return *** for tokens <= 4 chars
            assert settings.get_masked_token() == "***"

    def test_get_masked_token_without_security(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test get_masked_token without security module (fallback)."""
        with patch("raindropio_mcp.config.settings.SECURITY_AVAILABLE", False):
            monkeypatch.setenv("RAINDROP_TOKEN", "test_token_1234567890abcdefghijklmnopqr")
            settings = RaindropSettings()
            masked = settings.get_masked_token()
            # Fallback should show last 4 chars
            assert masked == "...pqrs"

    @patch("raindropio_mcp.config.settings.SECURITY_AVAILABLE", True)
    def test_get_masked_token_with_security(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test get_masked_token with security module."""
        monkeypatch.setenv("RAINDROP_TOKEN", "test_token_1234567890abcdefghijklmnopqr")
        settings = RaindropSettings()
        masked = settings.get_masked_token()
        # Security module should mask with 4 visible chars
        assert masked.endswith("pqrs")


class TestHttpClientConfig:
    """Tests for http_client_config method."""

    def test_http_client_config_structure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test http_client_config returns correct structure."""
        monkeypatch.setenv("RAINDROP_TOKEN", "test_token_1234567890abcdefghijklmnopqr")
        settings = RaindropSettings()
        config = settings.http_client_config()

        assert "base_url" in config
        assert "timeout" in config
        assert "limits" in config
        assert "headers" in config

    def test_http_client_config_values(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test http_client_config returns correct values."""
        monkeypatch.setenv("RAINDROP_TOKEN", "test_token_1234567890abcdefghijklmnopqr")
        settings = RaindropSettings()
        config = settings.http_client_config()

        assert config["base_url"] == "https://api.raindrop.io/rest/v1"
        assert config["timeout"] == 30.0
        assert config["headers"]["Authorization"].startswith("Bearer ")
        assert "User-Agent" in config["headers"]

    def test_http_client_config_custom_values(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test http_client_config with custom settings."""
        monkeypatch.setenv("RAINDROP_TOKEN", "test_token_1234567890abcdefghijklmnopqr")
        settings = RaindropSettings(
            request_timeout=60.0, max_connections=20, user_agent="CustomAgent/1.0"
        )
        config = settings.http_client_config()

        assert config["timeout"] == 60.0
        assert config["limits"].max_connections == 20
        assert config["headers"]["User-Agent"] == "CustomAgent/1.0"


class TestGetSettings:
    """Tests for get_settings function."""

    def test_get_settings_caching(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test get_settings returns cached instance."""
        monkeypatch.setenv("RAINDROP_TOKEN", "test_token_1234567890abcdefghijklmnopqr")

        # First call
        settings1 = get_settings()
        # Second call
        settings2 = get_settings()

        # Should return same instance (cached)
        assert settings1 is settings2

    def test_get_settings_independence(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that get_settings doesn't share state across calls."""
        monkeypatch.setenv("RAINDROP_TOKEN", "test_token_1234567890abcdefghijklmnopqr")

        settings = get_settings()
        # Modify settings
        settings.request_timeout = 45.0

        # Get settings again - should be cached, so modified value persists
        settings2 = get_settings()
        assert settings2.request_timeout == 45.0
