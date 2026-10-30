"""Checks that the npm package in package.json can install the memory from its own files.

`npx vidbyte-memory init` runs scripts/install.py from inside the package, and the installer copies from the
folder it sits in only when that folder looks like the published template. So the package's "files" must carry
every folder in install.py's COPY_DIRS, every integration file the installer copies, and the files
is_pristine_template looks for; otherwise the install silently falls back to downloading from GitHub, or misses
files. The same package.json is a Pi package (its "pi" manifest), so those paths must exist too.
"""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
INCLUDED = [entry for entry in PACKAGE["files"] if not entry.startswith("!")]  # "!" entries keep caches out


def load_installer():
    spec = importlib.util.spec_from_file_location("vidbyte_memory_install", ROOT / "scripts" / "install.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def shipped(path: str) -> bool:
    """True when a file or folder path is covered by an entry in package.json "files"."""
    for entry in INCLUDED:
        folder = entry.rstrip("/")
        if path == folder or path.startswith(folder + "/"):
            return True
    return False


def test_files_cover_what_the_installer_reads():
    installer = load_installer()
    needed = [folder for folder in installer.COPY_DIRS if (ROOT / folder).is_dir()]
    source = (ROOT / "scripts" / "install.py").read_text(encoding="utf-8")
    needed += ["/".join(parts) for parts in re.findall(r'source / "(integrations)" / "([\w-]+)" / "([\w.-]+)"', source)]
    needed += ["AGENTS.md", "memory/MAP.md", "scripts/guard.py", "scripts/install.py", ".claude-plugin/plugin.json"]
    missing = [path for path in needed if not shipped(path)]
    assert not missing, f"add these to package.json files, or npx installs miss them: {missing}"
    assert any(path.startswith("integrations/") for path in needed), "the integration copies in install.py moved; update this test"


def test_every_packaged_path_exists():
    missing = [entry for entry in INCLUDED if not (ROOT / entry.rstrip("/")).exists()]
    assert not missing, f"package.json files names paths that do not exist: {missing}"
    for command, path in PACKAGE["bin"].items():
        assert shipped(path), f"bin {command} is not in files"
        assert (ROOT / path).read_text(encoding="utf-8").startswith("#!/usr/bin/env node"), f"{path} needs a node shebang"
    assert {"!**/__pycache__/", "!**/*.pyc"} <= set(PACKAGE["files"]), "files skips .gitignore inside listed folders; exclude caches"


def test_pi_manifest_points_at_real_files():
    pi = PACKAGE["pi"]
    assert "pi-package" in PACKAGE["keywords"], "the Pi gallery lists packages with the pi-package keyword"
    for path in pi["extensions"] + pi["skills"]:
        assert (ROOT / path).exists(), f"pi manifest names a missing path: {path}"
        assert shipped(path.removeprefix("./")), f"pi manifest path is not in files: {path}"
    assert (ROOT / "skills" / "install-memory" / "SKILL.md").is_file()


def test_opencode_package_ships_the_license():
    opencode = ROOT / "integrations" / "opencode"
    assert (opencode / "LICENSE").read_bytes() == (ROOT / "LICENSE").read_bytes(), "copy LICENSE into integrations/opencode"
