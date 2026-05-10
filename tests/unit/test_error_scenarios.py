"""Comprehensive error scenario tests for raindropio-mcp."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest

from raindropio_mcp.clients.base_client import BaseHTTPClient
from raindropio_mcp.clients.raindrop_client import RaindropClient
from raindropio_mcp.config.settings import RaindropSettings
from raindropio_mcp.utils.exceptions import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    NotFoundError,
    RateLimitError,
)

# Alias for backwards compatibility with tests
ResourceNotFoundError = NotFoundError


class TestConfigurationErrorScenarios:
    """Test configuration error scenarios."""

    def test_missing_token_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test error when token is missing."""
        monkeypatch.delenv("RAINDROP_TOKEN", raising=False)
        with pytest.raises(ConfigurationError) as exc_info:
            RaindropSettings()
        assert "RAINDROP_TOKEN is required" in str(exc_info.value)

    def test_empty_token_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test error when token is empty string."""
        monkeypatch.setenv("RAINDROP_TOKEN", "")
        with pytest.raises(ConfigurationError) as exc_info:
            RaindropSettings()
        assert "RAINDROP_TOKEN is required" in str(exc_info.value)

    def test_whitespace_only_token_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test error when token is only whitespace."""
        monkeypatch.setenv("RAINDROP_TOKEN", "   ")
        with pytest.raises(ConfigurationError) as exc_info:
            RaindropSettings()
        assert "RAINDROP_TOKEN is required" in str(exc_info.value)


class TestAPIErrorScenarios:
    """Test API error scenarios."""

    @pytest.mark.asyncio
    async def test_404_not_found_error(self) -> None:
        """Test 404 error handling."""
        client = RaindropClient(token="test_token_1234567890abcdefghijklmnopqr")

        with patch.object(client, "_get", return_value=None) as mock_get:
            mock_get.side_effect = ResourceNotFoundError("Bookmark not found")

            with pytest.raises(ResourceNotFoundError):
                await client.get_bookmark(999999)

    @pytest.mark.asyncio
    async def test_401_unauthorized_error(self) -> None:
        """Test 401 unauthorized error handling."""
        client = RaindropClient(token="invalid_token")

        with patch.object(client, "_get") as mock_get:
            mock_get.side_effect = AuthenticationError("Invalid token")

            with pytest.raises(AuthenticationError):
                await client.get_me()

    @pytest.mark.asyncio
    async def test_403_forbidden_error(self) -> None:
        """Test 403 forbidden error handling."""
        client = RaindropClient(token="test_token_1234567890abcdefghijklmnopqr")

        with patch.object(client, "_delete") as mock_delete:
            mock_delete.side_effect = APIError("Forbidden", status_code=403)

            with pytest.raises(APIError) as exc_info:
                await client.delete_bookmark(123)
            assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_429_rate_limit_error(self) -> None:
        """Test 429 rate limit error handling."""
        client = RaindropClient(token="test_token_1234567890abcdefghijklmnopqr")

        with patch.object(client, "_get") as mock_get:
            mock_get.side_effect = RateLimitError("Rate limit exceeded")

            with pytest.raises(RateLimitError):
                await client.list_bookmarks()

    @pytest.mark.asyncio
    async def test_500_server_error(self) -> None:
        """Test 500 server error handling."""
        client = RaindropClient(token="test_token_1234567890abcdefghijklmnopqr")

        with patch.object(client, "_get") as mock_get:
            mock_get.side_effect = APIError("Internal server error", status_code=500)

            with pytest.raises(APIError) as exc_info:
                await client.list_collections()
            assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_502_bad_gateway_error(self) -> None:
        """Test 502 bad gateway error handling."""
        client = RaindropClient(token="test_token_1234567890abcdefghijklmnopqr")

        with patch.object(client, "_get") as mock_get:
            mock_get.side_effect = APIError("Bad gateway", status_code=502)

            with pytest.raises(APIError) as exc_info:
                await client.get_bookmark(123)
            assert exc_info.value.status_code == 502

    @pytest.mark.asyncio
    async def test_503_service_unavailable_error(self) -> None:
        """Test 503 service unavailable error handling."""
        client = RaindropClient(token="test_token_1234567890abcdefghijklmnopqr")

        with patch.object(client, "_get") as mock_get:
            mock_get.side_effect = APIError("Service unavailable", status_code=503)

            with pytest.raises(APIError) as exc_info:
                await client.search_bookmarks("test")
            assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_504_gateway_timeout_error(self) -> None:
        """Test 504 gateway timeout error handling."""
        client = RaindropClient(token="test_token_1234567890abcdefghijklmnopqr")

        with patch.object(client, "_get") as mock_get:
            mock_get.side_effect = APIError("Gateway timeout", status_code=504)

            with pytest.raises(APIError) as exc_info:
                await client.list_tags()
            assert exc_info.value.status_code == 504


class TestNetworkErrorScenarios:
    """Test network error scenarios."""

    @pytest.mark.asyncio
    async def test_connection_timeout(self) -> None:
        """Test connection timeout handling."""
        client = RaindropClient(token="test_token_1234567890abcdefghijklmnopqr")

        with patch.object(client, "client") as mock_client:
            mock_client.get.side_effect = httpx.ConnectTimeout("Connection timeout")

            with pytest.raises(httpx.ConnectTimeout):
                await client.list_bookmarks()

    @pytest.mark.asyncio
    async def test_read_timeout(self) -> None:
        """Test read timeout handling."""
        client = RaindropClient(token="test_token_1234567890abcdefghijklmnopqr")

        with patch.object(client, "client") as mock_client:
            mock_client.get.side_effect = httpx.ReadTimeout("Read timeout")

            with pytest.raises(httpx.ReadTimeout):
                await client.get_bookmark(123)

    @pytest.mark.asyncio
    async def test_network_error(self) -> None:
        """Test generic network error handling."""
        client = RaindropClient(token="test_token_1234567890abcdefghijklmnopqr")

        with patch.object(client, "client") as mock_client:
            mock_client.get.side_effect = httpx.NetworkError("Network unreachable")

            with pytest.raises(httpx.NetworkError):
                await client.list_collections()

    @pytest.mark.asyncio
    async def test_connection_refused(self) -> None:
        """Test connection refused error handling."""
        client = RaindropClient(token="test_token_1234567890abcdefghijklmnopqr")

        with patch.object(client, "client") as mock_client:
            mock_client.get.side_effect = httpx.ConnectError("Connection refused")

            with pytest.raises(httpx.ConnectError):
                await client.get_me()


class TestRetryLogicScenarios:
    """Test retry logic scenarios."""

    @pytest.mark.asyncio
    async def test_retry_on_429(self) -> None:
        """Test retry logic on rate limit."""
        client = RaindropClient(token="test_token_1234567890abcdefghijklmnopqr")

        with patch.object(client, "client") as mock_client:
            # First call: 429, second call: success
            mock_client.get.side_effect = [
                httpx.HTTPStatusCodes(
                    status_code=429,
                    request=MagicMock(),
                    headers=MagicMock(),
                ),
                MagicMock(json=MagicMock(return_value={"result": True})),
            ]

            # Should retry and succeed
            result = await client.list_bookmarks()
            assert result is not None

    @pytest.mark.asyncio
    async def test_retry_on_500(self) -> None:
        """Test retry logic on server error."""
        client = RaindropClient(token="test_token_1234567890abcdefghijklmnopqr")

        with patch.object(client, "client") as mock_client:
            # First call: 500, second call: success
            mock_client.get.side_effect = [
                httpx.HTTPStatusCodes(
                    status_code=500,
                    request=MagicMock(),
                    headers=MagicMock(),
                ),
                MagicMock(json=MagicMock(return_value={"result": True})),
            ]

            # Should retry and succeed
            result = await client.list_bookmarks()
            assert result is not None

    @pytest.mark.asyncio
    async def test_retry_exhausted(self) -> None:
        """Test retry exhaustion."""
        client = RaindropClient(token="test_token_1234567890abcdefghijklmnopqr")

        with patch.object(client, "client") as mock_client:
            # Always return 500
            mock_client.get.side_effect = httpx.HTTPStatusCodes(
                status_code=500,
                request=MagicMock(),
                headers=MagicMock(),
            )

            # Should retry and eventually fail
            with pytest.raises(APIError) as exc_info:
                await client.list_bookmarks()
            assert exc_info.value.status_code == 500


class TestValidationErrorScenarios:
    """Test validation error scenarios."""

    def test_invalid_url_format(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test validation of invalid URL format."""
        monkeypatch.setenv("RAINDROP_TOKEN", "test_token_1234567890abcdefghijklmnopqr")
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            RaindropSettings(base_url="not-a-valid-url")  # type: ignore[arg-type]

    def test_invalid_port_number(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test validation of invalid port number."""
        monkeypatch.setenv("RAINDROP_TOKEN", "test_token_1234567890abcdefghijklmnopqr")
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            RaindropSettings(http_port=99999)

    def test_negative_port_number(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test validation of negative port number."""
        monkeypatch.setenv("RAINDROP_TOKEN", "test_token_1234567890abcdefghijklmnopqr")
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            RaindropSettings(http_port=-1)

    def test_invalid_timeout_value(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test validation of invalid timeout value."""
        monkeypatch.setenv("RAINDROP_TOKEN", "test_token_1234567890abcdefghijklmnopqr")
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            RaindropSettings(request_timeout=0.5)

    def test_invalid_max_connections(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test validation of invalid max_connections value."""
        monkeypatch.setenv("RAINDROP_TOKEN", "test_token_1234567890abcdefghijklmnopqr")
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            RaindropSettings(max_connections=0)


class TestBookmarkErrorScenarios:
    """Test bookmark-specific error scenarios."""

    @pytest.mark.asyncio
    async def test_create_bookmark_missing_url(self) -> None:
        """Test error when creating bookmark without URL."""
        client = RaindropClient(token="test_token_1234567890abcdefghijklmnopqr")

        with pytest.raises(Exception):  # Pydantic validation error
            await client.create_bookmark(
                title="Test Bookmark",
                link="",  # Empty URL
            )

    @pytest.mark.asyncio
    async def test_update_nonexistent_bookmark(self) -> None:
        """Test error when updating non-existent bookmark."""
        client = RaindropClient(token="test_token_1234567890abcdefghijklmnopqr")

        with patch.object(client, "_put") as mock_put:
            mock_put.side_effect = ResourceNotFoundError("Bookmark not found")

            with pytest.raises(ResourceNotFoundError):
                await client.update_bookmark(
                    bookmark_id=999999,
                    title="Updated Title",
                )

    @pytest.mark.asyncio
    async def test_delete_nonexistent_bookmark(self) -> None:
        """Test error when deleting non-existent bookmark."""
        client = RaindropClient(token="test_token_1234567890abcdefghijklmnopqr")

        with patch.object(client, "_delete") as mock_delete:
            mock_delete.side_effect = ResourceNotFoundError("Bookmark not found")

            with pytest.raises(ResourceNotFoundError):
                await client.delete_bookmark(999999)


class TestCollectionErrorScenarios:
    """Test collection-specific error scenarios."""

    @pytest.mark.asyncio
    async def test_get_nonexistent_collection(self) -> None:
        """Test error when getting non-existent collection."""
        client = RaindropClient(token="test_token_1234567890abcdefghijklmnopqr")

        with patch.object(client, "_get") as mock_get:
            mock_get.side_effect = ResourceNotFoundError("Collection not found")

            with pytest.raises(ResourceNotFoundError):
                await client.get_collection(999999)

    @pytest.mark.asyncio
    async def test_delete_nonexistent_collection(self) -> None:
        """Test error when deleting non-existent collection."""
        client = RaindropClient(token="test_token_1234567890abcdefghijklmnopqr")

        with patch.object(client, "_delete") as mock_delete:
            mock_delete.side_effect = ResourceNotFoundError("Collection not found")

            with pytest.raises(ResourceNotFoundError):
                await client.delete_collection(999999)


class TestHighlightErrorScenarios:
    """Test highlight-specific error scenarios."""

    @pytest.mark.asyncio
    async def test_create_highlight_missing_text(self) -> None:
        """Test error when creating highlight without text."""
        client = RaindropClient(token="test_token_1234567890abcdefghijklmnopqr")

        with pytest.raises(Exception):  # Validation error
            await client.create_highlight(
                bookmark_id=123,
                text="",  # Empty text
            )

    @pytest.mark.asyncio
    async def test_update_nonexistent_highlight(self) -> None:
        """Test error when updating non-existent highlight."""
        client = RaindropClient(token="test_token_1234567890abcdefghijklmnopqr")

        with patch.object(client, "_put") as mock_put:
            mock_put.side_effect = ResourceNotFoundError("Highlight not found")

            with pytest.raises(ResourceNotFoundError):
                await client.update_highlight(
                    highlight_id=999999,
                    text="Updated text",
                )

    @pytest.mark.asyncio
    async def test_delete_nonexistent_highlight(self) -> None:
        """Test error when deleting non-existent highlight."""
        client = RaindropClient(token="test_token_1234567890abcdefghijklmnopqr")

        with patch.object(client, "_delete") as mock_delete:
            mock_delete.side_effect = ResourceNotFoundError("Highlight not found")

            with pytest.raises(ResourceNotFoundError):
                await client.delete_highlight(999999)


class TestBatchOperationErrorScenarios:
    """Test batch operation error scenarios."""

    @pytest.mark.asyncio
    async def test_batch_move_empty_list(self) -> None:
        """Test batch move with empty bookmark list."""
        client = RaindropClient(token="test_token_1234567890abcdefghijklmnopqr")

        with pytest.raises(Exception):  # Validation error
            await client.batch_move_bookmarks(
                bookmark_ids=[],
                collection_id=1,
            )

    @pytest.mark.asyncio
    async def test_batch_delete_empty_list(self) -> None:
        """Test batch delete with empty bookmark list."""
        client = RaindropClient(token="test_token_1234567890abcdefghijklmnopqr")

        with pytest.raises(Exception):  # Validation error
            await client.batch_delete_bookmarks([])

    @pytest.mark.asyncio
    async def test_batch_update_missing_data(self) -> None:
        """Test batch update with missing data."""
        client = RaindropClient(token="test_token_1234567890abcdefghijklmnopqr")

        with pytest.raises(Exception):  # Validation error
            await client.batch_update_bookmarks(
                updates={},  # Empty updates
            )


class TestTagErrorScenarios:
    """Test tag-specific error scenarios."""

    @pytest.mark.asyncio
    async def test_rename_nonexistent_tag(self) -> None:
        """Test error when renaming non-existent tag."""
        client = RaindropClient(token="test_token_1234567890abcdefghijklmnopqr")

        with patch.object(client, "_post") as mock_post:
            mock_post.side_effect = ResourceNotFoundError("Tag not found")

            with pytest.raises(ResourceNotFoundError):
                await client.rename_tag(
                    old_tag="nonexistent",
                    new_tag="new_tag",
                )

    @pytest.mark.asyncio
    async def test_delete_nonexistent_tag(self) -> None:
        """Test error when deleting non-existent tag."""
        client = RaindropClient(token="test_token_1234567890abcdefghijklmnopqr")

        with patch.object(client, "_delete") as mock_delete:
            mock_delete.side_effect = ResourceNotFoundError("Tag not found")

            with pytest.raises(ResourceNotFoundError):
                await client.delete_tag("nonexistent")


class TestImportExportErrorScenarios:
    """Test import/export error scenarios."""

    @pytest.mark.asyncio
    async def test_import_invalid_data(self) -> None:
        """Test error when importing invalid data."""
        client = RaindropClient(token="test_token_1234567890abcdefghijklmnopqr")

        with patch.object(client, "_post") as mock_post:
            mock_post.side_effect = APIError("Invalid import data", status_code=400)

            with pytest.raises(APIError) as exc_info:
                await client.import_bookmarks(
                    bookmarks=[{"invalid": "data"}],
                )
            assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_export_collection_not_found(self) -> None:
        """Test error when exporting from non-existent collection."""
        client = RaindropClient(token="test_token_1234567890abcdefghijklmnopqr")

        with patch.object(client, "_get") as mock_get:
            mock_get.side_effect = ResourceNotFoundError("Collection not found")

            with pytest.raises(ResourceNotFoundError):
                await client.export_bookmarks(collection_id=999999)
