# Development Workflow

## Style

This project uses specification-driven development for non-trivial features.

Canonical flow (task-gated loop, Spec 003):

```text
idea
  ↓
spec-planner (BEST)         Decision Brief → requirements → design → tasks, each approved by the user
  ↓
spec-orchestrator           routes every step from repository state; never reads code
  ↓
spec-implementer            one task per run, on branch spec/<NNN>
  ↓
task-reviewer (BEST)        verifies that task, PASS/FAIL, writes a user summary
  ├─ FAIL (IMPLEMENTATION) → implementer, next round (max 2 consecutive FAILs, then user)
  ├─ FAIL (SPEC_DEFECT)    → blocked — spec issue → spec-planner "revise an approved spec"
  ▼ PASS
user                        approves, or gives feedback (implementation → implementer, spec → planner)
  ↓ approved → orchestrator pushes spec/<NNN>; next task
all tasks approved
  ↓ [optional] spec-reviewer retrospective (review.md, "Notes for the next spec")
orchestrator merges spec/<NNN> into main (--no-ff) → verified
```

Skills live in `agent-skills/` and are mirrored to `.claude/skills/`, `.agents/skills/` (Codex) and `.kiro/skills/`. See `agent-skills/README.md`. Contributors not using the skills follow the same steps, states and trailers.

Roles run in fresh contexts (the orchestrator spawns them as subagents where the host allows, otherwise the user starts them) and hand off through repository files (`tasks.md`, `task-reviews.md`, commit trailers), not chat. Model tiers are advisory and applied when a session starts, never switched mid-session (`agent-skills/MODEL_PREFERENCES.md`).

The specification is part of the implementation contract.

## Feature specs

Store specs under:

```text
.kiro/specs/<feature>/
  requirements.md
  design.md
  tasks.md
```

Recommended initial sequence:

1. project foundation;
2. document model + DocumentRepository;
3. task-gated agent workflow (003, process work);
4. local ingestion pipeline;
5. dense retrieval baseline;
6. evaluation framework;
7. BM25 + hybrid/RRF;
8. structure-aware chunking;
9. multilingual retrieval;
10. reranking + context builder;
11. grounded generation + citations;
12. observability;
13. security + authorization regression;
14. graceful degradation;
15. AWS/Terraform deployment;
16. CI/CD + evaluation gates;
17. recruiter demo/RAG Lab.

Create specs progressively.

## Spec status

Approval, task and review state are recorded in the repository, never only in chat.

Each spec file starts with a `Status:` line under its title.

| File | Allowed values |
|---|---|
| `requirements.md`, `design.md` | `draft` · `approved (YYYY-MM-DD)` |
| `tasks.md` | `draft` · `approved (YYYY-MM-DD)` · `implementing (branch spec/<NNN>, base <sha>)` · `all tasks approved (YYYY-MM-DD)` · `verified (YYYY-MM-DD, merged <sha>)` |

Retired values (kept only in the history of Specs 001–002): `implemented — pending review (…)`, `review failed — round N (…)`, `verified (…, review round N)`.

Rules:
- A spec is ready for implementation only when all three files are `approved`.
- Only a human approves. Agents set `approved` only after explicit approval and record the date.
- The base SHA is the commit the spec branch was created from.
- `all tasks approved` is set by the orchestrator when every task is `approved`; the optional retrospective and the merge follow.
- A spec is **verified** when every task is approved and `spec/<NNN>` is merged into `main`. A final `spec-reviewer` run is not required.
- Approved amendments are recorded as dated lines in `## Change log` at the end of `requirements.md`.
- Specs completed before this lifecycle (001) carry only a `tasks.md` status explaining that.

### Task state

Directly under each task heading in `tasks.md`, above the checkboxes, a `**State:**` line. Checkbox text is never changed (Kiro's `tasks.meta.json` is keyed by it).

| State | Set by | Next action |
|---|---|---|
| `not started` | planner | implementer, round 1 |
| `implementing (round N)` | implementer at start | implementer resumes round N |
| `in task review (round N)` | implementer at end | task-reviewer |
| `task review failed — round N` | task-reviewer | implementer, round N+1 (if N < 2), else orchestrator escalates to the user |
| `awaiting user review (round N)` | task-reviewer on PASS | orchestrator shows the summary and asks the user |
| `changes requested — round N` | orchestrator (user feedback) | implementer, round N+1 |
| `approved (YYYY-MM-DD)` | orchestrator (user approval) | next task, or spec completion |
| `blocked — spec issue` | any role | user + `spec-planner` revise flow |

Rounds count implementer runs for a task. The automatic limit counts consecutive reviewer `FAIL`s; a user "changes requested" resets it. A task re-opened by a spec amendment returns to `not started`, recorded in the change log.

### Branching and commits

- One branch per spec: `spec/<NNN>` (e.g. `spec/002`), created from up-to-date `main` by the orchestrator before the first task.
- **Task work is committed and pushed only after the user approves it.** The implementer and task reviewer never commit; the task's changes (and its `tasks.md` / `task-reviews.md` updates) stay uncommitted through every round.
- Task diff for review: `git status --porcelain` and `git diff HEAD -- . ':(exclude).kiro/specs/*/task-reviews.md'`, plus untracked files.
- On approval the orchestrator makes one commit for the task, ending with the trailer `Spec-Task: <NNN>/<task-id>` (`T3`, `RM1.2`), and pushes `spec/<NNN>`. Find it later with `git log --grep='^Spec-Task: 002/T3$'`.
- While a task is in progress nobody stashes, resets or switches branches. Never rebase, amend or force-push a pushed spec branch.
- Completion: `git merge --no-ff spec/<NNN>` into up-to-date `main`, `make verify`, push `main`. Conflicts or failures abort the merge and go to the user.
- Specs predating this flow (001, 002 T1–T2) stay on `main`.

### `task-reviews.md`

`.kiro/specs/<spec>/task-reviews.md` is append-only, newest at the bottom, created on the first task run. Per task and round (template: `agent-skills/task-reviewer/assets/task-review-template.md`):

```markdown
## T3 — round 1

### Implementation
- Model: <model id>
- Files changed: <paths>
- Verification run: `make verify` → pass (N tests)
- Notes: <decisions, deviations, open questions>
- Usage: <tokens, e.g. 180K or 1.2M> tokens · <tool uses> tool uses · <duration> (recorded by the orchestrator; `not measured` if the role ran outside it)

### Review
- Model: <model id>
- Verdict: PASS | FAIL
- Commands: `make verify` → pass (N tests, M collected integration); `<task check>` → pass
- Findings: F1 [MAJOR, IMPLEMENTATION, R5] <what> → <expected fix> (none on PASS)
- Summary for user (PASS only):
  - Changed: ...
  - Verified by: ...
  - Worth your attention: ...
- Usage: <tokens, e.g. 180K or 1.2M> tokens · <tool uses> tool uses · <duration> (recorded by the orchestrator; `not measured` if the role ran outside it)

### User decision
- 2026-10-14 — approved | changes requested: "<feedback verbatim>" | spec issue: "<feedback>"
```

The Implementation block is written by the implementer, Review by the task-reviewer, User decision by the orchestrator. The reviewer may read the Implementation block for orientation but never treats it as evidence. Findings of a failed round are the remediation items; they are not added to `tasks.md`.

### Optional retrospective

`spec-reviewer` may run after `all tasks approved`. It reviews cross-task concerns, appends a `## Round N` to `review.md` with "Notes for the next spec", and may add `RM<N>.<k>` tasks to `tasks.md`; those run through the same implement → task review → user loop.

## Requirements

Requirements describe **what must be true**, not implementation details.

Use explicit acceptance criteria.

## Design

Design describes:
- interfaces;
- components;
- data flow;
- error behavior;
- storage choices;
- security constraints;
- observability;
- testing strategy;
- alternatives/tradeoffs where relevant.

## Tasks

Tasks should be small enough that one coding agent can implement and verify them without broad interpretation.

Examples:
- create Pydantic model;
- implement Protocol;
- implement local adapter;
- add schema validation;
- add unit test;
- add integration test.

## Implementation rule

If implementation reveals a problem with approved requirements/design:

1. stop expanding implementation;
2. note it under the affected task in `tasks.md` as `> BLOCKED: spec issue — ...`;
3. revise the spec (`spec-planner` → "revise an approved spec") and get human approval;
4. record the amendment in the spec's `## Change log`;
5. continue only after the spec is correct.

Do not silently change architecture.

## Protected source-of-truth data

Implementation work must not create, edit, re-version or delete files under `evaluation/`, `knowledge/` or `config/` unless an approved task explicitly requires it.

Never change evaluation cases or knowledge to make tests or metrics pass. Agent-written evaluation cases start as `status: suggested` and need human approval (Constitution C6).

Do not edit Kiro's `tasks.meta.json`. It is keyed by exact task text, so avoid rewording completed tasks.

## Verification layers

### Fast local checks
- formatting/lint;
- type checking;
- unit tests;
- JSON/YAML/schema validation;
- knowledge metadata validation.

### Integration checks
- local Qdrant;
- repository/ingestion integration;
- retrieval behavior;
- authorization filters;
- citation validation.

### RAG evaluation
- Recall@5;
- MRR;
- HitRate@5;
- multilingual slices;
- refusal behavior;
- security regression;
- later generation metrics.

### CI
CI should strongly gate deterministic failures.

Stochastic/LLM-judge metrics should normally be warnings/reporting unless an active spec explicitly defines a stable gate.

## Multi-agent handoff

The repository is the handoff medium between Codex, Claude Code and Kiro.

Before ending substantial work:

1. update active spec tasks;
2. run relevant verification;
3. update `docs/project/CURRENT_STATE.md`;
4. update `docs/project/DECISIONS.md` for meaningful decisions;
5. leave future work as explicit spec tasks/TODOs, not hidden chat context.

Another coding agent should be able to continue from:
- Git state;
- `AGENTS.md`;
- current project docs;
- active spec.

## Git practices

One commit per approved task; see "Branching and commits". State changes and `task-reviews.md` are committed with the work they describe.

Do not commit:
- secrets;
- `.env`;
- generated credentials;
- local vector indexes;
- model caches;
- large temporary artifacts unless intentionally versioned.

## Phase discipline

Phase 1 stays focused on the one-week production-oriented RAG project.

Do not pull Phase 2 Knowledge Operations into Phase 1 beyond:
- stable IDs;
- version fields;
- DocumentRepository abstraction;
- lightweight release identifiers;
- compatible telemetry fields.
