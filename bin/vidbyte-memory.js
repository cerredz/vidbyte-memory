#!/usr/bin/env node
// vidbyte-memory: `npx vidbyte-memory init` installs the memory into the repo in the current folder.
//
// The package carries the template, so this runs its own scripts/install.py with the first working Python 3.9+,
// and the installer copies from these files: offline, and the same release as the package. `init` is the
// installer's `install`; `uninstall`, `--dry-run`, `--agents`, `--all`, `--target` and the rest pass through
// unchanged (`npx vidbyte-memory --help` lists them). Node built-ins only.

import { spawnSync } from "node:child_process"
import { dirname, join } from "node:path"
import { fileURLToPath } from "node:url"

const INSTALLER = join(dirname(fileURLToPath(import.meta.url)), "..", "scripts", "install.py")
const PROBE = "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)"

// Same order as the agent plugins: on Windows `python3` is often the Microsoft Store stub.
function pythonCandidates(platform = process.platform, override = process.env.VIDBYTE_MEMORY_PYTHON) {
  const list = platform === "win32" ? [["py", "-3"], ["python"], ["python3"]] : [["python3"], ["python"]]
  return override ? [[override], ...list] : list
}

function findPython() {
  for (const [command, ...prefix] of pythonCandidates()) {
    const probe = spawnSync(command, [...prefix, "-c", PROBE], { stdio: "ignore", windowsHide: true, timeout: 15000 })
    if (probe.status === 0) return [command, ...prefix]
  }
  return null
}

const args = process.argv.slice(2)
if (args[0] === "init") args[0] = "install"

const python = findPython()
if (!python) {
  const tried = pythonCandidates().map((candidate) => candidate.join(" ")).join(", ")
  console.error(`vidbyte-memory needs Python 3.9 or later (tried ${tried}). Set VIDBYTE_MEMORY_PYTHON to its path.`)
  process.exit(1)
}
const result = spawnSync(python[0], [...python.slice(1), INSTALLER, ...args], { stdio: "inherit" })
process.exit(result.status ?? 1)
