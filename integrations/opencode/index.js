// opencode-vidbyte-memory: the vidbyte-memory turn-end gate for OpenCode 1.x, OpenCode 2.x and Kilo.
//
// When the agent finishes a turn, this runs `python <project>/scripts/guard.py --format claude` with
// {"session_id", "cwd"} on stdin. When the guard answers {"decision": "block", "reason": ...}, the reason goes
// back into the same session as a new prompt, so the agent keeps working. The guard caps itself at 5 rounds per
// session; this plugin keeps its own cap as a backstop. Nothing here throws into the host.
//
// One default export serves every host:
// - OpenCode 1.x and Kilo read {id, server}: the `event` hook sees session.idle, and the turn continues through
//   client.session.promptAsync.
// - OpenCode 2.x reads {id, setup}: ctx.session.hook("experimental.idle") runs just before the session would go
//   idle, and ctx.session.synthetic continues the same execution.
// No named exports on purpose: OpenCode 1.x calls named exports as plugins when the default is not a plugin object.
//
// Installed by scripts/install.py as .opencode/plugins/vidbyte-memory.js (OpenCode) and .kilo/plugins/vidbyte-memory.js
// (Kilo, which does not read .opencode/), or from npm as opencode-vidbyte-memory. Plain ESM, Node built-ins only.

import { spawn } from "node:child_process"
import { existsSync } from "node:fs"
import path from "node:path"

const ID = "opencode-vidbyte-memory"
const SERVICE = "vidbyte-memory"
const DEFAULT_MAX_CONTINUATIONS = 6 // the guard gives up after 5 rounds; one spare
const DEFAULT_TIMEOUT_MS = 15 * 60 * 1000
const MESSAGE_WINDOW = 30
const COMMAND_NOT_FOUND = 9009 // Windows: unknown command, also the Microsoft Store python stub

// Shared by every copy of this plugin in the process (an npm copy and a local file can both load).
const SHARED = (globalThis[Symbol.for("vidbyte-memory.opencode-gate")] ??= {
  running: new Set(),
  continuations: new Map(),
})

async function quiet(fn) {
  try {
    return await fn()
  } catch {
    return undefined
  }
}

const created = (info) => (info ? Number(info.time?.created) || 0 : -1)

// The nearest folder with memory/MAP.md, upward from the session directory, as guard.py finds it.
function findProjectRoot(start) {
  if (typeof start !== "string" || start === "") return undefined
  let dir = path.resolve(start)
  for (;;) {
    if (existsSync(path.join(dir, "memory", "MAP.md"))) {
      return existsSync(path.join(dir, "scripts", "guard.py")) ? dir : undefined
    }
    const parent = path.dirname(dir)
    if (parent === dir) return undefined
    dir = parent
  }
}

function pythonCandidates(options) {
  const list = []
  const override = options?.python || process.env.VIDBYTE_MEMORY_PYTHON
  if (typeof override === "string" && override !== "") list.push([override, []])
  if (process.platform === "win32") list.push(["py", ["-3"]], ["python", []], ["python3", []])
  else list.push(["python3", []], ["python", []])
  return list
}

function runProcess(command, args, { cwd, input, timeoutMs }) {
  return new Promise((resolve) => {
    let child
    try {
      child = spawn(command, args, {
        cwd,
        // guard.py reads CLAUDE_PROJECT_DIR before the payload cwd: pin it, so a value inherited from an outer
        // Claude Code session cannot point the guard at another repo.
        env: { ...process.env, CLAUDE_PROJECT_DIR: cwd },
        stdio: ["pipe", "pipe", "pipe"],
        windowsHide: true,
      })
    } catch (error) {
      resolve({ launched: false, error })
      return
    }
    let stdout = ""
    let stderr = ""
    let settled = false
    const timer = setTimeout(() => {
      try {
        child.kill()
      } catch {}
      finish({ launched: true, code: null, stdout, stderr, timedOut: true })
    }, timeoutMs)
    timer.unref?.()
    function finish(result) {
      if (settled) return
      settled = true
      clearTimeout(timer)
      resolve(result)
    }
    child.on("error", (error) => finish({ launched: false, error }))
    child.on("close", (code) => finish({ launched: code !== COMMAND_NOT_FOUND, code, stdout, stderr }))
    child.stdout?.setEncoding("utf8")
    child.stderr?.setEncoding("utf8")
    child.stdout?.on("data", (chunk) => {
      stdout += chunk
    })
    child.stderr?.on("data", (chunk) => {
      stderr += chunk
    })
    child.stdin?.on("error", () => {})
    try {
      child.stdin?.end(input)
    } catch {}
  })
}

async function runGuard(root, sessionID, options) {
  const script = path.join(root, "scripts", "guard.py")
  const input = JSON.stringify({ session_id: sessionID, cwd: root, hook_event_name: "Stop" })
  const timeoutMs = Number(options?.timeoutMs) > 0 ? Number(options.timeoutMs) : DEFAULT_TIMEOUT_MS
  let failed
  for (const [command, prefix] of pythonCandidates(options)) {
    const result = await runProcess(command, [...prefix, script, "--format", "claude"], { cwd: root, input, timeoutMs })
    if (!result.launched) continue
    if (result.code === 0 || result.timedOut || String(result.stdout).trim() !== "") return result
    failed = result // launched but unusable (Python 2, a launcher with no runtime): try the next one
  }
  return failed
}

function parseGuardOutput(stdout) {
  const lines = String(stdout ?? "")
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
  for (let i = lines.length - 1; i >= 0; i--) {
    try {
      const value = JSON.parse(lines[i])
      if (value && typeof value === "object") return value
    } catch {}
  }
  return undefined
}

function createGate({ directory, options, inspect, proceed, notify, log }) {
  const limit = Number(options?.maxContinuations) > 0 ? Number(options.maxContinuations) : DEFAULT_MAX_CONTINUATIONS
  return async function gate(sessionID, stillIdle) {
    if (typeof sessionID !== "string" || sessionID === "") return "skip:no-session"
    if (SHARED.running.has(sessionID)) return "skip:running"
    SHARED.running.add(sessionID)
    let holding = true
    try {
      const root = findProjectRoot(directory)
      if (!root) return "skip:no-memory"
      const seen = (await quiet(() => inspect(sessionID))) ?? {}
      if (seen.skip) return `skip:${seen.skip}`
      const result = await runGuard(root, sessionID, options)
      const output = result?.code === 0 ? parseGuardOutput(result.stdout) : undefined
      const reason = output?.decision === "block" && typeof output.reason === "string" ? output.reason.trim() : ""
      if (reason === "") {
        SHARED.continuations.delete(sessionID)
        if (typeof output?.systemMessage === "string") await quiet(() => notify(output.systemMessage))
        else if (!result) await quiet(() => log("warn", "guard not run: no working Python 3 (tried py, python3, python)"))
        else if (result.timedOut) await quiet(() => log("warn", "guard timed out"))
        else if (result.code !== 0)
          await quiet(() => log("warn", `guard exited ${result.code}: ${String(result.stderr).slice(-400)}`))
        return "allow"
      }
      const count = (SHARED.continuations.get(sessionID) ?? 0) + 1
      if (count > limit) {
        SHARED.continuations.delete(sessionID)
        await quiet(() =>
          notify(`vidbyte-memory: the guard still blocks after ${limit} continuations; the request is NOT finished.\n${reason}`),
        )
        return "skip:limit"
      }
      if (typeof stillIdle === "function" && !stillIdle()) return "skip:busy"
      SHARED.continuations.set(sessionID, count)
      SHARED.running.delete(sessionID) // the continuation's own turn end must be able to run the gate
      holding = false
      await proceed(sessionID, `[vidbyte-memory guard] This turn cannot end yet.\n\n${reason}`, seen.context)
      return "continued"
    } catch (error) {
      await quiet(() => log("error", `gate failed: ${error instanceof Error ? error.message : String(error)}`))
      return "error"
    } finally {
      if (holding) SHARED.running.delete(sessionID)
    }
  }
}

// OpenCode 1.x and Kilo.
async function server(input, options) {
  const client = input?.client
  const directory = input?.directory || input?.worktree || process.cwd()
  const parents = new Map() // sessionID -> parentID, or null for a main session
  const turns = new Map() // sessionID -> busy transitions seen
  const handled = new Map() // sessionID -> turn count at the last idle handled

  const log = async (level, message) => {
    await client?.app?.log?.({ body: { service: SERVICE, level, message } })
  }
  const notify = async (message) => {
    await quiet(() => log("warn", message))
    await quiet(() => client?.tui?.showToast?.({ body: { title: "vidbyte-memory", message, variant: "warning" } }))
  }
  const isSubagent = async (sessionID) => {
    if (!parents.has(sessionID)) {
      const res = await quiet(() => client?.session?.get?.({ path: { id: sessionID } }))
      const info = res && typeof res === "object" && "data" in res ? res.data : res
      if (!info || typeof info !== "object") return false
      parents.set(sessionID, typeof info.parentID === "string" && info.parentID !== "" ? info.parentID : null)
    }
    return parents.get(sessionID) !== null
  }
  const inspect = async (sessionID) => {
    if (await isSubagent(sessionID)) return { skip: "subagent" }
    const res = await quiet(() =>
      client?.session?.messages?.({ path: { id: sessionID }, query: { limit: MESSAGE_WINDOW } }),
    )
    const list = Array.isArray(res?.data) ? res.data : Array.isArray(res) ? res : []
    let user
    let assistant
    for (const item of list) {
      const info = item?.info
      if (!info || typeof info !== "object") continue
      if (info.role === "user" && created(info) >= created(user)) user = info
      if (info.role === "assistant" && created(info) >= created(assistant)) assistant = info
    }
    // An aborted or failed turn ends without the gate, like a Claude Code Stop hook after an interrupt.
    if (assistant?.error) return { skip: "aborted" }
    return { context: { agent: typeof user?.agent === "string" ? user.agent : undefined } }
  }
  const proceed = async (sessionID, text, context) => {
    const session = client?.session
    const request = { path: { id: sessionID }, body: { parts: [{ type: "text", text }] } }
    if (context?.agent) request.body.agent = context.agent // without it the server uses the default agent
    if (typeof session?.promptAsync === "function") {
      const res = await session.promptAsync(request)
      if (res?.error) await quiet(() => log("warn", `promptAsync failed: ${JSON.stringify(res.error).slice(0, 400)}`))
      return
    }
    // prompt() resolves only after the new turn ends; never hold the gate for it.
    Promise.resolve()
      .then(() => session.prompt(request))
      .catch(() => {})
  }
  const gate = createGate({ directory, options, inspect, proceed, notify, log })

  return {
    event: async ({ event } = {}) => {
      try {
        const type = event?.type
        const props = event?.properties ?? {}
        if (type === "session.created" || type === "session.updated") {
          const info = props.info
          if (typeof info?.id === "string")
            parents.set(info.id, typeof info.parentID === "string" && info.parentID !== "" ? info.parentID : null)
          return
        }
        if (type === "session.deleted") {
          const id = props.info?.id
          if (typeof id === "string") {
            parents.delete(id)
            turns.delete(id)
            handled.delete(id)
            SHARED.continuations.delete(id)
          }
          return
        }
        const sessionID = props.sessionID
        if (typeof sessionID !== "string" || sessionID === "") return
        if (type === "session.status") {
          if (props.status?.type === "busy") {
            turns.set(sessionID, (turns.get(sessionID) ?? 0) + 1)
            return
          }
          if (props.status?.type !== "idle") return
        } else if (type !== "session.idle") {
          return
        }
        // session.status(idle) and session.idle arrive together: handle each turn's end once.
        const turn = turns.get(sessionID) ?? 0
        if (handled.get(sessionID) === turn) return
        handled.set(sessionID, turn)
        await gate(sessionID, () => (turns.get(sessionID) ?? 0) === turn)
      } catch {
        // never throw into the host
      }
    },
  }
}

// OpenCode 2.x.
async function setup(ctx) {
  const session = ctx?.session
  if (!session || typeof session.hook !== "function") return
  const gate = createGate({
    directory: ctx?.location?.directory || process.cwd(),
    options: ctx?.options,
    inspect: async (sessionID) => {
      const info = await quiet(() => session.get({ sessionID }))
      return typeof info?.parentID === "string" && info.parentID !== "" ? { skip: "subagent" } : {}
    },
    proceed: async (sessionID, text) => {
      await session.synthetic({ sessionID, text, description: "vidbyte-memory guard", metadata: { source: SERVICE } })
    },
    notify: async () => {},
    log: async () => {},
  })
  await session.hook("experimental.idle", async (event) => {
    try {
      const sessionID = event?.sessionID
      const background = Array.isArray(event?.background) ? event.background : []
      // The session's own subagent or image job wakes it again when it finishes; check the work then.
      if (background.some((work) => work?.sessionID === sessionID && (work.kind === "subagent" || work.kind === "image")))
        return
      await gate(sessionID)
    } catch {
      // a throwing hook fails the whole execution in OpenCode 2.x
    }
  })
}

export default { id: ID, server, setup }
