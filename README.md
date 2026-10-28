# vidbyte-memory

A GitHub template for a task repo whose agent learns from human feedback. Memory lives in typed markdown files, feedback is handled by three subagents, every generation is verified in rounds, and every request ends with a commit that says how the memory footprint changed.

The design rests on three findings from the published memory systems: memory files must never be rewritten whole (the context collapse the ACE paper measured), memory is context rather than enforcement (Claude Code's auto memory), and stored facts are checked at read time if ever, never at write time (GitHub Copilot verifies its memory citations when they are used). So facts stay slim and rare, deterministic tests carry the enforcement, and a human correction is the only way a fact or rule gets in.

## The loop

1. **Start of a request.** The agent reads `AGENTS.md`, which is an index, then opens only the memory files whose "load when" matches.
2. **Generation.** Each generative step gets 3 to 5 verification rounds with the full suite: the tests in `tests/` and the verifier agents listed in `verifiers/INDEX.md`.
3. **Feedback.** Any correction triggers three subagents in parallel: one decides whether the feedback becomes a long-lasting fact and writes it, one turns the feedback into deterministic tests or a verifier agent, one updates existing memory that the feedback contradicts or confirms.
4. **End of a request.** All tests pass, no feedback is left pending, and `scripts/footprint.py --commit` regenerates `memory/footprint.md`, commits with the delta in the message, and pushes.

## Quick start

1. Click "Use this template", clone it, and open it in Claude Code, Codex, Cursor or any agent that reads `AGENTS.md`.
2. Replace the `## Task` block in `AGENTS.md` with the recurring task this repo serves.
3. Run `python -m pytest -q tests` once. It passes on the empty template.
4. Give the agent a request. Correct it when it is wrong. Watch `memory/` and `tests/` grow, and `memory/run-log.md` record each request's footprint delta.

Requirements: Python 3.9 or later, `pytest`, `git`, and a remote named `origin` for the push at the end of each request. The scripts use only the standard library.

## Layout

| Path | Purpose |
|---|---|
| `AGENTS.md` | The index and the runtime protocol. Under 200 lines. Never holds memory contents. |
| `CLAUDE.md` | One line that imports `AGENTS.md` for Claude Code. |
| `facts/` | Slim facts, 4 to 5 sentences each, split by subject file. Each file has a title and description. |
| `memory/` | The memory map (`MAP.md`) and 17 typed files: rules, hints, guarantees, failures, verification recipes, decisions, open questions, scope, workflows, glossary, pointers, owner profile, examples, feedback log, run log, progress, footprint. |
| `skills/` | Six skills loaded on demand: handle-feedback, create-fact, create-test, create-verifier, update-memory, verify-generation. |
| `prompts/` | The three feedback subagent prompts. |
| `verifiers/` | Verification agents and their index. |
| `tests/` | Deterministic checks, including the memory integrity test. |
| `scripts/` | `footprint.py` (counts, delta, commit) and `guard.py` (the Stop hook). |
| `.claude/` | Claude Code subagent wrappers and the Stop hook. |
| `.github/workflows/tests.yml` | Runs the tests on every push and pull request. |

## Harness notes

- **Claude Code.** Works out of the box. `.claude/agents/` wraps the three feedback subagents and a generic verifier runner, and `.claude/settings.json` installs a Stop hook that blocks ending a turn while tests fail, feedback is pending, or memory changes are uncommitted. Delete `.claude/settings.json` to turn the hook off; the protocol in `AGENTS.md` still asks for the same behavior.
- **Codex, Cursor, others.** `AGENTS.md`, the skills, the prompts and the scripts work unchanged. Where the harness has no subagents, the agent runs the three feedback prompts one after another itself, reading only each prompt and its inputs. The skills live in `skills/` rather than in the Claude Code-only skills folder, so every harness finds them; `AGENTS.md` links them by path.

## Design rules the files follow

- Facts are admitted only through five checks: the model gets it wrong without it, it cannot be derived from the repo, it will still matter in later runs, a human stated it or asked for it, and it can be stated narrowly and checked.
- Entries have ids that are never reused, a source, a status, and a check. Nothing is deleted; entries are superseded or retired.
- Every memory file starts with frontmatter that says what it holds and when to load it, so the index in `AGENTS.md` can stay one line per file.
- Tests are the first choice for every check because they are cheap and deterministic. A verifier agent is created only when a test cannot encode the judgment.
- The footprint commit after every request is the audit trail: `git log` shows what memory changed and when.

## License

MIT. See `LICENSE`.
