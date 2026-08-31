# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.2] - 2026-08-31

### Internal

- cleanup: Drop hardcoded-path smoke test script

## [0.5.0] - 2026-08-28

### Documentation

- readme: Bump Python badge from 3.13+ to 3.14+

### Internal

- Bump requires-python to >=3.14
- Bump version to 0.4.0
- Bump version to 0.4.0
- claude-md: Add oneiric action-kit discovery breadcrumb
- raindropio-mcp: Bump tool-config pins from 3.13 to 3.14
- raindropio-mcp: Uv python pin 3.14

## [0.4.0] - 2026-08-21

### Added

- raindropio-mcp: Adopt apply_tool_profile() (W4.7)
- raindropio: Bodai plugin conversion (manifest, mcp.json, slash commands)

### Fixed

- raindropio-mcp: Add trailing newlines to W4.7 files (task-20 Minor 3)
- raindropio-mcp: Resolve 74 pre-existing test failures (test-failure-batch 2026-08-19)
- raindropio-mcp: Sync version stamps (2026-08-19)
- raindropio-mcp: Untrack .pyscn/reports/ artifacts

### Documentation

- raindropio-mcp: Fix documented-but-not-wired audit findings (2026-08-19)
- raindropio-mcp: Refresh tool category count (2026-08-19)

### Testing

- raindropio-mcp: Add doc-drift CI guard (2026-08-19)

### Internal

- Gitignore runtime artifacts + untrack user-authorized cache files (bodai cleanup 2026-08-17)
- gitignore: Untrack .pyscn/ (bodai 2026-08-20)
- raindropio-mcp: Fill [tool.crackerjack] baseline + uv sync upgrade
- raindropio-mcp: Gitignore .lycheecache (file, not just dir)
- raindropio-mcp: Gitignore .lycheecache + .hypothesis
- raindropio-mcp: Refresh crackerjack + oneiric deps
- raindropio-mcp: Untrack .lycheecache + .hypothesis runtime artifacts

## [0.3.1] - 2026-08-16

### Documentation

- Align env-var docs with pydantic-settings, add base_url/cache_dir, fix tool category count

### Internal

- Untrack backup files (.backup, .backup.json, .bak)

## [0.3.0] - 2026-08-12

### Fixed

- Revert "chore: fix pre-existing test failures surfaced by FastMCP 3.x bump"

### Internal

- Adopt register_http_health_route from mcp-common
- Bump oneiric dep to >=0.16.0
- Fix pre-existing test failures surfaced by FastMCP 3.x bump
- Restore LICENSE and normalize attribution

## [0.2.6] - 2026-06-20

### Internal

- Add .cache dir for gitleaks quality tooling
- gitignore: Add backup file patterns to silence checkpoint tool artifacts

## [0.2.5] - 2026-05-10

### Internal

- Update LICENSE copyright to 2026

## [0.2.4] - 2026-01-24

### Changed

- Update config, core, deps

## [0.2.3] - 2026-01-22

### Changed

- Raindropio-mcp (quality: 77/100) - 2026-01-22 17:00:08
- Update config, core, docs

## [0.2.2] - 2026-01-05

### Changed

- Update config, core

### Fixed

- Correct MCP server default port to 3034 and update tests

## [0.2.1] - 2026-01-05

### Changed

- Update config, core, deps

## [0.2.0] - 2026-01-04

### Changed

- Migrate raindropio-mcp to mcp-common v0.4.4
- Update config, core, deps, tests

## [0.1.3] - 2025-12-20

### Changed

- Update config, core, deps, docs, tests

### Fixed

- test: Update 181 files
