# Implementation Checklist

## Before
- Spec named by the user; only one spec active.
- requirements/design/tasks all `Status: approved`, or a failed review with `RM` tasks.
- Dependencies/prerequisites satisfied.
- Git/repository state understood; `tasks.md` set to `implementing (base <sha>)`.

## During
- Requirement/design references clear.
- Existing code inspected.
- Minimum complete change implemented.
- Tests added/updated.
- Focused verification passed.
- Task not marked complete prematurely.
- One commit per task (or small coherent group).

## Scope
- No next-spec feature implemented.
- No Phase 2 drift without approval.
- No unapproved dependency/framework.
- No silent architecture/public-contract change.
- No unrequested changes under `evaluation/`, `knowledge/`, `config/`.
- Spec problems raised as `> BLOCKED:` notes, not silently patched.

## Final
- Definition of Done checked.
- Full relevant verification run; unrun or empty checks reported honestly.
- `tasks.md` set to `implemented — pending review`.
- CURRENT_STATE says "implemented, pending review".
- Durable decisions recorded.
- Work committed; repo ready for independent review.
