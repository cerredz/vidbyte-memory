# opencode-vidbyte-memory

The turn-end gate of [vidbyte-memory](https://github.com/cerredz/vidbyte-memory) for OpenCode and Kilo Code. vidbyte-memory turns each correction you give a coding agent into a slim fact, a test and a footprint commit in your repo.

When a session goes idle, this plugin runs the project's `scripts/guard.py`. While the tests fail, feedback is pending, or changes are uncommitted or unpushed, it sends the guard's reason back into the same session as a new prompt, so the agent keeps working. In any folder without `memory/MAP.md` it does nothing.

## Install

The vidbyte-memory installer writes this file into the repo for you: `.opencode/plugins/vidbyte-memory.js` for OpenCode and `.kilo/plugins/vidbyte-memory.js` for Kilo. Both load it with no npm step. See the [OpenCode](https://github.com/cerredz/vidbyte-memory/blob/main/docs/hosts/opencode.md) and [Kilo](https://github.com/cerredz/vidbyte-memory/blob/main/docs/hosts/kilo-code.md) pages.

From npm instead, in `opencode.json` or `kilo.json`:

```json
{ "plugin": ["opencode-vidbyte-memory"] }
```

Use one route, not both.

## Hosts

- **OpenCode 1.x and Kilo:** the `event` hook on `session.idle`, continuing through `client.session.promptAsync` with the session's own agent.
- **OpenCode 2.x:** the `experimental.idle` session hook, continuing the same run through `session.synthetic`.

Subagent sessions and interrupted turns are not gated. The guard stops after 5 rounds per session and the plugin after 6 continuations.

## Options

`["opencode-vidbyte-memory", { "python": "...", "maxContinuations": 6, "timeoutMs": 900000 }]`, or `VIDBYTE_MEMORY_PYTHON` to choose the interpreter.

## Test

`node --test test/` loads the plugin with fake OpenCode 1.x and 2.x hosts and drives stub guards and the real `scripts/guard.py`. It needs Python 3 with pytest. MIT licensed.
