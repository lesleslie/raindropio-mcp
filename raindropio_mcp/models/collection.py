"""Pydantic models describing Raindrop.io collections."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CollectionRef(BaseModel):
    """Lightweight representation used in bookmark payloads."""

    id: int = Field(..., alias="$id", serialization_alias="$id")
    title: str | None = None
    oid: int | None = None  # Original collection ID in nested refs

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class Collection(BaseModel):
    """Full Raindrop.io collection entity."""

    id: int = Field(..., alias="_id", serialization_alias="_id")
    title: str
    description: str | None = None
    slug: str | None = None
    created: str | None = None  # API returns ISO date string, not datetime
    last_update: str | None = Field(default=None, alias="lastUpdate")
    last_action: str | None = Field(default=None, alias="lastAction")
    parent_id: int | None = Field(default=None, alias="parentId")
    parent: int | None = None  # Can be None for root collections
    public: bool | None = None
    view: str | None = None
    sort: int | None = None  # FIX: API returns int, not str
    count: int | None = None
    cover: list[Any] | None = None  # FIX: API returns list, not str
    color: str | None = None
    expanded: bool | None = None
    author: bool | None = None
    access: dict[str, Any] | None = None
    user: dict[str, Any] | None = None
    creator_ref: dict[str, Any] | None = Field(default=None, alias="creatorRef")
    permissions: dict[str, bool] | None = None

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class CollectionResponse(BaseModel):
    """Standard response wrapper returned by Raindrop.io for collections."""

    result: bool
    collection: Collection | None = None
    error: str | None = None


class CollectionsResponse(BaseModel):
    """List response for collections endpoints."""

    result: bool
    items: list[Collection]
    count: int | None = None
    error: str | None = None


__all__ = [
    "Collection",
    "CollectionRef",
    "CollectionResponse",
    "CollectionsResponse",
]
