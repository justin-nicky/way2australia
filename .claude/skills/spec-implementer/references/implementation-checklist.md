# Implementation Checklist (one task)

## Before
- Spec and task named; only this task will be worked on.
- requirements/design/tasks approved; task State allows a run; no `> BLOCKED:` note.
- On `spec/<NNN>`, clean tree, not `main`.
- State set to `implementing (round N)`.

## During
- Requirement/design references clear; existing code inspected.
- Minimum complete change; tests added/updated.
- Focused verification passed, then the task's verification block and `make verify`.
- Round > 1: only the latest findings/feedback addressed.

## Scope
- No other task's work, no next-spec feature, no Phase 2 drift.
- No unapproved dependency, silent architecture or public-contract change.
- No unrequested changes under `evaluation/`, `knowledge/`, `config/`.
- Spec problems raised as `> BLOCKED:` notes.

## Final
- Checkboxes ticked only for verified work; text unchanged.
- Implementation block appended to `task-reviews.md` with the model used.
- State set to `in task review (round N)`.
- Nothing committed, pushed or merged; changes left uncommitted for user approval.
