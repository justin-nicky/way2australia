### Review
- Model: <model id>
- Verdict: PASS | FAIL
- Commands: `make verify` → pass (N tests, M collected integration); `<task check>` → pass
- Findings: F1 [BLOCKING|MAJOR|MINOR, IMPLEMENTATION|SPEC_DEFECT|NOT_VERIFIED, R#] <what> → <expected fix> (none on PASS)
- Summary for user (PASS only):
  - Changed: <what and where>
  - Verified by: <commands, tests>
  - Worth your attention: <decisions, risks, deviations; "nothing" if none>
- Usage: <tokens> tokens · <tool uses> tool uses · <duration> (left for the orchestrator; recorded by the orchestrator; `not measured` if the role ran outside it)
