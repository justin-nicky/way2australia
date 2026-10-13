# Review Checklist

- Working from repository evidence only, in a fresh session/context.
- Contract read before code; `## Change log` read.
- Every requirement/DoD/out-of-scope item extracted.
- Implementation delta inspected from the recorded base SHA.
- Every requirement has implementation and verification evidence/status.
- Package boundaries/security invariants/scope checked.
- Protected paths (`evaluation/`, `knowledge/`, `config/`) diffed; unrequested changes are BLOCKING.
- Required tests/evals/security checks actually run and recorded (including collected counts).
- Only TRIVIAL issues fixed directly, each mapped to a category.
- Relevant checks rerun after trivial fixes.
- Findings classified IMPLEMENTATION or SPEC_DEFECT.
- `review.md` round appended; `tasks.md` status and CURRENT_STATE updated.
- On FAIL: RM tasks appended to `tasks.md`.
- Verdict reflects evidence, not confidence.
