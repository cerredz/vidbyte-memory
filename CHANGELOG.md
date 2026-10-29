# Changelog

All notable changes to the vidbyte-memory template. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/). Each entry says who asked for the change, because release notes credit requesters as well as authors.

Task repos made from the template do not update themselves. When a change matters for existing task repos, its entry says which files to copy.

## [Unreleased]

## [0.2.0] - 2026-10-29

Install the memory into any existing repo, from inside the coding agents people already use. Requested by @cerredz.

### Added

- **One-command installer**, `scripts/install.py`: `curl -fsSL https://raw.githubusercontent.com/cerredz/vidbyte-memory/main/scripts/install.py | python3 -`. It copies the memory into an existing repo without overwriting any file, folds an existing `AGENTS.md` into the Task section (or keeps a long one as `AGENTS.previous.md`), adds `@AGENTS.md` to `CLAUDE.md`, backs up every file it edits, wires the Stop hook for each agent it finds (Claude Code, Codex, GitHub Copilot, Gemini CLI, Antigravity; Kiro and Qoder skill folders), and records every write in `.vidbyte-memory/install.json`. `--dry-run` prints the plan; a second run changes nothing.
- **The `install-memory` skill**, which runs the installer from inside an agent, fills the Task section with the owner and commits.
- **Plugin manifests**, so the repo installs as a plugin: `.claude-plugin/` (Claude Code marketplace `vidbyte`, with an icon), `plugin.json` (Agent Plugins 1.0, read by Codex, Copilot, Cursor, Kiro, Devin, Goose and others), `.agents/plugins/marketplace.json` (Codex), `hooks/hooks.json` (the plugin's Stop hook) and `gemini-extension.json`.
- **Skill mirrors** in `.agents/skills/` and `.claude/skills/`, where about 25 agents look for project skills; `scripts/sync_skills.py` writes them and a test fails when they drift.
- **`docs/hosts/`**: one page per agent (24) with the install command, what it reads and how much is enforced.

### Changed

- `scripts/guard.py` checks the project the agent works in (from `CLAUDE_PROJECT_DIR`, the hook's `cwd` or the current directory), so it also runs from a plugin cache; it does nothing in a repo without `memory/MAP.md`, and a plugin copy defers to the repo's own hook. `--format gemini|antigravity|exit2` speaks those agents' hook protocols. Existing task repos: copy `scripts/guard.py`.
- Only `tests/test_fb*.py` files are treated as feedback tests, so a repo's own tests can live in `tests/`. Existing task repos: copy `tests/test_memory_integrity.py`.
- `SECURITY.md` moved to the repo root, where plugin scanners look for it.

### Fixed

- `scripts/footprint.py --write` and `--commit` crashed on Python 3.9, the oldest version the README supports, because `Path.write_text(newline=...)` needs Python 3.10. They now write through `open()`. Found by the 3.9 CI job once a test ran the footprint writer. Task repos made from v0.1.0: copy `scripts/footprint.py`.
- Five files had frontmatter values that YAML cannot parse, because an unquoted value contained `": "`. Skill and agent loaders parse frontmatter as YAML and skip such a file without a warning, so the `skills` CLI found only 4 of the 6 skills and missed `handle-feedback`, the protocol's entry point. The values are now quoted, and `test_frontmatter_values_parse_as_yaml` fails on any unquoted value YAML would reject. Found while preparing agent-marketplace listings requested by @cerredz. Task repos made from v0.1.0: copy `skills/handle-feedback/SKILL.md`, `skills/update-memory/SKILL.md`, `.claude/agents/verifier.md`, `tests/helpers.py` and `tests/test_memory_integrity.py`, and quote the `description` lines of `memory/pointers.md` and `memory/progress.md` and the `write` line of `memory/progress.md`.

## [0.1.0] - 2026-10-28

First public release. Requested by @cerredz.

### Added

- The template: `AGENTS.md` as the runtime protocol and memory index, 17 typed memory files mapped in `memory/MAP.md`, slim facts in `facts/`, six skills, three feedback subagent prompts with Claude Code wrappers, the memory-conformance verifier, the memory integrity tests, `scripts/footprint.py` and the `scripts/guard.py` Stop hook.
- Footprint commits end with a `Memory-Template: vidbyte-memory` git trailer, so public task repos made from the template can be counted with GitHub commit search. `--no-marker` leaves it out of one commit; setting `TEMPLATE_MARKER = ""` in `scripts/footprint.py` removes it for good. Existing task repos: copy `scripts/footprint.py` and `tests/test_memory_integrity.py` to get it.
- A landing-page README with a quick start, a demo, a before-and-after comparison, known limits and an FAQ.
- `llms.txt`, `context7.json` and `.devin/wiki.json`, so coding agents and their documentation indexes can read the template.
- Community files: contributing guide, code of conduct, security policy, issue forms (including "A correction didn't stick"), a pull request template and release-note categories.
- `template-ci.yml`, which tests Python 3.9 and 3.13 on Ubuntu and 3.11 on Windows, only in this repo.
- A live example, [cerredz/vidbyte-memory-example](https://github.com/cerredz/vidbyte-memory-example), made from the template.

[Unreleased]: https://github.com/cerredz/vidbyte-memory/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/cerredz/vidbyte-memory/releases/tag/v0.1.0
