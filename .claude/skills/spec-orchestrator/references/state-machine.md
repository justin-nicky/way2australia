# Orchestrator state machine

## Spec-level (check first)

| # | Condition | Action |
|---|---|---|
| 1 | Uncommitted changes with no task in progress, or checked-out branch not implied by state | stop; ask the user (uncommitted changes during an in-progress task are its work awaiting approval) |
| 2 | No approved spec in progress (any of the three files not `approved`) | offer `spec-planner` (pass the latest "Notes for the next spec" from the previous spec's `review.md`, if any) |
| 3 | Spec approved (`tasks.md` `approved (…)`), no `spec/<NNN>` branch | create `spec/<NNN>` from up-to-date `main`; set `Status: implementing (branch spec/<NNN>, base <sha>)`; commit; continue to task level |
| 4 | Otherwise | task level: first task whose State is not `approved` |
| 5 | Every task `approved` | set `all tasks approved`, offer optional `spec-reviewer`, then merge on user go-ahead (SKILL.md → Completion) |

Be on `spec/<NNN>` for task-level actions; switch only if the tree is clean, otherwise ask.

## Task-level (exactly one next action per State)

| State | Owner of next step | Orchestrator action |
|---|---|---|
| `not started` | implementer | start `spec-implementer <NNN> <task>` (round 1) |
| `implementing (round N)` | implementer | role interrupted: restart `spec-implementer` for round N |
| `in task review (round N)` | task-reviewer | start `task-reviewer <NNN> <task>` |
| `task review failed — round N`, N < 2 | implementer | start `spec-implementer` for round N+1 (findings are in the review block) |
| `task review failed — round N`, N ≥ 2 and last two reviews both FAIL | user | escalate with the findings; await decision |
| `awaiting user review (round N)` | user | show the "Summary for user"; record the decision (SKILL.md → User interaction) |
| `changes requested — round N` | implementer | start `spec-implementer` for round N+1 |
| `approved (YYYY-MM-DD)` | — | move to the next task |
| `blocked — spec issue` | user + planner | tell the user to run `spec-planner` "revise an approved spec"; do nothing else until the change log records it, after which the task is `not started` |

A user "changes requested" resets the consecutive-FAIL count; rounds keep increasing.
