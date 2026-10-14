---
name: spec-reviewer
description: Optional end-of-spec retrospective for one Way2Australia AI spec under .kiro/specs/, named by the user, whose tasks are all approved. Reviews cross-task concerns (Definition of Done, consistency, scope drift) on main...spec/<NNN>, appends a round to review.md with "Notes for the next spec", and turns code-level findings into RM tasks.
---

# Spec Reviewer (optional retrospective)

## Model tier

Intended tier: **BEST** (`agent-skills/MODEL_PREFERENCES.md`). Tiers are advisory and applied when a session starts; never switch models mid-session. Record the model actually used. Run in a fresh session, not one that implemented the spec.

## Purpose

Per-task checks already happened in `task-reviewer`; do not repeat them. Review what no single task review sees. A spec is verified when every task is approved and the branch is merged, so this review is optional and never blocks verification. Lifecycle: `docs/project/WORKFLOW.md` → "Spec status".

Input: `<NNN-spec>` with `tasks.md` `Status: all tasks approved (…)`. Otherwise stop and report. Work only from the repository, not from chat or implementer summaries.

## 1. Read

- `AGENTS.md`, `docs/project/CONSTITUTION.md`, `ARCHITECTURE.md`, `DECISIONS.md`;
- the full spec (`requirements.md` with `## Change log`, `design.md`, `tasks.md`), `task-reviews.md`, earlier rounds in `review.md`;
- the delta: `git diff --stat main...spec/<NNN>`, then files as needed.

## 2. Review cross-task concerns

- **Definition of Done:** every item met; requirement → task → evidence traceability complete (`SATISFIED`, `PARTIAL`, `UNSATISFIED`, `NOT_VERIFIED`).
- **Consistency:** interfaces, naming, errors and tests agree across tasks; no duplicated or contradictory logic; docs match code.
- **Scope drift across the spec:** next-spec work, unapproved Phase 2, speculative abstractions, unrecorded spec edits (MAJOR).
- **Architecture and security:** package boundaries, authorization (including fallbacks), secrets, fixture isolation, retrieved-content trust.
- **Protected data:** `git diff --stat main...spec/<NNN> -- evaluation/ knowledge/ config/`; any change no task requires is BLOCKING.
- **Whole-spec checks:** run `make verify` and any spec-level command from the Definition of Done; record exact commands, results and collected counts.
- **Patterns in `task-reviews.md`:** repeated findings, escalations, models used.

Severity: BLOCKING (requirement, DoD, security or protected-data failure) · MAJOR · MINOR. Classify each as `IMPLEMENTATION` or `SPEC_DEFECT`. You do not fix anything.

## 3. Record

Append `## Round N` to `.kiro/specs/<spec>/review.md` using [review-report-template.md](assets/review-report-template.md); never delete earlier rounds. Include **Notes for the next spec**: lessons, deferred items, follow-up risks, decisions that affect upcoming specs. `spec-planner` reads these before drafting.

Findings:
- `IMPLEMENTATION` needing code: append `## Review remediation — round N` to `tasks.md` with unchecked `- [ ] RM<N>.<k> — <fix> (finding <id>, <R#>)` tasks, each with `**State:** not started`. Set the spec `Status:` back to `implementing (branch spec/<NNN>, base <sha>)`. They run through implementer → task-reviewer → user like any task (`Spec-Task: <NNN>/RM<N>.<k>`).
- `SPEC_DEFECT`: list for the user to take to `spec-planner`.
- MINOR: record under known issues in `CURRENT_STATE.md`.

Commit `review.md` and any `tasks.md` / `CURRENT_STATE.md` changes with trailer `Spec-Review: <NNN>/retrospective` on `spec/<NNN>`. Do not merge or push; the orchestrator does after the user's go-ahead.

Final message: findings summary, RM tasks added (if any), and whether merging can proceed.

Use [review-checklist.md](references/review-checklist.md).
