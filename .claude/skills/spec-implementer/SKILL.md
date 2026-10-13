---
name: spec-implementer
description: Implement exactly one approved Way2Australia AI spec under .kiro/specs/, named by the user (e.g. 002-document-model-and-repository). Use only when that spec's requirements.md, design.md and tasks.md all are marked approved in their Status line, or when the spec has a failed review with remediation tasks. Executes the unchecked approved tasks in dependency order, stays inside scope, verifies continuously, and leaves the spec pending independent review.
disable-model-invocation: true
argument-hint: <NNN-spec-name>
---

# Spec Implementer

## Model tier

Intended tier: **BEST_MINUS_ONE**. See `agent-skills/MODEL_PREFERENCES.md` at the repository root. Tiers are advisory: if the host cannot switch models, tell the user which model is intended and continue. Record the model actually used in the handoff.

## Purpose

Implement one complete approved spec faithfully. Do not work on multiple specs in parallel.

The active spec is the one the user names when invoking this skill. If none is named, or it is ambiguous, stop and ask. Do not pick a spec yourself.

Spec status values and the review/remediation lifecycle are defined in `docs/project/WORKFLOW.md` → "Spec status".

## 1. Establish implementation context

Read:
- the `AGENTS.md` "Read first" list, plus `docs/project/DECISIONS.md` and `docs/project/COMMANDS.md`;
- the active spec's `requirements.md`, `design.md`, `tasks.md` and, if present, `review.md`;
- relevant code/tests/config and knowledge/schema docs.

Before editing, briefly state: active spec, file statuses, approved scope, task order, expected verification, known prerequisites/blockers.

Do not reopen approved architecture merely because another implementation seems interesting.

## 2. Validate spec readiness

Proceed only if one of these holds:
- all three spec files have `Status: approved (...)` and `tasks.md` has unchecked tasks; or
- `tasks.md` has `Status: review failed — round N` and unchecked `RM<N>.x` remediation tasks.

Otherwise stop and report what is missing (e.g. "design.md is draft — run spec-planner"). Never mark a spec approved yourself.

Also confirm dependencies are met and the repository state does not contradict the spec.

When starting, set `tasks.md` to `Status: implementing (base <short-sha>)`, using the commit you start from. The reviewer diffs from this base.

## Material-decision rule

Ask before changing:
- public interfaces/contracts;
- architecture/package boundaries;
- persistence/storage model;
- security/authorization;
- source-of-truth behavior;
- evaluation semantics;
- provider/model strategy;
- significant dependency choice;
- Phase 1/Phase 2 boundary;
- meaningful latency/cost/reliability tradeoff.

For small internal choices, choose a clear, simple implementation and continue.

## Protected source-of-truth data

Do not create, edit, re-version or delete files under these paths unless an approved task explicitly requires that change:

- `evaluation/` (datasets, suites, schemas);
- `knowledge/` (documents, manifest, inventory, releases, schemas);
- `config/` (access policy, source precedence, language registry).

Never change evaluation cases or knowledge to make tests or metrics pass. Agent-written evaluation cases are candidates only (`status: suggested`) and need human approval (Constitution C6). If such a change seems necessary, stop and ask.

## When the spec is wrong

If implementation reveals a material contradiction, missing decision or incorrect requirement/design (`docs/project/WORKFLOW.md` → "Implementation rule"):

1. stop expanding implementation in the affected area;
2. add a note under the affected task in `tasks.md`: `> BLOCKED: spec issue — <what and why>`;
3. ask the user to approve a revision through `spec-planner` ("revise an approved spec");
4. resume only after the revision is recorded in the spec's `## Change log`.

Never silently make code and spec agree after the fact.

## 3. Implement task by task

For each task:

1. Re-read the requirement/design references it lists.
2. Inspect existing code before creating abstractions.
3. Implement the minimum complete solution.
4. Add or update tests together with the behavior.
5. Run the narrowest relevant verification immediately.
6. Fix task-local failures before moving on.
7. Mark the task/subtasks complete only after verification.
8. Commit the task (small commits aligned with tasks; `docs/project/WORKFLOW.md` → "Git practices"). Never commit secrets, `.env`, local indexes, model caches or generated artifacts.

Prefer simple explicit code and existing project abstractions/tooling. Do not introduce a framework/library the stack did not select (`docs/project/TECH_STACK.md`) merely to save a few lines.

Do not reword completed checkbox text: Kiro's `tasks.meta.json` is keyed by it. Do not edit `tasks.meta.json`.

## One-spec-at-a-time rule

The full active spec is the current work unit. If a discovered improvement belongs to another roadmap section, do not implement it now. Record it as a deferred item in the handoff and continue.

## Remediation rounds

If `tasks.md` has `Status: review failed — round N`:
- read the latest round in `review.md`;
- implement only the unchecked `RM<N>.x` tasks (plus anything they strictly require);
- `SPEC_DEFECT` items go to `spec-planner`, not into code;
- finish with the same verification and handoff as a normal run.

## Verification

Use the `Makefile` targets (`make verify`, `make test`, `make test-unit`, `make test-integration`, ...). `docs/project/COMMANDS.md` is the target interface; if a command it lists is not in the `Makefile`, say so rather than inventing a substitute, unless a task in this spec creates it.

`make test-integration` exits 0 when no integration tests are collected. Report "no integration tests collected" rather than "passed" in that case.

Never claim verification for a command that was not actually run. If an external dependency prevents verification, state exactly what was and was not verified.

## Security/data invariants

Preserve the `AGENTS.md` architectural rules relevant to the active spec, especially:
- no secrets in source;
- no production indexing of security/test fixtures;
- authorization before LLM context, including on fallback paths;
- source documents only through `DocumentRepository`;
- language metadata never broadens authorization;
- prompts are not a security boundary;
- retrieved content is untrusted data.

Do not prematurely implement future systems.

## Completion semantics

A checked task means **implemented and verified**. Do not mark a task complete with failing required tests, unmet acceptance criteria, missing required verification, or blocking TODOs.

## Spec-wide completion

After all tasks:
1. run the Definition of Done checks;
2. inspect the full diff from the base for scope drift, generated artifacts and protected-path changes;
3. update task checkboxes;
4. set `tasks.md` to `Status: implemented — pending review (YYYY-MM-DD, base <short-sha>)`;
5. update `docs/project/CURRENT_STATE.md` to say the spec is **implemented, pending review**, not complete or verified;
6. record durable decisions in `docs/project/DECISIONS.md`;
7. commit, and leave the repository ready for `spec-reviewer`.

Use [implementation-checklist.md](references/implementation-checklist.md).

## Final handoff

Report:
- spec implemented and the base..head commit range;
- tasks completed;
- materially changed components;
- verification commands and results;
- anything not verified;
- decisions made;
- deferred/follow-up items;
- host and model used;
- readiness for independent review.

Do not perform the independent review yourself. Tell the user to run `spec-reviewer` in a fresh session or context.
