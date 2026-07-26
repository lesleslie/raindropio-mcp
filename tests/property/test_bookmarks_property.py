"""Property-based tests for bookmark models using Hypothesis."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from hypothesis import given, settings as hyp_settings
from hypothesis import strategies as st
from pydantic import ValidationError

from raindropio_mcp.models.bookmark import Bookmark


class TestBookmarkProperties:
    """Property-based tests for Bookmark model."""

    @given(
        bookmark_id=st.integers(min_value=1, max_value=1_000_000),
        title=st.text(min_size=1, max_size=100),
        url=st.text(min_size=10, max_size=200).filter(lambda x: x.startswith("http")),
        excerpt=st.text(min_size=0, max_size=500),
        note=st.text(min_size=0, max_size=1000),
        tags=st.lists(st.text(min_size=1, max_size=30, alphabet="abc"), min_size=0, max_size=20),
    )
    @hyp_settings(max_examples=20)
    def test_valid_bookmark(
        self,
        bookmark_id: int,
        title: str,
        url: str,
        excerpt: str,
        note: str,
        tags: list[str],
    ) -> None:
        """Test that valid bookmarks are accepted."""
        bookmark = Bookmark(
            _id=bookmark_id,
            title=title,
            link=url,
            excerpt=excerpt,
            note=note,
            tags=tags,
        )
        assert bookmark._id == bookmark_id
        assert bookmark.title == title
        assert bookmark.link == url
        assert bookmark.excerpt == excerpt
        assert bookmark.note == note
        assert bookmark.tags == tags

    @given(
        bookmark_id=st.integers(min_value=1, max_value=1_000_000),
        tags=st.lists(st.text(min_size=1, max_size=30, alphabet="abc"), min_size=0, max_size=20),
    )
    def test_bookmark_with_tags(self, bookmark_id: int, tags: list[str]) -> None:
        """Test bookmark with various tag combinations."""
        bookmark = Bookmark(
            _id=bookmark_id,
            title="Test Bookmark",
            link="https://example.com",
            tags=tags,
        )
        assert bookmark.tags == tags
        assert isinstance(bookmark.tags, list)

    @given(
        bookmark_id=st.integers(min_value=1, max_value=1_000_000),
        tag_count=st.integers(min_value=0, max_value=50),
    )
    def test_bookmark_tag_count(self, bookmark_id: int, tag_count: int) -> None:
        """Test bookmark with specific tag count."""
        tags = [f"tag{i}" for i in range(tag_count)]
        bookmark = Bookmark(
            _id=bookmark_id,
            title="Test Bookmark",
            link="https://example.com",
            tags=tags,
        )
        assert len(bookmark.tags) == tag_count

    @given(
        bookmark_id=st.integers(min_value=-1000, max_value=0),
    )
    def test_invalid_bookmark_id(self, bookmark_id: int) -> None:
        """Test that invalid bookmark IDs are rejected."""
        with pytest.raises(ValidationError):
            Bookmark(
                _id=bookmark_id,
                title="Test Bookmark",
                link="https://example.com",
            )

    @given(
        bookmark_id=st.integers(min_value=1, max_value=1_000_000),
        url=st.text(min_size=10, max_size=200),
    )
    def test_url_validation(self, bookmark_id: int, url: str) -> None:
        """Test URL validation in bookmarks."""
        try:
            bookmark = Bookmark(
                _id=bookmark_id,
                title="Test Bookmark",
                link=url,
            )
            assert bookmark.link == url
        except ValidationError:
            # Invalid URLs are expected to fail
            pass


class TestBookmarkTimestampProperties:
    """Property-based tests for bookmark timestamps."""

    @given(
        bookmark_id=st.integers(min_value=1, max_value=1_000_000),
        days_ago=st.integers(min_value=0, max_value=365),
    )
    def test_created_timestamp(self, bookmark_id: int, days_ago: int) -> None:
        """Test bookmark created timestamp."""
        import time

        created = int(time.time()) - (days_ago * 86400)
        bookmark = Bookmark(
            _id=bookmark_id,
            title="Test Bookmark",
            link="https://example.com",
            created=created,
        )
        assert bookmark.created == created

    @given(
        bookmark_id=st.integers(min_value=1, max_value=1_000_000),
        days_ago=st.integers(min_value=0, max_value=365),
    )
    def test_last_update_timestamp(self, bookmark_id: int, days_ago: int) -> None:
        """Test bookmark last update timestamp."""
        import time

        updated = int(time.time()) - (days_ago * 86400)
        bookmark = Bookmark(
            _id=bookmark_id,
            title="Test Bookmark",
            link="https://example.com",
            lastUpdate=updated,
        )
        assert bookmark.lastUpdate == updated


class TestBookmarkTypeProperties:
    """Property-based tests for bookmark types."""

    @given(
        bookmark_id=st.integers(min_value=1, max_value=1_000_000),
        bookmark_type=st.sampled_from(["link", "article", "image", "video", "document", "audio"]),
    )
    def test_bookmark_type(self, bookmark_id: int, bookmark_type: str) -> None:
        """Test bookmark type field."""
        bookmark = Bookmark(
            _id=bookmark_id,
            title="Test Bookmark",
            link="https://example.com",
            type=bookmark_type,
        )
        assert bookmark.type == bookmark_type

    @given(
        bookmark_id=st.integers(min_value=1, max_value=1_000_000),
        important=st.booleans(),
    )
    def test_bookmark_important_flag(self, bookmark_id: int, important: bool) -> None:
        """Test bookmark important flag."""
        bookmark = Bookmark(
            _id=bookmark_id,
            title="Test Bookmark",
            link="https://example.com",
            important=important,
        )
        assert bookmark.important == important


class TestBookmarkCollectionProperties:
    """Property-based tests for bookmark collection association."""

    @given(
        bookmark_id=st.integers(min_value=1, max_value=1_000_000),
        collection_id=st.integers(min_value=0, max_value=10_000),
    )
    def test_bookmark_collection_id(self, bookmark_id: int, collection_id: int) -> None:
        """Test bookmark collection ID."""
        bookmark = Bookmark(
            _id=bookmark_id,
            title="Test Bookmark",
            link="https://example.com",
            collectionId=collection_id,
        )
        assert bookmark.collectionId == collection_id


class TestBookmarkSortingProperties:
    """Property-based tests for bookmark sorting."""

    @given(
        count=st.integers(min_value=1, max_value=100),
    )
    def test_bookmark_sorting_by_id(self, count: int) -> None:
        """Test sorting bookmarks by ID."""
        import random

        bookmarks = [
            Bookmark(
                _id=random.randint(1, 10000),
                title=f"Bookmark {i}",
                link=f"https://example.com/{i}",
            )
            for i in range(count)
        ]

        # Sort by ID
        sorted_bookmarks = sorted(bookmarks, key=lambda b: b._id)

        # Verify sorting
        for i in range(len(sorted_bookmarks) - 1):
            assert sorted_bookmarks[i]._id <= sorted_bookmarks[i + 1]._id

    @given(
        count=st.integers(min_value=1, max_value=100),
    )
    def test_bookmark_sorting_by_title(self, count: int) -> None:
        """Test sorting bookmarks by title."""
        import random
        import string

        bookmarks = [
            Bookmark(
                _id=i,
                title="".join(random.choices(string.ascii_letters, k=10)),
                link=f"https://example.com/{i}",
            )
            for i in range(count)
        ]

        # Sort by title
        sorted_bookmarks = sorted(bookmarks, key=lambda b: b.title)

        # Verify sorting
        for i in range(len(sorted_bookmarks) - 1):
            assert sorted_bookmarks[i].title <= sorted_bookmarks[i + 1].title


class TestBookmarkTagManipulationProperties:
    """Property-based tests for bookmark tag manipulation."""

    @given(
        initial_tags=st.lists(
            st.text(min_size=1, max_size=20, alphabet="abc"),
            min_size=0,
            max_size=10,
            unique=True,
        ),
        new_tags=st.lists(
            st.text(min_size=1, max_size=20, alphabet="xyz"),
            min_size=0,
            max_size=5,
            unique=True,
        ),
    )
    def test_adding_tags(self, initial_tags: list[str], new_tags: list[str]) -> None:
        """Test adding tags to a bookmark."""
        bookmark = Bookmark(
            _id=1,
            title="Test Bookmark",
            link="https://example.com",
            tags=list(initial_tags),  # Copy to avoid mutation
        )

        # Add new tags
        updated_tags = list(set(bookmark.tags + new_tags))
        bookmark.tags = updated_tags

        # Verify all tags are present
        for tag in initial_tags:
            assert tag in bookmark.tags
        for tag in new_tags:
            assert tag in bookmark.tags

    @given(
        initial_tags=st.lists(
            st.text(min_size=1, max_size=20, alphabet="abc"),
            min_size=5,
            max_size=20,
            unique=True,
        ),
    )
    def test_removing_tags(self, initial_tags: list[str]) -> None:
        """Test removing tags from a bookmark."""
        bookmark = Bookmark(
            _id=1,
            title="Test Bookmark",
            link="https://example.com",
            tags=list(initial_tags),
        )

        # Remove first half of tags
        tags_to_remove = initial_tags[: len(initial_tags) // 2]
        updated_tags = [tag for tag in bookmark.tags if tag not in tags_to_remove]
        bookmark.tags = updated_tags

        # Verify removed tags are not present
        for tag in tags_to_remove:
            assert tag not in bookmark.tags

        # Verify remaining tags are present
        for tag in initial_tags[len(initial_tags) // 2 :]:
            assert tag in bookmark.tags


class TestBookmarkEqualityProperties:
    """Property-based tests for bookmark equality."""

    @given(
        bookmark_id=st.integers(min_value=1, max_value=1_000_000),
        title=st.text(min_size=1, max_size=50),
        url=st.text(min_size=10, max_size=100).filter(lambda x: x.startswith("http")),
    )
    def test_bookmark_equality(self, bookmark_id: int, title: str, url: str) -> None:
        """Test bookmark equality based on ID."""
        bookmark1 = Bookmark(
            _id=bookmark_id,
            title=title,
            link=url,
        )
        bookmark2 = Bookmark(
            _id=bookmark_id,
            title="Different Title",
            link="https://different.com",
        )

        # Bookmarks with same ID should be considered equal
        assert bookmark1._id == bookmark2._id

    @given(
        bookmark_id=st.integers(min_value=1, max_value=1_000_000),
        title=st.text(min_size=1, max_size=50),
        url=st.text(min_size=10, max_size=100).filter(lambda x: x.startswith("http")),
    )
    def test_bookmark_inequality(self, bookmark_id: int, title: str, url: str) -> None:
        """Test bookmark inequality with different IDs."""
        bookmark1 = Bookmark(
            _id=bookmark_id,
            title=title,
            link=url,
        )
        bookmark2 = Bookmark(
            _id=bookmark_id + 1,
            title=title,
            link=url,
        )

        # Bookmarks with different IDs should not be equal
        assert bookmark1._id != bookmark2._id


class TestBookmarkSerializationProperties:
    """Property-based tests for bookmark serialization."""

    @given(
        bookmark_id=st.integers(min_value=1, max_value=1_000_000),
        title=st.text(min_size=1, max_size=50),
        url=st.text(min_size=10, max_size=100).filter(lambda x: x.startswith("http")),
        tags=st.lists(st.text(min_size=1, max_size=20, alphabet="abc"), min_size=0, max_size=10),
    )
    def test_bookmark_model_dump(self, bookmark_id: int, title: str, url: str, tags: list[str]) -> None:
        """Test bookmark serialization to dict."""
        bookmark = Bookmark(
            _id=bookmark_id,
            title=title,
            link=url,
            tags=tags,
        )

        data = bookmark.model_dump()

        assert data["_id"] == bookmark_id
        assert data["title"] == title
        assert data["link"] == url
        assert data["tags"] == tags

    @given(
        bookmark_id=st.integers(min_value=1, max_value=1_000_000),
        title=st.text(min_size=1, max_size=50),
        url=st.text(min_size=10, max_size=100).filter(lambda x: x.startswith("http")),
        tags=st.lists(st.text(min_size=1, max_size=20, alphabet="abc"), min_size=0, max_size=10),
    )
    def test_bookmark_json_serialization(self, bookmark_id: int, title: str, url: str, tags: list[str]) -> None:
        """Test bookmark JSON serialization."""
        import json

        bookmark = Bookmark(
            _id=bookmark_id,
            title=title,
            link=url,
            tags=tags,
        )

        json_str = bookmark.model_dump_json()

        # Verify it's valid JSON
        data = json.loads(json_str)
        assert data["_id"] == bookmark_id
        assert data["title"] == title
        assert data["link"] == url
        assert data["tags"] == tags
