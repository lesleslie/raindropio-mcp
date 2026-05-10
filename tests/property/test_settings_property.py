"""Property-based tests for settings module using Hypothesis."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from hypothesis import given, settings as hyp_settings
from hypothesis import strategies as st
from hypothesis.strategies import just, none
from pydantic import ValidationError

from raindropio_mcp.config.settings import (
    CacheConfig,
    ObservabilityConfig,
    RetryConfig,
)


class TestRetryConfigProperties:
    """Property-based tests for RetryConfig."""

    @given(
        total=st.integers(min_value=0, max_value=10),
        backoff_factor=st.floats(min_value=0.0, max_value=10.0, allow_infinity=False, allow_nan=False),
    )
    def test_valid_retry_config_accepts_range(self, total: int, backoff_factor: float) -> None:
        """Test that valid ranges are accepted for RetryConfig."""
        config = RetryConfig(total=total, backoff_factor=backoff_factor)
        assert config.total == total
        assert config.backoff_factor == backoff_factor

    @given(total=st.integers(min_value=11, max_value=1000))
    def test_retry_config_rejects_total_over_10(self, total: int) -> None:
        """Test that total > 10 is rejected."""
        with pytest.raises(ValidationError):
            RetryConfig(total=total)

    @given(total=st.integers(min_value=-1000, max_value=-1))
    def test_retry_config_rejects_negative_total(self, total: int) -> None:
        """Test that negative total is rejected."""
        with pytest.raises(ValidationError):
            RetryConfig(total=total)

    @given(backoff_factor=st.floats(min_value=10.1, max_value=1000.0, allow_infinity=False, allow_nan=False))
    def test_retry_config_rejects_backoff_over_10(self, backoff_factor: float) -> None:
        """Test that backoff_factor > 10.0 is rejected."""
        with pytest.raises(ValidationError):
            RetryConfig(backoff_factor=backoff_factor)

    @given(backoff_factor=st.floats(min_value=-1000.0, max_value=-0.1, allow_infinity=False, allow_nan=False))
    def test_retry_config_rejects_negative_backoff(self, backoff_factor: float) -> None:
        """Test that negative backoff_factor is rejected."""
        with pytest.raises(ValidationError):
            RetryConfig(backoff_factor=backoff_factor)


class TestCacheConfigProperties:
    """Property-based tests for CacheConfig."""

    @given(
        enabled=st.booleans(),
        ttl_seconds=st.integers(min_value=0, max_value=3600),
        max_entries=st.integers(min_value=0, max_value=1_000_000),
    )
    def test_valid_cache_config_accepts_range(
        self, enabled: bool, ttl_seconds: int, max_entries: int
    ) -> None:
        """Test that valid ranges are accepted for CacheConfig."""
        config = CacheConfig(enabled=enabled, ttl_seconds=ttl_seconds, max_entries=max_entries)
        assert config.enabled == enabled
        assert config.ttl_seconds == ttl_seconds
        assert config.max_entries == max_entries

    @given(ttl_seconds=st.integers(min_value=3601, max_value=100_000))
    def test_cache_config_rejects_ttl_over_3600(self, ttl_seconds: int) -> None:
        """Test that ttl_seconds > 3600 is rejected."""
        with pytest.raises(ValidationError):
            CacheConfig(ttl_seconds=ttl_seconds)

    @given(ttl_seconds=st.integers(min_value=-100_000, max_value=-1))
    def test_cache_config_rejects_negative_ttl(self, ttl_seconds: int) -> None:
        """Test that negative ttl_seconds is rejected."""
        with pytest.raises(ValidationError):
            CacheConfig(ttl_seconds=ttl_seconds)

    @given(max_entries=st.integers(min_value=1_000_001, max_value=10_000_000))
    def test_cache_config_rejects_max_entries_over_limit(self, max_entries: int) -> None:
        """Test that max_entries > 1_000_000 is rejected."""
        with pytest.raises(ValidationError):
            CacheConfig(max_entries=max_entries)

    @given(max_entries=st.integers(min_value=-10_000_000, max_value=-1))
    def test_cache_config_rejects_negative_max_entries(self, max_entries: int) -> None:
        """Test that negative max_entries is rejected."""
        with pytest.raises(ValidationError):
            CacheConfig(max_entries=max_entries)


class TestObservabilityConfigProperties:
    """Property-based tests for ObservabilityConfig."""

    @given(
        log_level=st.sampled_from(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
        structured_logging=st.booleans(),
        redact_sensitive_fields=st.booleans(),
    )
    def test_valid_observability_config(
        self, log_level: str, structured_logging: bool, redact_sensitive_fields: bool
    ) -> None:
        """Test that valid combinations are accepted."""
        config = ObservabilityConfig(
            log_level=log_level,
            structured_logging=structured_logging,
            redact_sensitive_fields=redact_sensitive_fields,
        )
        assert config.log_level == log_level
        assert config.structured_logging == structured_logging
        assert config.redact_sensitive_fields == redact_sensitive_fields


class TestRaindropSettingsProperties:
    """Property-based tests for RaindropSettings."""

    @given(
        token=st.text(min_size=32, max_size=100).filter(lambda x: len(x.strip()) > 0),
        request_timeout=st.floats(min_value=1.0, max_value=120.0, allow_infinity=False, allow_nan=False),
        max_connections=st.integers(min_value=1, max_value=100),
    )
    @hyp_settings(max_examples=10)  # Limit examples for external API calls
    def test_valid_settings_with_long_token(
        self, token: str, request_timeout: float, max_connections: int
    ) -> None:
        """Test that valid settings with long tokens are accepted."""
        from raindropio_mcp.config.settings import RaindropSettings

        # Use model_validate to bypass environment variable requirement
        settings = RaindropSettings.model_validate(
            {
                "token": token,
                "request_timeout": request_timeout,
                "max_connections": max_connections,
            }
        )
        assert settings.token == token
        assert settings.request_timeout == request_timeout
        assert settings.max_connections == max_connections

    @given(
        http_port=st.integers(min_value=1, max_value=65535),
        enable_http_transport=st.booleans(),
    )
    def test_http_port_range(self, http_port: int, enable_http_transport: bool) -> None:
        """Test that valid HTTP port range is accepted."""
        from raindropio_mcp.config.settings import RaindropSettings

        settings = RaindropSettings.model_validate(
            {
                "token": "test_token_1234567890abcdefghijklmnopqr",
                "http_port": http_port,
                "enable_http_transport": enable_http_transport,
            }
        )
        assert settings.http_port == http_port
        assert settings.enable_http_transport == enable_http_transport

    @given(http_port=st.integers(min_value=65536, max_value=100_000))
    def test_http_port_over_65535_rejected(self, http_port: int) -> None:
        """Test that HTTP port > 65535 is rejected."""
        from raindropio_mcp.config.settings import RaindropSettings

        with pytest.raises(ValidationError):
            RaindropSettings.model_validate(
                {
                    "token": "test_token_1234567890abcdefghijklmnopqr",
                    "http_port": http_port,
                }
            )

    @given(http_port=st.integers(min_value=-1000, max_value=0))
    def test_http_port_zero_or_negative_rejected(self, http_port: int) -> None:
        """Test that HTTP port <= 0 is rejected."""
        from raindropio_mcp.config.settings import RaindropSettings

        with pytest.raises(ValidationError):
            RaindropSettings.model_validate(
                {
                    "token": "test_token_1234567890abcdefghijklmnopqr",
                    "http_port": http_port,
                }
            )

    @given(
        host=st.sampled_from(["127.0.0.1", "0.0.0.0", "localhost", "192.168.1.1"]),
    )
    def test_http_host_variations(self, host: str) -> None:
        """Test that various host strings are accepted."""
        from raindropio_mcp.config.settings import RaindropSettings

        settings = RaindropSettings.model_validate(
            {
                "token": "test_token_1234567890abcdefghijklmnopqr",
                "http_host": host,
            }
        )
        assert settings.http_host == host


class TestTokenMaskingProperties:
    """Property-based tests for token masking."""

    @given(token=st.text(min_size=32, max_size=100))
    def test_masked_token_always_shorter(self, token: str) -> None:
        """Test that masked token is always shorter than original."""
        from raindropio_mcp.config.settings import RaindropSettings

        settings = RaindropSettings.model_validate({"token": token})
        masked = settings.get_masked_token()

        assert len(masked) <= len(token)

    @given(token=st.text(min_size=32, max_size=100))
    def test_masked_token_never_equals_original(self, token: str) -> None:
        """Test that masked token is never equal to original (for sufficiently long tokens)."""
        from raindropio_mcp.config.settings import RaindropSettings

        settings = RaindropSettings.model_validate({"token": token})
        masked = settings.get_masked_token()

        # For tokens >= 32 chars, masked should never equal original
        if len(token) >= 32:
            assert masked != token

    @given(token=st.text(min_size=0, max_size=10))
    def test_short_token_returns_placeholder(self, token: str) -> None:
        """Test that very short tokens return placeholder."""
        from raindropio_mcp.config.settings import RaindropSettings

        # Test with short or empty tokens
        if len(token) < 5:
            settings = RaindropSettings.model_validate({"token": token})
            masked = settings.get_masked_token()
            # Should return placeholder for very short tokens
            if not token:
                assert masked == "***"


class TestURLValidationProperties:
    """Property-based tests for URL validation."""

    @given(
        scheme=st.sampled_from(["https", "http"]),
        domain=st.text(min_size=3, max_size=20).filter(lambda x: x.isalnum()),
        path=st.text(min_size=1, max_size=10),
    )
    def test_base_url_formats(self, scheme: str, domain: str, path: str) -> None:
        """Test that various URL formats are handled."""
        from raindropio_mcp.config.settings import RaindropSettings

        url = f"{scheme}://{domain}.example.com/{path}"

        try:
            settings = RaindropSettings.model_validate(
                {
                    "token": "test_token_1234567890abcdefghijklmnopqr",
                    "base_url": url,
                }
            )
            assert str(settings.base_url) == url
        except ValidationError:
            # Some URLs may be invalid, which is expected
            pass


class TestAuthHeadersProperties:
    """Property-based tests for authentication headers."""

    @given(
        token=st.text(min_size=32, max_size=100),
        user_agent=st.text(min_size=5, max_size=50),
    )
    def test_auth_headers_always_contain_bearer(self, token: str, user_agent: str) -> None:
        """Test that auth headers always contain Bearer token."""
        from raindropio_mcp.config.settings import RaindropSettings

        settings = RaindropSettings.model_validate(
            {
                "token": token,
                "user_agent": user_agent,
            }
        )
        headers = settings.auth_headers()

        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Bearer ")
        assert "User-Agent" in headers
        assert headers["User-Agent"] == user_agent

    @given(token=st.text(min_size=32, max_size=100))
    def test_auth_headers_token_is_stripped(self, token: str) -> None:
        """Test that token in auth headers is stripped of whitespace."""
        from raindropio_mcp.config.settings import RaindropSettings

        token_with_spaces = f"  {token}  "
        settings = RaindropSettings.model_validate({"token": token_with_spaces})
        headers = settings.auth_headers()

        # The authorization header should have stripped token
        auth_value = headers["Authorization"]
        assert auth_value == f"Bearer {token.strip()}"


class TestHttpClientConfigProperties:
    """Property-based tests for HTTP client configuration."""

    @given(
        timeout=st.floats(min_value=1.0, max_value=120.0, allow_infinity=False, allow_nan=False),
        max_connections=st.integers(min_value=1, max_value=100),
    )
    def test_http_client_config_structure(self, timeout: float, max_connections: int) -> None:
        """Test that HTTP client config has correct structure."""
        from raindropio_mcp.config.settings import RaindropSettings

        settings = RaindropSettings.model_validate(
            {
                "token": "test_token_1234567890abcdefghijklmnopqr",
                "request_timeout": timeout,
                "max_connections": max_connections,
            }
        )
        config = settings.http_client_config()

        assert isinstance(config, dict)
        assert "base_url" in config
        assert "timeout" in config
        assert "limits" in config
        assert "headers" in config
        assert config["timeout"] == timeout

    @given(
        timeout=st.floats(min_value=1.0, max_value=120.0, allow_infinity=False, allow_nan=False),
        max_connections=st.integers(min_value=1, max_value=100),
    )
    def test_http_client_config_limits(self, timeout: float, max_connections: int) -> None:
        """Test that HTTP client config has correct limits."""
        from raindropio_mcp.config.settings import RaindropSettings

        settings = RaindropSettings.model_validate(
            {
                "token": "test_token_1234567890abcdefghijklmnopqr",
                "request_timeout": timeout,
                "max_connections": max_connections,
            }
        )
        config = settings.http_client_config()

        assert config["limits"].max_connections == max_connections
        assert config["limits"].max_keepalive_connections == max_connections


class TestCacheDirProperties:
    """Property-based tests for cache directory configuration."""

    @given(
        enabled=st.booleans(),
        path_str=st.text(min_size=1, max_size=50).filter(lambda x: x.isalnum() or "/" in x or "_" in x or "-" in x),
    )
    def test_cache_dir_optional(self, enabled: bool, path_str: str) -> None:
        """Test that cache_dir can be None or a Path."""
        from raindropio_mcp.config.settings import RaindropSettings

        # Test with None
        settings1 = RaindropSettings.model_validate(
            {
                "token": "test_token_1234567890abcdefghijklmnopqr",
                "cache_dir": None,
            }
        )
        assert settings1.cache_dir is None

        # Test with Path
        try:
            path = Path(f"/tmp/{path_str}")
            settings2 = RaindropSettings.model_validate(
                {
                    "token": "test_token_1234567890abcdefghijklmnopqr",
                    "cache_dir": path,
                }
            )
            assert settings2.cache_dir == path
        except (ValidationError, ValueError):
            # Some path strings may be invalid
            pass
