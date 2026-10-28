---
title: Run log
description: One line per request with the footprint delta it produced. Load when reporting history or checking what a past request changed.
write: scripts/footprint.py --commit appends the line. Agents do not edit it by hand.
---

# Run log

Format: `- YYYY-MM-DD | <request in a few words> | <footprint delta>`.

## Log
- 2026-10-27 | scaffold the template | +6 guarantees, +4 verification, +18 tests, +1 verifiers
- 2026-10-27 | verification sweep | +6 tests
- 2026-10-27 | deepen skills and prompts, add stopping condition | no change
