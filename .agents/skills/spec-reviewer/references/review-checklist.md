# Retrospective Checklist

- Required; runs when the spec is `all tasks approved`; works from repository evidence in a fresh session.
- Per-task checks not repeated; focus is cross-task.
- Contract and `## Change log` read; `task-reviews.md` read.
- Definition of Done and every requirement have evidence/status.
- Cross-task consistency, docs vs. code, duplicated logic checked.
- Scope drift and unrecorded spec edits checked over `main...spec/<NNN>`.
- Package boundaries and security invariants checked.
- Protected paths (`evaluation/`, `knowledge/`, `config/`) diffed; unrequired changes are BLOCKING.
- `make verify` and spec-level checks actually run and recorded.
- Deviations from requirements/design listed; unrecorded material ones are MAJOR findings.
- Docs reconciled with the code (DECISIONS, TECH_STACK, ARCHITECTURE, COMMANDS, CURRENT_STATE, touched docs, design `## As-built notes`); every edit listed; no code, tests, protected paths or `requirements.md` edited.
- No code fixed by the reviewer; findings classified IMPLEMENTATION or SPEC_DEFECT.
- `review.md` round appended with "Notes for the next spec".
- RM tasks (with `State: not started`) added for code findings; `Status:` set back to `implementing (…)` if so.
- Outcome `PASS`/`FAIL` reflects evidence, not confidence; nothing committed.
