"""Improved tests for the raindrop client to increase coverage."""

from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from raindropio_mcp.clients.raindrop_client import RaindropClient
from raindropio_mcp.config.settings import RaindropSettings
from raindropio_mcp.models import (
    BatchDeleteBookmarks,
    BatchMoveBookmarks,
    BatchOperationResponse,
    BatchTagBookmarks,
    BatchUntagBookmarks,
    BatchUpdateBookmarks,
    Bookmark,
    BookmarkCreate,
    BookmarkFilter,
    BookmarkUpdate,
    Collection,
    CollectionCreate,
    CollectionUpdate,
    ExportFormat,
    Highlight,
    HighlightCreate,
    HighlightUpdate,
    ImportSource,
    Tag,
    User,
)


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    settings = RaindropSettings(token="test_token_12345678901234567890123456789012")
    return settings


@pytest.fixture
def client(mock_settings):
    """Create a RaindropClient instance for testing."""
    return RaindropClient(mock_settings)


@pytest.mark.asyncio
async def test_get_me_invalid_response(client):
    """Test get_me with invalid response."""
    with patch.object(client, 'get_json', return_value={"result": False}):
        with pytest.raises(Exception):  # Should raise APIError
            await client.get_me()


@pytest.mark.asyncio
async def test_list_collections_invalid_response(client):
    """Test list_collections with invalid response."""
    with patch.object(client, 'get_json', return_value={"result": False}):
        with pytest.raises(Exception):  # Should raise APIError
            await client.list_collections()


@pytest.mark.asyncio
async def test_get_collection_invalid_response(client):
    """Test get_collection with invalid response."""
    with patch.object(client, 'get_json', return_value={"result": False}):
        with pytest.raises(Exception):  # Should raise APIError
            await client.get_collection(123)


@pytest.mark.asyncio
async def test_create_collection_invalid_response(client):
    """Test create_collection with invalid response."""
    data = CollectionCreate(title="Test Collection")
    with patch.object(client, 'get_json', return_value={"result": False}):
        with pytest.raises(Exception):  # Should raise APIError
            await client.create_collection(data)


@pytest.mark.asyncio
async def test_update_collection_invalid_response(client):
    """Test update_collection with invalid response."""
    data = CollectionUpdate(title="Updated Collection")
    with patch.object(client, 'get_json', return_value={"result": False}):
        with pytest.raises(Exception):  # Should raise APIError
            await client.update_collection(123, data)


@pytest.mark.asyncio
async def test_delete_collection_invalid_response(client):
    """Test delete_collection with invalid response."""
    with patch.object(client, 'get_json', return_value={"result": False}):
        with pytest.raises(Exception):  # Should raise APIError
            await client.delete_collection(123)


@pytest.mark.asyncio
async def test_list_bookmarks_invalid_response(client):
    """Test list_bookmarks with invalid response."""
    with patch.object(client, 'get_json', return_value={"result": False}):
        with pytest.raises(Exception):  # Should raise APIError
            await client.list_bookmarks(123)


@pytest.mark.asyncio
async def test_search_bookmarks_invalid_response(client):
    """Test search_bookmarks with invalid response."""
    with patch.object(client, 'get_json', return_value={"result": False}):
        with pytest.raises(Exception):  # Should raise APIError
            await client.search_bookmarks("test query")


@pytest.mark.asyncio
async def test_get_bookmark_invalid_response(client):
    """Test get_bookmark with invalid response."""
    with patch.object(client, 'get_json', return_value={"result": False}):
        with pytest.raises(Exception):  # Should raise APIError
            await client.get_bookmark(123)


@pytest.mark.asyncio
async def test_create_bookmark_invalid_response(client):
    """Test create_bookmark with invalid response."""
    data = BookmarkCreate(link="https://example.com")
    with patch.object(client, 'get_json', return_value={"result": False}):
        with pytest.raises(Exception):  # Should raise APIError
            await client.create_bookmark(123, data)


@pytest.mark.asyncio
async def test_update_bookmark_invalid_response(client):
    """Test update_bookmark with invalid response."""
    data = BookmarkUpdate(title="Updated Title", link="https://example.com")
    with patch.object(client, 'get_json', return_value={"result": False}):
        with pytest.raises(Exception):  # Should raise APIError
            await client.update_bookmark(123, data)


@pytest.mark.asyncio
async def test_delete_bookmark_invalid_response(client):
    """Test delete_bookmark with invalid response."""
    with patch.object(client, 'get_json', return_value={"result": False}):
        with pytest.raises(Exception):  # Should raise APIError
            await client.delete_bookmark(123)


@pytest.mark.asyncio
async def test_list_tags_invalid_response(client):
    """Test list_tags with invalid response."""
    with patch.object(client, 'get_json', return_value={"result": False}):
        with pytest.raises(Exception):  # Should raise APIError
            await client.list_tags()


@pytest.mark.asyncio
async def test_rename_tag_invalid_response(client):
    """Test rename_tag with invalid response."""
    with patch.object(client, 'get_json', return_value={"result": False}):
        with pytest.raises(Exception):  # Should raise APIError
            await client.rename_tag("old_tag", "new_tag")


@pytest.mark.asyncio
async def test_delete_tag_invalid_response(client):
    """Test delete_tag with invalid response."""
    with patch.object(client, 'get_json', return_value={"result": False}):
        with pytest.raises(Exception):  # Should raise APIError
            await client.delete_tag("test_tag")


@pytest.mark.asyncio
async def test_list_highlights_invalid_response(client):
    """Test list_highlights with invalid response."""
    with patch.object(client, 'get_json', return_value={"result": False}):
        with pytest.raises(Exception):  # Should raise APIError
            await client.list_highlights(123)


@pytest.mark.asyncio
async def test_get_highlight_invalid_response(client):
    """Test get_highlight with invalid response."""
    with patch.object(client, 'get_json', return_value={"result": False}):
        with pytest.raises(Exception):  # Should raise APIError
            await client.get_highlight(123)


@pytest.mark.asyncio
async def test_create_highlight_invalid_response(client):
    """Test create_highlight with invalid response."""
    data = HighlightCreate(text="Test highlight")
    with patch.object(client, 'get_json', return_value={"result": False}):
        with pytest.raises(Exception):  # Should raise APIError
            await client.create_highlight(123, data)


@pytest.mark.asyncio
async def test_update_highlight_invalid_response(client):
    """Test update_highlight with invalid response."""
    data = HighlightUpdate(text="Updated highlight")
    with patch.object(client, 'get_json', return_value={"result": False}):
        with pytest.raises(Exception):  # Should raise APIError
            await client.update_highlight(123, data)


@pytest.mark.asyncio
async def test_delete_highlight_invalid_response(client):
    """Test delete_highlight with invalid response."""
    with patch.object(client, 'get_json', return_value={"result": False}):
        with pytest.raises(Exception):  # Should raise APIError
            await client.delete_highlight(123)


@pytest.mark.asyncio
async def test_batch_move_bookmarks_invalid_response(client):
    """Test batch_move_bookmarks with invalid response."""
    data = BatchMoveBookmarks(bookmark_ids=[1, 2, 3], collection_id=456)
    with patch.object(client, 'get_json', return_value={"error": "failed"}):
        with pytest.raises(Exception):  # Should raise APIError
            await client.batch_move_bookmarks(data)


@pytest.mark.asyncio
async def test_batch_delete_bookmarks_invalid_response(client):
    """Test batch_delete_bookmarks with invalid response."""
    data = BatchDeleteBookmarks(bookmark_ids=[1, 2, 3])
    with patch.object(client, 'get_json', return_value={"error": "failed"}):
        with pytest.raises(Exception):  # Should raise APIError
            await client.batch_delete_bookmarks(data)


@pytest.mark.asyncio
async def test_batch_update_bookmarks_invalid_response(client):
    """Test batch_update_bookmarks with invalid response."""
    data = BatchUpdateBookmarks(bookmark_ids=[1, 2, 3], tags=["test"])
    with patch.object(client, 'get_json', return_value={"error": "failed"}):
        with pytest.raises(Exception):  # Should raise APIError
            await client.batch_update_bookmarks(data)


@pytest.mark.asyncio
async def test_batch_tag_bookmarks_invalid_response(client):
    """Test batch_tag_bookmarks with invalid response."""
    data = BatchTagBookmarks(bookmark_ids=[1, 2, 3], tags=["test"])
    with patch.object(client, 'get_json', return_value={"error": "failed"}):
        with pytest.raises(Exception):  # Should raise APIError
            await client.batch_tag_bookmarks(data)


@pytest.mark.asyncio
async def test_batch_untag_bookmarks_invalid_response(client):
    """Test batch_untag_bookmarks with invalid response."""
    data = BatchUntagBookmarks(bookmark_ids=[1, 2, 3], tags=["test"])
    with patch.object(client, 'get_json', return_value={"error": "failed"}):
        with pytest.raises(Exception):  # Should raise APIError
            await client.batch_untag_bookmarks(data)


@pytest.mark.asyncio
async def test_apply_filters_invalid_response(client):
    """Test apply_filters with invalid response."""
    filter_params = BookmarkFilter()
    with patch.object(client, 'get_json', return_value={"result": False}):
        with pytest.raises(Exception):  # Should raise APIError
            await client.apply_filters(filter_params)


@pytest.mark.asyncio
async def test_get_filtered_bookmarks_by_collection_invalid_response(client):
    """Test get_filtered_bookmarks_by_collection with invalid response."""
    filter_params = BookmarkFilter()
    with patch.object(client, 'get_json', return_value={"result": False}):
        with pytest.raises(Exception):  # Should raise APIError
            await client.get_filtered_bookmarks_by_collection(123, filter_params)


@pytest.mark.asyncio
async def test_import_bookmarks_invalid_response(client):
    """Test import_bookmarks with invalid response."""
    import_source = ImportSource(source="test", data="test data", format="json")
    with patch.object(client, 'get_json', return_value={"result": False}):
        with pytest.raises(Exception):  # Should raise APIError
            await client.import_bookmarks(import_source)


@pytest.mark.asyncio
async def test_export_bookmarks(client):
    """Test export_bookmarks functionality."""
    # Mock the request method to return a response with text content
    mock_response = Mock()
    mock_response.text = "exported content"
    export_format = ExportFormat(format="json")
    with patch.object(client, 'request', return_value=mock_response):
        result = await client.export_bookmarks(export_format)
        assert result == "exported content"


@pytest.mark.asyncio
async def test_get_me_success(client):
    """Test get_me with successful response."""
    mock_response = {
        "result": True,
        "user": {
            "id": 123,
            "email": "test@example.com",
            "name": "Test User"
        }
    }
    with patch.object(client, 'get_json', return_value=mock_response):
        user = await client.get_me()
        assert isinstance(user, User)


@pytest.mark.asyncio
async def test_list_collections_success(client):
    """Test list_collections with successful response."""
    mock_response = {
        "result": True,
        "items": [
            {
                "id": 1,
                "title": "Test Collection"
            }
        ]
    }
    with patch.object(client, 'get_json', return_value=mock_response):
        collections = await client.list_collections()
        assert len(collections) == 1
        assert isinstance(collections[0], Collection)


@pytest.mark.asyncio
async def test_get_collection_success(client):
    """Test get_collection with successful response."""
    mock_response = {
        "result": True,
        "collection": {
            "id": 1,
            "title": "Test Collection"
        }
    }
    with patch.object(client, 'get_json', return_value=mock_response):
        collection = await client.get_collection(1)
        assert isinstance(collection, Collection)


@pytest.mark.asyncio
async def test_create_collection_success(client):
    """Test create_collection with successful response."""
    data = CollectionCreate(title="New Collection")
    mock_response = {
        "result": True,
        "collection": {
            "id": 1,
            "title": "New Collection"
        }
    }
    with patch.object(client, 'get_json', return_value=mock_response):
        collection = await client.create_collection(data)
        assert isinstance(collection, Collection)


@pytest.mark.asyncio
async def test_update_collection_success(client):
    """Test update_collection with successful response."""
    data = CollectionUpdate(title="Updated Collection")
    mock_response = {
        "result": True,
        "collection": {
            "id": 1,
            "title": "Updated Collection"
        }
    }
    with patch.object(client, 'get_json', return_value=mock_response):
        collection = await client.update_collection(1, data)
        assert isinstance(collection, Collection)


@pytest.mark.asyncio
async def test_delete_collection_success(client):
    """Test delete_collection with successful response."""
    mock_response = {"result": True}
    with patch.object(client, 'get_json', return_value=mock_response):
        result = await client.delete_collection(1)
        assert result is True


@pytest.mark.asyncio
async def test_list_bookmarks_success(client):
    """Test list_bookmarks with successful response."""
    mock_response = {
        "result": True,
        "items": [
            {
                "id": 1,
                "link": "https://example.com",
                "title": "Test Title"
            }
        ],
        "count": 1
    }
    with patch.object(client, 'get_json', return_value=mock_response):
        bookmarks = await client.list_bookmarks(1)
        assert bookmarks.count == 1
        assert len(bookmarks.items) == 1


@pytest.mark.asyncio
async def test_search_bookmarks_success(client):
    """Test search_bookmarks with successful response."""
    mock_response = {
        "result": True,
        "items": [
            {
                "id": 1,
                "link": "https://example.com",
                "title": "Test Title"
            }
        ],
        "count": 1
    }
    with patch.object(client, 'get_json', return_value=mock_response):
        bookmarks = await client.search_bookmarks("test")
        assert bookmarks.count == 1
        assert len(bookmarks.items) == 1


@pytest.mark.asyncio
async def test_get_bookmark_success(client):
    """Test get_bookmark with successful response."""
    mock_response = {
        "result": True,
        "item": {
            "id": 1,
            "link": "https://example.com",
            "title": "Test Title"
        }
    }
    with patch.object(client, 'get_json', return_value=mock_response):
        bookmark = await client.get_bookmark(1)
        assert isinstance(bookmark, Bookmark)


@pytest.mark.asyncio
async def test_create_bookmark_success(client):
    """Test create_bookmark with successful response."""
    data = BookmarkCreate(link="https://example.com", title="Test Title")
    mock_response = {
        "result": True,
        "item": {
            "id": 1,
            "link": "https://example.com",
            "title": "Test Title"
        }
    }
    with patch.object(client, 'get_json', return_value=mock_response):
        bookmark = await client.create_bookmark(1, data)
        assert isinstance(bookmark, Bookmark)


@pytest.mark.asyncio
async def test_update_bookmark_success(client):
    """Test update_bookmark with successful response."""
    data = BookmarkUpdate(title="Updated Title", link="https://example.com")
    mock_response = {
        "result": True,
        "item": {
            "id": 1,
            "link": "https://example.com",
            "title": "Updated Title"
        }
    }
    with patch.object(client, 'get_json', return_value=mock_response):
        bookmark = await client.update_bookmark(1, data)
        assert isinstance(bookmark, Bookmark)


@pytest.mark.asyncio
async def test_delete_bookmark_success(client):
    """Test delete_bookmark with successful response."""
    mock_response = {"result": True}
    with patch.object(client, 'get_json', return_value=mock_response):
        result = await client.delete_bookmark(1)
        assert result is True


@pytest.mark.asyncio
async def test_list_tags_success(client):
    """Test list_tags with successful response."""
    mock_response = {
        "result": True,
        "items": [
            {
                "_id": "1",
                "name": "test",
                "count": 5
            }
        ]
    }
    with patch.object(client, 'get_json', return_value=mock_response):
        tags = await client.list_tags()
        assert len(tags) == 1
        assert isinstance(tags[0], Tag)


@pytest.mark.asyncio
async def test_rename_tag_success(client):
    """Test rename_tag with successful response."""
    mock_response = {"result": True}
    with patch.object(client, 'get_json', return_value=mock_response):
        result = await client.rename_tag("old", "new")
        assert result is True


@pytest.mark.asyncio
async def test_delete_tag_success(client):
    """Test delete_tag with successful response."""
    mock_response = {"result": True}
    with patch.object(client, 'get_json', return_value=mock_response):
        result = await client.delete_tag("test")
        assert result is True


@pytest.mark.asyncio
async def test_list_highlights_success(client):
    """Test list_highlights with successful response."""
    mock_response = {
        "result": True,
        "items": [
            {
                "id": 1,
                "text": "test highlight",
                "raindropId": 1,
                "type": "highlight"
            }
        ]
    }
    with patch.object(client, 'get_json', return_value=mock_response):
        highlights = await client.list_highlights(1)
        assert len(highlights) == 1
        assert isinstance(highlights[0], Highlight)


@pytest.mark.asyncio
async def test_get_highlight_success(client):
    """Test get_highlight with successful response."""
    mock_response = {
        "result": True,
        "item": {
            "id": 1,
            "text": "test highlight",
            "raindropId": 1,
            "type": "highlight"
        }
    }
    with patch.object(client, 'get_json', return_value=mock_response):
        highlight = await client.get_highlight(1)
        assert isinstance(highlight, Highlight)


@pytest.mark.asyncio
async def test_create_highlight_success(client):
    """Test create_highlight with successful response."""
    data = HighlightCreate(text="test highlight", type="highlight")
    mock_response = {
        "result": True,
        "item": {
            "id": 1,
            "text": "test highlight",
            "raindropId": 1,
            "type": "highlight"
        }
    }
    with patch.object(client, 'get_json', return_value=mock_response):
        highlight = await client.create_highlight(1, data)
        assert isinstance(highlight, Highlight)


@pytest.mark.asyncio
async def test_update_highlight_success(client):
    """Test update_highlight with successful response."""
    data = HighlightUpdate(text="updated highlight", type="highlight")
    mock_response = {
        "result": True,
        "item": {
            "id": 1,
            "text": "updated highlight",
            "raindropId": 1,
            "type": "highlight"
        }
    }
    with patch.object(client, 'get_json', return_value=mock_response):
        highlight = await client.update_highlight(1, data)
        assert isinstance(highlight, Highlight)


@pytest.mark.asyncio
async def test_delete_highlight_success(client):
    """Test delete_highlight with successful response."""
    mock_response = {"result": True}
    with patch.object(client, 'get_json', return_value=mock_response):
        result = await client.delete_highlight(1)
        assert result is True


@pytest.mark.asyncio
async def test_batch_move_bookmarks_success(client):
    """Test batch_move_bookmarks with successful response."""
    data = BatchMoveBookmarks(bookmark_ids=[1, 2, 3], collection_id=456)
    mock_response = {
        "result": True,
        "processed_count": 3,
        "success_count": 3,
        "error_count": 0
    }
    with patch.object(client, 'get_json', return_value=mock_response):
        result = await client.batch_move_bookmarks(data)
        assert isinstance(result, BatchOperationResponse)


@pytest.mark.asyncio
async def test_batch_delete_bookmarks_success(client):
    """Test batch_delete_bookmarks with successful response."""
    data = BatchDeleteBookmarks(bookmark_ids=[1, 2, 3])
    mock_response = {
        "result": True,
        "processed_count": 3,
        "success_count": 3,
        "error_count": 0
    }
    with patch.object(client, 'get_json', return_value=mock_response):
        result = await client.batch_delete_bookmarks(data)
        assert isinstance(result, BatchOperationResponse)


@pytest.mark.asyncio
async def test_batch_update_bookmarks_success(client):
    """Test batch_update_bookmarks with successful response."""
    data = BatchUpdateBookmarks(bookmark_ids=[1, 2, 3], tags=["test"])
    mock_response = {
        "result": True,
        "processed_count": 3,
        "success_count": 3,
        "error_count": 0
    }
    with patch.object(client, 'get_json', return_value=mock_response):
        result = await client.batch_update_bookmarks(data)
        assert isinstance(result, BatchOperationResponse)


@pytest.mark.asyncio
async def test_batch_tag_bookmarks_success(client):
    """Test batch_tag_bookmarks with successful response."""
    data = BatchTagBookmarks(bookmark_ids=[1, 2, 3], tags=["test"])
    mock_response = {
        "result": True,
        "processed_count": 3,
        "success_count": 3,
        "error_count": 0
    }
    with patch.object(client, 'get_json', return_value=mock_response):
        result = await client.batch_tag_bookmarks(data)
        assert isinstance(result, BatchOperationResponse)


@pytest.mark.asyncio
async def test_batch_untag_bookmarks_success(client):
    """Test batch_untag_bookmarks with successful response."""
    data = BatchUntagBookmarks(bookmark_ids=[1, 2, 3], tags=["test"])
    mock_response = {
        "result": True,
        "processed_count": 3,
        "success_count": 3,
        "error_count": 0
    }
    with patch.object(client, 'get_json', return_value=mock_response):
        result = await client.batch_untag_bookmarks(data)
        assert isinstance(result, BatchOperationResponse)


@pytest.mark.asyncio
async def test_apply_filters_success(client):
    """Test apply_filters with successful response."""
    filter_params = BookmarkFilter()
    mock_response = {
        "result": True,
        "items": [
            {
                "id": 1,
                "link": "https://example.com",
                "title": "Test Title"
            }
        ],
        "count": 1,
        "total": 1,
        "page": 0,
        "per_page": 50,
        "filters_applied": []
    }
    with patch.object(client, 'get_json', return_value=mock_response):
        result = await client.apply_filters(filter_params)
        assert result.items is not None


@pytest.mark.asyncio
async def test_get_filtered_bookmarks_by_collection_success(client):
    """Test get_filtered_bookmarks_by_collection with successful response."""
    filter_params = BookmarkFilter()
    mock_response = {
        "result": True,
        "items": [
            {
                "id": 1,
                "link": "https://example.com",
                "title": "Test Title"
            }
        ],
        "count": 1,
        "total": 1,
        "page": 0,
        "per_page": 50,
        "filters_applied": []
    }
    with patch.object(client, 'get_json', return_value=mock_response):
        result = await client.get_filtered_bookmarks_by_collection(1, filter_params)
        assert result.items is not None


@pytest.mark.asyncio
async def test_import_bookmarks_success(client):
    """Test import_bookmarks with successful response."""
    import_source = ImportSource(source="test", data="test data", format="json")
    mock_response = {
        "result": True,
        "imported_count": 5,
        "skipped_count": 0,
        "errors": []
    }
    with patch.object(client, 'get_json', return_value=mock_response):
        result = await client.import_bookmarks(import_source)
        assert result.imported_count == 5