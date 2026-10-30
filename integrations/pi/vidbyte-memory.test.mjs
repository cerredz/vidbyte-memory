// Loads the Pi extension with a fake ExtensionAPI and fires agent_before_settle against the real
// scripts/guard.py in a throwaway project. No Pi install, no model, no network.
// Run: node --test vidbyte-memory.test.mjs   (GUARD_PY=<path to scripts/guard.py> to override)
import assert from "node:assert/strict";
import { copyFileSync, mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { after, test } from "node:test";
import { fileURLToPath } from "node:url";
import extension, { findProjectRoot, parseGuardOutput } from "./vidbyte-memory.js";

const here = dirname(fileURLToPath(import.meta.url));
const GUARD_PY = process.env.GUARD_PY ?? resolve(here, "..", "..", "scripts", "guard.py");

/** The fake host: records on() registrations and action calls; fire() mirrors ExtensionRunner.emitBoundary. */
function fakePi() {
	const handlers = new Map();
	const calls = [];
	const pi = {
		on(event, handler) {
			if (!handlers.has(event)) handlers.set(event, []);
			handlers.get(event).push(handler);
			return () => {};
		},
		sendMessage: (...args) => calls.push(["sendMessage", ...args]),
		sendUserMessage: (...args) => calls.push(["sendUserMessage", ...args]),
		appendEntry: (...args) => calls.push(["appendEntry", ...args]),
	};
	async function fireBoundary(type, base, ctx) {
		let entries = base.entries ?? [];
		let shouldContinue = false;
		for (const handler of handlers.get(type) ?? []) {
			const result = await handler({ ...base, type, entries, continue: shouldContinue, context: {} }, ctx);
			if (result?.entries !== undefined) entries = result.entries;
			if (result?.continue !== undefined) shouldContinue = result.continue;
		}
		return { entries, continue: shouldContinue };
	}
	async function fire(type, event, ctx) {
		for (const handler of handlers.get(type) ?? []) await handler({ ...event, type }, ctx);
	}
	return { pi, handlers, calls, fireBoundary, fire };
}

function fakeCtx(cwd, { mode = "tui", sessionId = "session-1" } = {}) {
	const notes = [];
	const ctx = {
		cwd,
		mode,
		hasUI: mode === "tui" || mode === "rpc",
		signal: undefined,
		sessionManager: { getSessionId: () => sessionId },
		ui: { notify: (message, type) => notes.push({ type, message }), setStatus: () => {} },
	};
	return { ctx, notes };
}

const scratch = mkdtempSync(join(tmpdir(), "pi-vidbyte-memory-"));
after(() => rmSync(scratch, { recursive: true, force: true }));

/** A project with memory/MAP.md, the real guard.py, one passing test, and optional pending feedback. */
function makeProject(name, { pendingFeedback }) {
	const root = join(scratch, name);
	mkdirSync(join(root, "memory"), { recursive: true });
	mkdirSync(join(root, "scripts"), { recursive: true });
	mkdirSync(join(root, "tests"), { recursive: true });
	mkdirSync(join(root, "src", "deep"), { recursive: true });
	writeFileSync(join(root, "memory", "MAP.md"), "# map\n");
	writeFileSync(join(root, "tests", "test_ok.py"), "def test_ok():\n    assert True\n");
	writeFileSync(join(root, "memory", "feedback-log.md"), pendingFeedback ? "disposition: pending\n" : "disposition: applied\n");
	copyFileSync(GUARD_PY, join(root, "scripts", "guard.py"));
	return root;
}

test("registers agent_before_settle and agent_settled, calls nothing at load", () => {
	const host = fakePi();
	extension(host.pi);
	assert.deepEqual([...host.handlers.keys()].sort(), ["agent_before_settle", "agent_settled"]);
	assert.equal(host.calls.length, 0);
});

test("finds the project root upward from a subfolder", () => {
	const root = makeProject("rooted", { pendingFeedback: false });
	assert.equal(findProjectRoot(join(root, "src", "deep")), root);
	assert.equal(findProjectRoot(scratch), null);
});

test("parses guard output", () => {
	assert.deepEqual(parseGuardOutput(""), { block: false });
	assert.deepEqual(parseGuardOutput('{"decision": "block", "reason": "fix it"}\n'), { block: true, reason: "fix it" });
	assert.deepEqual(parseGuardOutput('{"systemMessage": "gave up"}'), { block: false, message: "gave up" });
	assert.deepEqual(parseGuardOutput("not json"), { block: false });
});

test("does nothing outside a memory project", async () => {
	const host = fakePi();
	extension(host.pi);
	const { ctx } = fakeCtx(scratch);
	assert.deepEqual(await host.fireBoundary("agent_before_settle", { outcome: "completed" }, ctx), { entries: [], continue: false });
});

test("lets a clean project settle", async () => {
	const root = makeProject("clean", { pendingFeedback: false });
	const host = fakePi();
	extension(host.pi);
	const { ctx } = fakeCtx(join(root, "src", "deep"), { sessionId: "clean-session" });
	assert.deepEqual(await host.fireBoundary("agent_before_settle", { outcome: "completed" }, ctx), { entries: [], continue: false });
});

test("blocks with the guard's reason, keeps earlier drafts, gives up after the guard's 5 rounds", async () => {
	const root = makeProject("pending", { pendingFeedback: true });
	const host = fakePi();
	extension(host.pi);
	const { ctx, notes } = fakeCtx(join(root, "src"), { sessionId: "pending-session" });
	const earlier = { type: "custom", customType: "other-extension", data: 1 };

	for (let round = 1; round <= 5; round++) {
		const result = await host.fireBoundary("agent_before_settle", { outcome: "completed", entries: [earlier] }, ctx);
		assert.equal(result.continue, true, `round ${round} continues`);
		assert.deepEqual(result.entries[0], earlier);
		assert.equal(result.entries[1].type, "custom_message");
		assert.equal(result.entries[1].customType, "vidbyte-memory-guard");
		assert.equal(result.entries[1].display, true);
		assert.match(result.entries[1].content, /G-003/);
		assert.match(result.entries[1].content, new RegExp(`guard round ${round} of 5`));
	}
	const sixth = await host.fireBoundary("agent_before_settle", { outcome: "completed" }, ctx);
	assert.equal(sixth.continue, false);
	assert.match(notes.at(-1).message, /guard gave up after 5 rounds/);
	assert.equal(host.calls.length, 0, "no sendMessage/sendUserMessage: the boundary result is the channel");
});

test("skips errored runs and JSON-mode children", async () => {
	const root = makeProject("skips", { pendingFeedback: true });
	const host = fakePi();
	extension(host.pi);
	assert.equal((await host.fireBoundary("agent_before_settle", { outcome: "error" }, fakeCtx(root).ctx)).continue, false);
	assert.equal((await host.fireBoundary("agent_before_settle", { outcome: "completed" }, fakeCtx(root, { mode: "json" }).ctx)).continue, false);
});

test("never throws, even with a broken context", async () => {
	const host = fakePi();
	extension(host.pi);
	const [handler] = host.handlers.get("agent_before_settle");
	assert.equal(await handler(undefined, undefined), undefined);
	const previous = process.cwd();
	process.chdir(scratch); // a bad ctx.cwd falls back to the process cwd, which must not be a memory repo here
	try {
		assert.equal(await handler({ outcome: "completed" }, { cwd: 42, sessionManager: { getSessionId() { throw new Error("x"); } } }), undefined);
	} finally {
		process.chdir(previous);
	}
	await host.fire("agent_settled", { aborted: false }, {});
});
