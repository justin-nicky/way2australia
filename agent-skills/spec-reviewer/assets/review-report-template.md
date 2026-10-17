## Round <N> — <YYYY-MM-DD>

- **Spec:** `<NNN-feature-name>`
- **Diff reviewed:** `main...spec/<NNN>` (head `<sha>`)
- **Reviewer host / model:** <e.g. Claude Code / model id>
- **Outcome:** `PASS | FAIL` (required for verification; FAIL = any BLOCKING or MAJOR finding)
- **Usage:** <tokens, e.g. 180K> (recorded by the orchestrator)

### Verification run

| Command/check | Result | Notes |
|---|---|---|

### Requirements traceability

| Requirement | Implementation evidence | Test/verification evidence | Status |
|---|---|---|---|

### Protected-data check

`git diff --stat main...spec/<NNN> -- evaluation/ knowledge/ config/` → <result and justification per changed file>

### Findings

| ID | Severity | Class | Requirement/Task | Finding |
|---|---|---|---|---|
| F1 | BLOCKING / MAJOR / MINOR | IMPLEMENTATION / SPEC_DEFECT | R# / T# | ... |

### Documentation reconciled

| File | Change | Reason |
|---|---|---|

### Deviations from the approved plan

| Deviation | Where approved (change log / task-reviews round) or finding ID |
|---|---|

### Cross-task consistency

### Scope-drift review

### Remediation required

<!-- RM<N>.<k> tasks appended to tasks.md; SPEC_DEFECT items for spec-planner. -->

### Notes for the next spec

<!-- Lessons, deferred items, risks, decisions affecting upcoming specs. -->

### Final handoff
