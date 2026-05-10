"""Bookmark models mirroring Raindrop.io responses."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from raindropio_mcp.models.collection import CollectionRef


class MediaPreview(BaseModel):
    """Media metadata present on certain bookmarks."""

    type: str | None = None
    link: str | None = None
    screenshot: str | None = None

    model_config = ConfigDict(extra="ignore")


class Bookmark(BaseModel):
    """Raindrop (bookmark) entity."""

    id: int = Field(..., alias="_id", serialization_alias="_id")
    title: str
    link: str
    excerpt: str | None = None
    note: str | None = None
    tags: list[str] = Field(default_factory=list)
    important: bool | None = None
    favorite: bool | None = None
    type: str | None = None
    cover: str | None = None
    collection: CollectionRef | None = None
    collection_id: int | None = Field(default=None, alias="collectionId")
    created: str | None = None  # API returns ISO date string
    last_update: str | None = Field(default=None, alias="lastUpdate")
    domain: str | None = None
    source: str | None = None
    sort: int | None = None
    media: list[Any] | None = None  # Can be list of MediaPreview or empty list
    highlights: list[Any] | None = None
    please_parse: dict[str, Any] | None = Field(default=None, alias="pleaseParse")
    creator_ref: dict[str, Any] | None = Field(default=None, alias="creatorRef")
    user: dict[str, Any] | None = None
    removed: bool | None = None

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class BookmarkResponse(BaseModel):
    """Single bookmark response wrapper."""

    result: bool
    item: Bookmark | None = None
    error: str | None = None


class BookmarksResponse(BaseModel):
    """List response for bookmarks."""

    result: bool
    items: list[Bookmark]
    count: int | None = None
    collection_id: int | None = None
    error: str | None = None


__all__ = [
    "Bookmark",
    "BookmarkResponse",
    "BookmarksResponse",
    "MediaPreview",
]
