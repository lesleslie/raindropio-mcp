from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from typing import Any
from unittest.mock import AsyncMock

import httpx
import pytest

from raindropio_mcp.clients.base_client import BaseHTTPClient
from raindropio_mcp.config.settings import RaindropSettings
from raindropio_mcp.utils.exceptions import APIError, NotFoundError, RateLimitError


@dataclass
class FakeResponse:
    status_code: int
    payload: Any
    headers: dict[str, Any] = field(default_factory=dict)

    def json(self) -> Any:
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload

    @property
    def text(self) -> str:
        if isinstance(self.payload, Exception):
            return ""
        return json.dumps(self.payload)


@pytest.fixture
async def base_client(monkeypatch: pytest.MonkeyPatch) -> BaseHTTPClient:
    settings = RaindropSettings(token="demo")
    client = BaseHTTPClient(settings)
    yield client
    await client.close()


@pytest.mark.asyncio
async def test_request_success(monkeypatch: pytest.MonkeyPatch, base_client: BaseHTTPClient) -> None:
    fake = FakeResponse(200, {"ok": True})
    base_client._client.request = AsyncMock(return_value=fake)
    response = await base_client.request("GET", "/collections")
    assert response is fake


@pytest.mark.asyncio
async def test_request_handles_rate_limit(monkeypatch: pytest.MonkeyPatch, base_client: BaseHTTPClient) -> None:
    fake = FakeResponse(429, {"result": False}, headers={"Retry-After": "12"})
    base_client._client.request = AsyncMock(return_value=fake)
    with pytest.raises(RateLimitError) as exc:
        await base_client.request("GET", "/collections")
    assert exc.value.backoff_seconds() == 12


@pytest.mark.asyncio
async def test_request_retries_and_succeeds(monkeypatch: pytest.MonkeyPatch, base_client: BaseHTTPClient) -> None:
    first = FakeResponse(500, {"error": "server"})
    second = FakeResponse(200, {"ok": True})
    base_client._client.request = AsyncMock(side_effect=[first, second])
    sleep = AsyncMock(return_value=None)
    monkeypatch.setattr(asyncio, "sleep", sleep)

    response = await base_client.request("GET", "/collections")
    assert response is second
    sleep.assert_awaited()


@pytest.mark.asyncio
async def test_get_json_not_found(monkeypatch: pytest.MonkeyPatch, base_client: BaseHTTPClient) -> None:
    fake = FakeResponse(404, {"error": "missing"})
    base_client._client.request = AsyncMock(return_value=fake)
    with pytest.raises(NotFoundError):
        await base_client.get_json("GET", "/raindrop/1")


@pytest.mark.asyncio
async def test_get_json_invalid_json(monkeypatch: pytest.MonkeyPatch, base_client: BaseHTTPClient) -> None:
    error = FakeResponse(200, json.JSONDecodeError("invalid", "", 0))
    base_client._client.request = AsyncMock(return_value=error)
    with pytest.raises(APIError):
        await base_client.get_json("GET", "/collections")
