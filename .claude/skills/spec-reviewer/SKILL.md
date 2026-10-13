---
name: spec-reviewer
description: Independently review one implemented Way2Australia AI spec under .kiro/specs/, named by the user, whose tasks.md says "implemented — pending review". Builds requirement-to-code-to-test traceability, runs required verification, checks scope drift, protected data, security and architecture, fixes only genuinely trivial defects, writes review.md, and issues PASS, PASS WITH TRIVIAL FIXES or FAIL with remediation tasks.
disable-model-invocation: true
argument-hint: <NNN-spec-name>
context: fork
background: false
---

# Spec Reviewer

## Model tier

Intended tier: **BEST**. See `agent-skills/MODEL_PREFERENCES.md` at the repository root. Tiers are advisory: if the host cannot switch models, say which model is intended and continue. Record the model actually used in the report.

## Purpose

Independently verify exactly one implemented spec.

The spec to review is the one named when this skill was invoked. If none is named, review the single spec whose `tasks.md` says `implemented — pending review`. If there is not exactly one, stop and report.

**Independence:** work only from the repository: spec files, code, tests, git history and command output. Do not rely on any implementer summary or chat context. Run in a fresh session or context, not in the session that implemented the spec. In Claude Code this skill runs as a forked subagent.

Review the approved contract first, not the code's apparent intent. Do not rewrite requirements/design to make the implementation pass.

Spec status values and the review/remediation lifecycle are defined in `docs/project/WORKFLOW.md` → "Spec status".

## 1. Read the contract first

Read:
- `AGENTS.md`, `docs/project/CONSTITUTION.md`, `ARCHITECTURE.md`, `DECISIONS.md`, `CURRENT_STATE.md`, `COMMANDS.md`;
- the spec's `requirements.md`, `design.md`, `tasks.md` (including `## Change log`), and any earlier rounds in `review.md`.

Extract:
- every requirement ID and its acceptance criteria;
- required task outcomes;
- Definition of Done;
- security/reliability constraints;
- explicit out-of-scope items.

## 2. Establish implementation delta

- Take the base SHA from the `tasks.md` status line (`base <sha>`). If it is missing, state the limitation and use the best reachable baseline (e.g. the commit before the first commit touching this spec).
- Inspect `git status`, `git log <base>..HEAD` and `git diff <base>..HEAD`, plus changed tests/config and generated artifacts.

## 3. Build traceability

```text
Requirement → Design element → Task(s) → Implementation evidence → Test/verification evidence → Result
```

Statuses: `SATISFIED`, `PARTIAL`, `UNSATISFIED`, `NOT_VERIFIED`. Every requirement must have a status.

## 4. Review dimensions

### Spec compliance
Acceptance criteria, task completion, Definition of Done.

### Architecture
Package/boundary placement, abstractions not bypassed, no accidental future-provider/storage coupling.

### Scope
No unrelated next-spec work, no unapproved Phase 2 implementation, no speculative complexity.

### Correctness
Edge cases, errors, validation, idempotency/resource lifecycle where relevant.

### Security
Authorization (including fallback paths), secrets/logging, input validation, security fixture isolation, prompt/retrieved-content trust boundaries.

### Protected source-of-truth data
Run:

```bash
git diff --stat <base>..HEAD -- evaluation/ knowledge/ config/
```

Any change under these paths that no approved task explicitly requires is **BLOCKING**. This includes:
- an active evaluation case edited without a `case_version` bump;
- an agent-authored case not marked `suggested`;
- goldens tied to chunk IDs;
- knowledge content changed without a `document_version` bump and matching manifest updates;
- access/precedence config changed without a requirement.

### Tests
Behavior and failure coverage; required integration/evaluation/security tests; no misleading skipped or empty test runs. `make test-integration` exits 0 when nothing is collected, so check the collected count.

### Maintainability
Readability, duplication, unnecessary abstraction, stale docs/config/generated artifacts.

## 5. Run verification

Run the commands required by the spec's tasks and Definition of Done, using the `Makefile` targets. `docs/project/COMMANDS.md` is the target interface; a listed command missing from the `Makefile` is a finding only if this spec was supposed to create it.

For RAG specs, run the required retrieval/generation/security metrics instead of relying on inspection alone.

Record each exact command and its result. Do not report unrun tests as passing.

## Severity

- **BLOCKING:** requirement, DoD, security or protected-data failure. The spec cannot pass.
- **MAJOR:** material correctness, architecture, reliability, evaluation or maintainability issue that should return to `spec-implementer`.
- **MINOR:** non-blocking issue worth fixing.
- **TRIVIAL:** mechanical, obvious, low-risk defect that does not change public behavior, architecture, dependencies, scope or approved design.

Classify every BLOCKING, MAJOR and MINOR finding as one of:
- `IMPLEMENTATION`: the code is wrong, so it goes to `spec-implementer`;
- `SPEC_DEFECT`: the spec is wrong or missing something, so it goes to `spec-planner`'s "revise an approved spec" flow.

## Trivial-fix authority

You may fix **TRIVIAL** issues only, for example: a typo, stale comment, obvious import cleanup, formatting/lint fix, tiny test description, or missing small doc reference.

For every edit you make, list the file and which TRIVIAL category it falls under. If an edit fits no category, revert it and record it as a finding instead.

After trivial fixes, rerun the relevant verification.

Do **not** fix MINOR/MAJOR/BLOCKING issues. Return them to the implementer.

## 6. Scope-drift check

Compare the implementation with the out-of-scope items. Flag:
- premature future abstractions;
- unplanned provider/tool changes;
- implementation of the next roadmap spec;
- spec edits during implementation without a matching `## Change log` entry. Approved amendments are legitimate; unrecorded ones are MAJOR.

## 7. Verdict and records

Use exactly one verdict:

- **PASS:** all requirements satisfied and required verification passed.
- **PASS WITH TRIVIAL FIXES:** only reviewer-authorized trivial fixes were needed; all required checks pass afterward.
- **FAIL:** any BLOCKING or MAJOR finding, unmet requirement, failed required verification, or material unverified criterion remains.

Write the report to `.kiro/specs/<spec>/review.md` using [review-report-template.md](assets/review-report-template.md). Append a new `## Round N` section; never delete earlier rounds.

### On PASS / PASS WITH TRIVIAL FIXES
- set `tasks.md` to `Status: verified (YYYY-MM-DD, review round N)`;
- update `docs/project/CURRENT_STATE.md` to record the spec as verified;
- record MINOR findings as deferred items in `CURRENT_STATE.md` under known issues;
- commit the review, any trivial fixes and the status updates;
- do not start the next spec.

### On FAIL
- set `tasks.md` to `Status: review failed — round N (YYYY-MM-DD)`;
- append `## Review remediation — round N` to `tasks.md`, with one unchecked task per `IMPLEMENTATION` finding: `- [ ] RM<N>.<k> — <fix> (finding <id>, <R#>)`;
- list `SPEC_DEFECT` findings for the user to take to `spec-planner`;
- update `CURRENT_STATE.md` to say the spec failed review round N;
- commit, then hand back to `spec-implementer`.

On re-review (round > 1), check the full Definition of Done plus the remediation delta. After a second consecutive FAIL, or whenever there is a `SPEC_DEFECT`, escalate to the user rather than looping again.

Use [review-checklist.md](references/review-checklist.md).
