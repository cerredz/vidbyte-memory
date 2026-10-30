# vidbyte-memory in every coding agent

The memory is files, so every agent that reads `AGENTS.md` can use it. What differs is enforcement: in agents with a blocking Stop hook, `scripts/guard.py` keeps the turn going while tests fail, feedback is pending or memory is uncommitted. Each page says how to install, what the agent reads, and how much is enforced.

One command installs into any repo and wires the agents it finds:

```bash
curl -fsSL https://raw.githubusercontent.com/cerredz/vidbyte-memory/main/scripts/install.py | python3 -
```

| Agent | Enforcement | Status |
|---|---|---|
| [Claude Code](claude-code.md) | Enforced | Tested |
| [Codex](codex.md) | Enforced | Tested |
| [GitHub Copilot (CLI, VS Code, cloud agent)](github-copilot.md) | Enforced | Per the docs |
| [Cursor](cursor.md) | Enforced | Per the docs |
| [Gemini CLI](gemini-cli.md) | Enforced | Tested |
| [Antigravity (app, `agy` CLI, IDE)](antigravity.md) | Enforced | Tested |
| [Devin (CLI, cloud, Desktop)](devin.md) | Enforced in some products | Per the docs |
| [Grok Build](grok-build.md) | Enforced | Per the docs |
| [Factory Droid](factory-droid.md) | Enforceable, wired by hand | Per the docs |
| [Qwen Code](qwen-code.md) | Enforceable, wired by hand | Per the docs |
| [OpenCode](opencode.md) | Enforced (plugin) | Run live in 1.19.5 and 2.2.4; not in 1.x headless `run` |
| [Kilo Code](kilo-code.md) | Enforced (plugin) | Run live in 7.8.18; not in headless `kilo run` |
| [Pi](pi.md) | Enforced (extension) | Run live in 1.4.0 |
| [Hermes Agent](hermes.md) | Enforced on turns that edit files (plugin) | Run live in-process; CLI path not run |
| [OpenClaw](openclaw.md) | Advisory | Per the docs |
| [Goose](goose.md) | Enforceable, wired by hand | Per the docs |
| [Cline](cline.md) | Advisory | Per the docs |
| [Amp](amp.md) | Advisory | Per the docs |
| [Junie (JetBrains)](junie.md) | Enforceable, wired by hand | Per the docs |
| [Kiro](kiro.md) | Advisory | Per the docs |
| [Zed](zed.md) | Advisory | Per the docs |
| [Warp](warp.md) | Advisory | Per the docs |
| [Crush](crush.md) | Advisory | Per the docs |
| [Augment / Auggie](augment.md) | Advisory | Per the docs |

"Tested" means the plugin was installed or validated with that agent's own CLI on 2026-10-29. "Tested with a fake host" means the plugin in [`integrations/`](../../integrations/) was loaded the way that agent loads it and driven against the real guard by template CI, but not yet run in a live session. "Per the docs" means the setup follows the vendor's documentation and has not been run end to end yet. Ran it somewhere? [Tell us](https://github.com/cerredz/vidbyte-memory/discussions) so the page can say "tested".

Continue and Roo Code are not listed: Continue is read-only after its final 2.0.0 release, and Roo Code was archived on 2026-05-15.
