---
description: Add a new bookmark to a Raindrop.io collection, with optional title, tags, and notes.
argument-hint: <url> --collection <id> [--title <text>] [--tags <a,b,c>] [--note <text>]
allowed-tools: mcp__raindropio__create_bookmark, mcp__raindropio__list_collections
---

# /raindrop-add

Add a bookmark to a Raindrop.io collection.

## Usage

`/raindrop-add <url> --collection <id> [--title <text>] [--tags <a,b,c>] [--note <text>]`

Arguments:

- `<url>`: absolute URL to bookmark. Must include scheme (`https://` / `http://`).
- `--collection <id>`: numeric ID of the destination collection. Use `mcp__raindropio__list_collections` to look up the ID if the caller only knows the title.
- `--title <text>`: optional override for the page title. When omitted, the server stores the page's `<title>` (or the URL as a fallback).
- `--tags <a,b,c>`: optional comma-separated tag list. Stored as-is (lowercased by the server).
- `--note <text>`: optional markdown note attached to the bookmark.

## Workflow

1. If the collection ID is not supplied, call `mcp__raindropio__list_collections` and match the user-supplied title to pick the correct `id`.
2. Build the `payload` dict (`link`, optional `title`, optional `tags`, optional `note`) and call `mcp__raindropio__create_bookmark` with `collection_id` and `payload`.
3. Report the created bookmark's id, the destination collection title, and the final `link`.

## Example

`/raindrop-add https://docs.anthropic.com/en/docs/build-with-claude/tool-use --collection 12345 --tags claude,mcp --note "Tool-use overview"`
