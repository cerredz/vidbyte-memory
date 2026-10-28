# Contributing to vidbyte-memory

Thanks for helping. This repo is a template: every file in it is copied into every task repo made from it, so a change here changes how every agent that uses it remembers. Small, well-argued changes land fastest.

## Two kinds of repo, two kinds of commit

- **This repo (the template).** Changes go through pull requests with ordinary commit messages. `AGENTS.md` here is the runtime protocol that task repos follow, not a guide for working on the template.
- **Task repos made from it.** Those end every request with a footprint commit from `scripts/footprint.py`. Please do not open PRs that contain footprint commits from your own task repo.

## What is most useful

Each of these fits in one file and one PR:

| Contribution | Where it goes |
|---|---|
| A verifier recipe for a kind of artifact (code review, data table, prose) | `verifiers/<name>.md`, copied from `verifiers/_template.md`, plus a row in `verifiers/INDEX.md` |
| A note on running the template in another harness (Codex, Cursor, Gemini CLI, OpenCode, Aider) | an issue first, then the harness section of `README.md` |
| A fix to a skill, a prompt, `scripts/` or `tests/` | the file itself |
| A report that a correction did not stick | the "A correction didn't stick" issue form; accepted cases become tests |

For anything larger, such as a new memory type, a change to the entry format or a new script, open an issue first so the design is agreed before code is written. Pull requests written by coding agents are welcome when they implement an agreed issue.

## Rules every change keeps

- **Standard library only** in `scripts/` and `tests/`; the only runtime requirement is pytest.
- **Tests stay deterministic and fast**: no network, no model calls, no wall-clock dependence, under two seconds each (see `tests/README.md`).
- **`AGENTS.md` stays under 200 lines.** It is an index; detail belongs in the files it points to.
- **Every skill and prompt keeps its seven sections**, in order: Goal, Objective, Tasks, Instructions, Checklist, Output, Runtime behavior.
- **Every path a document names in backticks exists.** The integrity test checks this.
- **Memory files are never rewritten whole.** Append entries, edit metadata lines in place.

## Before you open a pull request

```bash
python scripts/footprint.py --write
python -m pytest -q tests
```

Both must pass; the footprint test compares `memory/footprint.md` with a fresh scan, so regenerate it whenever you add or remove a test. Add a line under `## [Unreleased]` in `CHANGELOG.md` that says what changed and who asked for it, for example `requested in #12 by @someone`.

## Credit

Release notes credit everyone who asked for or built a change, by GitHub handle, and new contributors are named in the release that ships their first change. If you reported the problem a fix solves, you are credited too.

## Conduct and security

Everyone taking part follows the [code of conduct](CODE_OF_CONDUCT.md). Report security problems privately as described in [SECURITY.md](SECURITY.md), never in a public issue.
