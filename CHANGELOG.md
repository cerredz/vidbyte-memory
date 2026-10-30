# Changelog

All notable changes to the vidbyte-memory template. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/). Each entry says who asked for the change, because release notes credit requesters as well as authors.

Task repos made from the template do not update themselves. When a change matters for existing task repos, its entry says which files to copy.

## [Unreleased]

## [0.3.0] - 2026-10-30

Install from npm and as a Pi package. Requested by @cerredz.

### Added

- **The npm package `vidbyte-memory`** (the root `package.json`). `npx vidbyte-memory init` runs `scripts/install.py` from the package's own copy of the template, so it works offline and installs the same release as the package; `uninstall` and every installer option pass through. It looks for Python 3.9+ the way the agent plugins do (`VIDBYTE_MEMORY_PYTHON`, then `py -3`, `python`, `python3` on Windows). It works once the package is published to npm.
- **A Pi package** in the same `package.json`: `pi install git:github.com/cerredz/vidbyte-memory@v0.3.0` loads the turn-end extension for every repo and the `install-memory` skill. The `pi-package` keyword lists it in the Pi gallery once it is on npm.
- Template CI tests the npm command end to end (install, then uninstall, from the package's files), packs both npm packages, and fails when `package.json` stops shipping a file the installer copies.

### Fixed

- **Hermes on Windows never blocked a turn.** Hermes runs from its own venv, whose launcher exports `PYTHONHOME`. The project's Python inherited it, died at startup, and the plugin let every turn end. The plugin now drops `PYTHONHOME` before it starts the guard. Found in a live Hermes run.
- **Pi ran the guard twice with both copies loaded.** With the Pi package and the project's `.pi/extensions/vidbyte-memory.js` both loaded, each copy ran the guard. After the guard gave up at round 5, the other copy started a second cycle of 5. Now only the copy loaded last gates the process. Existing task repos: copy `integrations/pi/vidbyte-memory.js` to `.pi/extensions/vidbyte-memory.js`.

### Tested

- **The turn-end plugins were run live on 2026-10-30** against a local mock model, in repos with a failing test and an uncommitted file. Each kept the session working until the guard's cap (Hermes: its own cap of 3 nudges per turn).
  - OpenCode 1.19.5 and 2.2.4, Kilo 7.8.18, Pi 1.4.0, and Hermes from git through its in-process runner.
  - Headless `opencode run` (1.x) and `kilo run` exit before the plugin's new prompt starts. The host pages in `docs/hosts/` say so.

### Changed

- `opencode-vidbyte-memory` ships its license file, ready for `npm publish` from `integrations/opencode`.

## [0.2.1] - 2026-10-30

Listing fixes found while submitting v0.2.0 to agent marketplaces. Requested by @cerredz.

### Added

- `.codex-plugin/plugin.json`, Codex's own plugin manifest, with the full listing metadata (long description, icon, screenshots, privacy and license links) and a `.codexignore`. Codex reads it before the root `plugin.json`; the HOL plugin scanner (`plugin-scanner` 3.58.0) now scores the repo 100/100 with no findings, which the awesome-codex-plugins catalog requires. Requested by @cerredz.

### Changed

- GitHub Actions are pinned to commit SHAs, with the version in a comment; Dependabot keeps them current.
- The `install-memory` skill no longer pipes `curl` into Python when it runs outside the plugin. It clones the release it shipped with (`--branch v0.2.1`) into a temporary folder and runs `scripts/install.py` from there, so the owner can read the script first and the install is the reviewed release. Marketplaces that mirror the skill (Kilo) require that pin, and a test keeps it equal to the plugin version. The README one-liner for people is unchanged. Existing task repos: copy `skills/install-memory/SKILL.md` and run `python scripts/sync_skills.py`.

## [0.2.0] - 2026-10-30

Install the memory into any existing repo, from inside the coding agents people already use. Requested by @cerredz.

### Added

- **One-command installer**, `scripts/install.py`: `curl -fsSL https://raw.githubusercontent.com/cerredz/vidbyte-memory/main/scripts/install.py | python3 -`. It copies the memory into an existing repo without overwriting any file, folds an existing `AGENTS.md` into the Task section (or keeps a long one as `AGENTS.previous.md`), adds `@AGENTS.md` to `CLAUDE.md`, backs up every file it edits, wires the Stop hook for each agent it finds (Claude Code, Codex, GitHub Copilot, Gemini CLI, Antigravity; Kiro and Qoder skill folders), and records every write, with its hash and backup, in `.vidbyte-memory/install.json`. `--dry-run` prints the plan; a second run changes nothing.
- **`install.py uninstall`**, which undoes an install from that manifest: it deletes the files the install created, restores the files it changed from their backups, takes the guard hook out of agent settings files the owner edited since (keeping the owner's own settings and hooks), and keeps memory the agent wrote unless `--force`.
- **The `install-memory` skill**, which runs the installer from inside an agent, fills the Task section with the owner and commits.
- **Plugin manifests**, so the repo installs as a plugin: `.claude-plugin/` (Claude Code marketplace `vidbyte`, with an icon), `plugin.json` (Agent Plugins 1.0, read by Codex, Copilot, Cursor, Kiro, Devin, Goose and others), `.agents/plugins/marketplace.json` (Codex), `hooks/hooks.json` (the plugin's Stop hook) and `gemini-extension.json`.
- **Skill mirrors** in `.agents/skills/` and `.claude/skills/`, where about 25 agents look for project skills; `scripts/sync_skills.py` writes them and a test fails when they drift.
- **`docs/hosts/`**: one page per agent (24) with the install command, what it reads and how much is enforced.
- **Plugins that enforce the guard in agents without a blocking Stop hook**, in `integrations/`. The installer wires the first two into the repo; Hermes plugins are per user, so the installer prints the install command.
  - OpenCode and Kilo Code: one plugin file, written to `.opencode/plugins/` and `.kilo/plugins/`, that re-prompts the session while the guard blocks. It serves OpenCode 1.x, OpenCode 2.x and Kilo, and skips subagent sessions and interrupted turns.
  - Pi: an extension in `.pi/extensions/` that continues the run from `agent_before_settle` (Pi 0.87.0 or later).
  - Hermes Agent: a `pre_verify` plugin, `hermes plugins install cerredz/vidbyte-memory/integrations/hermes --enable`.
  - Each is tested in template CI against a fake host built from that agent's plugin API, driving the real `scripts/guard.py`.

### Changed

- `scripts/guard.py` checks the project the agent works in (from `CLAUDE_PROJECT_DIR`, the hook's `cwd` or the current directory), so it also runs from a plugin cache; it does nothing in a repo without `memory/MAP.md`, and a plugin copy defers to the repo's own hook. `--format gemini|antigravity|exit2` speaks those agents' hook protocols. Existing task repos: copy `scripts/guard.py`.
- Only `tests/test_fb*.py` files are treated as feedback tests, so a repo's own tests can live in `tests/`. Existing task repos: copy `tests/test_memory_integrity.py`.
- `SECURITY.md` moved to the repo root, where plugin scanners look for it.
- When the interpreter running the guard has no pytest, G-001 now says that pytest is missing and how to install it, instead of reporting failing tests.

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

[Unreleased]: https://github.com/cerredz/vidbyte-memory/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/cerredz/vidbyte-memory/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/cerredz/vidbyte-memory/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/cerredz/vidbyte-memory/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/cerredz/vidbyte-memory/releases/tag/v0.1.0
