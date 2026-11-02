# Workflow review checklist

Patterns seen in this project's Specs 007–009, how to detect them, and what usually fixes them. Use it as a starting point, not a limit: new patterns belong in the report and, once confirmed twice, in this file.

## Contents
- Token and time waste
- Quality risks
- Process slips
- Quality signals to protect

## Token and time waste

| Pattern | Detect | Usual fix |
|---|---|---|
| Full verification run repeatedly while iterating | script: `make verify runs` > 2, many before the last edit | targeted `pytest` while iterating; `make verify` and `make test-integration` once after the last edit |
| Verification re-run because of the environment (sandbox, permissions) | consecutive identical verify commands, the second with extra permissions | host note: run outside the sandbox from the start |
| Long-lived orchestrator context | script: orchestrator tokens dominated by cache reads, growing per call; many tasks in one session | start a fresh orchestrator session per task or after each approval; keep state in repository files |
| Same file read many times in one invocation | script: `repeated_reads` (spec files, tests) | read once and keep notes; briefs name sections to start from |
| Every subagent re-derives the whole spec | short brief (< 500 chars) followed by full reads of requirements, design and reviews | brief names the task box, design sections and R numbers to start from (reading more stays allowed) |
| Bookkeeping churn | script: many edits to `tasks.md` or `task-reviews.md` in one round | state change at start and end; one record write per round |
| Test-file churn | one test file edited ≥ 10 times in a round | run that test file alone until green before broader runs |
| Graph queried then ignored | one `graphify query`, then whole-file reads of everything anyway | keep one orienting query; don't add more graph steps where the task already names its files |
| Rework from spec ambiguity | review rounds whose findings are tagged spec or point at unclear design wording | clarify the design (dated amendment) before the next implementer round, instead of another round on the same text |
| Reviewer-invented requirement | a finding enforcing a rule that is in neither requirements nor design (e.g. byte-exact substrings) | the reviewer cites the requirement or design line for each finding; otherwise it is a suggestion, not a blocker |
| Orchestrator side work | many steps on usage lines, duplicate user messages, extra state-only commits | drop or batch bookkeeping; one commit per logical change |

## Quality risks

| Pattern | Detect | Why it matters |
|---|---|---|
| Dependent roles spawned in the same turn | implementer and reviewer started together | a reviewer may review incomplete work |
| Uncommitted changes reverted by a subagent | `git restore`, `git stash`, `git checkout --` in a subagent's commands | silently loses user changes (it happened to a MODEL_PREFERENCES edit) |
| Tests that pass only on this machine | verification without offline or empty-cache conditions where a dependency is cached | hides missing dependencies (Spec 009 T1 F1) |
| Reviewer on a weaker or same model as the implementer | model notes in `task-reviews.md`, script `models` | weaker independent check |
| Thin reviews | rounds with no findings across several tasks, short review blocks, few files read by the reviewer | the gate may be passing unchecked work |
| Results with false provenance | records stating facts from the user's report as file-checked | the record misleads later readers |

## Process slips

| Slip | Detect |
|---|---|
| Post-approval amendment without a dated change-log line | amendment commits vs `## Change log` lines |
| Status date changed on amendment | `Status: approved (<new date>)` after an amendment |
| Task work and workflow changes in one commit | files outside the task in a `Spec-Task` commit |
| Graph not updated after code changes | no `graphify update` in an implementer run that edited code |
| Learning notes missing after a PASS | no `~/learning/way2australia/specs/<NNN>-<slug>/T<id>.md` (full spec folder name) for a PASS task |
| Usage lines unfilled | `not filled` or empty Usage lines in `task-reviews.md` |
| Model tier mismatch not noted | model used differs from `MODEL_PREFERENCES.md` (read it on the spec branch at that time, with `git show <commit>:agent-skills/MODEL_PREFERENCES.md`) and the record says nothing; a host with no tier row is itself a finding |
| A PASS that leaves an earlier finding open | review block says "Findings: none" while a previous round's finding is not closed or recorded as accepted |
| Commit message does not match its content | e.g. "T2: record approval" changing T3's state |
| Workflow changes on two branches mid-spec | the same workflow file committed differently on `main` and `spec/<NNN>` |
| Agent ignores a "never" rule in its own skill | e.g. a `git stash` by an orchestrator whose skill says never stash |

## Quality signals to protect

These show the workflow is working; a proposal must not reduce them.
- Review rounds that FAIL with findings later confirmed as real bugs.
- Findings that cite requirement or design lines.
- Final verification on the committed state, including offline or empty-cache runs where dependencies matter.
- Security gates (`make eval-security`) and their sanity checks.
- User decisions quoted verbatim in `task-reviews.md`.
- Retrospective reconciliation of docs with code.
