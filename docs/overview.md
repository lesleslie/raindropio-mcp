# Overview

The Raindrop.io MCP server is built with FastMCP and organised around a small
set of Python packages:

- `raindropio_mcp.config` – `RaindropSettings` for environment-driven
  configuration. The settings object is cached via `get_settings()` and validates
  the presence of `RAINDROP_TOKEN`.
- `raindropio_mcp.clients` – shared HTTP utilities plus `RaindropClient`, a thin
  wrapper over the Raindrop REST API with typed responses and error handling.
- `raindropio_mcp.tools` – tool registry, tool groups, and metadata for the
  Model Context Protocol. `register_all_tools` wires every tool into FastMCP.
- `raindropio_mcp.server` – creates the FastMCP application, registers tools, and
  exposes an `app` object for import by MCP clients or HTTP servers.
- `raindropio_mcp.main` – CLI entrypoint used by `python -m raindropio_mcp` and
  the `raindropio-mcp` console script.

## Package Dependency Graph

![Package dependency graph showing inter-package dependencies between config, client, models, tools, and server layers](https://mermaid.ink/svg/pako:eNp9kF1rwjAUhu_3K4K7dlOrGx1D6EdqKwxk612QEttjF4hNSbJB__00VnuQ4bnJ0_OE9_Sk1rz9Jnn8QI5lfna1-x6VqtmLeuS6pwrYJxdNpVX7BdaKpjbvO_28rMEWpm9s3WVoKnfe5kkBjTVDYMhCbiDN803k1PZqouuoWxOzc0yx56VVurs78aAqkGggZZuu4o0VJflwashN2IZ3UvHq_g5WKRy4YqdGoaEWxl5-5lQp80l-VCQREu5HGtC_oIfMjJUauIWCt-0QuGaH44s8tf8tHJPxeEkCx5HjEDHuU8SJ49TxCnGEmCI-388cp4gjxOdZa8cZWtZ2EkhA9kLKt0fqz0NvgUTUi1cae7MpErQXySJ4mXlIpL2YB_6EzpDIeuFPpl5C_wCmcbZo)

## Tool Registration Flow

1. `create_app()` (server.py) instantiates a FastMCP app.
1. We build a shared `RaindropClient` using `build_raindrop_client()`.
1. `register_all_tools()` receives the app and client, registering tools grouped
   by category (collections, bookmarks, tags, account, system).
1. A shutdown hook closes the `RaindropClient` to release `httpx` resources.

![Component interaction flowchart showing tool registration and lifecycle](https://mermaid.ink/svg/pako:eNptktFugjAUhu_3FA270Qs3AVFZFhOQ4q6Nd2QhtVRprJS0Nerbr9ZmOcsg4TQ_31dKOT0IeaUtUQbtihdkr6wKqGLEsJr0_WgcfKPJZIXyKthfuGhqRXjXKNnXVHDWmYfgpuVOW1fB1gtrxxHvtCEdZV7LnFZUgWJHrg1TNRGiNlIK_fsqVwon4hCYVArBqOGye07wujcjYO6lPJ2JOg15MfAMOQ4pM6C0_NgKe5shMYFrEkPbIWkOpAMXbt3_1gJY_NxLZWp2c8OAvIT_j1J56Qa1FGj6bofzH8sVHDq3rILdA6Gtn8Aab-HoKTxDDMMMhgSGOQwLGJYwpCC4UroHmyqwPdbtxTTy2qHWdtN_zMbxL3tE3el6o0JqNhp_7tX7assEI5qh1pj-hnq7G7hPbe6C2eNnOyA-XtNpGJcYgNyDBS7iKASg8GCWpVMcAVB6kExxvIZg4wFOZ3mcAPDlQZlk8yj-Abll-60)

Tools use the minimal wrappers in `raindropio_mcp.tools.*` to validate payloads
with Pydantic models (`BookmarkCreate`, `CollectionUpdate`, etc.) before calling
into `RaindropClient`.

## Data Models

`raindropio_mcp.models` mirrors the responses documented by Raindrop.io. Each
model honours nested identifiers (e.g. `_id` mapped via aliases) and optional
fields so the serialized output from tools matches the API closely.
