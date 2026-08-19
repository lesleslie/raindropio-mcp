"""Doc-drift CI guard tests for raindropio-mcp.

These tests pin three classes of facts that have drifted in past releases:

1. The total number of MCP tools exposed by the server (matches README/CLAUDE.md claims).
2. Documented environment variables are actually read by the package code.
3. The HTTP ``User-Agent`` string interpolates from ``__version__`` rather than
   hardcoding a version literal.

If a test fails, fix the documentation to match the code *or* fix the code to
match the documentation. The pinned thresholds are deliberately loose (using
``>=`` rather than ``==``) so that adding new tools does not require updating
this file.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Tool count guard
# ---------------------------------------------------------------------------

# raindropio-mcp has 32 tools via FastMCPToolRegistry at full profile.
# Floor at 25 to permit additions without churn.
EXPECTED_MIN_TOOLS = 25


@pytest.mark.asyncio
async def test_mcp_tool_count_matches_documented() -> None:
    """Pin the canonical MCP tool count so README/CLAUDE.md claims stay in sync."""
    old_profile = os.environ.get("RAINDROPIO_TOOL_PROFILE")
    os.environ["RAINDROPIO_TOOL_PROFILE"] = "full"
    try:
        from raindropio_mcp.server import create_app

        app = await create_app()
        tools = await app.list_tools()
    finally:
        if old_profile is None:
            os.environ.pop("RAINDROPIO_TOOL_PROFILE", None)
        else:
            os.environ["RAINDROPIO_TOOL_PROFILE"] = old_profile

    assert len(tools) >= EXPECTED_MIN_TOOLS, (
        f"Expected >= {EXPECTED_MIN_TOOLS} tools at full profile, got {len(tools)}. "
        "Update README.md / CLAUDE.md tool counts, or relax this threshold."
    )


# ---------------------------------------------------------------------------
# Env var wiring guard
# ---------------------------------------------------------------------------

# Documented env vars from README.md / CLAUDE.md / .env.example. Each entry
# is verified to be read via ``os.getenv`` (or ``os.environ.get``) somewhere
# in the raindropio-mcp package source tree, OR via Pydantic Settings
# auto-resolve (env_prefix="RAINDROP_" + field_name.upper()).
#
# Limitation: ``RAINDROPIO_TOOL_PROFILE`` is consumed indirectly via
# string-literal forwarding to ``mcp-common``. It is not pinned here because
# the wiring is dispatched through a helper. Add new entries below whenever a
# new ``os.getenv``-backed env var is documented.
DOCUMENTED_ENV_VARS: tuple[str, ...] = (
    "RAINDROP_TOKEN",
    "RAINDROP_BASE_URL",
    "RAINDROP_USER_AGENT",
    "RAINDROP_REQUEST_TIMEOUT",
    "RAINDROP_HTTP_PORT",
    "RAINDROP_HTTP_HOST",
)


def _read_source_text() -> str:
    """Read every Python file under ``raindropio_mcp/`` into a single string."""
    pkg_root = Path(__file__).resolve().parent.parent / "raindropio_mcp"
    chunks: list[str] = []
    for py_file in pkg_root.rglob("*.py"):
        if "__pycache__" in py_file.parts:
            continue
        try:
            chunks.append(py_file.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            continue
    return "\n".join(chunks)


def test_documented_env_vars_are_wired() -> None:
    """Every env var documented in README/CLAUDE.md must be read by package code.

    Pydantic Settings fields with env_prefix="RAINDROP_" auto-resolve to
    env vars of the form ``<prefix><field_name.upper()>``. We verify the
    package's settings model exposes these documented env vars as fields.
    """
    from raindropio_mcp.config.settings import RaindropSettings

    # Resolve via Pydantic field definitions (deterministic).
    fields = RaindropSettings.model_fields
    pydantic_env_vars = {"RAINDROP_" + name.upper() for name in fields}

    src = _read_source_text()
    missing: list[str] = []
    for var in DOCUMENTED_ENV_VARS:
        if var in pydantic_env_vars:
            continue
        pattern = re.compile(
            rf"os\.getenv\(\s*[\"']{re.escape(var)}[\"']|"
            rf"os\.environ\.get\(\s*[\"']{re.escape(var)}[\"']",
        )
        if not pattern.search(src):
            missing.append(var)
    assert not missing, (
        f"Documented env vars not read by package code: {missing}. "
        "Either remove them from docs or wire them via os.getenv or Settings."
    )


# ---------------------------------------------------------------------------
# Version stamp guard
# ---------------------------------------------------------------------------

# Heuristic: any User-Agent-looking string literal that contains a digit is
# considered a probable hardcoded version. Strings with an f-string prefix
# (``f"..."`` or ``f'...'``) or with literal ``{`` are accepted as dynamic.
_USER_AGENT_RE = re.compile(r"""User-Agent[\"'][^\"']{0,200}[\"']""")
_VERSION_LITERAL_RE = re.compile(r"\d+\.\d+")


def test_user_agent_matches_package_version() -> None:
    """Detect hardcoded User-Agent version strings that should interpolate from __version__."""
    pkg_root = Path(__file__).resolve().parent.parent / "raindropio_mcp"
    hardcoded: list[tuple[str, str]] = []
    for py_file in pkg_root.rglob("*.py"):
        if "__pycache__" in py_file.parts:
            continue
        try:
            text = py_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for match in _USER_AGENT_RE.finditer(text):
            ua = match.group(0)
            # Skip dynamic strings (f-strings, .format, concatenation).
            if "{" in ua or "f\"" in ua or "f'" in ua or ".format(" in ua:
                continue
            if _VERSION_LITERAL_RE.search(ua):
                hardcoded.append((str(py_file), ua))
    assert not hardcoded, (
        f"Hardcoded User-Agent versions found (should interpolate from __version__): {hardcoded}"
    )
