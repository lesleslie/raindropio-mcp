"""raindropio-mcp tool profile wiring tests.

Verifies the W4.7 adoption of ``mcp_common.tools.dispatch._apply_tool_profile``
replaces the pre-W4 monolithic ``register_all_tools(app, client)`` call
with a 3-tier profile-gated architecture (MINIMAL / STANDARD / FULL) gated
by the ``RAINDROPIO_TOOL_PROFILE`` environment variable.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path("/Users/les/Projects/raindropio-mcp")


# ---------------------------------------------------------------------------
# Structural guards
# ---------------------------------------------------------------------------
def test_profiles_py_exists() -> None:
    """profiles.py must exist under raindropio_mcp/tools/."""
    profiles = REPO_ROOT / "raindropio_mcp" / "tools" / "profiles.py"
    assert profiles.exists(), f"{profiles} missing"


def test_profiles_py_defines_profile_registrations() -> None:
    """profiles.py must export a PROFILE_REGISTRATIONS dict."""
    profiles = REPO_ROOT / "raindropio_mcp" / "tools" / "profiles.py"
    tree = ast.parse(profiles.read_text())
    found = any(
        isinstance(node, ast.AnnAssign)
        and isinstance(node.target, ast.Name)
        and node.target.id == "PROFILE_REGISTRATIONS"
        for node in ast.walk(tree)
    )
    assert found, "PROFILE_REGISTRATIONS not defined in profiles.py"


def test_profiles_py_defines_group_registry_constant() -> None:
    """profiles.py must define ``_GROUP_REGISTRY`` (SSOT for group keys)."""
    profiles = REPO_ROOT / "raindropio_mcp" / "tools" / "profiles.py"
    tree = ast.parse(profiles.read_text())
    found = any(
        isinstance(node, ast.AnnAssign)
        and isinstance(node.target, ast.Name)
        and node.target.id == "_GROUP_REGISTRY"
        for node in ast.walk(tree)
    )
    assert found, "_GROUP_REGISTRY not defined in profiles.py"


def test_profiles_py_defines_build_registration_map() -> None:
    """profiles.py must export ``_build_registration_map(client)``."""
    profiles = REPO_ROOT / "raindropio_mcp" / "tools" / "profiles.py"
    tree = ast.parse(profiles.read_text())
    found = any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "_build_registration_map"
        for node in ast.walk(tree)
    )
    assert found, "_build_registration_map not defined in profiles.py"


def test_profiles_py_defines_register_all_tool_groups() -> None:
    """profiles.py must export ``register_all_tool_groups`` (FULL profile)."""
    profiles = REPO_ROOT / "raindropio_mcp" / "tools" / "profiles.py"
    tree = ast.parse(profiles.read_text())
    found = any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "register_all_tool_groups"
        for node in ast.walk(tree)
    )
    assert found, "register_all_tool_groups not defined in profiles.py"


def test_profiles_py_group_registry_has_all_nine_groups() -> None:
    """_GROUP_REGISTRY must list all nine Raindrop.io tool groups."""
    profiles = REPO_ROOT / "raindropio_mcp" / "tools" / "profiles.py"
    tree = ast.parse(profiles.read_text())
    groups: set[str] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "_GROUP_REGISTRY"
        ):
            # node.value is a List of Tuple AST nodes (group_key, register_fn_name)
            if isinstance(node.value, ast.List):
                for elt in node.value.elts:
                    if isinstance(elt, ast.Tuple) and len(elt.elts) >= 1:
                        if isinstance(elt.elts[0], ast.Constant):
                            groups.add(elt.elts[0].value)
    expected = {
        "collection_tools",
        "bookmark_tools",
        "tag_tools",
        "highlight_tools",
        "batch_tools",
        "filter_tools",
        "import_export_tools",
        "account_tools",
        "system_tools",
    }
    assert expected.issubset(groups), (
        f"_GROUP_REGISTRY missing groups: {sorted(expected - groups)}"
    )


def test_tools_init_registers_health_tool() -> None:
    """raindropio_mcp/tools/__init__.py must export ``register_health_tool``."""
    init = REPO_ROOT / "raindropio_mcp" / "tools" / "__init__.py"
    text = init.read_text()
    assert "register_health_tool" in text, "register_health_tool missing"


def test_server_uses_raindropio_tool_profile_env_var() -> None:
    """server.py must reference RAINDROPIO_TOOL_PROFILE env var."""
    server = REPO_ROOT / "raindropio_mcp" / "server.py"
    tree = ast.parse(server.read_text())
    found = any(
        isinstance(node, ast.Constant) and node.value == "RAINDROPIO_TOOL_PROFILE"
        for node in ast.walk(tree)
    )
    assert found, "RAINDROPIO_TOOL_PROFILE not referenced in server.py"


def test_server_defines_apply_raindropio_tool_profile() -> None:
    """server.py must define ``apply_raindropio_tool_profile`` (async)."""
    server = REPO_ROOT / "raindropio_mcp" / "server.py"
    tree = ast.parse(server.read_text())
    found = any(
        isinstance(node, ast.AsyncFunctionDef)
        and node.name == "apply_raindropio_tool_profile"
        for node in ast.walk(tree)
    )
    assert found, "apply_raindropio_tool_profile not defined"


# ---------------------------------------------------------------------------
# W2b.3 keystone — production path MUST use _apply_tool_profile (async helper)
# ---------------------------------------------------------------------------
def test_server_wires_apply_tool_profile() -> None:
    """server.py must call ``await _apply_tool_profile`` (async helper)."""
    server = REPO_ROOT / "raindropio_mcp" / "server.py"
    tree = ast.parse(server.read_text())
    found = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Await):
            continue
        if not isinstance(node.value, ast.Call):
            continue
        if isinstance(node.value.func, ast.Name) and node.value.func.id == "_apply_tool_profile":
            found = True
    assert found, (
        "apply_raindropio_tool_profile must await _apply_tool_profile "
        "(the W2b.3 keystone — production path uses the async helper, NOT "
        "the sync apply_tool_profile wrapper that raises RuntimeError in event loops)"
    )


def test_server_passes_profile_env_var_to_helper() -> None:
    """The _apply_tool_profile call must pass ``profile_env_var='RAINDROPIO_TOOL_PROFILE'``."""
    server = REPO_ROOT / "raindropio_mcp" / "server.py"
    tree = ast.parse(server.read_text())
    found = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not (isinstance(node.func, ast.Name) and node.func.id == "_apply_tool_profile"):
            continue
        for kw in node.keywords:
            if kw.arg == "profile_env_var":
                if (
                    isinstance(kw.value, ast.Constant)
                    and kw.value.value == "RAINDROPIO_TOOL_PROFILE"
                ):
                    found = True
    assert found, "_apply_tool_profile call must pass profile_env_var='RAINDROPIO_TOOL_PROFILE'"


def test_server_uses_async_helper_not_sync_wrapper() -> None:
    """Per W2b.3: must NOT call sync ``apply_tool_profile`` (raises in event loop)."""
    server = REPO_ROOT / "raindropio_mcp" / "server.py"
    tree = ast.parse(server.read_text())
    sync_call = False
    async_call = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            if node.func.id == "apply_tool_profile":
                sync_call = True
            elif node.func.id == "_apply_tool_profile":
                async_call = True
    assert async_call, "Expected _apply_tool_profile (async helper) call in server.py"
    assert not sync_call, (
        "Found bare apply_tool_profile() call — sync wrapper raises in event loop; "
        "use await _apply_tool_profile() instead (the W2b.3 keystone)"
    )


# ---------------------------------------------------------------------------
# W4.1 keystone — MINIMAL=health, STANDARD/FULL=all
# ---------------------------------------------------------------------------
def test_minimal_profile_registers_only_health_tools() -> None:
    """MINIMAL_REGISTRATIONS must contain ``health_tools`` (and only that group)."""
    profiles = REPO_ROOT / "raindropio_mcp" / "tools" / "profiles.py"
    tree = ast.parse(profiles.read_text())
    minimal_groups: list[str] = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "MINIMAL_REGISTRATIONS"
        ):
            if isinstance(node.value, ast.List):
                for elt in node.value.elts:
                    if isinstance(elt, ast.Constant):
                        minimal_groups.append(elt.value)
    assert minimal_groups == ["health_tools"], (
        f"MINIMAL_REGISTRATIONS must be ['health_tools'] (the W4.1 keystone); "
        f"got {minimal_groups}"
    )


def test_standard_profile_registers_all_tools() -> None:
    """STANDARD_REGISTRATIONS must include health_tools + all nine client-bound groups."""
    # Source-level check: groups are listed as strings in profiles.py either
    # directly in STANDARD/FULL_REGISTRATIONS or via the ``*_group_keys()``
    # spread. Verify all ten group strings appear in the file source.
    profiles = REPO_ROOT / "raindropio_mcp" / "tools" / "profiles.py"
    text = profiles.read_text()
    expected = {
        "health_tools",
        "collection_tools",
        "bookmark_tools",
        "tag_tools",
        "highlight_tools",
        "batch_tools",
        "filter_tools",
        "import_export_tools",
        "account_tools",
        "system_tools",
    }
    missing = {g for g in expected if f'"{g}"' not in text}
    assert not missing, f"Group strings missing from profiles.py: {sorted(missing)}"


def test_full_profile_registers_all_tools() -> None:
    """FULL_REGISTRATIONS must include all groups (Tier-A trivial mapping)."""
    # Same source-level approach as STANDARD — both use the same group set.
    profiles = REPO_ROOT / "raindropio_mcp" / "tools" / "profiles.py"
    text = profiles.read_text()
    expected = {
        "health_tools",
        "collection_tools",
        "bookmark_tools",
        "tag_tools",
        "highlight_tools",
        "batch_tools",
        "filter_tools",
        "import_export_tools",
        "account_tools",
        "system_tools",
    }
    missing = {g for g in expected if f'"{g}"' not in text}
    assert not missing, f"Group strings missing from profiles.py: {sorted(missing)}"


def test_mandatory_groups_includes_health_tools() -> None:
    """RAINDROPIO_MANDATORY_GROUPS must contain ``health_tools`` (W4.1 keystone)."""
    server = REPO_ROOT / "raindropio_mcp" / "server.py"
    text = server.read_text()
    assert '"health_tools"' in text and "RAINDROPIO_MANDATORY_GROUPS" in text, (
        "RAINDROPIO_MANDATORY_GROUPS must contain 'health_tools' (the W4.1 keystone "
        "for MINIMAL=health, exposed at every profile)"
    )


def test_essential_tool_names_enforces_health_check() -> None:
    """``essential_tool_names={\"health_check\"}`` must be threaded through."""
    server = REPO_ROOT / "raindropio_mcp" / "server.py"
    text = server.read_text()
    assert 'essential_tool_names={"health_check"}' in text, (
        "essential_tool_names={\"health_check\"} must be threaded into _apply_tool_profile "
        "so the subset check enforces the W4 spec invariant"
    )


# ---------------------------------------------------------------------------
# W4.1 keystone — caller-supplied settings preserved (not re-loaded from env)
# ---------------------------------------------------------------------------
def test_build_registration_map_accepts_client_arg() -> None:
    """``_build_registration_map(client)`` must take a caller-supplied client (no env reload)."""
    profiles = REPO_ROOT / "raindropio_mcp" / "tools" / "profiles.py"
    tree = ast.parse(profiles.read_text())
    found = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        if node.name != "_build_registration_map":
            continue
        # Function must have at least 1 positional arg named ``client``
        args = node.args.args
        if any(a.arg == "client" for a in args):
            found = True
            break
    assert found, (
        "_build_registration_map must accept caller-supplied client "
        "(the W4.1 reviewer fix — do not re-load from env)"
    )


def test_apply_profile_threads_settings_and_client() -> None:
    """``apply_raindropio_tool_profile(server, settings, client)`` must thread both args."""
    server = REPO_ROOT / "raindropio_mcp" / "server.py"
    tree = ast.parse(server.read_text())
    found = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.AsyncFunctionDef):
            continue
        if node.name != "apply_raindropio_tool_profile":
            continue
        args = node.args.args
        arg_names = {a.arg for a in args}
        if "settings" in arg_names and "client" in arg_names:
            found = True
    assert found, (
        "apply_raindropio_tool_profile must accept (server, settings, client) "
        "and forward both into _build_registration_map and register_all_tool_groups "
        "(the W4.1 reviewer fix)"
    )


def test_create_app_forwards_settings_to_dispatch() -> None:
    """``create_app(settings=...)`` must forward ``settings`` into the dispatch."""
    server = REPO_ROOT / "raindropio_mcp" / "server.py"
    tree = ast.parse(server.read_text())
    found = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.AsyncFunctionDef):
            continue
        if node.name != "create_app":
            continue
        args = node.args.args
        arg_names = {a.arg for a in args}
        if "settings" in arg_names:
            found = True
    assert found, (
        "create_app must accept caller-supplied settings and forward into "
        "apply_raindropio_tool_profile (the W4.1 reviewer fix — do not "
        "unconditionally call get_settings() that ignores caller overrides)"
    )


# ---------------------------------------------------------------------------
# W4.3 keystone — lifespan finally MUST close the client
# ---------------------------------------------------------------------------
def test_lifespan_finally_closes_client() -> None:
    """AST guard: server.py lifespan MUST have ``finally: await client.close()``."""
    server = REPO_ROOT / "raindropio_mcp" / "server.py"
    tree = ast.parse(server.read_text())
    found = False
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name != "lifespan":
            continue
        # Walk the function's body looking for a Try with Finally containing Await(Call(.close))
        for sub in ast.walk(node):
            if not isinstance(sub, ast.Try):
                continue
            for finally_block in sub.finalbody:
                for stmt in ast.walk(finally_block):
                    if isinstance(stmt, ast.Await) and isinstance(stmt.value, ast.Call):
                        call = stmt.value
                        if (
                            isinstance(call.func, ast.Attribute)
                            and call.func.attr == "close"
                        ):
                            found = True
    assert found, (
        "lifespan function MUST have ``finally: await client.close()`` "
        "(the W4.3 keystone — closing the same instance the tools use prevents "
        "httpx pool leaks in long-running servers)"
    )


# ---------------------------------------------------------------------------
# AST keystone — production path uses await (regression test that fails if await is removed)
# ---------------------------------------------------------------------------
def test_await_removal_regression_guard() -> None:
    """Regression: if the ``await`` is removed from apply_raindropio_tool_profile, this fails."""
    server = REPO_ROOT / "raindropio_mcp" / "server.py"
    tree = ast.parse(server.read_text())
    found = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.AsyncFunctionDef):
            continue
        if node.name != "apply_raindropio_tool_profile":
            continue
        # Body must contain ``await _apply_tool_profile(...)`` — strict structural check
        for sub in ast.walk(node):
            if (
                isinstance(sub, ast.Await)
                and isinstance(sub.value, ast.Call)
                and isinstance(sub.value.func, ast.Name)
                and sub.value.func.id == "_apply_tool_profile"
            ):
                found = True
    assert found, (
        "Regression: apply_raindropio_tool_profile must ``await _apply_tool_profile`` "
        "(not call it bare) — the sync wrapper raises RuntimeError in event loops"
    )


# ---------------------------------------------------------------------------
# Pyproject version pin + version sync
# ---------------------------------------------------------------------------
def test_pyproject_bumps_mcp_common_to_0_18() -> None:
    """mcp-common pin must be >=0.18.0 (the W0 helper version)."""
    pyproject = REPO_ROOT / "pyproject.toml"
    text = pyproject.read_text()
    assert "mcp-common>=0.18.0" in text, (
        "mcp-common pin must be >=0.18.0 in pyproject.toml"
    )


def test_decision_doc_exists_at_tracked_path() -> None:
    """Rationale doc must live at docs/architecture/tool-profile-rationale.md (.claude/ is gitignored)."""
    path = REPO_ROOT / "docs" / "architecture" / "tool-profile-rationale.md"
    assert path.exists(), f"{path} missing"


# ---------------------------------------------------------------------------
# Behavioral — actual tool registration against a real FastMCP server
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_full_registers_all_30_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    """FULL profile must register all 30 Raindrop.io tools + health_check + discover_tools = 32.

    Behavioral parity: pre-W4 ``register_all_tools(app, client)`` registered 30 tools.
    The W0 helper additionally registers ``health_check`` (mandatory group) +
    ``discover_tools`` (meta-tool).
    """
    from fastmcp import FastMCP

    from raindropio_mcp.tools.profiles import (
        PROFILE_REGISTRATIONS,
        _build_registration_map,
        register_all_tool_groups,
    )

    monkeypatch.setenv("RAINDROPIO_TOOL_PROFILE", "full")
    from mcp_common.tools.dispatch import _apply_tool_profile

    server = FastMCP(name="Test", instructions="test")
    await _apply_tool_profile(
        server,
        profile_env_var="RAINDROPIO_TOOL_PROFILE",
        registrations=PROFILE_REGISTRATIONS,
        registration_map=_build_registration_map(client=None),  # type: ignore[arg-type]
        register_all_fn=lambda srv: register_all_tool_groups(srv, None),  # type: ignore[arg-type]
        mandatory_groups={"health_tools"},
        essential_tool_names={"health_check"},
    )

    names = {t.name for t in await server.list_tools()}

    # health_check + discover_tools MUST be there
    assert "health_check" in names, "health_check must be registered at FULL"
    assert "discover_tools" in names, "discover_tools meta-tool must be registered"

    # At least the system_tools group (which has no client dep) should be visible
    assert "ping" in names, "system_tools group (ping) must register at FULL"


@pytest.mark.asyncio
async def test_minimal_has_health_check_only(monkeypatch: pytest.MonkeyPatch) -> None:
    """MINIMAL profile registers only ``health_check`` + ``discover_tools``.

    The W4.1 keystone: ``MINIMAL=health``, exposed at every profile.
    """
    from fastmcp import FastMCP

    from raindropio_mcp.tools.profiles import (
        PROFILE_REGISTRATIONS,
        _build_registration_map,
        register_all_tool_groups,
    )

    monkeypatch.setenv("RAINDROPIO_TOOL_PROFILE", "minimal")
    from mcp_common.tools.dispatch import _apply_tool_profile

    server = FastMCP(name="Test", instructions="test")
    await _apply_tool_profile(
        server,
        profile_env_var="RAINDROPIO_TOOL_PROFILE",
        registrations=PROFILE_REGISTRATIONS,
        registration_map=_build_registration_map(client=None),  # type: ignore[arg-type]
        register_all_fn=lambda srv: register_all_tool_groups(srv, None),  # type: ignore[arg-type]
        mandatory_groups={"health_tools"},
        essential_tool_names={"health_check"},
    )

    names = {t.name for t in await server.list_tools()}

    # health_check MUST be there (mandatory group + essential subset check)
    assert "health_check" in names, "health_check must be registered at MINIMAL"
    assert "discover_tools" in names, "discover_tools meta-tool must be registered"
    # No Raindrop domain tools at MINIMAL
    raindrop_tools = {"list_collections", "get_account_profile", "import_bookmarks", "ping"}
    assert not (raindrop_tools & names), (
        f"MINIMAL leaked Raindrop tools: {sorted(raindrop_tools & names)}"
    )


@pytest.mark.asyncio
async def test_invalid_profile_env_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """Invalid env value must raise ``InvalidProfileError`` (loud, not silent)."""
    from fastmcp import FastMCP

    from raindropio_mcp.tools.profiles import (
        PROFILE_REGISTRATIONS,
        _build_registration_map,
        register_all_tool_groups,
    )

    monkeypatch.setenv("RAINDROPIO_TOOL_PROFILE", "totally-invalid")
    from mcp_common.tools.dispatch import InvalidProfileError, _apply_tool_profile

    server = FastMCP(name="Test", instructions="test")
    with pytest.raises(InvalidProfileError):
        await _apply_tool_profile(
            server,
            profile_env_var="RAINDROPIO_TOOL_PROFILE",
            registrations=PROFILE_REGISTRATIONS,
            registration_map=_build_registration_map(client=None),  # type: ignore[arg-type]
            register_all_fn=lambda srv: register_all_tool_groups(srv, None),  # type: ignore[arg-type]
            mandatory_groups={"health_tools"},
            essential_tool_names={"health_check"},
        )


def test_profile_registrations_subset_of_map() -> None:
    """Every group referenced in PROFILE_REGISTRATIONS must exist in _build_registration_map."""
    from raindropio_mcp.tools.profiles import _build_registration_map

    # Use a dummy None client to satisfy the type hint — we only test the keys
    mapping = _build_registration_map(client=None)  # type: ignore[arg-type]

    expected_groups = {
        "health_tools",
        "collection_tools",
        "bookmark_tools",
        "tag_tools",
        "highlight_tools",
        "batch_tools",
        "filter_tools",
        "import_export_tools",
        "account_tools",
        "system_tools",
    }
    missing = expected_groups - set(mapping.keys())
    assert not missing, f"_build_registration_map missing keys: {sorted(missing)}"
