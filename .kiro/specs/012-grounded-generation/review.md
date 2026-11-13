# Spec 012 — retrospective review

## Round 1 — 2026-11-13

- **Spec:** `012-grounded-generation`
- **Diff reviewed:** `main...spec/012` (head `1730ef9`, merge base `416fc3a`), plus the uncommitted orchestrator edits (`tasks.md` Status, `CURRENT_STATE.md` table and next step, `graphify-out/` rebuild; not reviewed as spec work)
- **Reviewer host / model:** Claude Code, `claude-opus-5-5` (Opus 5.5), run as a subagent in a fresh session. Intended tier BEST (`agent-skills/MODEL_PREFERENCES.md`, Claude Code `Opus`) matches. No Anthropic API or Bedrock call; `ANTHROPIC_API_KEY` was unset for every command.
- **Outcome:** `PASS`
- **Usage:** 264K tokens · 60 tool uses · 17:15

### Verification run

| Command/check | Result | Notes |
|---|---|---|
| `HF_HUB_OFFLINE=1 HF_HOME=<empty scratch dir> make verify` (no `ANTHROPIC_API_KEY`) | pass | 1795 passed, 5 skipped, 3 warnings (Qdrant insecure-connection and version-check warnings) in 255.7 s; lint, format, typecheck, skills-check, validate steps clean; Docker tests ran inside it (Qdrant reachable) |
| `make test-integration` | pass | 28 passed, 1772 deselected (Docker Qdrant reachable) |
| `HF_HUB_OFFLINE=1 make eval-security` | PASS | suite `public-eval-v4` v4; 3 chunker runs, 8 paths each, 93 queries; result schema 1.6, `passed` true; `generation_checks.passed` true (`generation_prompt_isolation` 8 paths, 40 prompts rendered; `generation_poisoned_evidence` and `generation_citation_manipulation` pass); result in `experiments/results/tmp/` (git-ignored) |
| `make validate-evaluation` | OK | `OK, 0 problems` |
| `make eval-continuity BASE=…20261106T072428Z.json CANDIDATE=…20261113T101802Z.json` | no differences | shared goldens 87, only in CANDIDATE `g088 v1`, "continuity: no shared-case differences" (file comparison only, no model) |
| Generation result files (script) | consistent with D090 | Haiku `…080223Z` 1.1 / `e84e098` clean / answer 0.8621 refusal 0.8000 / $0.027876; Sonnet v3 `…082549Z` 0.9655 / 0.8667 / $0.525794; Sonnet v4 `…102514Z` `a0869a5` clean / 0.9659 / 0.8824 / $0.546976 |
| `git diff --name-status main...spec/012 -- evaluation knowledge config` | as R15 allows | see protected-data check |
| `git diff --stat main...spec/012 --` retrieval, rerank, lexical, ingestion, repositories, `apps/`, `packages/core` | only `retrieval/cli.py` and the new `retrieval/cli_args.py` | the T4 argument-helper extraction the tasks allow; no retrieval test changed |
| Secret scan of the added lines (`sk-ant-`, AKIA/ASIA, ARN with account ID, `Bearer`, `x-api-key`) | none | only the T6 reviewer's description of its own scan matches |
| Language-literal scan of `generation/` (`"ml"`, `'ml'`, Malayalam) | none | |
| `git status --porcelain -- evaluation knowledge config experiments` | empty | |

### Requirements traceability

| Requirement | Implementation evidence | Test/verification evidence | Status |
|---|---|---|---|
| R1 context builder | `generation/context.py` `ContextBuilder.build` (exact-text dedup, budget, rank order, `S1…Sn`, payload metadata); D081 | `tests/generation/test_context.py` (dedup, budget, IDs, determinism, language grep) | SATISFIED |
| R2 versioned prompts | `config/prompts/registry.yaml`, `answer/v1/*`, `generation/prompts.py` `PromptRegistry`, `render_prompt`; D082 | `test_prompts.py` (hash pin, unknown pair, escaping, clauses, secret patterns) | SATISFIED |
| R3 answer contract and language | `generation/models.py`, `service.py` `_response`, `language.py`, `messages.yaml` (en, ml approved at T2) | `test_models.py`, `test_service.py`, `test_language.py` | SATISFIED (token counts are dropped on raised outcomes, F1) |
| R4 generator interface and fake | `generation/base.py` Protocol, `fake.py` hooks | `test_fake.py`; R9 defect matrix in `test_generation_eval.py` | SATISFIED |
| R5 Bedrock adapter, config, outage policy | `generation/bedrock.py`, shared `claude.py` (loop, deadline, D-B table incl. 413), `config.py`, `config/generation.yaml`; `bedrock` extra, `make setup-bedrock`; D084, D085 | `test_bedrock.py`, `test_generation_config.py`, lazy-import subprocess test; opt-in `test_bedrock_smoke.py` (skipped; Bedrock smoke still open, not a gate) | SATISFIED (deadline is soft, known carry-over D084) |
| R17 direct Anthropic API | `generation/anthropic_api.py` (key only from `ANTHROPIC_API_KEY`, `ANTHROPIC_BASE_URL` / `ANTHROPIC_CUSTOM_HEADERS` refused, Bedrock-form ID refused, response-model check, no fallbacks); `anthropic` extra, `make setup-anthropic`; D086 | `test_anthropic_api.py`; T3 assertions unchanged (T5b review); user smoke gate passed for both models (`task-reviews.md` T6) | SATISFIED |
| R6 answerability and citations | `service.py` pre-gate and outcome mapping; `citations.py` `validate_citations` (rule order recorded in As-built notes); D083 | `test_citations.py`, `test_service.py` (zero-call pre-gate) | SATISFIED |
| R7 authorization and untrusted evidence | `AnswerService` holds no repository or client; evidence only from `open_retrieval` hits; escaping; `safe_text` snippets | `test_service_isolation.py` (with negative control), `eval-security` generation checks | SATISFIED |
| R8 `make ask` | `generation/cli.py`, `retrieval/cli_args.py`, `Makefile` `ask` | `test_ask_cli.py` (exit codes, fake warning, default from file, hybrid fake reranker, close on both paths) | SATISFIED |
| R9 `make eval-generation` | `evaluation/generation_eval.py`, `evaluation/cli.py` `_generation`; result 1.1; cost guard; D088 | `test_generation_eval.py` (crafted 19-case suite with exact metrics, defect matrix, cost guard, `--min-*` exit 1) | SATISFIED (actual cost is a lower bound, F1) |
| R10 generation security | `evaluation/security_eval.py` three checks, result 1.6; D089 | `test_security_eval.py` (pass on throwaway index; broken validator fails); `make eval-security` PASS | SATISFIED (stale deferral owner labels, F3) |
| R11 candidates | `evaluation/candidates/012-candidates.jsonl` (7 rows, contradiction case included) | `make validate-evaluation` OK; candidates not loaded as cases | SATISFIED |
| R12 suite v4 | `evaluation/suites/public-eval-v4.json`, `datasets/v4/*`, v3 `replaced`, `DEFAULT_SUITE` v4; D091 | `test_suite_v4.py` (v3 rows byte-equal except suite id); continuity re-run above | SATISFIED |
| R13 unchanged behaviour | retrieval code unchanged except the allowed helper; no HTTP route; protected paths as allowed | retrieval tests unchanged and passing; T4 reviewer's byte-identical `make retrieve` check | SATISFIED |
| R14 real runs and model choice | thresholds, prices, smoke gate, choice recorded verbatim (`task-reviews.md` T6 stages 1–5, user decisions); `config/generation.yaml` `default_generator: anthropic`, `claude-sonnet-5-5`, pricing 2 / 10; D090 | four committed result files (checked above); zero `generator_unavailable` in each | SATISFIED |
| R15 spec-wide verification | — | `make verify` hub-free, `make test-integration`, `make eval-security`, protected-path diff (this round) | SATISFIED |
| R16 docs and decisions | D081–D091; ARCHITECTURE, COMMANDS, TECH_STACK, ROADMAP, CURRENT_STATE; design As-built notes | T7 review rounds 1–2; this round's reconciliation | SATISFIED (two decision headers cite the wrong requirement numbers, F4) |

Definition of Done: R1–R17 satisfied and traced; R14 runs recorded, checked and committed (`12534f0`); default chosen by the recorded rule (D090); suite v4 promoted (D091); `make verify` (hub-free), `make test-integration` and `make eval-security` pass; protected-path check matches R15; docs match the code after this round's reconciliation. The remaining items are this retrospective's PASS and the user's merge approval.

### Protected-data check

`git diff --stat main...spec/012 -- evaluation/ knowledge/ config/` lists:

- `config/generation.yaml` (A): T3, schema 1.1 in T5b, T6 default, model and pricing. Required by R5, R17, R14.
- `config/prompts/registry.yaml`, `config/prompts/answer/v1/{messages.yaml,output_schema.json,system.md}` (A): T2. Required by R2, R3.
- `evaluation/candidates/012-candidates.jsonl` (A): T5 rows; T6 `review` fields plus the user-accepted `cand012_en_001` `proposed_case` deviation (Spec 006 precedent). Required by R11, R12.
- `evaluation/datasets/v4/{golden,unanswerable,security}_public.jsonl`, `evaluation/suites/public-eval-v4.json` (A): T6. Required by R12.
- `evaluation/suites/public-eval-v3.json` (M): `status` active → replaced only (diff checked). Required by R12.
- `knowledge/`: no change.

No unrequired change. Working tree: no protected-path change.

### Findings

| ID | Severity | Class | Requirement/Task | Finding |
|---|---|---|---|---|
| F1 | MINOR | IMPLEMENTATION | R3, R9 / T4, T5 | Token counts and actual cost omit billed responses that end in an exception. `GeneratorOutputError` (`max_tokens`, `json`, `schema`) and `GeneratorDeclinedError` (refusal stop reason) carry no usage (`generation/errors.py`), and `AnswerService` records `usage=None` for them (`service.py`), so `actual_cost_usd` and the token totals in `generation_eval.py` count only cases that returned output (`cases_with_usage` shows the gap). In the Haiku run, the three `max_tokens` cases (g065, g076, g086) were billed but are missing from its $0.027876. The figure is a lower bound. It did not affect the T6 choice (Sonnet had no such case; Haiku already fell short), but a later model comparison with many `max_tokens` cases would understate cost. Carry-over: attach usage to `GeneratorOutputError` / `GeneratorDeclinedError` in the adapter and record it in the response. |
| F2 | MINOR | IMPLEMENTATION | R16 / T3, T6 | `config/generation.yaml` has more stale comments than the known `deadline_s` one. `backoff_s` says "delay … capped by the deadline" in both sections, but since the T3 review F1 change the backoff is not capped (As-built note T4 F3: the loop stops without sleeping instead). `bedrock.model_id` says "null until T6 commits the chosen model's Bedrock ID", but T6 committed `anthropic` and Bedrock stays null until the switch (D086). Config was not edited in this round. Carry-over: fix these together with the `deadline_s` comment and the hard wall-clock cap. |
| F3 | MINOR | IMPLEMENTATION | R10 / T5 | The `make eval-security` lines `deferred s005 (ungrounded_generation): roadmap-10` and `deferred s006 (citation_manipulation): roadmap-10` take the attack types from evaluation data. The owner label `roadmap-10` is a code constant, `DEFERRED_OWNERS` in `evaluation/security_eval.py`; `UNANSWERABLE_OWNER = "roadmap-10"` with status `not_evaluable_before_generation` in `retrieval_eval.py` is the same kind. Item 10 is now done except the route. s006's threat (a model-written URL) is covered by the synthetic `generation_citation_manipulation` / `generation_poisoned_evidence` checks. The s005 and s006 queries themselves still do not run through the answer path, so "deferred" stays true and only the owner is stale. Carry-over, not a remediation: retarget the owners (s006 to the generation checks or item 12, s005 to faithfulness, item 12). The result content changes, so this needs its own task. |
| F4 | MINOR | IMPLEMENTATION | R16 / T7 | Two new decision headers cite the wrong requirements. D083 (answerability and citations) says "Spec 012 R3, R5, R7"; the requirement is R6 (with R7). D084 (generator interface, client, config) says "Spec 012 R6; D-A, D-C"; it is R4/R5. The decision bodies are correct. Not edited, because decisions are never rewritten. A correcting note can go in the next decision that touches them. |

No BLOCKING or MAJOR finding.

### Documentation reconciled

| File | Change | Reason |
|---|---|---|
| `docs/project/CURRENT_STATE.md` | "Last updated", the goal paragraph (said T7 was in task review), the Spec 012 status row and Next step item 1 now say all tasks approved and the retrospective round 1 passed, waiting for the user's merge approval | implemented reality after the T7 approval and this round |
| `docs/project/CURRENT_STATE.md` | Known issues: new "Spec 012 retrospective (round 1)" block with F1–F4 | the skill puts MINOR findings under known issues on PASS |
| `.kiro/specs/012-grounded-generation/design.md` | As-built notes: two notes added: usage and cost on raised outcomes (F1), and stale config comments beyond `deadline_s` (F2) | design "Result" says token totals and actual cost come from actual usage; the code records usage only when output is returned |

Not changed, on purpose: `DECISIONS.md` (D081–D091 cover every durable choice; F4 is a header mislabel and decisions are not rewritten), `TECH_STACK.md`, `ARCHITECTURE.md`, `COMMANDS.md`, `ROADMAP.md` (checked against the code: `make ask` / `make eval-generation` options and exit codes, extras and setup targets, module table, result and security schema versions, default suite and generator all match), `config/generation.yaml` (protected; F2), `tasks.md` (Status already set by the orchestrator).

### Deviations from the approved plan

| Deviation | Where approved (change log / task-reviews round) or finding ID |
|---|---|
| Direct Anthropic API generator (`anthropic`), shared `ClaudeMessagesAdapter`, T5b, T6 default `anthropic` | requirements change log 2026-11-10; design amendment; As-built "T6: default generator" |
| 413 is a configuration error | change log 2026-11-10 |
| Deadline keeps the classified sub-reason; backoff not capped by the remaining time | change log 2026-11-07 (T4 boxes); As-built T4 F3 |
| Citation rules run in a fixed order | change log 2026-11-09; As-built T4 F2 |
| `make ask` retrieval line format differs from `make retrieve` | change log 2026-11-09; As-built T4 F1 |
| `ANTHROPIC_CUSTOM_HEADERS` also refused | T5b review (task-reviews T5b round 2); As-built T5b |
| `deadline_s` is soft (per-phase httpx timeout) | task-reviews T6 stage 2 section C; As-built T6; D084 (carry-over) |
| T6 in two commits (checkpoint `a0869a5` plus final `12534f0`) | user decision after T6 stage 4 (Spec 010 precedent) |
| `cand012_en_001` `proposed_case` reworded (original kept in `review.original_*`) | user decision after T6 stage 4; As-built T6 |
| Generation checks run once, on the first passing chunker run, not per chunker | consistent with design ("run once on the throwaway security index"); not a deviation |
| Usage and cost are missing on raised outcomes | F1 (MINOR) |

### Cross-task consistency

- The D-B table, the deadline loop and parsing live in one place (`generation/claude.py`). Both Claude generators delegate to it, and only client construction, credentials and the response-model hook differ, as the amendment asked. No duplicated classification logic is left in `bedrock.py`.
- Outcome mapping is the same in the service, the CLI output, the eval metrics and the security checks: `AnswerService` is the only path in all four. `AnswerService` catches only the three outcome errors. Configuration errors (including the response-model mismatch) end a `make ask` or `eval-generation` run with exit 2 and write no result.
- Minor duplication, not a finding: `evaluation/cli.py` `_generation` repeats the "no generator is configured" refusal that `build_generator` already raises, and defines its own retrieval arguments instead of `retrieval/cli_args.py`. R8 asks for sharing only between `make retrieve` and `make ask`. Worth folding together when Spec 013 reworks `open_retrieval`.
- The default suite (v4), generator (`anthropic`), model and prices are read from config or `DEFAULT_SUITE` everywhere. The tests read them from the file and never use a literal.
- Error messages name variables, IDs and statuses, never key values or URLs. Unexpected exceptions print the class name only, on both CLIs.

### Scope-drift review

- No HTTP route, no Phase 2 workflow, no new `index_version`, no re-ingestion, no retrieval behaviour change, no non-Anthropic provider, no failover. The `anthropic` endpoint is a chosen config value, not a fallback (Out of scope respected).
- `7ccfc9a` ("Set Cursor model preferences to Grok 4.7 for both tiers", `agent-skills/MODEL_PREFERENCES.md`) is a user workflow commit on the spec branch with no `Spec-Task` trailer and no spec content. It is not spec scope. Noted so the merge description mentions it.
- The T7 Makefile change is comment-only (accepted in T7 review).
- Every spec edit after approval has a change-log line.

Patterns in `task-reviews.md`:
- Five FAIL rounds:
  - T2 round 1;
  - T5 rounds 1–2, where the R9 metric gates were not really tested until a crafted suite was added;
  - T5b round 1;
  - T7 round 1 (stale "not implemented" lines).
- A recurring theme: a checked test box backed by a test that cannot fail (T4 F5 isolation negative control, T5 recording fake). Later rounds fixed each one with a wrong-value or negative control.
- Models: Sonnet 5.5, Composer 2.5 and Grok 4.7 implemented; Opus 5.5 and Grok 4.7 reviewed. T5 round 3 used the same model ID for implementer and reviewer, by the user's assignment. Cursor rounds did not measure usage.

### Remediation required

None. No BLOCKING or MAJOR finding. F1–F4 are MINOR carry-overs (recorded in `CURRENT_STATE.md`). No SPEC_DEFECT item.

### Notes for the next spec

- **Spec 013 (HTTP route and serving):**
  - the serving items in `CURRENT_STATE.md` ("Spec 013 serving items"): the `open_retrieval` rework (011 F1/F2/F3, 008 F4), Qdrant client and model lifecycle, async freshness, lexical startup and tokenizer policy, circuit breaker, reranker reload and health;
  - a binding per-request budget whose generation share is `deadline_s`;
  - a **hard wall-clock generation cap** (today `deadline_s` is soft: three overruns of about 32 s against 30 s), with the `config/generation.yaml` comment fixes (`deadline_s`, `backoff_s`, `bedrock.model_id`; F2);
  - streaming;
  - the route must resolve `rerank.enabled` and `default_generator` from config (011 F2), and must map `AnswerResponse` without exposing `sub_reason` text the client does not need.
- **Prompt v2 spec:** the `model_url` habit is the main input. 6 of Sonnet's 15 v4 refusals are backend-enforced, and the rate would be 9/17 (0.5294) without them, so the 0.86 threshold is met through validation, not the model's judgement. Further inputs:
  - marker use (Haiku `marker_mismatch`);
  - the answer language for romanized input (g080);
  - a deterministic safe-redirect marker with `safe_handling_rate` and generation result 1.2 (u001, u003 count as false misses today);
  - usage on raised outcomes (F1), so cost comparisons stay honest when `max_tokens` cases appear.
- **Security labels (F3):** retarget the `DEFERRED_OWNERS` and `UNANSWERABLE_OWNER` `roadmap-10` labels when item 12 or prompt v2 runs the s005/s006 queries through the answer path.
- **Bedrock switch:** its own spec or task once AWS grants access. It needs the Bedrock D-A smoke test (`W2A_RUN_BEDROCK_SMOKE=1`, `global.` profiles), a timeout and latency re-check, and a decision on the response-model check, which Bedrock does not apply by design. Every latency figure in D090 is a direct-API figure from the user's network.
- **Evaluation:**
  - refusal rates rest on 17 unanswerable cases (one case is about 5.9 %);
  - expected-facts coverage is English-substring only (0 for Malayalam script);
  - citation validation proves provenance, not faithfulness (D083). A faithfulness check (item 12) has the contradiction candidate and g088 to start from.
- **Process:** T5 needed three rounds because metric tests asserted that keys exist, not values. For any new metric or gate, plan a crafted case set with exact expected values and a wrong-value control in the task box itself.

### Final handoff

- Outcome **PASS**. No BLOCKING or MAJOR finding, four MINOR carry-overs (F1–F4), no RM tasks, docs reconciled.
- Merging `spec/012` into `main` can proceed after the user approves. The orchestrator then commits `review.md`, the `CURRENT_STATE.md` and `design.md` edits, the `tasks.md` Status line and the `graphify-out/` rebuild.
- After the merge, the spec row becomes `verified`.
