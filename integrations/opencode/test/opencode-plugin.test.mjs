// Loads the OpenCode/Kilo plugin with a fake client (1.x and Kilo) and a fake plugin context (2.x), then fires the
// turn-end events. Stub guards answer block or pass; the last test runs the real scripts/guard.py. No OpenCode,
// no model, no network. Run: node --test integrations/opencode/test/   (needs Python 3 on PATH)
import test from "node:test"
import assert from "node:assert/strict"
import { copyFileSync, mkdtempSync, mkdirSync, writeFileSync } from "node:fs"
import { tmpdir } from "node:os"
import path from "node:path"
import { fileURLToPath } from "node:url"

const mod = await import(new URL("../index.js", import.meta.url))
const plugin = mod.default
const GUARD_PY = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..", "..", "scripts", "guard.py")

const BLOCK = [
  "import json, sys",
  "payload = json.load(sys.stdin)",
  'print(json.dumps({"decision": "block", "reason": "G-001: tests fail (" + payload["session_id"] + ")"}))',
  "",
].join("\n")
const PASS = "import sys\nsys.stdin.read()\n"

function project(guard, { memory = true } = {}) {
  const root = mkdtempSync(path.join(tmpdir(), "vbm-gate-"))
  mkdirSync(path.join(root, "src"))
  mkdirSync(path.join(root, "scripts"))
  writeFileSync(path.join(root, "scripts", "guard.py"), guard)
  if (memory) {
    mkdirSync(path.join(root, "memory"))
    writeFileSync(path.join(root, "memory", "MAP.md"), "# Memory map\n")
  }
  return root
}

function fakeClient({ parentID, lastError, fail } = {}) {
  const calls = []
  const method = (name, reply) => async (options) => {
    calls.push({ name, options })
    if (fail) throw new Error(`${name} failed`)
    return reply(options)
  }
  return {
    calls,
    named: (name) => calls.filter((c) => c.name === name).map((c) => c.options),
    session: {
      get: method("session.get", (o) => ({ data: { id: o.path.id, parentID } })),
      messages: method("session.messages", () => ({
        data: [
          { info: { role: "user", agent: "plan", time: { created: 1 } }, parts: [] },
          { info: { role: "assistant", time: { created: 2 }, ...(lastError ? { error: lastError } : {}) }, parts: [] },
        ],
      })),
      promptAsync: method("session.promptAsync", () => ({ data: undefined })),
    },
    app: { log: method("app.log", () => ({ data: true })) },
    tui: { showToast: method("tui.showToast", () => ({ data: true })) },
  }
}

const event = (type, properties) => ({ event: { id: `evt_${type}`, type, properties } })
const idle = (id) => event("session.idle", { sessionID: id })
const status = (id, type) => event("session.status", { sessionID: id, status: { type } })
const load = (root, client, options) =>
  plugin.server({ client, project: { id: "prj" }, directory: path.join(root, "src"), worktree: root, $: undefined }, options)

test("one default export both loaders accept", () => {
  assert.deepEqual(Object.keys(mod), ["default"])
  assert.equal(typeof plugin.id, "string")
  assert.equal(typeof plugin.server, "function")
  assert.equal(typeof plugin.setup, "function")
  assert.equal("tui" in plugin, false)
})

test("block re-prompts the same session with the reason and the last agent", async () => {
  const client = fakeClient()
  const hooks = await load(project(BLOCK), client)
  await hooks.event(idle("ses_block"))
  const sent = client.named("session.promptAsync")
  assert.equal(sent.length, 1)
  assert.equal(sent[0].path.id, "ses_block")
  assert.equal(sent[0].body.agent, "plan")
  assert.equal(sent[0].body.parts[0].type, "text")
  assert.match(sent[0].body.parts[0].text, /G-001: tests fail \(ses_block\)/)
})

test("pass lets the turn end", async () => {
  const client = fakeClient()
  const hooks = await load(project(PASS), client)
  await hooks.event(idle("ses_pass"))
  assert.equal(client.named("session.promptAsync").length, 0)
})

test("subagent sessions are skipped", async () => {
  const client = fakeClient({ parentID: "ses_parent" })
  const hooks = await load(project(BLOCK), client)
  await hooks.event(idle("ses_child"))
  assert.equal(client.named("session.promptAsync").length, 0)
})

test("a subagent known from session.created needs no lookup", async () => {
  const client = fakeClient()
  const hooks = await load(project(BLOCK), client)
  await hooks.event(event("session.created", { info: { id: "ses_child2", parentID: "ses_p" } }))
  await hooks.event(idle("ses_child2"))
  assert.equal(client.named("session.get").length, 0)
  assert.equal(client.named("session.promptAsync").length, 0)
})

test("an aborted turn is not re-prompted", async () => {
  const client = fakeClient({ lastError: { name: "MessageAbortedError", data: { message: "Aborted" } } })
  const hooks = await load(project(BLOCK), client)
  await hooks.event(idle("ses_abort"))
  assert.equal(client.named("session.promptAsync").length, 0)
})

test("no memory/MAP.md: no calls at all", async () => {
  const client = fakeClient()
  const hooks = await load(project(BLOCK, { memory: false }), client)
  await hooks.event(idle("ses_nomem"))
  assert.equal(client.calls.length, 0)
})

test("status idle + session.idle for one turn run the gate once", async () => {
  const client = fakeClient()
  const hooks = await load(project(BLOCK), client)
  await hooks.event(status("ses_dup", "busy"))
  await hooks.event(status("ses_dup", "idle"))
  await hooks.event(idle("ses_dup"))
  assert.equal(client.named("session.promptAsync").length, 1)
})

test("the user typing while the guard runs wins", async () => {
  const client = fakeClient()
  const hooks = await load(project(BLOCK), client)
  const pending = hooks.event(idle("ses_typed"))
  await hooks.event(status("ses_typed", "busy"))
  await pending
  assert.equal(client.named("session.promptAsync").length, 0)
})

test("the loop is bounded when the guard never passes", async () => {
  const client = fakeClient()
  const hooks = await load(project(BLOCK), client, { maxContinuations: 2 })
  for (let i = 0; i < 3; i++) {
    await hooks.event(status("ses_loop", "busy"))
    await hooks.event(idle("ses_loop"))
  }
  assert.equal(client.named("session.promptAsync").length, 2)
  assert.equal(client.named("tui.showToast").length, 1)
})

test("a throwing client never throws into the host", async () => {
  const hooks = await load(project(BLOCK), fakeClient({ fail: true }))
  await assert.doesNotReject(hooks.event(idle("ses_fail")))
})

function fakeContext(root, { parentID } = {}) {
  const calls = []
  const hooks = new Map()
  return {
    calls,
    fire: (name, input) => hooks.get(name)(input),
    ctx: {
      location: { directory: path.join(root, "src"), project: { id: "prj", directory: root, canonical: root } },
      options: {},
      session: {
        hook: async (name, cb) => (hooks.set(name, cb), { dispose: async () => {} }),
        get: async (input) => (calls.push({ name: "session.get", options: input }), { id: input.sessionID, parentID }),
        synthetic: async (input) => (calls.push({ name: "session.synthetic", options: input }), {}),
      },
    },
  }
}

test("OpenCode 2.x: experimental.idle continues with a synthetic message", async () => {
  const fake = fakeContext(project(BLOCK))
  await plugin.setup(fake.ctx)
  await fake.fire("experimental.idle", { sessionID: "ses_v2", background: [] })
  const sent = fake.calls.filter((c) => c.name === "session.synthetic")
  assert.equal(sent.length, 1)
  assert.equal(sent[0].options.sessionID, "ses_v2")
  assert.match(sent[0].options.text, /G-001/)
})

test("OpenCode 2.x: waits on its own subagent and skips child sessions", async () => {
  const waiting = fakeContext(project(BLOCK))
  await plugin.setup(waiting.ctx)
  await waiting.fire("experimental.idle", {
    sessionID: "ses_v2w",
    background: [{ kind: "subagent", sessionID: "ses_v2w", childSessionID: "c", agent: "explore", description: "x" }],
  })
  const child = fakeContext(project(BLOCK), { parentID: "ses_v2p" })
  await plugin.setup(child.ctx)
  await child.fire("experimental.idle", { sessionID: "ses_v2c", background: [] })
  const synthetic = [...waiting.calls, ...child.calls].filter((c) => c.name === "session.synthetic")
  assert.equal(synthetic.length, 0)
})

test("the real guard.py blocks on pending feedback", async () => {
  const root = project("")
  copyFileSync(GUARD_PY, path.join(root, "scripts", "guard.py"))
  mkdirSync(path.join(root, "tests"))
  writeFileSync(path.join(root, "tests", "test_ok.py"), "def test_ok():\n    assert True\n")
  writeFileSync(path.join(root, "memory", "feedback-log.md"), "disposition: pending\n")
  const client = fakeClient()
  const hooks = await load(root, client)
  await hooks.event(idle("ses_real"))
  const sent = client.named("session.promptAsync")
  assert.equal(sent.length, 1)
  assert.match(sent[0].body.parts[0].text, /G-003/)
  assert.match(sent[0].body.parts[0].text, /guard round 1 of 5/)
})
