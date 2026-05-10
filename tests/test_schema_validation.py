"""
Schema validation tests to catch API/Model mismatches.

These tests validate that Pydantic models correctly match the actual
API response structures. Run these tests to catch schema drift.

Usage:
    pytest tests/test_schema_validation.py -v

To add to other MCP servers, copy this file and adapt the
API response fixtures for that service.
"""

import pytest

from raindropio_mcp.models.bookmark import Bookmark, BookmarksResponse
from raindropio_mcp.models.collection import Collection, CollectionsResponse


class TestCollectionSchema:
    """Test Collection model matches actual API responses."""

    def test_collection_sort_is_int(self):
        """Verify sort field is int (API returns int, not str)."""
        # Simulate actual API response
        api_response = {
            "_id": 12345,
            "title": "Test Collection",
            "sort": 12345,  # int, not str!
            "cover": [],  # list, not str!
            "count": 10,
        }
        # Should not raise validation error
        collection = Collection.model_validate(api_response)
        assert collection.sort == 12345
        assert isinstance(collection.sort, int)

    def test_collection_cover_is_list(self):
        """Verify cover field accepts list (API returns list, not str)."""
        api_response = {
            "_id": 12345,
            "title": "Test Collection",
            "cover": [],
        }
        collection = Collection.model_validate(api_response)
        assert collection.cover == []

    def test_collection_extra_fields_ignored(self):
        """Verify extra API fields don't cause validation errors."""
        api_response = {
            "_id": 12345,
            "title": "Test Collection",
            # Extra fields from API that model doesn't define
            "access": {"for": 1, "level": 4},
            "author": True,
            "creatorRef": {"_id": 1, "name": "Test"},
            "expanded": True,
            "lastAction": "2024-01-01T00:00:00Z",
            "user": {"$ref": "users", "$id": 1},
        }
        # Should not raise validation error with extra="ignore"
        collection = Collection.model_validate(api_response)
        assert collection.id == 12345

    def test_full_collection_response(self, collection_response_fixture):
        """Test parsing a full API collection response."""
        response = CollectionsResponse.model_validate(collection_response_fixture)
        assert response.result is True
        assert len(response.items) > 0


class TestBookmarkSchema:
    """Test Bookmark model matches actual API responses."""

    def test_bookmark_dates_are_strings(self):
        """Verify date fields accept ISO strings (API returns str, not datetime)."""
        api_response = {
            "_id": 12345,
            "title": "Test Bookmark",
            "link": "https://example.com",
            "created": "2024-01-01T00:00:00.000Z",
            "lastUpdate": "2024-01-01T00:00:00.000Z",
        }
        bookmark = Bookmark.model_validate(api_response)
        assert bookmark.created == "2024-01-01T00:00:00.000Z"

    def test_bookmark_collection_ref_with_oid(self):
        """Verify collection ref accepts oid field."""
        api_response = {
            "_id": 12345,
            "title": "Test Bookmark",
            "link": "https://example.com",
            "collection": {"$id": 123, "$ref": "collections", "oid": 123},
        }
        bookmark = Bookmark.model_validate(api_response)
        assert bookmark.collection.id == 123

    def test_bookmark_extra_fields_ignored(self):
        """Verify extra API fields don't cause validation errors."""
        api_response = {
            "_id": 12345,
            "title": "Test Bookmark",
            "link": "https://example.com",
            # Extra fields from API
            "collectionId": 123,
            "creatorRef": {"_id": 1, "name": "Test"},
            "highlights": [],
            "removed": False,
            "user": {"$ref": "users", "$id": 1},
        }
        bookmark = Bookmark.model_validate(api_response)
        assert bookmark.id == 12345

    def test_full_bookmark_response(self, bookmark_response_fixture):
        """Test parsing a full API bookmark response."""
        response = BookmarksResponse.model_validate(bookmark_response_fixture)
        assert response.result is True
        assert len(response.items) > 0


class TestSchemaFieldTypeValidation:
    """
    Meta-tests to catch type mismatches between model and API.

    These tests document the expected types and will fail if
    the model types don't match actual API response types.
    """

    @pytest.mark.parametrize(
        "field,expected_type",
        [
            ("sort", int),  # NOT str!
            ("cover", list),  # NOT str!
            ("count", int),
            ("public", bool),
        ],
    )
    def test_collection_field_types(self, field, expected_type, collection_response_fixture):
        """Verify Collection field types match API response types."""
        response = CollectionsResponse.model_validate(collection_response_fixture)
        if response.items:
            collection = response.items[0]
            value = getattr(collection, field, None)
            if value is not None:
                assert isinstance(
                    value, expected_type
                ), f"Field '{field}' should be {expected_type.__name__}, got {type(value).__name__}"


# Fixtures with actual API response data
# Update these when API responses change


@pytest.fixture
def collection_response_fixture():
    """Sample collection response from Raindrop.io API."""
    return {
        "result": True,
        "items": [
            {
                "_id": 67275445,
                "title": "Business",
                "description": "",
                "user": {"$ref": "users", "$id": 3894883},
                "public": False,
                "view": "list",
                "count": 270,
                "cover": [],
                "expanded": True,
                "creatorRef": {"_id": 3894883, "name": "Les", "email": ""},
                "lastAction": "2026-02-22T07:58:15.791Z",
                "created": "2026-02-22T07:58:15.791Z",
                "lastUpdate": "2026-02-22T07:58:15.791Z",
                "parent": None,
                "sort": 67275445,
                "slug": "business",
                "access": {"for": 3894883, "level": 4, "root": False, "draggable": True},
                "author": True,
            }
        ],
    }


@pytest.fixture
def bookmark_response_fixture():
    """Sample bookmark response from Raindrop.io API."""
    return {
        "result": True,
        "items": [
            {
                "_id": 1612031828,
                "collection": {"$ref": "collections", "$id": 67274449, "oid": 67274449},
                "collectionId": 67274449,
                "cover": "",
                "created": "2026-02-22T09:07:58.679Z",
                "creatorRef": {"_id": 3894883, "avatar": "", "name": "Les", "email": ""},
                "domain": "example.com",
                "excerpt": "",
                "highlights": [],
                "lastUpdate": "2026-02-22T09:07:58.679Z",
                "link": "https://example.com/article",
                "media": [],
                "note": "",
                "removed": False,
                "sort": 1612031828,
                "tags": ["test", "example"],
                "title": "Test Article",
                "type": "link",
                "user": {"$ref": "users", "$id": 3894883},
            }
        ],
    }


class TestModelConfigBestPractices:
    """
    Tests to ensure models follow best practices for API integration.

    All models that parse external API responses should have:
    - extra="ignore" or extra="allow" to handle API changes
    - populate_by_name=True for alias support
    """

    def test_collection_has_extra_ignore(self):
        """Collection model should ignore extra fields."""
        config = Collection.model_config
        assert config.get("extra") in ("ignore", "allow"), (
            "Collection should have extra='ignore' or extra='allow' "
            "to handle API response changes"
        )

    def test_bookmark_has_extra_ignore(self):
        """Bookmark model should ignore extra fields."""
        config = Bookmark.model_config
        assert config.get("extra") in ("ignore", "allow"), (
            "Bookmark should have extra='ignore' or extra='allow' "
            "to handle API response changes"
        )
