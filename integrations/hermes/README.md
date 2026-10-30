# vidbyte-memory for Hermes Agent

The turn-end gate of [vidbyte-memory](https://github.com/cerredz/vidbyte-memory), the template that turns each correction you give a coding agent into a slim fact, a test and a footprint commit in your repo.

Before Hermes finishes a turn that edited files, this plugin runs the project's own `scripts/guard.py`, the same check the Claude Code Stop hook runs. While the tests fail, feedback is still pending, or changes are uncommitted or unpushed, it hands the guard's reason back to the agent and Hermes keeps working. In any folder without `memory/MAP.md` and `scripts/guard.py` it does nothing.

## Install

```bash
hermes plugins install cerredz/vidbyte-memory/integrations/hermes --enable
```

Then, in each repo that has the memory, run `hermes skills trust` so Hermes loads the memory skills from `.agents/skills/`. To add the memory to a repo, see the [install guide](https://github.com/cerredz/vidbyte-memory/blob/main/docs/hosts/hermes.md).

## What it runs

- The project's `scripts/guard.py`, on the host, with the project's Python: its `.venv` when there is one, otherwise `python` on PATH.
- The guard runs the project's pytest suite, `git status` and `git rev-list`, and writes `.claude/.guard_state.json` in the project.
- No network calls, no credentials, no telemetry.

## Limits

- Hermes fires `pre_verify` only on turns where `write_file` or `patch` changed a file. A turn that edits nothing, or edits only through the terminal, is not gated.
- Hermes allows 3 continues per turn (`agent.max_verify_nudges`), and the guard allows 5 blocking rounds per session before it lets the turn end with a note that the request is unfinished.
- Hermes gives a hook 30 seconds by default. The plugin stops the guard just before that and lets the turn end. For a slower test suite, raise the limit with `hermes config set plugins.hook_callback_timeout 200`.

Requires Hermes 0.21.6 or later. MIT licensed.
