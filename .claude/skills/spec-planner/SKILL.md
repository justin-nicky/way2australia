---
name: spec-planner
description: Create or revise one major Way2Australia AI project spec under .kiro/specs/. Use for requirements, design, acceptance criteria and task planning, or to amend an approved spec when implementation reveals a problem. Inspects repository context first, asks only material questions, briefs the user on decisions and tradeoffs, and records each staged approval (requirements, design, tasks) in the spec files themselves.
---

# Spec Planner

## Model tier

Intended tier: **BEST**. See `agent-skills/MODEL_PREFERENCES.md` at the repository root. Tiers are advisory: if the host cannot switch models, tell the user which model is intended and continue.

Model check, before anything else: compare the model you are running on (from your system prompt) with the tier's model in `MODEL_PREFERENCES.md`. If they differ, tell the user which model is intended and ask whether to continue or switch first.

## Purpose

Create or revise one coherent major spec:

```text
.kiro/specs/<NNN-feature-name>/
├── requirements.md
├── design.md
└── tasks.md
```

Do not implement production code while using this skill.

Spec status values, task `State:` values and the task-gated loop are defined in `docs/project/WORKFLOW.md` → "Spec status". Follow them exactly; do not invent new states.

## Spec sizing

A spec represents one major roadmap capability, not a tiny edit and not several unrelated systems. Typical Phase 1 units: foundation, document repository, ingestion, dense retrieval, evaluation, hybrid retrieval, chunking, multilingual retrieval, reranking, generation/citations, observability, security, graceful degradation, deployment, CI/CD, recruiter demo.

`docs/project/ROADMAP.md` is the authority for scope and sequencing. Use the master plan (`Way2Australia_AI_Platform_Implementation_Plan.md`) only if it is committed to the repository; never rely on an uncommitted local copy.

## Mode selection

- **New spec** → follow "Workflow: new spec".
- **Revise an existing spec** (a problem found during implementation or review, or a user-requested change) → follow "Workflow: revise an approved spec".

## Workflow: new spec

### 1. Establish repository truth

Before asking questions, read enough context to avoid making the user repeat decisions:

- the `AGENTS.md` "Read first" list (mission, constitution, tech stack, roadmap, current state) plus `docs/project/DECISIONS.md` and `docs/project/ARCHITECTURE.md`;
- relevant `docs/knowledge/*`;
- existing `.kiro/specs/*`, and the latest "Notes for the next spec" in the previous spec's `review.md`, when present;
- relevant code/tests/config.

Do not rely on private chat history as required project context.

### 2. Ask only material questions

Ask only unresolved questions that can materially change scope, architecture, public contracts, security/authorization, data model, persistence, provider/model choice, reliability, observability, evaluation/acceptance criteria, cost/latency tradeoffs, or the Phase 1 / Phase 2 boundary.

Do not ask trivial implementation details or questions the repository already answers.

Prefer one compact batch of questions. Follow up only if answers expose another material dependency.

### 3. Decision Brief — approval gate 1

Present a concise Decision Brief:

- proposed spec number and name;
- objective and why this is the right next unit;
- in scope / explicitly out of scope;
- decisions already locked / resolved with the user;
- meaningful alternatives and tradeoffs;
- dependencies;
- expected verification/evaluation approach;
- risks/assumptions;
- proposed high-level implementation sequence.

Ask for explicit approval. Do not write spec files before this approval.

After approval, the brief's resolved decisions go into `requirements.md` (Goal, Dependencies, Out of scope) so they are not lost in chat.

### 4. Requirements — approval gate 2

Draft `requirements.md` from [requirements-template.md](assets/requirements-template.md) and **write it to disk immediately** with `Status: draft`.

Rules:
- describe **what must be true**, not low-level coding steps;
- stable IDs (`R1`, `R2`, ...);
- testable acceptance criteria;
- explicit out-of-scope items;
- Definition of Done;
- traceability table (filled in at step 6);
- preserve project terminology and constitutional constraints.

Present the requirements for review. On explicit approval, change the header to `Status: approved (YYYY-MM-DD)`.

Do not proceed to design until requirements are approved.

### 5. Design — approval gate 3

Draft `design.md` from [design-template.md](assets/design-template.md), write it with `Status: draft`.

Cover only relevant areas: components/interfaces, package/file placement, data models, data flow, concurrency, storage, error/failure behavior, security/authorization, observability, testing/evaluation, Phase 2 compatibility/migration, alternatives/deferred decisions.

Do not silently introduce requirements that were not approved.

Present the design. On explicit approval, set `Status: approved (YYYY-MM-DD)`.

### 6. Tasks — approval gate 4

Create **all implementation tasks for this spec together** in `tasks.md` from [tasks-template.md](assets/tasks-template.md), with `Status: draft`.

Each task:
- is a meaningful implementation unit;
- is dependency ordered;
- lists the requirement IDs it satisfies (`**Requirements:** R1, R3`);
- has subtasks and a verification block that names real commands or checks;
- carries `**State:** not started` directly under its heading (above `**Requirements:**`).

Include final spec-wide verification, documentation and handoff work. Explicitly prevent work that belongs to the next spec.

Fill the traceability table in `requirements.md` (Requirement → Task(s) → Verification). Every requirement maps to at least one task; no orphan tasks.

Present the tasks. On explicit approval, set `tasks.md` to `Status: approved (YYYY-MM-DD)`. The spec is now ready for `spec-implementer`.

Verification commands must exist in the `Makefile` or be created by a task in this spec. `docs/project/COMMANDS.md` is the target interface; several of its targets are not implemented yet.

## Workflow: revise an approved spec

Use this when an implementer or reviewer reports a spec defect, or the user requests a change. Skip the Decision Brief for small amendments; use the full new-spec flow if the change alters the spec's objective or scope boundary.

1. Read the current spec files, `tasks.md` status, task `State:` lines, and any `review.md`, `task-reviews.md` findings or `> BLOCKED:` notes.
2. Present a change note: what changes, why, affected `R#`/`T#`, which checked tasks must be re-opened.
3. Get explicit approval.
4. Edit only the affected sections.
5. Append one dated line to `## Change log` in `requirements.md` (e.g. `- 2026-10-14 — R5: manifest mismatch is an error, not a warning (found during T3). Re-opened T3.`).
6. Set each edited file to `Status: approved (YYYY-MM-DD)` with the new date. Uncheck tasks whose acceptance criteria changed, set their `**State:**` to `not started` (or, if the task already has uncommitted work from earlier rounds, `task review failed — round N` with N its last round, so the next round continues it), and remove any `> BLOCKED:` note you resolved.
7. Hand back to `spec-orchestrator` (or `spec-implementer` for the re-opened task).

Never rewrite requirements/design merely so that existing code passes.

## Host notes

- **Kiro:** do not use Quick Spec / auto-generated specs in this repo — they skip these approval gates. Invoke `/spec-planner` instead. Kiro's spec format uses EARS notation; this repo does not require it.
- Do not edit Kiro's `tasks.meta.json`. It is keyed by exact checkbox text, so prefer adding tasks over rewording completed ones.

## Quality bar

Before requesting tasks approval, check [spec-quality-checklist.md](references/spec-quality-checklist.md).

## Final handoff

Report:
- spec path and the status of each file;
- scope summary;
- approved decisions;
- number of tasks;
- prerequisites;
- expected implementation tier: **BEST_MINUS_ONE**;
- readiness for `spec-orchestrator` / `spec-implementer`.
