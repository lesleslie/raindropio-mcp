---
description: "Manage Raindrop.io collections: list, create, update, or delete a collection."
argument-hint: list | create <title> [--description <text>] [--color <hex>] | update <id> [--title <text>] | delete <id>
allowed-tools: mcp__raindropio__list_collections, mcp__raindropio__get_collection, mcp__raindropio__create_collection, mcp__raindropio__update_collection, mcp__raindropio__delete_collection
---

# /raindrop-collections

Manage Raindrop.io collections (folders): list, create, update, or delete.

## Usage

`/raindrop-collections list`

`/raindrop-collections create <title> [--description <text>] [--color <hex>]`

`/raindrop-collections update <id> [--title <text>] [--description <text>] [--color <hex>]`

`/raindrop-collections delete <id>`

Subcommands:

- `list` — return every collection visible to the authenticated account.
- `create <title>` — make a new collection. `--description` and `--color` are optional; `color` must be a 6-char hex string (without `#`).
- `update <id>` — patch the title, description, or color on an existing collection. Supply only the fields you want changed.
- `delete <id>` — remove a collection. Bookmarks inside move to Uncategorized (`id=0`).

## Workflow

1. Parse the first argument as the subcommand (`list` / `create` / `update` / `delete`).
2. For `list`: call `mcp__raindropio__list_collections` and present `id`, `title`, `count`, and `color` per collection.
3. For `create`: build a payload dict from the supplied title/description/color and call `mcp__raindropio__create_collection`. Return the new collection id.
4. For `update`: build a partial payload dict from the supplied flags and call `mcp__raindropio__update_collection`.
5. For `delete`: confirm the id with `mcp__raindropio__get_collection` if ambiguous, then call `mcp__raindropio__delete_collection`. Confirm the deletion in the report.

## Example

`/raindrop-collections create "AI Research" --description "RAG, agents, evaluation" --color "0ea5e9"`
