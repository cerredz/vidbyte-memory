/**
 * vidbyte-memory for Pi: the turn-end gate.
 *
 * Before Pi lets a run settle, this runs the project's own scripts/guard.py (the same check the
 * Claude Code Stop hook runs). When the guard answers {"decision":"block","reason":...}, the reason
 * goes back to the model as a user-role custom message and Pi makes one more request, so the agent
 * keeps working until the memory guarantees hold. guard.py caps itself at 5 rounds per session; this
 * file adds its own cap per settle so the loop always ends.
 *
 * Loads in Pi >= 0.87.0 (the release that added agent_before_settle) from:
 *   - npm:  pi install npm:pi-vidbyte-memory
 *   - a project file: <project>/.pi/extensions/vidbyte-memory.js (needs project trust)
 * Plain ESM JavaScript on purpose: Pi loads it through jiti, and Node can import it directly in tests.
 * No imports beyond Node built-ins. It never throws: any failure means "do not block".
 */

import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";

const STATUS_KEY = "vidbyte-memory";
const MESSAGE_TYPE = "vidbyte-memory-guard";
const GUARD_TIMEOUT_MS = 5 * 60 * 1000; // guard.py runs the project's pytest suite
const PROBE_TIMEOUT_MS = 15 * 1000;
const MAX_CONTINUES_PER_SETTLE = 6; // guard.py stops at 5; this is the backstop

/** The nearest folder with memory/MAP.md, searched upward from `start`; null when there is none. */
export function findProjectRoot(start) {
	if (typeof start !== "string" || start === "") return null;
	let dir = resolve(start);
	for (;;) {
		if (existsSync(join(dir, "memory", "MAP.md"))) return dir;
		const parent = dirname(dir);
		if (parent === dir) return null;
		dir = parent;
	}
}

/** Python launchers to try, in order. On Windows `python3` is often the Microsoft Store stub. */
export function pythonCandidates(platform = process.platform, override = process.env.VIDBYTE_MEMORY_PYTHON) {
	const list = platform === "win32" ? [["py", "-3"], ["python"], ["python3"]] : [["python3"], ["python"]];
	return override ? [[override], ...list] : list;
}

/** Run a program without a shell; resolves (never rejects) with { code, stdout, stderr }. */
export function runProcess(command, args, { cwd, input = "", env, timeoutMs, signal } = {}) {
	return new Promise((done) => {
		let child;
		try {
			child = spawn(command, args, { cwd, env, shell: false, windowsHide: true, stdio: ["pipe", "pipe", "pipe"] });
		} catch (error) {
			done({ code: null, stdout: "", stderr: String(error) });
			return;
		}
		let stdout = "";
		let stderr = "";
		let finished = false;
		const kill = () => {
			try {
				child.kill();
			} catch {}
		};
		const timer = timeoutMs ? setTimeout(kill, timeoutMs) : undefined;
		const finish = (code) => {
			if (finished) return;
			finished = true;
			if (timer) clearTimeout(timer);
			signal?.removeEventListener?.("abort", kill);
			done({ code, stdout, stderr });
		};
		if (signal?.aborted) kill();
		else signal?.addEventListener?.("abort", kill, { once: true });
		child.stdout.setEncoding("utf8").on("data", (chunk) => (stdout += chunk));
		child.stderr.setEncoding("utf8").on("data", (chunk) => (stderr += chunk));
		child.on("error", (error) => {
			stderr += String(error);
			finish(null);
		});
		child.on("close", (code) => finish(code));
		child.stdin.on("error", () => {});
		child.stdin.end(input);
	});
}

let pythonLookup;

/** The first launcher that really runs Python 3, found once per process; null when none does. */
export function resolvePython(cwd) {
	pythonLookup ??= (async () => {
		for (const [command, ...prefix] of pythonCandidates()) {
			const probe = await runProcess(command, [...prefix, "-c", "import sys; print(sys.version_info[0])"], {
				cwd,
				timeoutMs: PROBE_TIMEOUT_MS,
			});
			if (probe.code === 0 && probe.stdout.trim() === "3") return [command, ...prefix];
		}
		return null;
	})();
	return pythonLookup;
}

/** Read guard.py --format claude output: a block with its reason, a give-up message, or nothing. */
export function parseGuardOutput(stdout) {
	const lines = String(stdout ?? "")
		.split(/\r?\n/)
		.map((line) => line.trim())
		.filter(Boolean);
	for (let i = lines.length - 1; i >= 0; i--) {
		let data;
		try {
			data = JSON.parse(lines[i]);
		} catch {
			continue;
		}
		if (!data || typeof data !== "object") continue;
		if (data.decision === "block" && typeof data.reason === "string" && data.reason.trim() !== "") {
			return { block: true, reason: data.reason };
		}
		if (typeof data.systemMessage === "string") return { block: false, message: data.systemMessage };
		return { block: false };
	}
	return { block: false };
}

function sessionIdOf(ctx) {
	try {
		const id = ctx?.sessionManager?.getSessionId?.();
		if (typeof id === "string" && id !== "") return id;
	} catch {}
	return "pi";
}

function notify(ctx, message, type) {
	try {
		ctx?.ui?.notify?.(message, type);
	} catch {}
}

function setStatus(ctx, text) {
	try {
		ctx?.ui?.setStatus?.(STATUS_KEY, text);
	} catch {}
}

export default function vidbyteMemory(pi) {
	let continuesThisSettle = 0;
	let warnedNoPython = false;

	// agent_start fires again on every continuation, so the backstop resets only when Pi truly settles.
	pi.on("agent_settled", () => {
		continuesThisSettle = 0;
	});

	pi.on("agent_before_settle", async (event, ctx) => {
		try {
			if (!event || event.outcome !== "completed") return undefined; // errors and aborts end the run
			if (ctx?.mode === "json") return undefined; // JSON-mode children (subagents) are not gated
			if (process.env.VIDBYTE_MEMORY_GUARD === "off") return undefined;
			if (continuesThisSettle >= MAX_CONTINUES_PER_SETTLE) return undefined;

			const cwd = typeof ctx?.cwd === "string" && ctx.cwd ? ctx.cwd : process.cwd();
			const root = findProjectRoot(cwd);
			if (!root) return undefined;
			const guard = join(root, "scripts", "guard.py");
			if (!existsSync(guard)) return undefined;

			const python = await resolvePython(root);
			if (!python) {
				if (!warnedNoPython) {
					warnedNoPython = true;
					notify(ctx, "vidbyte-memory: no Python 3 found, so the turn-end guard did not run.", "warning");
				}
				return undefined;
			}

			setStatus(ctx, "vidbyte-memory: checking guarantees");
			let result;
			try {
				result = await runProcess(python[0], [...python.slice(1), guard, "--format", "claude"], {
					cwd: root,
					input: JSON.stringify({ session_id: sessionIdOf(ctx), cwd, hook_event_name: "Stop" }),
					env: { ...process.env, CLAUDE_PROJECT_DIR: root },
					timeoutMs: GUARD_TIMEOUT_MS,
					signal: ctx?.signal,
				});
			} finally {
				setStatus(ctx, undefined);
			}
			if (result.code !== 0) return undefined;

			const decision = parseGuardOutput(result.stdout);
			if (decision.message) notify(ctx, decision.message, "warning");
			if (!decision.block) return undefined;

			continuesThisSettle += 1;
			const prior = Array.isArray(event.entries) ? event.entries : [];
			return {
				entries: [
					...prior,
					{ type: "custom_message", customType: MESSAGE_TYPE, content: decision.reason, display: true },
				],
				continue: true,
			};
		} catch {
			return undefined;
		}
	});
}
