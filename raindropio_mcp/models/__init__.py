"""Pydantic models describing Raindrop.io entities."""

from raindropio_mcp.models.batch_payloads import (
    BatchDeleteBookmarks,
    BatchMoveBookmarks,
    BatchOperationResponse,
    BatchTagBookmarks,
    BatchUntagBookmarks,
    BatchUpdateBookmarks,
)
from raindropio_mcp.models.bookmark import Bookmark, BookmarkResponse, BookmarksResponse
from raindropio_mcp.models.collection import (
    Collection,
    CollectionRef,
    CollectionResponse,
    CollectionsResponse,
)
from raindropio_mcp.models.filter_payloads import (
    BookmarkFilter,
    FilteredBookmarksResponse,
)
from raindropio_mcp.models.highlight import (
    Highlight,
    HighlightCreate,
    HighlightResponse,
    HighlightsResponse,
    HighlightUpdate,
)
from raindropio_mcp.models.import_export_payloads import (
    ExportFormat,
    ImportResult,
    ImportSource,
)
from raindropio_mcp.models.payloads import (
    BookmarkCreate,
    BookmarkUpdate,
    CollectionCreate,
    CollectionUpdate,
    TagRename,
)
from raindropio_mcp.models.tag import Tag, TagsResponse
from raindropio_mcp.models.user import User, UserResponse

__all__ = [
    "Bookmark",
    "BookmarkCreate",
    "BookmarkResponse",
    "BookmarkUpdate",
    "BookmarksResponse",
    "BatchDeleteBookmarks",
    "BatchMoveBookmarks",
    "BatchOperationResponse",
    "BatchTagBookmarks",
    "BatchUntagBookmarks",
    "BatchUpdateBookmarks",
    "BookmarkFilter",
    "Collection",
    "CollectionCreate",
    "CollectionRef",
    "CollectionResponse",
    "CollectionUpdate",
    "CollectionsResponse",
    "ExportFormat",
    "FilteredBookmarksResponse",
    "Highlight",
    "HighlightCreate",
    "HighlightResponse",
    "HighlightUpdate",
    "HighlightsResponse",
    "ImportResult",
    "ImportSource",
    "Tag",
    "TagRename",
    "TagsResponse",
    "User",
    "UserResponse",
]
