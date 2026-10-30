# integrations

Plugins that enforce the vidbyte-memory guard in coding agents that have no blocking Stop hook. Each one runs the project's own `scripts/guard.py` when the agent is about to finish, and keeps the agent working while the guard reports failing tests, pending feedback or uncommitted work. Each does nothing in a folder without `memory/MAP.md`.

| Folder | Agent | Hook it uses | How it gets installed |
|---|---|---|---|
| `opencode/` | OpenCode 1.x and 2.x, Kilo Code | `session.idle` / `experimental.idle`, then a new prompt | `scripts/install.py` writes `.opencode/plugins/` and `.kilo/plugins/`; npm `opencode-vidbyte-memory` |
| `pi/` | Pi 0.87.0+ | `agent_before_settle`, returning `continue: true` | `scripts/install.py` writes `.pi/extensions/`; or the Pi package in the root `package.json`, `pi install git:github.com/cerredz/vidbyte-memory@v0.3.0` |
| `hermes/` | Hermes Agent 0.21.6+ | `pre_verify` (turns that edit files) | `hermes plugins install cerredz/vidbyte-memory/integrations/hermes --enable` |

Agents with a blocking Stop hook (Claude Code, Codex, Copilot, Gemini CLI, Antigravity, Cursor and others) need no plugin: the installer writes the hook into their settings.

Tests live next to the code (`opencode/test/`, `pi/*.test.mjs`) or in `tests/` here for Python, not in the template's `tests/`, which the installer copies into every repo. Template CI runs them all: `python -m pytest -q integrations/tests` and `node --test integrations/pi/vidbyte-memory.test.mjs integrations/opencode/test/opencode-plugin.test.mjs bin/vidbyte-memory.test.mjs`.

The root `package.json` is the npm package `vidbyte-memory`: `npx vidbyte-memory init` runs `scripts/install.py` from the package's own copy of the template, and its `pi` manifest makes the repo a Pi package. `integrations/tests/test_npm_package.py` fails when the package stops shipping a file the installer copies.
