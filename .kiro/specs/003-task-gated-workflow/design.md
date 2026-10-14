# 003 — Task-Gated Agent Workflow Design

Status: approved (2026-10-14)

## Design summary

Five skills cooperate through repository files. Each role runs in its own fresh session on its preferred model and reads a small, role-specific set of files.

```text
                     ┌───────────────────────────── spec-orchestrator (BEST_MINUS_ONE) ─────────────────────────────┐
                     │ reads: CURRENT_STATE.md, Status/State lines, latest task-reviews.md entry, MODEL_PREFERENCES │
                     └──────────────────────────────────────────────────────────────────────────────────────────────┘
                          │ starts / prints            │ starts / prints              │ relays summary
                          ▼                            ▼                              ▼
 spec-planner (BEST) ─► spec-implementer (BEST−1) ─► task-reviewer (BEST) ─PASS─► user ─approve─► orchestrator records, pushes
        ▲                  ▲     one task, one round        │                        │
        │                  └──────── FAIL (≤ 2 rounds) ─────┘                        │ changes requested
        │                  └─────────────────────────────────────────────────────────┘
        └──── SPEC_DEFECT / spec feedback ("revise an approved spec")

 all tasks approved ─► [optional] spec-reviewer (BEST) retrospective ─► orchestrator merges spec branch into main, pushes
```

The repository is the only shared memory: `tasks.md` holds state, `task-reviews.md` holds the per-task log, and commit trailers tie commits to tasks.

## Package / file placement

```text
agent-skills/                       # canonical, the only editable source
├── MODEL_PREFERENCES.md            # + spec-orchestrator, task-reviewer tiers
├── README.md                       # flow + per-host usage
├── spec-orchestrator/              # NEW
│   ├── SKILL.md
│   ├── agents/openai.yaml          # explicit-only
│   └── references/state-machine.md # state → next action table
├── task-reviewer/                  # NEW
│   ├── SKILL.md
│   ├── agents/openai.yaml          # explicit-only
│   └── assets/task-review-template.md
├── spec-implementer/               # CHANGED: one task per run, branch, trailer
├── spec-reviewer/                  # CHANGED: optional retrospective, next-spec notes
└── spec-planner/                   # CHANGED: reads next-spec notes, writes State lines

scripts/sync_agent_skills.py        # CHANGED: Claude frontmatter for new skills; no forked reviewer
CLAUDE.md                           # CHANGED: two imports only
AGENTS.md                           # CHANGED: role-based reading, new flow steps
docs/project/WORKFLOW.md            # CHANGED: lifecycle, branching, loop
docs/project/DECISIONS.md           # + D023
docs/project/COMMANDS.md, ROADMAP.md, CURRENT_STATE.md

.kiro/specs/<NNN>/task-reviews.md   # NEW per spec, created on first task run
```

## Components / boundaries

| Role | Tier | Writes | Never |
|---|---|---|---|
| `spec-orchestrator` | BEST_MINUS_ONE | task `State:` lines for user decisions, spec `Status:` for branch/merge transitions, `task-reviews.md` "User decision" blocks, `CURRENT_STATE.md`; runs git merge/push | reads code or diffs; writes spec content; implements or reviews |
| `spec-planner` | BEST | spec files; initial `State: not started` lines; `## Change log` | implements code |
| `spec-implementer` | BEST_MINUS_ONE | code/tests for one task; that task's checkboxes and `State:`; "Implementation" block in `task-reviews.md` | starts a second task; merges; pushes |
| `task-reviewer` | BEST | "Review" block in `task-reviews.md`; that task's `State:` | edits code, tests, spec text or data; fixes anything |
| `spec-reviewer` (optional) | BEST | `review.md` round with "Notes for the next spec"; `RM` tasks on findings | blocks verification by not running |

One writer at a time per checkout: the orchestrator never starts a role while another role on the same spec is still running.

## Branching and commits

- Branch: `spec/<NNN>` (e.g. `spec/002`), created from up-to-date `main` by the orchestrator before the first task, if missing.
- Every implementer commit ends with the trailer `Spec-Task: <NNN>/<task-id>` (`T3`, `RM1.2`).
- Reviewer and orchestrator bookkeeping commits use `Spec-Review: <NNN>/<task-id>` and `Spec-Decision: <NNN>/<task-id>` respectively, so they never count as task changes.
- Task diff for review: the task's `Spec-Task` commits, found with

  ```bash
  git log --format=%H --reverse --grep='^Spec-Task: 002/T3$' main..spec/002
  ```

  then `git diff <first>^ <last> -- . ':(exclude).kiro/specs/*/task-reviews.md'`.
- Rework is new commits on the same branch. No rebase, amend or force-push on a pushed spec branch.
- Final merge: `git merge --no-ff spec/<NNN>` into up-to-date `main`, `make verify`, push `main`. Merge conflicts stop the orchestrator and go to the user.

## Interfaces / models

### Task state line

Directly under each task heading in `tasks.md`, above the checkboxes:

```markdown
## T3 — Implement manifest and metadata validation

**State:** awaiting user review (round 1)
**Requirements:** R2, R5, R6
```

Checkbox text is never changed. Allowed values:

| State | Set by | Next action |
|---|---|---|
| `not started` | planner | implementer, round 1 |
| `implementing (round N)` | implementer at start | implementer resumes round N |
| `in task review (round N)` | implementer at end | task-reviewer |
| `task review failed — round N` | reviewer | implementer, round N+1 (if N < 2), else escalate to user |
| `awaiting user review (round N)` | reviewer on PASS | orchestrator shows summary, asks user |
| `changes requested — round N` | orchestrator (user feedback) | implementer, round N+1 |
| `approved (YYYY-MM-DD)` | orchestrator (user approval) | next task, or spec completion |
| `blocked — spec issue` | any role | user + `spec-planner` revise flow |

Rounds count implementer runs for a task. The 2-round automatic limit counts consecutive reviewer `FAIL`s; a user "changes requested" resets it.

### Spec status line (`tasks.md`)

`requirements.md`/`design.md` values are unchanged. `tasks.md` values become:

- `draft`
- `approved (YYYY-MM-DD)`
- `implementing (branch spec/<NNN>, base <sha>)`
- `all tasks approved (YYYY-MM-DD)`: optional retrospective, then merge
- `verified (YYYY-MM-DD, merged <sha>)`

`implemented — pending review` and `review failed — round N` are retired. Specs 001 and 002 keep their history.

### `task-reviews.md`

One file per spec, append-only, newest at the bottom. Per task and round:

```markdown
## T3 — round 1

### Implementation
- Model: <model id>
- Commits: <short shas>
- Verification run: `make verify` → pass (N tests)
- Notes: <decisions, deviations, open questions>

### Review
- Model: <model id>
- Verdict: PASS | FAIL
- Commands: `make verify` → pass (N tests, M collected integration); `<task check>` → pass
- Findings: F1 [MAJOR, IMPLEMENTATION, R5] <what> → <expected fix> (none on PASS)
- Summary for user (PASS only):
  - Changed: ...
  - Verified by: ...
  - Worth your attention: ...

### User decision
- 2026-10-14 — approved | changes requested: "<user feedback verbatim>" | spec issue: "<feedback>"
```

The reviewer may read the Implementation block for orientation but never treats it as evidence.

Remediation for a failed round lives in that round's Findings, not in `tasks.md`. This keeps the reviewer read-only for spec files and avoids churn in Kiro's `tasks.meta.json`.

### Orchestrator decision procedure

Stated as a table in `spec-orchestrator/references/state-machine.md`:

1. Working tree dirty, or the checked-out branch is not what the state implies → stop and ask the user.
2. No approved spec in progress → offer `spec-planner` (pass the latest "Notes for the next spec", if any).
3. Spec approved, no branch → create `spec/<NNN>` from `main`, set `implementing (branch …, base …)`.
4. Otherwise, take the first task whose state is not `approved` and act on its state (table above).
5. All tasks approved → set `all tasks approved`, offer the optional `spec-reviewer` retrospective, then merge on user approval.

### Starting roles

- Hosts that can start sessions with a model (Claude desktop app): a fresh session, model from `MODEL_PREFERENCES.md`, same checkout, brief of at most ~10 lines: spec, task ID, round, and "follow the skill". The skill's own reading list does the rest.
- Other hosts: print the exact command and intended model, for example `New session on Sonnet: /spec-implementer 002 T3`.
- The orchestrator does not wait or poll. It resumes from repository state when the user or host returns.

## Data flow

```text
implementer ──commits (Spec-Task)──► spec/<NNN>
     └─ task-reviews.md: Implementation block; State → in task review
task-reviewer ── reads task slice of spec + task diff, runs checks
     └─ task-reviews.md: Review block; State → awaiting user review | failed
orchestrator ── reads State + Summary ─► user
     └─ task-reviews.md: User decision; State → approved | changes requested; push spec/<NNN>
```

## Context loading (token budget)

| Role | Must read | Reads only if needed |
|---|---|---|
| orchestrator | `CURRENT_STATE.md`, the spec's Status/State lines (grep), latest `task-reviews.md` block, `MODEL_PREFERENCES.md` | nothing else |
| planner | `AGENTS.md` read-first docs, `ARCHITECTURE.md`, existing specs, previous spec's next-spec notes | knowledge docs, code |
| implementer | the task block, its R# sections, the referenced design sections, latest `task-reviews.md` round for the task, touched code | `CONVENTIONS.md`, `DECISIONS.md`, `COMMANDS.md` |
| task-reviewer | the task block, its R# sections, the referenced design sections, the task diff, `AGENTS.md` rules (auto-loaded) | other docs to judge a specific finding |
| spec-reviewer | full spec, `task-reviews.md`, diff `main...spec/<NNN>` | the rest |

`CLAUDE.md` imports only `@AGENTS.md` and `@docs/project/CURRENT_STATE.md`. `AGENTS.md` "Read first" becomes role-based: the skill's reading list applies when a skill is in use; the full list applies to work done without a skill. Codex reads `AGENTS.md` directly, so the same saving applies there.

No skill switches models inside a running session (the prompt cache is per model, so a switch re-bills the whole conversation).

## Host frontmatter (sync script)

`HOST_FRONTMATTER["claude"]`:

| Skill | Injected |
|---|---|
| `spec-implementer` | `disable-model-invocation: true`, `argument-hint: <NNN-spec> [task-id]` |
| `task-reviewer` | `disable-model-invocation: true`, `argument-hint: <NNN-spec> <task-id>` |
| `spec-reviewer` | `disable-model-invocation: true`, `argument-hint: <NNN-spec>` |
| `spec-orchestrator` | `disable-model-invocation: true`, `argument-hint: [NNN-spec]` |

`context: fork` and `background: false` are removed from `spec-reviewer`. A fork inherits the invoking session's model, which with advisory tiers could be BEST_MINUS_ONE. Independence comes from starting the reviewer in a fresh session instead.

Codex: `agents/openai.yaml` with `allow_implicit_invocation: false` for orchestrator, implementer, task-reviewer and spec-reviewer. The planner stays implicit-capable.

## Error and failure behavior

| Situation | Behavior |
|---|---|
| Role interrupted mid-run (state `implementing` / `in task review` without its block) | orchestrator restarts the same role for the same round |
| Dirty working tree at orchestrator start | stop; ask the user (never stash or discard) |
| Reviewer cannot run a verification command | verdict `FAIL` with a `NOT_VERIFIED` finding; never PASS on unrun checks |
| Second consecutive reviewer FAIL | state stays `task review failed — round 2`; orchestrator escalates to the user |
| `SPEC_DEFECT` finding or user spec feedback | `blocked — spec issue`; planner revise flow; the task re-opens per its change log |
| Merge conflict or `make verify` failure after merge | abort the merge; ask the user |
| Push rejected | report; never force-push |
| State line and checkboxes disagree | treat as interrupted; ask the user if unclear |

## Security / authorization

No product security change. Process safeguards:
- the protected-path rule (`evaluation/`, `knowledge/`, `config/`) is checked by every task review;
- the orchestrator only pushes after a recorded user approval and never force-pushes;
- user approvals are recorded verbatim with dates, so the audit trail lives in git.

## Observability

Per task: models used, rounds, verdicts, commands and test counts in `task-reviews.md`. Per spec: branch, base, merge SHA in the `tasks.md` status line.

## Testing / evaluation strategy

- `make verify` (includes `make skills-check`) after the skill and sync changes.
- Static review: every state in the table has exactly one owner and one next action; every skill uses the same values as `WORKFLOW.md`.
- Acceptance dry run (R13): Spec 002 T3 through orchestrator → implementer → task-reviewer → user approval on `spec/002`. Any defect found is fixed in the skills/docs before this spec completes.

## Bootstrap

This spec cannot use the workflow it creates. It is implemented under the existing flow, directly on `main`, by `spec-implementer`. Its final task is the dry run on Spec 002 T3, which is the first use of the new flow. A `spec-reviewer` run on 003 is optional, as the new flow allows.

## Phase 2 compatibility / migration

- Spec 001: unchanged history.
- Spec 002: `tasks.md` status becomes `implementing (branch spec/002, base 5bbb333)`. T1 and T2 get `**State:** approved (2026-10-14)` with a note that they predate task review. T3–T9 get `**State:** not started`.
- Spec 003 (this spec): `State:` lines from the start.
- Roadmap: ingestion and later specs shift by one number.

## Alternatives / deferred decisions

- **Remediation items in `tasks.md`** (today's `RM` pattern) for task reviews: rejected, because the task reviewer would edit spec files and churn `tasks.meta.json`. `RM` stays only for the optional spec retrospective.
- **Forked reviewer subagent:** rejected under advisory tiers (it inherits the caller's model).
- **Branch per task / GitHub PRs:** rejected by the user in favour of one branch per spec.
- **Hook- or CI-enforced states and trailers:** deferred.
