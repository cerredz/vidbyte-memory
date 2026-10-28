# Facts

Slim facts the model gets wrong without being told, split by subject into one file each. A fact is 4 to 5 full sentences: the subject and when it applies, the fact stated as the narrowest rule, why, how to apply it, and optionally the boundary or evidence. Facts are rare on purpose: a fact enters only through `skills/create-fact/SKILL.md` after the five admission checks, or when the owner says "collect facts about X".

Each file starts with frontmatter (`title`, `description`, `write`) and is listed in the facts index in `AGENTS.md` with its title and when to load it. `tests/test_memory_integrity.py` fails when a file here is missing from that index, when a fact is not 4 to 5 sentences, or when a fact has no metadata line.

Starter files:

| File | Holds |
|---|---|
| `project.md` | what the project is, its users, its history |
| `environment.md` | machines, paths, runtimes, what does and does not run where; a location alone is a pointer in `memory/pointers.md`, a location plus a behaviour the model gets wrong is an environment fact |
| `conventions.md` | formatting, naming, style the owner insists on |
| `domain.md` | subject-matter facts the model gets wrong |
| `tooling.md` | how a specific tool, library, CLI or service actually behaves |

Create a new file only when a fact fits none of these; the create-fact skill says how.

The ledger of every fact is the set of `### F-` headings across this folder: `grep -rn "^### F-" facts/` lists it, and `memory/footprint.md` counts it.
