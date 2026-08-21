# Tool Profile Adoption (W4.7)

This document captures the architectural decision to adopt
`mcp_common.tools.dispatch._apply_tool_profile` for the raindropio-mcp MCP
server. The decision replaces a monolithic `register_all_tools(app, client)`
call with a 3-tier profile-gated dispatch (MINIMAL / STANDARD / FULL).

## Context

Before W4.7, `raindropio_mcp/server.py` registered every Raindrop.io tool
unconditionally at module import time:

```python
client = build_raindrop_client(settings)
register_all_tools(app, client)
```

That gave operators no way to shrink the tool surface for minimal /
standard deployments — every server carried all 30 tools regardless of
load. For containerized deployments that need a small liveness probe or a
load-balanced setup where the AI orchestrator only needs a couple of
discovery tools, exposing the full Raindrop.io API surface wastes context
tokens and increases attack surface area.

## Plan vs. Reality

The plan listed raindropio-mcp as "0 tools (MANDATORY opt-out)". **That
reconnaissance was stale.** The actual repo exposes **30 tools** through
a custom `FastMCPToolRegistry` wrapper at
`raindropio_mcp/tools/tool_registry.py`. The "MANDATORY opt-out"
assumption is therefore invalid — we adopt the standard pattern with
backend-lambda adapters (the W3.1 lesson).

## Architectural Choice

### Custom registry wrapper

Unlike sister Tier-A repos (mailgun-mcp, porkbun-domain-mcp, etc.),
raindropio-mcp uses a custom `FastMCPToolRegistry` that wraps
`self._app.tool(name=..., description=...)(func)`. Each
`register_<group>_tools(registry, client)` function takes a registry +
client pair — NOT the `(server, settings)` contract the W0 dispatch
helper expects.

The W3.1 backend-lambda lesson applies: each register fn is wrapped in a
closure that captures a caller-supplied `RaindropClient` and constructs
`FastMCPToolRegistry(server)` inside the call. The adapter map is built
fresh per-dispatch via `_build_registration_map(client)`.

### Sync vs. async create_app

`create_app` is now `async` (per the W2b.3 keystone — the W0 helper is
async; the sync wrapper raises `RuntimeError` inside an event loop).
A `create_app_sync` shim wraps the async coroutine via `_run_async_safely`
(asyncio.run when no loop, private ThreadPoolExecutor with a fresh
asyncio.run when pytest-asyncio has a loop — the W4 unifi-mcp / W4.6
porkbun-domain-mcp precedent). The `__main__.py` `RaindropMCPServer`
class uses `create_app_sync()` so the sync constructor still works.

### Lifespan (W4.3)

The pre-W4 lifespan pattern already wraps `app._mcp_server.lifespan` so
the W0 client is closed in `finally`:

```python
@asynccontextmanager
async def lifespan(server: Any) -> AsyncGenerator[dict[str, Any]]:
    async with original_lifespan(server) as state:
        try:
            yield state
        finally:
            await client.close()
```

The W4.7 refactor preserves this — the same `client` instance is
attached to `app._raindrop_client` (informational, so the dispatch
adapters can re-derive it) AND is the one closed in the lifespan finally
block. No httpx pool leak.

## Profile Tiers

Tier-A canonical mapping per the W4 plan: `MINIMAL=health, STANDARD/FULL=all`.

| Profile | Tools |
|-----------|--------------------------------------------------------------|
| MINIMAL | `health_check` + `discover_tools` + `/health` + `/healthz` |
| STANDARD | All 30 Raindrop.io tools + `health_check` + `discover_tools` |
| FULL | All 30 Raindrop.io tools + `health_check` + `discover_tools` |

`RAINDROPIO_MANDATORY_GROUPS = {"health_tools"}` so `health_check` is
exposed at every level. The W0 helper's `essential_tool_names={"health_check"}`
subset check enforces this at runtime.

## Files

- `raindropio_mcp/tools/profiles.py` — dispatch machinery (new in W4.7)
- `raindropio_mcp/tools/__init__.py` — adds `register_health_tool` callable
- `raindropio_mcp/server.py` — async `create_app` + sync shim + dispatch
- `raindropio_mcp/__main__.py` — uses `create_app_sync()` (sync constructor compat)
- `raindropio_mcp/pyproject.toml` — bumps `mcp-common>=0.18.0`
- `tests/unit/test_tool_profile.py` — structural + behavioral guards
- `docs/architecture/tool-profile-rationale.md` — this doc

## Lessons Applied

- **W3.1**: backend-lambda adapter for non-`(server, settings)` register fns
- **W2b.3**: production uses `_apply_tool_profile` (async helper), not sync wrapper
- **W4.1**: `MINIMAL=health`, `STANDARD/FULL=all`; caller-supplied settings + client
- **W4.3**: lifespan finally closes client (already in place; regression test added)
- **W3.2**: `_GROUP_REGISTRY: list[tuple[str, str]]` SSOT constant; AST guard
  for `ast.Await(value=ast.Call(...))`
- **W2b.1**: startup banners gated behind `RAINDROPIO_TOOL_PROFILE in {"", "full"}`
- **W2b.2**: `__init__.py` `__version__` sourced from
  `importlib.metadata.version()` (already in place pre-W4)
