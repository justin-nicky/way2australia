# 003 — Task-Gated Agent Workflow Requirements

Status: approved (2026-10-17)

## Goal

Replace the current "implement the whole spec, then review it once" flow with a token-efficient, task-gated loop:

```text
spec-orchestrator (BEST_MINUS_ONE) ── routes every step, never reads code
  │
  ├─ spec-planner      (BEST)            discuss with user → requirements/design/tasks
  ├─ spec-implementer  (BEST_MINUS_ONE)  one task per run, on the spec branch
  ├─ task-reviewer     (BEST)            verifies that task, summarizes it for the user
  ├─ user              approves the task or gives feedback
  └─ spec-reviewer     (BEST, optional)  end-of-spec retrospective + notes for the next spec
```

Every task is verified by a strong model before the user sees it. Each role runs from a small, file-based brief instead of chat history.

This is Phase 0 process work ("SDD workflow" in `docs/project/ROADMAP.md`). It changes no product code.

Decisions resolved with the user (2026-10-14):
- the implementer stops after each task;
- the task reviewer is read-only and records results in `task-reviews.md`;
- one branch per spec; the user approves tasks one by one; the branch merges to `main` when the spec is complete;
- model tiers stay advisory (no model pinning in skill frontmatter);
- the orchestrator runs on BEST_MINUS_ONE;
- the end-of-spec review becomes optional;
- `CLAUDE.md` imports are trimmed for token efficiency;
- this spec is numbered 003; the roadmap's ingestion spec becomes 004;
- Spec 002 pauses after T2; its T3 is the acceptance dry run of this workflow. T1–T2 stay on `main` without retroactive task review.

## Dependencies

- Spec 001 complete.
- Existing skills `spec-planner`, `spec-implementer`, `spec-reviewer` and `scripts/sync_agent_skills.py` (D021).
- Spec 002 approved, T1–T2 merged on `main`.

## R1 — Spec branch

Implementation work for a spec happens on one branch per spec, not directly on `main`.

### Acceptance criteria

- the branch name is derived deterministically from the spec number (for example `spec/002`);
- task work is committed and pushed only after the user approves the task, as one commit carrying a `Spec-Task: <NNN>/<task-id>` trailer (task IDs include `T#` and remediation IDs);
- the commit for any approved task can be found from git history alone, without commit-message wording conventions;
- history on a pushed spec branch is never rewritten and never force-pushed.

## R2 — One task per implementer run

`spec-implementer` implements exactly one task (or one remediation item set for one task) per run, then stops.

### Acceptance criteria

- the run is invoked with a spec and a task ID, or the orchestrator supplies the next unchecked task;
- a run never starts a second task;
- at the end of a run the task's changes are left uncommitted on the spec branch and its state is "in task review";
- the implementer records the model it used in the task's handoff note;
- the existing rules still apply: approved spec required, material-decision rule, protected paths, `> BLOCKED:` spec-issue notes.

## R3 — Task reviewer

A new `task-reviewer` skill verifies one implemented task before the user sees it.

### Acceptance criteria

- reads only what the task needs: its requirement IDs and their acceptance criteria, the referenced design sections, the task's checklist and verification block, and the task's uncommitted changes;
- runs the task's verification commands and `make verify`, and records each command with its result and collected test counts;
- checks that every checked box is backed by code and tests, that the diff stays inside the task's scope, that protected paths (`evaluation/`, `knowledge/`, `config/`) are untouched unless the task requires them, and that the `AGENTS.md` architecture/security rules hold;
- is read-only for code, tests, specs and data: it writes only to `task-reviews.md` and the task's state line;
- gives exactly one verdict: `PASS` or `FAIL`;
- on `FAIL`, lists each finding with severity and classification (`IMPLEMENTATION` or `SPEC_DEFECT`);
- on `PASS`, produces a short change summary for the user: what changed, where, how it was verified, and any decisions or risks worth the user's attention;
- records the model it used;
- must not rely on the implementer's chat or handoff narrative as evidence.

## R4 — Automatic rework loop

Failed task reviews return to the implementer without involving the user, within a limit.

### Acceptance criteria

- `IMPLEMENTATION` findings become remediation items for that task and go back to `spec-implementer`;
- `SPEC_DEFECT` findings stop the loop and go to the user and `spec-planner`;
- after 2 consecutive `FAIL` verdicts on the same task, the loop stops and escalates to the user;
- each round is recorded in `task-reviews.md`.

## R5 — User approval gate per task

The user approves each task after it passes task review.

### Acceptance criteria

- the user sees the reviewer's change summary, not a raw diff, by default, together with the task's total token usage and a per-round, per-stage split with the model used (as measured by the orchestrator);
- approval is recorded in the repository (task state and `task-reviews.md`) with a date, never only in chat;
- user feedback is recorded and routed: implementation feedback to `spec-implementer`, spec feedback to `spec-planner` ("revise an approved spec");
- after approval, the spec branch is pushed to the remote;
- a task is never shown to the user as ready while its latest task review is `FAIL`.

## R6 — Orchestrator

A new `spec-orchestrator` skill decides and starts the next step.

### Acceptance criteria

- reads only `docs/project/CURRENT_STATE.md`, spec `Status:` lines, task state lines, and the latest `task-reviews.md` entry;
- determines the next action from repository state alone, so any agent can resume after an interruption;
- starts each role with a short brief naming the spec, task and files to read; on hosts that can start sessions with a chosen model it uses the role's preferred model, otherwise it prints the exact command and intended model for the user;
- never reads or edits product code or diffs and never writes spec content;
- merges and pushes only after recorded user approval; merges the spec branch into `main` with a merge commit only when every task is approved; never force-pushes;
- keeps `CURRENT_STATE.md` accurate at each transition.

## R7 — Task and spec state lifecycle

Task-level and spec-level state are recorded in the repository and form one defined lifecycle.

### Acceptance criteria

- each task carries a machine-readable state line in `tasks.md` that does not alter checkbox text (Kiro's `tasks.meta.json` is keyed by it);
- task states cover at least: not started, implementing, in task review, task review failed (round N), awaiting user review, approved, blocked (spec issue);
- the spec-level `Status:` values in `docs/project/WORKFLOW.md` are updated to match the new flow;
- a spec is **verified** when every task is approved and the spec branch is merged into `main`; a final review is not required;
- the lifecycle is defined in `docs/project/WORKFLOW.md` and every skill uses the same values.

## R8 — Optional spec retrospective

`spec-reviewer` becomes an optional end-of-spec review.

### Acceptance criteria

- it is not required for a spec to be verified;
- when run, it reviews cross-task concerns (Definition of Done, cross-task consistency, scope drift across the spec) rather than repeating per-task checks;
- it appends a round to `review.md`, including a "Notes for the next spec" section;
- `spec-planner` reads the latest notes for the next spec, when present, before drafting a new spec;
- findings that need code changes still go back through the implementer → task-reviewer → user loop.

## R9 — Advisory model tiers without in-session switching

Model choice stays advisory and is applied when a role starts, not mid-session.

### Acceptance criteria

- `agent-skills/MODEL_PREFERENCES.md` lists tiers for all five skills (orchestrator and task reviewer added);
- no skill instructs switching models inside an ongoing working session;
- the model actually used is recorded for every implementer run and every task review;
- no skill frontmatter pins a model.

## R10 — Token-efficient context loading

Fresh role sessions load only the context they need.

### Acceptance criteria

- `CLAUDE.md` imports only `AGENTS.md` and `docs/project/CURRENT_STATE.md`;
- each skill lists the minimal files it must read for its role, and reads further docs only when needed;
- handoffs between roles go through repository files (`tasks.md`, `task-reviews.md`, commit trailers), not long chat briefs;
- the orchestrator never loads code or diffs.

## R11 — Portability and mirrors

The workflow works in Claude Code, Codex and Kiro.

### Acceptance criteria

- the new skills live only in `agent-skills/` and are mirrored by `scripts/sync_agent_skills.py`;
- `make skills-check` passes;
- the implementer, task reviewer and spec reviewer stay explicit-invocation only on every host that supports that setting;
- on hosts without session-starting tools, the orchestrator's printed commands are sufficient to run the loop by hand.

## R12 — Documentation and decisions

Project docs describe the new flow as current reality.

### Acceptance criteria

- `docs/project/WORKFLOW.md` describes the new flow, lifecycle and branching;
- `docs/project/DECISIONS.md` records D023 (task-gated workflow), stating which parts of D022 it supersedes;
- `AGENTS.md` spec-driven steps, `agent-skills/README.md` and `docs/project/COMMANDS.md` match the new flow;
- `docs/project/ROADMAP.md`/`WORKFLOW.md` spec numbering reflects ingestion as 004;
- `docs/project/CURRENT_STATE.md` shows Spec 002 paused after T2 and resuming under the new flow.

## R13 — Acceptance dry run

The full loop is exercised once on real work before this spec is complete.

### Acceptance criteria

- Spec 002 T3 runs through orchestrator → implementer → task reviewer → user approval on branch `spec/002`;
- the run produces a `task-reviews.md` entry, a task state transition to approved, and a pushed spec branch;
- problems found in the dry run are fixed in the skills/docs before this spec is complete.

## Out of scope

- CI enforcement of the workflow (for example GitHub Actions checks on trailers or states);
- GitHub pull requests;
- pinning models through skill frontmatter or hooks;
- any product/RAG code change other than Spec 002 T3 during the dry run;
- retroactive task reviews of Spec 002 T1–T2;
- rewriting existing `review.md` content or past commits;
- changes under `evaluation/`, `knowledge/` or `config/`.

## Definition of Done

- `task-reviewer` and `spec-orchestrator` exist in `agent-skills/` and are mirrored;
- `spec-implementer`, `spec-reviewer`, `spec-planner` and `MODEL_PREFERENCES.md` match the new flow;
- `CLAUDE.md` is trimmed;
- `WORKFLOW.md`, `DECISIONS.md` (D023), `AGENTS.md`, `agent-skills/README.md`, `COMMANDS.md`, `ROADMAP.md` and `CURRENT_STATE.md` are updated;
- the Spec 002 T3 dry run completed through user approval;
- `make verify` passes;
- another agent can run the loop from repository files alone.

## Traceability

| Requirement | Task(s) | Verification |
|---|---|---|
| R1 | T1, T3 | WORKFLOW.md branching section; implementer skill trailer/branch rules; dry run commits (T9) |
| R2 | T3 | implementer skill review; dry run (T9) |
| R3 | T2 | task-reviewer skill review; dry run review block (T9) |
| R4 | T2, T4 | state machine: FAIL → implementer, 2-round escalation |
| R5 | T4 | dry run user decision block and pushed `spec/002` (T9) |
| R6 | T4 | `state-machine.md` covers every state; dry run (T9) |
| R7 | T1, T5, T8 | WORKFLOW.md state table; Spec 002 migration diff |
| R8 | T5 | spec-reviewer/planner skill review |
| R9 | T2, T3, T4, T6 | `MODEL_PREFERENCES.md`; no `model:` frontmatter; models recorded in dry run |
| R10 | T2, T3, T4, T7 | `CLAUDE.md` has two imports; skill reading lists |
| R11 | T2, T4, T6 | `make skills-check` |
| R12 | T1, T7, T8 | docs updated; `make verify` |
| R13 | T9 | dry run evidence (state, `task-reviews.md`, `git ls-remote`) |

## Change log

- 2026-10-14 — R1, R2, R3, R5, R6: task work stays uncommitted through implementation and review; the orchestrator commits it (one `Spec-Task` commit) and pushes only after user approval. Implemented directly in skills/docs; no task re-opened.
- 2026-10-15 — R5, R9: the orchestrator records each role's token usage in `task-reviews.md` and shows the user a per-task usage table (stage, model, tokens, total) with the review summary. Implemented directly in skills/docs; no task re-opened.
- 2026-10-17 — R8: the retrospective is required, not optional; it also reconciles project documentation with the code as built (D031). Implemented directly in skills/docs; no task re-opened.

<!-- Approved amendments only, one dated line each:
- YYYY-MM-DD — <R#/T#>: <what changed and why>. Re-opened <T#>. -->
