---
name: spec-reviewer
description: Required end-of-spec retrospective for one Way2Australia AI spec under .kiro/specs/, named by the user or started by spec-orchestrator, whose tasks are all approved. Reviews cross-task concerns on main...spec/<NNN>, reconciles project documentation with the implemented code, appends a round to review.md with "Notes for the next spec", and turns code-level findings into RM tasks.
---

# Spec Reviewer (required retrospective)

## Model tier

Intended tier: **BEST** (`agent-skills/MODEL_PREFERENCES.md`). Tiers are advisory and applied when a session starts; never switch models mid-session. Record the model actually used. Run in a fresh session, not one that implemented the spec.

Model check, before anything else: compare the model you are running on (from your system prompt) with the tier's model in `MODEL_PREFERENCES.md`. If they differ, tell the user which model is intended and ask whether to continue or switch first; when started as a subagent with no user to ask, note the mismatch in your `review.md` round and continue.

## Purpose

Per-task checks already happened in `task-reviewer`; do not repeat them. Review what no single task review sees, and make the documentation say the same thing as the code. A spec is verified only after a retrospective round with outcome `PASS`, the user's approval and the merge. Lifecycle: `docs/project/WORKFLOW.md` → "Spec status".

Input: `<NNN-spec>` with `tasks.md` `Status: all tasks approved (…)`. Otherwise stop and report. Work only from the repository, not from chat or implementer summaries.

## 1. Read

- `AGENTS.md`, `docs/project/CONSTITUTION.md`, `ARCHITECTURE.md`, `DECISIONS.md`, `TECH_STACK.md`, `COMMANDS.md`, `CURRENT_STATE.md`;
- the full spec (`requirements.md` with `## Change log`, `design.md`, `tasks.md`), `task-reviews.md`, earlier rounds in `review.md`;
- the delta: `git diff --stat main...spec/<NNN> -- . ':(exclude)graphify-out'`, then files as needed (`graphify-out/` is the regenerated knowledge graph, not spec work).

## 2. Review cross-task concerns

- **Definition of Done:** every item met; requirement → task → evidence traceability complete (`SATISFIED`, `PARTIAL`, `UNSATISFIED`, `NOT_VERIFIED`).
- **Consistency:** interfaces, naming, errors and tests agree across tasks; no duplicated or contradictory logic.
- **Deviations from the approved plan:** compare the code with `requirements.md` and `design.md`. Each deviation is either recorded in the `## Change log`, or noted in `task-reviews.md` and minor, or a finding (material and unrecorded: MAJOR).
- **Scope drift across the spec:** next-spec work, unapproved Phase 2, speculative abstractions, unrecorded spec edits (MAJOR).
- **Architecture and security:** package boundaries, authorization (including fallbacks), secrets, fixture isolation, retrieved-content trust.
- **Protected data:** `git diff --stat main...spec/<NNN> -- evaluation/ knowledge/ config/`; any change no task requires is BLOCKING.
- **Whole-spec checks:** run `make verify` and any spec-level command from the Definition of Done; record exact commands, results and collected counts.
- **Patterns in `task-reviews.md`:** repeated findings, escalations, models used, token usage.

Severity: BLOCKING (requirement, DoD, security or protected-data failure) · MAJOR · MINOR. Classify each as `IMPLEMENTATION` or `SPEC_DEFECT`. You never fix code.

## 3. Reconcile documentation

Make the docs describe the code as built. Edit documentation only:

- `docs/project/DECISIONS.md`: add a decision for each durable choice the spec made and nobody recorded (dependencies, contracts, IDs, formats, refusal rules). Never rewrite an existing decision: if the spec changed one, add a new entry that says which one it supersedes.
- `docs/project/TECH_STACK.md`: every new runtime or optional dependency, with its purpose.
- `docs/project/ARCHITECTURE.md`: new components, package placement and data flow.
- `docs/project/COMMANDS.md`: every new `make` target and command, as it actually behaves.
- `docs/project/CURRENT_STATE.md`: implemented reality only.
- Other docs the spec touched (`docs/knowledge/*`, `README.md`, `agent-skills/README.md`) where they now contradict the code.
- The spec's `design.md`: append or update `## As-built notes`, listing each deviation from the approved design, why, and where it was approved (change-log line or `task-reviews.md` round). Never edit requirements, the approved design text or task text.

Rules:
- Docs follow the code only where the code matches the approved spec or a recorded amendment. If the code contradicts the approved spec without one, do not document it as correct: record a finding instead.
- Never edit code, tests, `evaluation/`, `knowledge/`, `config/`, or `requirements.md`.
- List every documentation edit (file and one-line reason) in the round's "Documentation reconciled" section.

## 4. Record

Append `## Round N` to `.kiro/specs/<spec>/review.md` using [review-report-template.md](assets/review-report-template.md); never delete earlier rounds. Include **Notes for the next spec**: lessons, deferred items, follow-up risks, decisions that affect upcoming specs. `spec-planner` reads these before drafting.

Outcome:
- `PASS`: no BLOCKING or MAJOR finding, docs reconciled. MINOR findings go under known issues in `CURRENT_STATE.md`.
- `FAIL`: any BLOCKING or MAJOR finding.
  - `IMPLEMENTATION`: append `## Review remediation — round N` to `tasks.md` with unchecked `- [ ] RM<N>.<k> — <fix> (finding <id>, <R#>)` tasks, each with `**State:** not started`. Set the spec `Status:` back to `implementing (branch spec/<NNN>, base <sha>)`. They run through implementer → task-reviewer → user like any task (`Spec-Task: <NNN>/RM<N>.<k>`), and the retrospective runs again afterwards.
  - `SPEC_DEFECT`: list for the user to take to `spec-planner`.

Do not commit, push or merge. Leave `review.md`, documentation and any `tasks.md` / `CURRENT_STATE.md` changes uncommitted; the orchestrator commits them after the user approves.

Final message: outcome, findings summary, documentation edits, RM tasks added (if any), and whether merging can proceed.

Use [review-checklist.md](references/review-checklist.md).
