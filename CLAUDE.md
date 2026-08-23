# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

For a shorter, tool-neutral bootstrap document, start with `AGENTS.md`.

## Project Overview

MCP server for the Raindrop.io bookmark management API. Exposes 30 tools
across 9 groups (account, batch, bookmarks, collections, filters,
highlights, import_export, system, tags) plus a `health_check` tool and
the `discover_tools` meta-tool.

## Tool Profile System

Tools are gated by the `RAINDROPIO_TOOL_PROFILE` environment variable:

- `full` (default): All 30 Raindrop.io tools + `health_check` + `discover_tools`
- `standard`: Same as `full` (Tier-A trivial mapping)
- `minimal`: Only `health_check` + `discover_tools` + HTTP `/health` + `/healthz`

`health_check` is always present (mandatory group) — the W4.1 keystone
for `MINIMAL=health, STANDARD/FULL=all`.

### Custom registry wrapper

raindropio-mcp uses a custom `FastMCPToolRegistry` (see
`raindropio_mcp/tools/tool_registry.py`) that wraps FastMCP's `@tool`
decorator. The W3.1 backend-lambda adapter pattern is used: each
`register_<group>_tools(registry, client)` is wrapped in a closure that
captures a caller-supplied `RaindropClient` and constructs
`FastMCPToolRegistry(server)` inside the call.

### Production path

`create_app` is async (calls `await _apply_tool_profile(...)`); sync
callers (CLI startup, `__main__.py`, `__getattr__`) use
`create_app_sync()` which wraps via `_run_async_safely` (asyncio.run or
private ThreadPoolExecutor — the W4.6 unifi-mcp / porkbun-domain-mcp
precedent).

### Lifespan

The MCP server's lifespan finally block closes the `RaindropClient`
instance — the W4.3 keystone prevents httpx pool leaks in long-running
deployments.

## Architecture

- **Entry point**: `raindropio_mcp/server.py` — async `create_app` + sync shim
- **Tools**: `raindropio_mcp/tools/` — 9 register fns + `register_health_tool` + `profiles.py`
- **Client**: `raindropio_mcp/clients/` — `RaindropClient` (httpx-based)
- **Config**: `raindropio_mcp/config/` — Oneiric-style layered settings
- **Tests**: `tests/unit/test_tool_profile.py` — W4 contract guards

See `docs/architecture/tool-profile-rationale.md` for the full
architectural decision rationale.

## Oneiric action kits

Before writing common primitives (HMAC, token gen, schema validation,
retries, redaction, HTTP probing, serialization, compression, hashing,
data transforms), check `oneiric.actions` — catalog lives at
`oneiric/docs/action-kits.md` in the oneiric project. Discovery hint:
`mahavishnu/.claude/decisions/promote-oneiric-action-kits.md`.
