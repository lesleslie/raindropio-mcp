# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastMCP-based Model Context Protocol server that exposes the Raindrop.io API to AI assistants. The server provides comprehensive bookmark management including collections, tags, highlights, batch operations, filtering, and import/export functionality.

**Tech Stack:** Python 3.13, FastMCP, httpx, Pydantic, pytest

## Common Commands

```bash
# Dependency management
uv sync                          # Install/sync all dependencies

# Running the server
uv run python -m raindropio_mcp           # Run in stdio mode (default)
uv run raindropio-mcp                     # Alternative via console script
uv run python -m raindropio_mcp --http    # Run with HTTP transport
uv run python -m raindropio_mcp --http --http-port 3034  # Custom port

# Testing
uv run pytest                             # Run all tests
uv run pytest tests/unit/test_client.py   # Run specific test file
uv run pytest -k "test_name"              # Run tests matching pattern
uv run pytest --cov=. --cov-report=html   # Generate HTML coverage report

# Code quality
uv run crackerjack                        # Run full suite (ruff + mypy + pytest + bandit)
uv run ruff check --fix                   # Lint and auto-fix
uv run mypy .                             # Type checking only
uv run bandit -r raindropio_mcp           # Security scanning
```

## Architecture Overview

### Core Components

1. **Configuration Layer** (`raindropio_mcp/config/`)

   - `RaindropSettings`: Pydantic-based settings that validate environment variables
   - Cached via `@lru_cache` in `get_settings()`
   - Required: `RAINDROP_TOKEN` (personal access token)
   - Optional: request timeout, connection limits, HTTP transport settings
   - Nested configs: `RetryConfig`, `CacheConfig`, `ObservabilityConfig`

1. **Client Layer** (`raindropio_mcp/clients/`)

   - `BaseHTTPClient`: Abstract async HTTP client with retry logic, error mapping, and rate-limit handling
   - `RaindropClient`: Typed wrapper around Raindrop.io REST API
     - Inherits retry/error handling from `BaseHTTPClient`
     - Returns typed Pydantic models for all responses
     - Includes pagination helpers for bookmark lists
   - `client_factory.py`: Factory functions for client instantiation

1. **Models Layer** (`raindropio_mcp/models/`)

   - Pydantic models mirroring Raindrop.io API responses
   - Key models: `Bookmark`, `Collection`, `Tag`, `User`, `Highlight`
   - Payload models: `BookmarkCreate`, `BookmarkUpdate`, `CollectionCreate`, `CollectionUpdate`
   - Batch operation models: `BatchMoveBookmarks`, `BatchDeleteBookmarks`, `BatchUpdateBookmarks`, `BatchTagBookmarks`, `BatchUntagBookmarks`
   - Filter models: `BookmarkFilter`, `FilteredBookmarksResponse`
   - Import/Export models: `ImportSource`, `ImportResult`, `ExportFormat`
   - Uses field aliases to map API's `_id` to Pydantic-friendly names

1. **Tools Layer** (`raindropio_mcp/tools/`)

   - FastMCP tools organized by domain (9 categories total):
     - `collections.py`: List, get, create, update, delete collections
     - `bookmarks.py`: List, search, get, create, update, delete bookmarks
     - `tags.py`: List, rename, delete tags
     - `highlights.py`: List, get, create, update, delete highlights/annotations
     - `batch.py`: Batch move, delete, update, tag, untag bookmarks
     - `filters.py`: Apply complex filters across collections
     - `import_export.py`: Import from external sources, export to various formats
     - `account.py`: Get authenticated user profile
     - `system.py`: Health check / ping
   - `tool_registry.py`: Custom registry that wraps FastMCP decorators with metadata
   - Tools registered via `register_all_tools()` in `__init__.py`

1. **Server & Entrypoint** (`raindropio_mcp/`)

   - `server.py`: `create_app()` builds FastMCP app with lifecycle management
     - Creates shared `RaindropClient` instance
     - Registers shutdown hook to close client and release HTTP connections
     - Stores client reference on app for access by tools
   - `main.py`: CLI entrypoint with argument parsing
     - Configures structured JSON or text logging
     - Supports both stdio and HTTP transports
     - Accepts `--http`, `--http-host`, `--http-port`, `--http-path` flags

### Layered Architecture

![Five-layer architecture diagram showing Config, Client, Models, Tools, and Server layers with dependencies](https://mermaid.ink/svg/pako:eNqFklFrgzAUhd_7K8Q9d1ZtN9zDQGNKBx2U1jcZkmmahqZGYjrw3y8mlcU5uoBcjt-9nOONRKDm5Gz3M0ed9vpJtAa8PlKSu6ZeBZKU184WdVi4H7q1P7Gfu3tE60rw5oClpDVpbRzkLsGyaMcI15WuvxwZxbVUjrpOrBJllaAWb7JsZ1psGPzkmMIwd0v9sjiiUnLR3c3xzivM2tw1dZID9Dk4P1-QOHuAM4bLfjVehoi3oeTE1GO7AxVthzrGUdV6CZLlyVtTJrG4v42M8z6ELpMMqcoQ6RYHIIkJFxTbe0-Vp1S0EJjQVv7zwQcsvrDIXVMnZlCZlQIrnwI1jQ2Uy0Ut_bHpHLB9-8sjDpz5_FVdz8zcklG-rcBYmc7U1yodqWSkbnODMgze5nxbxTdmHKBvrUB2DKuf2DlSxl4eYLRMwpVFVChDnmEaBr5FwDCzXsVPQWiRdCDLOFrAwCJwINHCD9fwG6-G56o)

### Data Flow

1. MCP client sends tool request → FastMCP receives and routes to registered tool
1. Tool validates input with Pydantic models → calls `RaindropClient` method
1. `RaindropClient` makes async HTTP request via `BaseHTTPClient`
1. `BaseHTTPClient` applies retry logic, handles errors, maps to exceptions
1. Response validated with Pydantic models → returned as JSON-serializable dict
1. FastMCP sends response back to MCP client

![Sequence diagram showing complete request lifecycle from MCP client through FastMCP, Tool, RaindropClient, BaseHTTPClient to Raindrop API with retry and error handling](https://mermaid.ink/svg/pako:eNp1kVFrwjAUhd_3K-4PqCibwixDaOuKG4srXdh71gYNxKRL0qH_fjdpXVdFHy7Id3rPPSeWf7dcVXwt2M6wwx3gr2HGiUo0TDkgGTCLs4BMCq7clSAnXpAz61B0RamHVGsJeasqJ7S6kpTBoWRC1UY3N1zSIEqZ5RtKixuipHj5v8r_D5owSDZZrXISd9eUPrbtVuQECY2h1K3j4HRQBEI78MmkqBmy4lSjj6iA6JpL-6cps7ivBwh3e11DxmS3ovS2KXJ_98g2PZOkaeQJkTMneNM7UQ0YE8Qhlt_39GWmq5Qzww0krdsHGcLJ2ME2Wlk-tiCsgWdjtLFhyYapWnKY3y-ni-PxLO2DFMxYXsPrx_t2SODBjRrOoq4remrw4wH0FWZa_XDjfLtrUbke9S_ircaH45MgI_7y7CJTGFuNZ2jciHdHoaSuPq1imM8eI4y28GMZwWI28-Pejwc_5hcbaOTDJVKC6X0sYMdDykN47F_iMOwi)

### Error Handling Strategy

- Custom exceptions in `raindropio_mcp/utils/exceptions.py`:
  - `APIError`: Base for all Raindrop API errors
  - `NotFoundError`: HTTP 404 responses
  - `RateLimitError`: HTTP 429 with optional retry-after
  - `NetworkError`: Transport/timeout failures
  - `ConfigurationError`: Missing/invalid settings
- Retry logic in `BaseHTTPClient` for status codes: 408, 425, 429, 500, 502, 503, 504
- Exponential backoff with configurable factor and max attempts

### Error Mapping Flow

![Flowchart showing HTTP status codes mapped to appropriate exception types including NotFoundError, RateLimitError, and APIError](https://mermaid.ink/svg/pako:eNpdkV1vgjAUhu_3K06yazIGss1lMeFTmR8xyh3xAuEYG5G6triRsf--WtkEetGc9H16Pt6zy-lnuk-YgMi7A3nseBJFS1ghP9GC4wY0bQTO91okouTg0gx_FKcu56LWhq5rxnBYgxuvUJSsgHWZpsj5pgUNdL0GL7aXoc8YZW9b9jBykkwW-iiRiy76WIPfRcPinOQkg4gesOjCZg1BFw4o25Is64ODGsbxgoqAlkV2o-WotGQpgpRAad1vLzVMLoOxqsFVwxCRI9Ky27hhSbbzIF0J41UicEaORNyKRpTCPCmqv_m5enX3mB5A1dLsnUDWzm5Jm62Lze-tbtbIzshAJd7cFuOqtU3jZZUlhSApzOXi8ivgKW32bxn4XymeBKGNXf5VV3HQiscqnncd7H8OFbTojdyn1MVFlaPsdEfy_PX-2fdM47EljBshsOwnw2wJYSP4w4FjWi1h2giW7puu8QuaANQT)

## Development Guidelines

### Code Style

- Python 3.13 syntax and features
- Ruff line length: 88 characters
- Type hints required for all functions (enforced by mypy)
- Async/await used throughout (no sync blocking calls)
- Prefer Pydantic models over raw dicts
- Use dataclasses with `slots=True` for internal data structures

### Adding New Tools

1. Define Pydantic models in `raindropio_mcp/models/` if needed
1. Add client method to `RaindropClient` with typed return
1. Create tool function in appropriate `raindropio_mcp/tools/*.py` file
1. Register with `@registry.register(ToolMetadata(...))` decorator
1. Call registration function from `register_all_tools()`
1. Write unit tests in `tests/unit/` mocking HTTP responses

### Testing Strategy

- All tests in `tests/unit/` (26 test files)
- `conftest.py` auto-injects `RAINDROP_TOKEN` via fixture
- `reset_settings_cache` fixture ensures clean state between tests
- Coverage threshold: 80% (enforced in `pyproject.toml`)
- Mock HTTP responses using `pytest` fixtures
- Tests never hit live Raindrop.io API

### Configuration & Environment

Required environment variable:

```bash
export RAINDROP_TOKEN="your-token-here"
```

Optional environment variables (all prefixed with `RAINDROP_`):

- `RAINDROP_BASE_URL`: API root (default: `https://api.raindrop.io/rest/v1`)
- `RAINDROP_USER_AGENT`: HTTP user agent (default: `raindropio-mcp/0.1.0`)
- `RAINDROP_REQUEST_TIMEOUT`: Timeout in seconds (default: 30.0)
- `RAINDROP_MAX_CONNECTIONS`: HTTP connection pool size (default: 10)
- `RAINDROP_ENABLE_HTTP_TRANSPORT`: Enable HTTP mode (default: false)
- `RAINDROP_HTTP_HOST`: HTTP bind address (default: `127.0.0.1`)
- `RAINDROP_HTTP_PORT`: HTTP port (default: 3034)
- `RAINDROP_HTTP_PATH`: HTTP endpoint path (default: `/mcp`)

Environment variables can also be set via `.env` file in project root.

## Key Implementation Notes

### Lifecycle Management

- The FastMCP app wraps its original lifespan context manager
- On shutdown, `client.close()` is called to release httpx connection pool
- This prevents resource leaks in long-running server processes

### Pagination Defaults

- `RaindropClient` stores pagination defaults: `{"page": 0, "perpage": 50}`
- `list_bookmarks()` and `search_bookmarks()` return `PaginatedBookmarks` dataclass
- Contains `items`, `count`, `collection_id`, `page`, `per_page` for pagination UI

### Authentication

- Bearer token authentication via `Authorization` header
- Token validation happens on first API call (not at startup)
- 401 responses raise `APIError` with helpful message about checking `RAINDROP_TOKEN`

### Tool Registry Pattern

- Custom `FastMCPToolRegistry` wraps FastMCP's `@app.tool` decorator
- Adds `ToolMetadata` with `name`, `description`, `category`, `examples`
- Enables programmatic inspection of registered tools
- All tools must be async functions (enforced at registration time)

## MCP Client Configuration

Example `mcp.json` for Claude Desktop:

```json
{
  "mcpServers": {
    "raindropio": {
      "command": "uv",
      "args": ["run", "python", "-m", "raindropio_mcp"],
      "env": {
        "RAINDROP_TOKEN": "your-token-here"
      }
    }
  }
}
```

For HTTP transport (see `example.mcp.json` and `example.mcp.dev.json` in repo).

## Troubleshooting

### Common Issues

- **Missing token error**: Ensure `RAINDROP_TOKEN` is set in environment or `.env`
- **Import errors**: Run `uv sync` to ensure all dependencies are installed
- **Test failures**: Check that `conftest.py` fixtures are being applied
- **Type errors**: Run `uv run mypy .` to catch type issues before running tests
- **Coverage below 80%**: Add tests for uncovered code paths or adjust threshold in `pyproject.toml`

### Debug Mode

Set `RAINDROP_OBSERVABILITY_LOG_LEVEL=DEBUG` for verbose logging.

<!-- CRACKERJACK INTEGRATION START -->

This project uses crackerjack for Python project management and quality assurance.

For optimal development experience with this crackerjack - enabled project, use these specialized agents:

- **🏗️ crackerjack-architect**: Expert in crackerjack's modular architecture and Python project management patterns. **Use PROACTIVELY** for all feature development, architectural decisions, and ensuring code follows crackerjack standards from the start.

- **🐍 python-pro**: Modern Python development with type hints, async/await patterns, and clean architecture

- **🧪 pytest-hypothesis-specialist**: Advanced testing patterns, property-based testing, and test optimization

- **🧪 crackerjack-test-specialist**: Advanced testing specialist for complex testing scenarios and coverage optimization

- **🏗️ backend-architect**: System design, API architecture, and service integration patterns

- **🔒 security-auditor**: Security analysis, vulnerability detection, and secure coding practices

```bash

Task tool with subagent_type ="crackerjack-architect" for feature planning


Task tool with subagent_type ="python-pro" for code implementation


Task tool with subagent_type ="pytest-hypothesis-specialist" for test development


Task tool with subagent_type ="security-auditor" for security analysis
```

**💡 Pro Tip**: The crackerjack-architect agent automatically ensures code follows crackerjack patterns from the start, eliminating the need for retrofitting and quality fixes.

This project follows crackerjack's clean code philosophy:

- **EVERY LINE OF CODE IS A LIABILITY**: The best code is no code

- **DRY (Don't Repeat Yourself)**: If you write it twice, you're doing it wrong

- **YAGNI (You Ain't Gonna Need It)**: Build only what's needed NOW

- **KISS (Keep It Simple, Stupid)**: Complexity is the enemy of maintainability

- \*\*Cognitive complexity ≤15 \*\*per function (automatically enforced)

- **Coverage ratchet system**: Never decrease coverage, always improve toward 100%

- **Type annotations required**: All functions must have return type hints

- **Security patterns**: No hardcoded paths, proper temp file handling

- **Python 3.13+ modern patterns**: Use `|` unions, pathlib over os.path

```bash

python -m crackerjack


python -m crackerjack - t


python -m crackerjack - - ai - agent - t


python -m crackerjack - a patch
```

1. **Plan with crackerjack-architect**: Ensure proper architecture from the start
1. **Implement with python-pro**: Follow modern Python patterns
1. **Test comprehensively**: Use pytest-hypothesis-specialist for robust testing
1. **Run quality checks**: `python -m crackerjack -t` before committing
1. **Security review**: Use security-auditor for final validation

- **Use crackerjack-architect agent proactively** for all significant code changes
- **Never reduce test coverage** - the ratchet system only allows improvements
- **Follow crackerjack patterns** - the tools will enforce quality automatically
- **Leverage AI agent auto-fixing** - `python -m crackerjack --ai-agent -t` for autonomous quality fixes

______________________________________________________________________

- This project is enhanced by crackerjack's intelligent Python project management.\*

<!-- CRACKERJACK INTEGRATION END -->
