// Runs the npm command the way `npx vidbyte-memory` does, against a throwaway folder: a dry run, a real install
// from this package's own files (no download), and an uninstall. Needs Python 3.9+; VIDBYTE_MEMORY_PYTHON picks it.
// Run: node --test bin/vidbyte-memory.test.mjs
import assert from "node:assert/strict"
import { spawnSync } from "node:child_process"
import { existsSync, mkdtempSync, readFileSync, rmSync } from "node:fs"
import { tmpdir } from "node:os"
import { dirname, join } from "node:path"
import { after, test } from "node:test"
import { fileURLToPath } from "node:url"

const BIN = join(dirname(fileURLToPath(import.meta.url)), "vidbyte-memory.js")
const scratch = mkdtempSync(join(tmpdir(), "vidbyte-memory-npx-"))
after(() => rmSync(scratch, { recursive: true, force: true }))

function run(...args) {
  const result = spawnSync(process.execPath, [BIN, ...args], { cwd: scratch, encoding: "utf8" })
  return { code: result.status, out: result.stdout + result.stderr }
}

test("init --dry-run prints the plan and writes nothing", () => {
  const { code, out } = run("init", "--dry-run", "--agents", "pi")
  assert.equal(code, 0, out)
  assert.match(out, /vidbyte-memory would write \d+ files/)
  assert.doesNotMatch(out, /downloading the template/)
  assert.equal(existsSync(join(scratch, "AGENTS.md")), false)
})

test("init installs from the package's own files, and uninstall takes it back out", () => {
  const install = run("init", "--agents", "pi")
  assert.equal(install.code, 0, install.out)
  assert.doesNotMatch(install.out, /downloading the template/)
  const record = JSON.parse(readFileSync(join(scratch, ".vidbyte-memory", "install.json"), "utf8"))
  assert.equal(record.source, "local")
  for (const path of ["AGENTS.md", "memory/MAP.md", "scripts/guard.py", ".pi/extensions/vidbyte-memory.js"]) {
    assert.ok(existsSync(join(scratch, path)), `${path} installed`)
  }

  const uninstall = run("uninstall")
  assert.equal(uninstall.code, 0, uninstall.out)
  assert.equal(existsSync(join(scratch, "AGENTS.md")), false)
  assert.equal(existsSync(join(scratch, "memory", "MAP.md")), false)
})
