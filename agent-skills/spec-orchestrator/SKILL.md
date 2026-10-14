---
name: spec-orchestrator
description: Decide and start the next step of the Way2Australia AI task-gated spec workflow (plan, implement one task, task review, user approval, merge) from repository state alone. Use to start or resume work on a spec, or after any role finishes. Never reads code or diffs.
---

# Spec Orchestrator

## Model tier

Intended tier: **BEST_MINUS_ONE** (`agent-skills/MODEL_PREFERENCES.md`). Tiers are advisory and applied when a session starts; never switch models mid-session.

## Purpose

Route the loop. Read repository state, perform the one next action, hand over. Lifecycle, states, branching and `task-reviews.md` format: `docs/project/WORKFLOW.md`. Decision table: [state-machine.md](references/state-machine.md).

Input: `[NNN-spec]`. If omitted, use the spec named in `CURRENT_STATE.md`; if unclear, ask.

## Read only this

- `docs/project/CURRENT_STATE.md`;
- the spec's `Status:` lines and `**State:**` lines (`grep -n "^Status:\|\*\*State:\*\*"`);
- the latest block in the spec's `task-reviews.md` (the current task's last round);
- `agent-skills/MODEL_PREFERENCES.md`.

Never read or edit product code or diffs. Never write spec content (requirements, design, task text). You write only: task `State:` lines for user decisions, `tasks.md` spec `Status:` for branch/merge transitions, "User decision" blocks, `CURRENT_STATE.md`.

## Procedure

1. Check `git status` and the current branch. Dirty tree, or a branch the state does not imply: stop and ask. Never stash or discard.
2. Follow the table in `state-machine.md` for the first task whose State is not `approved`. Do exactly one action.
3. Keep `CURRENT_STATE.md` accurate at each transition.

## Starting roles

One writer at a time per checkout: never start a role while another role on the same spec is running.

- Host can start a session with a chosen model (Claude desktop app `start_session`): start a fresh session on the role's model tier, same checkout, with a brief of at most ~10 lines: spec, task ID, round, "follow the skill".
- Otherwise print the exact command and intended model, e.g. `New session on Sonnet: /spec-implementer 002 T3`.

Do not wait or poll. Resume from repository state when the user or host returns.

## User interaction

When a task is `awaiting user review (round N)`, show the reviewer's "Summary for user" from `task-reviews.md`, not a diff, and ask: approve, or feedback?

Record the answer verbatim and dated in the task's "User decision" block, then:
- **approved:** `**State:** approved (YYYY-MM-DD)`; commit with trailer `Spec-Decision: <NNN>/<task-id>`; push `spec/<NNN>` (never force); then the next task.
- **implementation feedback:** `changes requested — round N`; commit; start `spec-implementer` (the consecutive-FAIL count resets).
- **spec feedback / `SPEC_DEFECT`:** `blocked — spec issue`; add `> BLOCKED: spec issue — <why>` under the task if missing; commit; tell the user to run `spec-planner` ("revise an approved spec"). Resume after the change log records it.

Never show a task as ready while its latest review is `FAIL`. After a second consecutive `FAIL` (`task review failed — round 2`), escalate to the user with the findings.

## Completion

When every task is `approved`:
1. set `tasks.md` to `Status: all tasks approved (YYYY-MM-DD)`; update `CURRENT_STATE.md`;
2. offer the optional `spec-reviewer` retrospective; wait for the user's choice;
3. on the user's go-ahead: `git switch main`, pull, `git merge --no-ff spec/<NNN>`, `make verify`, push `main`;
4. set `Status: verified (YYYY-MM-DD, merged <sha>)`, update `CURRENT_STATE.md`, commit, push.

Conflict or `make verify` failure: `git merge --abort`, report, ask the user.

## Failures

| Situation | Behavior |
|---|---|
| Role interrupted (`implementing` / `in task review` with no matching block) | restart the same role for the same round |
| State line and checkboxes disagree | treat as interrupted; ask the user if unclear |
| Push rejected | report; never force-push |
| Anything unlisted | stop and ask |

Push or merge only after a recorded user approval. Never force-push.
