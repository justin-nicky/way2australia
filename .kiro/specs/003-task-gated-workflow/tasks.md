# 003 — Task-Gated Agent Workflow Tasks

Status: implementing (base 9e95cfe)

Bootstrap: this spec is implemented under the pre-003 flow, directly on `main` (design → "Bootstrap"). The `State:` lines below follow the new format from the start.

## T1 — Define the lifecycle in WORKFLOW.md and record D023

**State:** in task review (round 1)
**Requirements:** R1, R7, R12

- [x] Rewrite the canonical flow in `docs/project/WORKFLOW.md` to the task-gated loop (design → "Design summary").
- [x] Define task `State:` values, owners and next actions, and the new `tasks.md` spec `Status:` values (design → "Interfaces / models").
- [x] Document branching: `spec/<NNN>`, `Spec-Task` / `Spec-Review` / `Spec-Decision` trailers, no history rewrite, final `--no-ff` merge.
- [x] Document the `task-reviews.md` format and the redefined "verified".
- [x] Add D023 to `docs/project/DECISIONS.md`, stating which D022 rules it supersedes and which remain.

### Verification

- Every state in the design's state table appears in `WORKFLOW.md` with exactly one owner and one next action.
- `grep -n "implemented — pending review\|review failed — round" docs/project/WORKFLOW.md` only matches text marking these values as retired.

## T2 — Create the task-reviewer skill

**State:** not started
**Requirements:** R3, R4, R9, R10, R11

- [ ] Add `agent-skills/task-reviewer/SKILL.md`: inputs, minimal reading list, task-diff command, checks, read-only rule, verdicts, finding severity/classification, user summary, model recording.
- [ ] Add `assets/task-review-template.md` matching design → "`task-reviews.md`".
- [ ] Add `agents/openai.yaml` (explicit-only).
- [ ] Specify state transitions the reviewer sets (`awaiting user review`, `task review failed — round N`, `blocked — spec issue`) and its `Spec-Review` commit.

### Verification

- `make skills-sync && make skills-check` pass.
- The skill text never tells the reviewer to edit code, tests, spec text or data.

## T3 — Update spec-implementer for one task per run

**State:** not started
**Requirements:** R1, R2, R9, R10

- [ ] Accept `<NNN-spec> [task-id]`; without a task ID, take the first task whose state needs implementation.
- [ ] Work on `spec/<NNN>`; refuse to commit task work on `main`.
- [ ] Add the `Spec-Task` trailer to every commit; never rebase, amend or force-push.
- [ ] Set `implementing (round N)` at start and `in task review (round N)` at end; write the Implementation block in `task-reviews.md`, with the model used.
- [ ] On round > 1, implement only the latest round's findings or user feedback.
- [ ] Stop after one task; do not merge or push.
- [ ] Replace the whole-spec completion section with the per-task handoff; keep the material-decision, protected-path and `> BLOCKED:` rules.
- [ ] Replace the reading list with the design's minimal list.

### Verification

- `make skills-sync && make skills-check` pass.
- The skill contains no instruction to implement more than one task per run, or to set the retired statuses.

## T4 — Create the spec-orchestrator skill

**State:** not started
**Requirements:** R4, R5, R6, R9, R10, R11

- [ ] Add `agent-skills/spec-orchestrator/SKILL.md`: minimal reading list, never reads code or diffs, never writes spec content.
- [ ] Add `references/state-machine.md` with the decision procedure (design → "Orchestrator decision procedure") and the state table.
- [ ] Define how to start roles: a fresh session on the preferred model where the host supports it; otherwise print the exact command and intended model.
- [ ] Define user interaction: relay the reviewer's summary, record approval/feedback verbatim in `task-reviews.md` and the `State:` line, `Spec-Decision` commit, push `spec/<NNN>` after approval.
- [ ] Define routing: implementation feedback → implementer; spec feedback / `SPEC_DEFECT` → `blocked — spec issue` + planner; 2 consecutive FAILs → escalate.
- [ ] Define spec completion: `all tasks approved`, optional retrospective offer, `--no-ff` merge, `make verify`, push, `verified (…, merged <sha>)`, `CURRENT_STATE.md` update.
- [ ] Define the failure behaviors in design → "Error and failure behavior" (dirty tree, interrupted roles, conflicts, push rejection).
- [ ] Add `agents/openai.yaml` (explicit-only).

### Verification

- `make skills-sync && make skills-check` pass.
- Every state in the state table has exactly one next action in `state-machine.md`.

## T5 — Adjust spec-reviewer and spec-planner

**State:** not started
**Requirements:** R7, R8, R10

- [ ] `spec-reviewer`: optional retrospective on `main...spec/<NNN>` and `task-reviews.md`; focus on cross-task concerns; write a "Notes for the next spec" section; no longer sets `verified`; findings that need code become `RM` tasks that run through the task loop.
- [ ] Update `spec-reviewer/assets/review-report-template.md` and `references/review-checklist.md` to match.
- [ ] `spec-planner`: read the previous spec's latest "Notes for the next spec"; write `**State:** not started` under every task; use the new `tasks.md` status values.
- [ ] Update `spec-planner/assets/tasks-template.md` to include the `State:` line.

### Verification

- `make skills-sync && make skills-check` pass.
- `grep -rn "implemented — pending review" agent-skills/` returns no instruction to set it.

## T6 — Model preferences, sync script and skills README

**State:** not started
**Requirements:** R9, R11

- [ ] Add `spec-orchestrator` (BEST_MINUS_ONE) and `task-reviewer` (BEST) to `agent-skills/MODEL_PREFERENCES.md`; state that no skill switches models mid-session.
- [ ] Update `HOST_FRONTMATTER` in `scripts/sync_agent_skills.py` per design → "Host frontmatter"; remove `context: fork` / `background: false` from `spec-reviewer`.
- [ ] Rewrite `agent-skills/README.md` for five skills, the loop and per-host usage.
- [ ] Regenerate the mirrors.

### Verification

- `make skills-sync && make skills-check` pass.
- `grep -rn "^model:" .claude/skills/ agent-skills/` returns nothing.

## T7 — Token-efficient context and project docs

**State:** not started
**Requirements:** R10, R12

- [ ] Trim `CLAUDE.md` to import only `@AGENTS.md` and `@docs/project/CURRENT_STATE.md`, keeping a pointer to the other docs.
- [ ] Make `AGENTS.md` "Read first" role-based and update its spec-driven steps to the new loop.
- [ ] Update `docs/project/COMMANDS.md` with the per-host skill commands.
- [ ] Renumber specs in `docs/project/ROADMAP.md`/`WORKFLOW.md` so ingestion is 004, and add 003 to Phase 0.

### Verification

- `CLAUDE.md` contains exactly two `@` imports.
- `make verify` passes.

## T8 — Migrate Spec 002 to the new state format

**State:** not started
**Requirements:** R7, R12

- [ ] Set Spec 002 `tasks.md` status to `implementing (branch spec/002, base 5bbb333)`.
- [ ] Add `**State:** approved (2026-10-14)` to T1 and T2, with a note that they predate task review.
- [ ] Add `**State:** not started` to T3–T9 without changing checkbox text.
- [ ] Update `docs/project/CURRENT_STATE.md`: Spec 002 paused after T2, resuming under the new flow; Spec 003 in progress.

### Verification

- `git diff` on Spec 002 `tasks.md` shows only added `State:` lines and the status change.
- `make verify` passes.

## T9 — Acceptance dry run on Spec 002 T3

**State:** not started
**Requirements:** R13

- [ ] Run `spec-orchestrator`: it creates `spec/002` from `main` and starts `spec-implementer` for 002 T3 on BEST_MINUS_ONE.
- [ ] `spec-implementer` completes 002 T3 (one or more rounds) with `Spec-Task: 002/T3` commits.
- [ ] `task-reviewer` reviews 002 T3 on BEST and records the result in `.kiro/specs/002-document-model-and-repository/task-reviews.md`.
- [ ] The orchestrator shows the user the summary; the user's decision is recorded and `spec/002` is pushed on approval.
- [ ] Fix every workflow defect found during the run in the skills/docs on `main`, and note it in this task.

### Verification

- 002 T3 state is `approved (YYYY-MM-DD)`.
- `task-reviews.md` contains Implementation, Review and User decision blocks for 002 T3.
- `git ls-remote origin spec/002` shows the pushed branch.

## T10 — Final verification and handoff

**State:** not started
**Requirements:** Definition of Done

- [ ] Run `make verify`.
- [ ] Check that every skill uses the same state/status values as `WORKFLOW.md`.
- [ ] Update `docs/project/CURRENT_STATE.md` with implemented reality.
- [ ] Set this file's status to `verified (YYYY-MM-DD, merged <sha>)` after user approval (bootstrap: no spec branch, so `<sha>` is the final commit on `main`).

### Verification

- `make verify` passes; results recorded in the handoff.
