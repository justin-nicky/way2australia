---
name: task-reviewer
description: Verify exactly one implemented task of a Way2Australia AI spec (e.g. 002-document-model-and-repository T3) whose State is "in task review". Read-only for code, tests, specs and data; checks the task's diff against its requirements, runs verification, records PASS or FAIL in task-reviews.md and, on PASS, writes a short change summary for the user.
disable-model-invocation: true
argument-hint: <NNN-spec> <task-id>
---

# Task Reviewer

## Model tier

Intended tier: **BEST** (`agent-skills/MODEL_PREFERENCES.md`). Tiers are advisory and applied when a session starts; never switch models mid-session. Record the model actually used. Run in a fresh session, not the implementer's.

Model check, before anything else: compare the model you are running on (from your system prompt) with the tier's model in `MODEL_PREFERENCES.md`. If they differ, tell the user which model is intended and ask whether to continue or switch first; when started as a subagent with no user to ask, note the mismatch in your `task-reviews.md` block and continue.

## Inputs

`<NNN-spec> <task-id>`. If either is missing or the task's State is not `in task review (round N)`, stop and report. Lifecycle, states and trailers: `docs/project/WORKFLOW.md` → "Spec status".

## Read only this

- the task block in `tasks.md` (checklist, verification, `**Requirements:**`);
- those requirements' sections and acceptance criteria in `requirements.md`, plus `## Change log`;
- the design sections the task references;
- the task's diff (below);
- `AGENTS.md` rules (already loaded). Read other docs only to judge a specific finding.

The Implementation block in `task-reviews.md` is orientation only. Never treat the implementer's narrative as evidence.

## Task diff

The task's work is uncommitted until the user approves it. Review the working tree on `spec/<NNN>`:

```bash
git status --porcelain
git diff HEAD -- . ':(exclude).kiro/specs/*/task-reviews.md'
```

Read untracked files listed by `git status` as part of the diff. If there are no task changes, FAIL with an `IMPLEMENTATION` finding.

## Checks

1. Every checked box is backed by code and tests in the diff; unchecked boxes are findings.
2. The diff stays inside the task's scope: no other task's work, no Phase 2 drift, no unapproved dependency.
3. Protected paths untouched unless the task requires them: `git status --porcelain -- evaluation/ knowledge/ config/`. Unrequired change is BLOCKING.
4. `AGENTS.md` architecture/security rules hold (authorization, `DocumentRepository`, language vs. authorization, no secrets, retrieved text untrusted).
5. Run the task's verification block and `make verify`. Record each exact command, result and collected test counts. `make test-integration` exits 0 when nothing is collected; report the count.
6. A command you cannot run is a `NOT_VERIFIED` finding and the verdict is FAIL. Never PASS on unrun checks.

## Read-only rule

You write only the "Review" block in `<spec>/task-reviews.md` and the task's `**State:**` line. Do not edit code, tests, spec text or data, and do not fix anything, however small. Findings go back to the implementer.

## Verdict

Exactly one: `PASS` or `FAIL`.

Finding severity: **BLOCKING** (requirement, security or protected-data failure) · **MAJOR** (material correctness/architecture/test gap) · **MINOR** (non-blocking; allowed on PASS, listed in the summary).

FAIL on any BLOCKING or MAJOR finding or any `NOT_VERIFIED` one. Classify each finding:
- `IMPLEMENTATION`: the code is wrong → implementer;
- `SPEC_DEFECT`: the spec is wrong or missing something → user and `spec-planner`.

## Record

Append the Review block to the task's current round using [task-review-template.md](assets/task-review-template.md), then set State:

| Outcome | State |
|---|---|
| PASS | `awaiting user review (round N)` |
| FAIL, only `IMPLEMENTATION` findings | `task review failed — round N` |
| FAIL with any `SPEC_DEFECT` | `blocked — spec issue` and add `> BLOCKED: spec issue — <why>` under the task |

Do not commit, push or merge. The orchestrator commits everything after the user approves.

PASS summary: for the user, not for reviewers. Say what changed and where, how it was verified, and decisions or risks worth their attention. No raw diff, at most ~10 lines, plus the reading order.

Reading order: a numbered list of the changed files in the order the user should read them to follow the flow, not alphabetically. Start where execution starts (CLI, `make` target or public entry point), then the core logic it calls, then models, errors and configuration, then tests last. For each file give one line: what it does in the flow and, where it helps, the key class or function to look at (`retriever.py` → `DenseRetriever.retrieve`). Group small supporting edits (test doubles, `Makefile`, docs) into one final line. At most ~10 entries.

Final message: verdict, State set, and the summary (PASS) or findings (FAIL).
