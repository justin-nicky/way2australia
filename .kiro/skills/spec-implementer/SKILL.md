---
name: spec-implementer
description: Implement exactly ONE task of an approved Way2Australia AI spec under .kiro/specs/ (e.g. "002-document-model-and-repository T3") on branch spec/<NNN>, then stop for task review. Use only when the spec's three files are approved and the task's State needs implementation.
---

# Spec Implementer

## Model tier

Intended tier: **BEST_MINUS_ONE** (`agent-skills/MODEL_PREFERENCES.md`). Tiers are advisory and applied when a session starts; never switch models mid-session. Record the model actually used.

Model check, before anything else: compare the model you are running on (from your system prompt) with the tier's model in `MODEL_PREFERENCES.md`. If they differ, tell the user which model is intended and ask whether to continue or switch first; when started as a subagent with no user to ask, note the mismatch in your `task-reviews.md` block and continue.

## Purpose

Implement one task (or one round of rework for it), then stop. Never start a second task. Lifecycle, states and trailers: `docs/project/WORKFLOW.md` → "Spec status" and "Branching and commits".

Input: `<NNN-spec> [task-id]`. If no spec is named, stop and ask. Without a task ID, take the first task whose State is `not started`, `implementing (…)`, `task review failed — round N` or `changes requested — round N`.

## 1. Read only this

- the task block in `tasks.md`, its R# sections in `requirements.md`, the design sections it references, and `## Change log`;
- the task's latest round in `task-reviews.md` (findings or user feedback), if any;
- the code and tests you will touch.

Read `CONVENTIONS.md`, `DECISIONS.md`, `COMMANDS.md` only when needed.

## 2. Check readiness

Proceed only if:
- `requirements.md`, `design.md` and `tasks.md` are `Status: approved (…)` or `tasks.md` is `implementing (…)`;
- the task's State allows a run (above) and it has no `> BLOCKED:` note;
- you are on `spec/<NNN>` (`git branch --show-current`); the orchestrator creates the branch. The tree is clean for round 1; on rework it holds this task's uncommitted earlier rounds. Otherwise stop and report.

Round N is 1 for `not started`; for rework it is the previous round + 1. Set `**State:** implementing (round N)` before editing.

## Material-decision rule

Ask before changing: public interfaces/contracts; architecture/package boundaries; persistence/storage; security/authorization; source-of-truth behavior; evaluation semantics; provider/model strategy; significant dependencies; the Phase 1/Phase 2 boundary; meaningful latency/cost/reliability tradeoffs. For small internal choices, pick a simple option and continue.

## Protected source-of-truth data

Do not create, edit, re-version or delete files under `evaluation/`, `knowledge/` or `config/` unless this task explicitly requires it. Never change evaluation cases or knowledge to make tests or metrics pass. Agent-written evaluation cases are candidates only (`status: suggested`, Constitution C6). If a change seems necessary, stop and ask.

## When the spec is wrong

If implementation reveals a contradiction, missing decision or incorrect requirement/design:

1. stop expanding implementation in the affected area;
2. add `> BLOCKED: spec issue — <what and why>` under the task and set `**State:** blocked — spec issue`;
3. tell the user to take it to `spec-planner` ("revise an approved spec").

Never silently make code and spec agree after the fact.

## 3. Implement the task

1. Inspect existing code before creating abstractions.
2. Implement the minimum complete solution; add or update tests with the behavior.
3. Run the narrowest verification as you go, then the task's verification block and `make verify`.
4. Tick the task's checkboxes only after verification. Never reword checkbox text; never edit `tasks.meta.json`.
5. On round > 1, implement only the latest round's findings or user feedback.

Prefer plain, explicit code and existing tooling. Do not add a framework the stack did not select (`docs/project/TECH_STACK.md`). Preserve `AGENTS.md` rules: no secrets, authorization before LLM context (including fallbacks), documents only through `DocumentRepository`, language never broadens authorization, retrieved content is untrusted. Do not build future systems; record other-roadmap ideas as deferred items.

A checked box means implemented and verified. Never tick with failing tests, unmet criteria or unrun required checks. Use `make` targets; if a listed command is missing, say so. `make test-integration` exits 0 when nothing is collected, so report "no integration tests collected". Never claim an unrun check.

## 4. Finish

1. Append the Implementation block for this round to `<spec>/task-reviews.md` (create the file if missing; format in `WORKFLOW.md` → "`task-reviews.md`"): model, files changed, verification run with test counts, notes on decisions/deviations.
2. Set `**State:** in task review (round N)`.
3. Do not commit, push or merge. Leave all changes uncommitted; the orchestrator commits and pushes them only after the user approves. Never stash, reset or switch branches.
4. Update `docs/project/CURRENT_STATE.md` only if the task says so.

## Final message

Task and round, files changed, verification commands and results, what was not verified, decisions, deferred items, host and model used. Say that `task-reviewer` runs next, in a fresh session. Do not review your own work.
