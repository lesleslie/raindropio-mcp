# API Endpoint Mapping

This document provides a comprehensive mapping of Raindrop.io REST API endpoints to RaindropClient methods and MCP tools. Use this to understand the complete flow from external API to internal implementation.

## Three-Layer Architecture

```
┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│                         │     │                         │     │                         │
│   Raindrop.io API       │────▶│   RaindropClient        │────▶│   MCP Tools             │
│   REST Endpoints        │     │   Methods               │     │   Functions             │
│                         │     │                         │     │                         │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
```

## Account & Collections

| Raindrop API Endpoint | RaindropClient Method | MCP Tool Function |
|----------------------|----------------------|-------------------|
| `GET /user` | `get_me()` | `get_account_profile()` |
| `GET /collection/:id` | `get_collection()` | `get_collection()` |
| `GET /collections` | `list_collections()` | `list_collections()` |
| `POST /collection` | `create_collection()` | `create_collection()` |
| `PUT /collection/:id` | `update_collection()` | `update_collection()` |
| `DELETE /collection/:id` | `delete_collection()` | `delete_collection()` |

## Bookmarks

| Raindrop API Endpoint | RaindropClient Method | MCP Tool Function |
|----------------------|----------------------|-------------------|
| `GET /raindrop/:id` | `get_bookmark()` | `get_bookmark()` |
| `GET /raindrops/:collectionId` | `list_bookmarks()` | `list_bookmarks()` |
| `GET /search` | `search_bookmarks()` | `search_bookmarks()` |
| `POST /raindrop` | `create_bookmark()` | `create_bookmark()` |
| `PUT /raindrop/:id` | `update_bookmark()` | `update_bookmark()` |
| `DELETE /raindrop/:id` | `delete_bookmark()` | `delete_bookmark()` |

## Highlights

| Raindrop API Endpoint | RaindropClient Method | MCP Tool Function |
|----------------------|----------------------|-------------------|
| `GET /raindrop/:id/highlights` | `list_highlights()` | `list_highlights()` |
| `GET /highlight/:id` | `get_highlight()` | `get_highlight()` |
| `POST /highlight` | `create_highlight()` | `create_highlight()` |
| `PUT /highlight/:id` | `update_highlight()` | `update_highlight()` |
| `DELETE /highlight/:id` | `delete_highlight()` | `delete_highlight()` |

## Tags

| Raindrop API Endpoint | RaindropClient Method | MCP Tool Function |
|----------------------|----------------------|-------------------|
| `GET /tags` | `list_tags()` | `list_tags()` |
| `PUT /tag` | `rename_tag()` | `rename_tag()` |
| `DELETE /tag` | `delete_tag()` | `delete_tag()` |

## Batch Operations

| Operation | RaindropClient Method | MCP Tool Function |
|-----------|----------------------|-------------------|
| Move Multiple | `batch_move_bookmarks()` | `batch_move_bookmarks()` |
| Delete Multiple | `batch_delete_bookmarks()` | `batch_delete_bookmarks()` |
| Update Multiple | `batch_update_bookmarks()` | `batch_update_bookmarks()` |
| Tag Multiple | `batch_tag_bookmarks()` | `batch_tag_bookmarks()` |
| Untag Multiple | `batch_untag_bookmarks()` | `batch_untag_bookmarks()` |

## Filters

| Operation | RaindropClient Method | MCP Tool Function |
|-----------|----------------------|-------------------|
| Apply Filters | `apply_filters()` | `apply_filters()` |
| Filter by Collection | `get_filtered_bookmarks_by_collection()` | `get_filtered_bookmarks_by_collection()` |

## Import/Export

| Operation | RaindropClient Method | MCP Tool Function |
|-----------|----------------------|-------------------|
| Import Bookmarks | `import_bookmarks()` | `import_bookmarks()` |
| Export Bookmarks | `export_bookmarks()` | `export_bookmarks()` |

## System

| Operation | RaindropClient Method | MCP Tool Function |
|-----------|----------------------|-------------------|
| Health Check | N/A | `ping()` |

## Visual Map

!API endpoint mapping flowchart showing Raindrop API endpoints, RaindropClient methods, and MCP tools

## Coverage Status

✅ **Fully Covered:**

- Account operations (100%)
- Collection CRUD (100%)
- Bookmark CRUD (100%)
- Highlight management (100%)
- Tag management (100%)
- Batch operations (100%)
- Filtering (100%)
- Import/Export (100%)

📋 **Not Yet Implemented:**

- Sharing functionality (when Raindrop exposes these endpoints)
- User profile updates beyond GET

## Adding New Endpoints

When adding new Raindrop.io API endpoints:

1. Add the HTTP client method to `RaindropClient` in `raindropio_mcp/clients/raindrop_client.py`
1. Create/update Pydantic models in `raindropio_mcp/models/` for request/response
1. Create a tool function in the appropriate `raindropio_mcp/tools/*.py` file
1. Register the tool with `@registry.register(ToolMetadata(...))`
1. Add the mapping to this document
1. Update the API mapping diagram above
