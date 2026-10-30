"""Unit tests for the Hermes plugin in integrations/hermes, with a fake Hermes context.

No Hermes install and no model: the plugin is imported the way Hermes's loader imports a directory
plugin (spec_from_file_location with the plugin folder as the package path), register(ctx) runs
against a recording context, and the pre_verify callback is called with the keyword arguments
Hermes passes (hermes_cli/plugins.py get_pre_verify_continue_message).
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import textwrap
import uuid
from pathlib import Path

import pytest

PLUGIN_DIR = Path(__file__).resolve().parents[1] / "hermes"
TEMPLATE = Path(os.environ.get("VIDBYTE_MEMORY_TEMPLATE", Path(__file__).resolve().parents[2]))


class FakeContext:
    """The slice of hermes_cli.plugins.PluginContext this plugin touches."""

    def __init__(self):
        self.hooks = {}

    def register_hook(self, hook_name, callback, *, hold_stream=False):
        self.hooks.setdefault(hook_name, []).append(callback)


def load_plugin():
    """Import integrations/hermes as Hermes does: package hermes_plugins.<slug>, path = plugin dir."""
    name = f"hermes_plugins_test_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(
        name, PLUGIN_DIR / "__init__.py", submodule_search_locations=[str(PLUGIN_DIR)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def fire_pre_verify(ctx, **overrides):
    """Hermes's call and its reading of the result (hermes_cli/plugins.py, get_pre_verify_continue_message)."""
    kwargs = dict(session_id="s-1", platform="cli", model="m", coding=True, attempt=0,
                  final_response="Done.", changed_paths=[], telemetry_schema_version=1)
    kwargs.update(overrides)
    for callback in ctx.hooks.get("pre_verify", []):
        result = callback(**kwargs)
        if not isinstance(result, dict):
            continue
        action = str(result.get("action") or result.get("decision") or "").strip().lower()
        message = result.get("message") or result.get("reason")
        if action in ("continue", "block") and isinstance(message, str) and message.strip():
            return message.strip()
    return None


FAKE_GUARD = textwrap.dedent("""
    import json, os, sys
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    payload = json.loads(sys.stdin.read() or "{}")
    (root / "guard-call.json").write_text(json.dumps({
        "argv": sys.argv[1:], "payload": payload, "project_dir": os.environ.get("CLAUDE_PROJECT_DIR"),
        "cwd": os.getcwd()}))
    mode = (root / "mode").read_text().strip() if (root / "mode").exists() else "block"
    if mode == "block":
        print(json.dumps({"decision": "block", "reason": "G-001: tests fail. (guard round 1 of 5)"}))
    elif mode == "giveup":
        print(json.dumps({"systemMessage": "guard gave up after 5 rounds"}))
    elif mode == "garbage":
        print("not json")
    elif mode == "sleep":
        import time; time.sleep(30)
""")


@pytest.fixture
def plugin(monkeypatch):
    module = load_plugin()
    monkeypatch.setattr(module, "project_python", lambda root: sys.executable)
    ctx = FakeContext()
    module.register(ctx)
    return module, ctx


@pytest.fixture
def project(tmp_path, monkeypatch):
    root = tmp_path / "proj"
    (root / "memory").mkdir(parents=True)
    (root / "memory" / "MAP.md").write_text("# map\n")
    (root / "scripts").mkdir()
    (root / "scripts" / "guard.py").write_text(FAKE_GUARD)
    (root / "src").mkdir()
    monkeypatch.chdir(root / "src")
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))  # an outer session's value must not leak
    return root


def test_register_declares_only_pre_verify(plugin):
    _module, ctx = plugin
    assert list(ctx.hooks) == ["pre_verify"]
    manifest = (PLUGIN_DIR / "plugin.yaml").read_text()
    assert "provides_hooks:\n  - pre_verify" in manifest


def test_block_becomes_continue_with_the_reason(plugin, project):
    _module, ctx = plugin
    message = fire_pre_verify(ctx, changed_paths=[str(project / "src" / "a.py")])
    assert message == "G-001: tests fail. (guard round 1 of 5)"
    call = json.loads((project / "guard-call.json").read_text())
    assert call["argv"] == ["--format", "claude"]
    assert call["payload"]["session_id"] == "s-1"
    assert Path(call["payload"]["cwd"]) == project.resolve()
    assert Path(call["project_dir"]) == project.resolve()
    assert Path(call["cwd"]) == project.resolve()


def test_hermes_pythonhome_does_not_reach_the_guard(plugin, project, tmp_path, monkeypatch):
    # Hermes's venv launcher on Windows exports PYTHONHOME; a Python started with a foreign home dies at
    # startup, which silently let every turn end. An empty folder stands in for that foreign home.
    _module, ctx = plugin
    monkeypatch.setenv("PYTHONHOME", str(tmp_path / "hermes-base"))
    message = fire_pre_verify(ctx, changed_paths=[str(project / "src" / "a.py")])
    assert message == "G-001: tests fail. (guard round 1 of 5)"


def test_no_memory_map_means_no_guard(plugin, tmp_path, monkeypatch):
    bare = tmp_path / "bare"
    (bare / "scripts").mkdir(parents=True)
    (bare / "scripts" / "guard.py").write_text(FAKE_GUARD)
    monkeypatch.chdir(bare)
    _module, ctx = plugin
    assert fire_pre_verify(ctx, changed_paths=[str(bare / "x.py")]) is None
    assert not (bare / "guard-call.json").exists()


def test_falls_back_to_edited_paths_when_cwd_is_elsewhere(plugin, project, tmp_path, monkeypatch):
    elsewhere = tmp_path / "hermes-home"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)  # a plugin host runs with cwd = HERMES_HOME
    _module, ctx = plugin
    assert fire_pre_verify(ctx, changed_paths=[str(project / "src" / "a.py")]).startswith("G-001")


@pytest.mark.parametrize("mode", ["pass", "giveup", "garbage"])
def test_anything_but_block_lets_the_turn_end(plugin, project, mode):
    (project / "mode").write_text(mode)
    _module, ctx = plugin
    assert fire_pre_verify(ctx, changed_paths=[str(project / "a.py")]) is None


def test_timeout_fails_open(plugin, project, monkeypatch):
    module, ctx = plugin
    (project / "mode").write_text("sleep")
    monkeypatch.setattr(module, "guard_timeout", lambda: 1.0)
    assert fire_pre_verify(ctx, changed_paths=[str(project / "a.py")]) is None


def test_project_venv_python_wins(tmp_path):
    module = load_plugin()
    venv_python = tmp_path / (".venv/Scripts/python.exe" if os.name == "nt" else ".venv/bin/python")
    venv_python.parent.mkdir(parents=True)
    venv_python.write_text("")
    assert module.project_python(tmp_path) == str(venv_python)


def test_guard_timeout_follows_hermes_setting(monkeypatch):
    module = load_plugin()
    assert module.guard_timeout() == 27.0  # Hermes absent: 30 s default minus 3


@pytest.mark.skipif(not (TEMPLATE / "scripts" / "guard.py").is_file(), reason="needs the vidbyte-memory template")
def test_real_guard_end_to_end(plugin, tmp_path, monkeypatch):
    """The real scripts/guard.py on a copy of the template: a failing test blocks, a green suite ends."""
    root = tmp_path / "repo"
    shutil.copytree(TEMPLATE, root, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)  # no upstream: G-004 checks status only
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-qm", "init"],
                   cwd=root, check=True)
    (root / ".git" / "info" / "exclude").write_text(".claude/.guard_state.json\n.pytest_cache/\n__pycache__/\n")
    monkeypatch.chdir(root)
    _module, ctx = plugin
    assert fire_pre_verify(ctx, changed_paths=[str(root / "facts" / "project.md")]) is None

    (root / "tests" / "test_broken.py").write_text("def test_broken():\n    assert False\n")
    message = fire_pre_verify(ctx, session_id="s-2", changed_paths=[str(root / "tests" / "test_broken.py")])
    assert "G-001: tests fail" in message and "guard round 1 of 5" in message
    assert "G-004" in message  # the new file is also uncommitted
