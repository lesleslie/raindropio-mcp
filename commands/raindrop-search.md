---
description: Full-text search across every Raindrop.io collection, returning paginated bookmark matches.
argument-hint: <query> [--page N] [--per-page N]
allowed-tools: mcp__raindropio__search_bookmarks, mcp__raindropio__list_collections
---

# /raindrop-search

Full-text search across every bookmark in the authenticated Raindrop.io account.

## Usage

`/raindrop-search <query> [--page N] [--per-page N]`

Arguments:

- `<query>`: the free-text search string sent to Raindrop's `/search` endpoint.
- `--page N`: optional, 1-indexed page number for paging through large result sets. Defaults to `1` on the server.
- `--per-page N`: optional, results per page (typically `25`, `50`, or `100`).

## Workflow

1. Call `mcp__raindropio__search_bookmarks` with `query`, and any optional `page` / `per_page` flags.
2. Present the returned items as a flat list with `title`, `link`, `excerpt`, `collection` (title resolved via `mcp__raindropio__list_collections` when needed), `tags`, and `created`.
3. Report the page count and total match count if the server returns them.

## Example

`/raindrop-search "fastmcp transport" --per-page 10`
