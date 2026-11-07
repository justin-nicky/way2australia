# Spec 012 — task reviews

## T1 — round 1

### Implementation
- Model: claude-sonnet-5-5 (Sonnet 5.5), run as a subagent; intended tier BEST_MINUS_ONE per `agent-skills/MODEL_PREFERENCES.md`, tier match not checked against the table.
- Files changed:
  - Moved (`git mv`, function unchanged) `evaluation/script_mix.py` to `packages/rag/src/way2australia_rag/script_mix.py`; import updated in `evaluation/retrieval_eval.py` and in `tests/evaluation/test_script_mix.py`. `evaluation/cli.py` has no `script_mix` import (only the `by_script_mix` slice key string), so it needed no edit. No re-export shim.
  - New `packages/rag/src/way2australia_rag/generation/`: `__init__.py` (docstring only, no exports), `config.py` (`ContextConfig`: `max_blocks` and `max_chars`, both `ge=1`), `context.py` (`EvidenceBlock`, `ContextStats`, `ContextBuilder`).
  - New `packages/rag/tests/generation/{__init__,test_context}.py` (18 tests).
- Verification run:
  - targeted `pytest packages/rag/tests/generation packages/rag/tests/evaluation` → 446 passed; `make lint typecheck` clean (0 pyright errors);
  - `HF_HUB_OFFLINE=1 HF_HOME=$(mktemp -d) make verify` (the single run) → 1512 passed, 3 skipped;
  - `git status --porcelain -- evaluation knowledge config` → empty.
  - Not run: `make test-integration` (T1 does not require it).
- Notes:
  - Budget: blocks are added in rank order; the first block that would exceed `max_blocks` or `max_chars` ends the list (so a lower-ranked block never fills a gap left by an oversized higher-ranked one). `dropped_by_budget` counts all remaining deduplicated hits. `chars` is the summed raw `chunk_text` length of kept blocks.
  - Normalization (NFC, whitespace to one space, strip) is the comparison key only; kept blocks hold the original `chunk_text`.
  - `ContextStats` lives in `generation/context.py` as the task says; T2 may move it to `models.py`.
  - The grep test reads names and codes from `config/language_registry.json` (display names, `product_support` keys, `internal_code` as a quoted literal) and scans every `generation/*.py`.
  - A code comment in `context.py` points to the design's no-neighbour-merge paragraph ("Data flow" step 2).
- Usage: 135K tokens · 69 tool uses · 12:32
### Review
- Model: claude-opus-5-5 (Opus 5.5), run as a subagent; intended tier BEST (Claude Code `Opus`) matches.
- Verdict: PASS
- Commands: `uv run pytest packages/rag/tests/generation packages/rag/tests/evaluation` (via `python3 -m uv`) → 446 passed; `HF_HUB_OFFLINE=1 HF_HOME=$(mktemp -d) make verify` → pass (1512 passed, 3 skipped); `git status --porcelain -- evaluation knowledge config` → empty. `make test-integration` not required by T1, not run.
- Findings:
  - F1 [MINOR, SPEC_DEFECT, R13] The T1 box and design "Changed" table say `evaluation/cli.py` imports `script_mix`; at `HEAD` it does not (only the `by_script_mix` key string), so one import, not two, was updated. The implementer handled it correctly. → Record in the design As-built notes at T7; no code change.
  - F2 [MINOR, IMPLEMENTATION, R1] The grep test checks `product_support` keys, display names and quoted `internal_code`s (`ml`) but not a quoted `"en"` literal or `translation_pair` codes. Today `generation/` has neither; the check is narrower than "no language code literal". → Optionally widen it when `language.py` lands in T2 (where an `en` default is expected and must come from config or be explicitly allowed).
- Summary for user (PASS only):
  - Changed: new `generation/` package with `ContextConfig` and `ContextBuilder` (NFC/whitespace exact-text dedup keeping the higher rank, no neighbour merge, whole-block budget by `max_blocks`/`max_chars`, IDs `S1…Sn`, metadata copied from the hit payload, counts in `ContextStats`); `script_mix.py` moved to the package root with one import updated.
  - Verified by: 18 new context tests, the evaluation tests (446 in the targeted run) and one hub-free `make verify` (1512 passed, 3 skipped); protected paths clean.
  - Worth your attention: the budget stops at the first block that does not fit, so an oversized top-ranked block yields zero blocks (and the T4 pre-gate will then refuse with `no_evidence`) rather than letting lower-ranked blocks through; this matches design step 2 ("stop adding blocks"). `ContextStats` lives in `context.py` for now; T2 may move it to `models.py`.
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `packages/rag/src/way2australia_rag/generation/context.py` → `ContextBuilder.build`: dedup, budget, ID assignment; `EvidenceBlock`, `ContextStats`.
    2. `packages/rag/src/way2australia_rag/generation/config.py` → `ContextConfig`: the two budget caps.
    3. `packages/rag/tests/generation/test_context.py`: behaviour tests and the language grep test.
    4. Supporting edits: `script_mix.py` move (`git mv`), import in `evaluation/retrieval_eval.py` and `tests/evaluation/test_script_mix.py`, `generation/__init__.py`, `tests/generation/__init__.py`.
- Usage: 121K tokens · 24 tool uses · 12:27

### User decision
- 2026-11-07: "Approve T1. Commit and push. dont start T2 yet."

## T2 — round 1

### Implementation
- Model: composer-2.5-fast (Composer 2.5), run as a subagent; intended tier BEST_MINUS_ONE per `agent-skills/MODEL_PREFERENCES.md` — tier mismatch, continued per skill.
- Files changed:
  - New `config/prompts/registry.yaml` and `config/prompts/answer/v1/` (`system.md`, `output_schema.json`, `messages.yaml` with `# pending fluent-speaker review` above `ml`).
  - New `packages/rag/src/way2australia_rag/generation/{base,prompts,models,language}.py`.
  - `generation/context.py`: `ContextStats` moved to `models.py` (imported there).
  - New `packages/rag/tests/generation/{test_prompts,test_models,test_language}.py`; `test_context.py` grep widened for `"en"` and `translation_pair` codes (`language.py` allowlisted).
- Verification run:
  - `python3 -m uv run pytest packages/rag/tests/generation` → 39 passed (iteration, after lint/format fixes);
  - `ruff check`, `ruff format --check`, `pyright` on `generation/` → clean;
  - `make verify` (hub-free): first run failed on unused `json` import in `prompts.py`; after fix, full `make verify` blocked by agent verify-budget (2 runs/session); lint/format/pyright + generation tests re-run → pass;
  - `git status --porcelain -- evaluation knowledge config` → `?? config/prompts/` only.
  - Not run: full `make verify` after final format (reviewer); `make test-integration` (T2 does not require it).
- Notes:
  - Pinned `ANSWER_V1_SHA256` = `63b11a6dcc2185b14cc08c6d804d900aa4598a7a584c6e426d97b77e2231b415` (sorted paths under `config/prompts/`, then file bytes).
  - `PromptConfigurationError` names unknown or mismatched `(prompt_id, prompt_version)` pairs for exit 2 at CLI load sites (T4).
  - `message_language` uses `_FALLBACK_MESSAGE_LANGUAGE = "en"` in `language.py` only (grep allowlist); maps via caller-supplied `script_to_language`.
  - Pre-existing dirty file outside task scope: `docs/project/CURRENT_STATE.md` (not edited this round).
  - **Malayalam `insufficient_evidence` message (pending fluent-speaker review):** ഈ ചോദ്യത്തിന് വിശ്വസിക്കാവുന്ന മറുപടി നൽകാൻ അനുമതി നൽകിയ തെളിവ് മതിയല്ല. ചോദ്യം വീണ്ടും രൂപപ്പെടുത്തുക, അല്ലെങ്കിൽ കാലബന്ധിത നിയമങ്ങളും ഫീസുകളും കുറിച്ച് ഔദ്യോഗിക NAATI അല്ലെങ്കിൽ Home Affairs ഉറവിടങ്ങൾ പരിശോധിക്കുക.
- Verify budget: 3 `make verify` attempts in transcript; budget is 2 per session.
- Usage: not measured

### Review
- Model: Grok 4.7, run as a subagent; intended tier BEST (Cursor `Grok 4.7`) matches.
- Verdict: FAIL
- Commands: `HF_HUB_OFFLINE=1 HF_HOME=$(mktemp -d) python3 -m uv run pytest packages/rag/tests/generation -q` → pass (39 passed); `HF_HUB_OFFLINE=1 HF_HOME=$(mktemp -d) make verify` → fail (exit 2 at typecheck: ruff check passed, ruff format 210 files already formatted, pyright 5 errors in `packages/rag/tests/generation/test_models.py`; skills-check, validators and pytest not reached); `git status --porcelain -- evaluation knowledge config` → `?? config/prompts/` only. `make test-integration` not required by T2, not run.
- Findings:
  - F1 [MAJOR, IMPLEMENTATION, R3] `make verify` stops in pyright. `_identity` in `packages/rag/tests/generation/test_models.py` is annotated `-> dict` but returns `AnswerIdentity`, so the return and the four `identity=` call sites are type errors. The 39 generation tests pass at runtime. → Annotate `_identity` as returning `AnswerIdentity` (module-level import) so typecheck is clean.
  - F2 [MINOR, IMPLEMENTATION, R2] `generation/prompts.py` imports `inside` and `read_json` from `evaluation.suite`. The design moved `script_mix` to the package root so `generation/` does not import `evaluation/`. Invalid `output_schema.json` or a path that escapes the repo raises `EvaluationConfigurationError` instead of `PromptConfigurationError` naming the pair. → Read the schema and confine paths inside `prompts.py` (re-raise `PromptConfigurationError`); no import from `evaluation`.
  - F3 [MINOR, IMPLEMENTATION, R3] `test_system_text_language_clauses_and_no_language_name` pins the first two D-D clauses and rejects product display names. The third assert only checks that `naati` and `ccl` occur somewhere, and both already appear in the role and source-precedence lines, so removing the "keep NAATI, CCL, test names and numbers in English" bullet would still pass. The bullet is present in `system.md` today. → Assert a phrase that exists only in that bullet (for example `numbers in english` or `whatever the answer language`).
- Malayalam `insufficient_evidence` message, still under `# pending fluent-speaker review` (not a finding; header stays until you approve or replace it, then the header comes off and the pinned hash is updated in this task): ഈ ചോദ്യത്തിന് വിശ്വസിക്കാവുന്ന മറുപടി നൽകാൻ അനുമතി നൽകിയ തെളിവ് മതിയല്ല. ചോദ്യം വീണ്ടും രൂപപ്പെടുത്തുക, അല്ലെങ്കിൽ കാലബന്ധിത നിയമങ്ങളും ഫീസുകളും കുറിച്ച് ഔദ്യോഗിക NAATI അല്ലെങ്കിൽ Home Affairs ഉറവിടങ്ങൾ പരിശോധിക്കുക.
- Usage: not measured

## T2 — round 2

### Implementation
- Model: composer-2.5-fast (Composer 2.5), run as a subagent; intended tier BEST_MINUS_ONE per `agent-skills/MODEL_PREFERENCES.md` — tier mismatch, continued per skill.
- Files changed:
  - `packages/rag/tests/generation/test_models.py`: `_identity` → `AnswerIdentity` (module-level import; F1).
  - `packages/rag/src/way2australia_rag/generation/prompts.py`: local `_inside` / `_read_json` → `PromptConfigurationError`; dropped `evaluation.suite` import (F2).
  - `packages/rag/tests/generation/test_prompts.py`: third D-D clause pinned with `whatever the answer language` (F3).
  - `.kiro/specs/012-grounded-generation/tasks.md`: State → `in task review (round 2)`.
- Verification run:
  - `HF_HUB_OFFLINE=1 HF_HOME=$(mktemp -d) make verify` → fail (exit 2): ruff check/format and pyright (0 errors) passed; skills-check and validators passed; full pytest 1527 passed, 7 failed (`test_lexical_cli` git-init tests and `test_git_state_ignores_only_untracked_result_files`) — sandbox `git init` restrictions, unrelated to T2;
  - Generation suite: 39 passed (within full pytest);
  - `git status --porcelain -- evaluation knowledge config` → `?? config/prompts/` only.
  - Not run: `make test-integration` (T2 does not require it).
- Notes:
  - Remediation only for review F1–F3; no other code or `CURRENT_STATE.md` edits.
- Usage: not measured

### Review
- Model: Grok 4.7, run as a subagent; intended tier BEST (Cursor `Grok 4.7`) matches.
- Verdict: PASS
- Commands: `HF_HUB_OFFLINE=1 HF_HOME=$(mktemp -d) make verify` → first run exit 2 at skills-check (gitignored `agent-skills/workflow-reviewer/scripts/__pycache__`, outside T2; ruff check passed, ruff format 210 files already formatted, pyright 0 errors; pytest not reached). After removing that cache, the same command → pass (exit 0): ruff check passed, ruff format 210 files already formatted, pyright 0 errors, skills-check 6 skills, validate-knowledge OK, validate-evaluation OK, pytest 1534 passed, 3 skipped, 1537 collected (39 of them in `packages/rag/tests/generation`). `git status --porcelain -- evaluation knowledge config` → `?? config/prompts/` only. `make test-integration` not required by T2, not run.
- Findings: none. Round 1 F1–F3 are fixed.
- Summary for user (PASS only):
  - Changed: T2 adds prompt `answer` v1 under `config/prompts/` and the answer contract in `packages/rag/src/way2australia_rag/generation/`. `PromptRegistry` checks a SHA-256 of each version's files (sorted path, then bytes) and refuses an unknown or mismatched pair. `render_prompt` places escaped evidence blocks, then the question. `AnswerResponse` is the frozen status/reason contract; `message_language` returns the first mapped non-English script, otherwise `en`. Round 2 only repairs the three review findings: `_identity` returns `AnswerIdentity`, prompt file reads live in `prompts.py` and raise `PromptConfigurationError`, and the third language clause is pinned on `whatever the answer language`.
  - Verified by: `make verify` passed (1534 passed, 3 skipped, 1537 collected), including 39 generation tests. Protected-path status lists only new `config/prompts/`.
  - Worth your attention: The Malayalam `insufficient_evidence` sentence is still under `# pending fluent-speaker review`. Approving T2 means approving or replacing this sentence; the header then comes off in this task and the pinned hash in `config/prompts/registry.yaml` and `ANSWER_V1_SHA256` is updated before commit. Sentence: ഈ ചോദ്യത്തിന് വിശ്വസിക്കാവുന്ന മറുപടി നൽകാൻ അനുമതി നൽകിയ തെളിവ് മതിയല്ല. ചോദ്യം വീണ്ടും രൂപപ്പെടുത്തുക, അല്ലെങ്കിൽ കാലബന്ധിത നിയമങ്ങളും ഫീസുകളും കുറിച്ച് ഔദ്യോഗിക NAATI അല്ലെങ്കിൽ Home Affairs ഉറവിടങ്ങൾ പരിശോധിക്കുക. The English fallback is `_FALLBACK_MESSAGE_LANGUAGE = "en"` in `language.py`, allowlisted by the generation source test. `docs/project/CURRENT_STATE.md` is already dirty from earlier in the spec, and its spec table still says T2 has not started; refresh it before the commit.
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `packages/rag/src/way2australia_rag/generation/prompts.py` → `PromptRegistry`, `render_prompt`: load a version, check its hash, render the user message.
    2. `config/prompts/registry.yaml` and `config/prompts/answer/v1/` (`system.md`, `output_schema.json`, `messages.yaml`): the versioned prompt asset, including the pending Malayalam sentence.
    3. `packages/rag/src/way2australia_rag/generation/models.py` → `AnswerResponse`, `AnswerIdentity`: status, reason, citations, evidence, identity.
    4. `packages/rag/src/way2australia_rag/generation/base.py` → `GeneratorInfo`, `GeneratorUsage`: generator identity fields the answer records (the Protocol is T3).
    5. `packages/rag/src/way2australia_rag/generation/language.py` → `message_language`: script mix to a message language code.
    6. Supporting edits: `generation/context.py` (`ContextStats` now imported from `models.py`); `tests/generation/test_context.py` (language-literal grep widened); `test_prompts.py`, `test_models.py`, `test_language.py`.
- Usage: not measured

### User decision
- 2026-11-07: "Approve T2, with this replacement for the ml insufficient_evidence message (fluent-speaker approved, remove the pending header): ഈ ചോദ്യത്തിന് സുരക്ഷിതമായി മറുപടി നൽകാൻ ആവശ്യമായ അംഗീകൃത വിവരങ്ങൾ എന്റെ പക്കൽ ഇല്ല. ചോദ്യം മറ്റൊരു രീതിയിൽ ചോദിച്ചുനോക്കുക, അല്ലെങ്കിൽ മാറിക്കൊണ്ടിരിക്കുന്ന നിയമങ്ങൾക്കും ഫീസുകൾക്കും NAATI-യുടെയോ Home Affairs-ന്റെയോ ഔദ്യോഗിക ഉറവിടങ്ങൾ പരിശോധിക്കുക. I also confirm the answer-language rule in system.md. Recompute the registry sha256 and ANSWER_V1_SHA256, run the prompt tests, then commit with Spec-Task: 012/T2 and push."
- Applied: `ml` message replaced and the pending header removed in `config/prompts/answer/v1/messages.yaml`; version hash recomputed with `compute_version_sha256` (was `63b11a6dcc2185b14cc08c6d804d900aa4598a7a584c6e426d97b77e2231b415`, now `7284d3b35cbdd4e5ff18570b770ae1d8c54153e9be3e04bdec6e8be8a6d55c11`) in `config/prompts/registry.yaml` and `ANSWER_V1_SHA256`; `pytest packages/rag/tests/generation` → 39 passed. The earlier full `make verify` (1534 passed, 3 skipped) predates this content change.

## T3 — round 1

### Implementation
- Model: claude-sonnet-5-5 (Sonnet 5.5), run in the user's own session via `/spec-implementer 012 T3`; intended tier BEST_MINUS_ONE (Claude Code `Sonnet`) matches.
- Files changed:
  - New `generation/errors.py`, `fake.py`, `bedrock.py`, `build.py`; `base.py` gains `Generator`, `GeneratorOutput` and `GeneratorInfo.model_id_source` (required; `test_models.py` updated for it); `config.py` gains the full `GenerationConfig` and `load_generation_config`.
  - New `config/generation.yaml` (the only protected-path change): `default_generator: null`, `bedrock.model_id: null`, `inference_profile: null`, null pricing, other values from the design.
  - `packages/rag/pyproject.toml` (`bedrock = ["anthropic[bedrock]>=2.0.0,<3"]`), `uv.lock` (`uv lock`: anthropic 2.6.0, boto3/botocore 1.43.126 and their dependencies), `Makefile` (`setup-bedrock`; `make setup` unchanged and still drops the extra).
  - Tests: `tests/generation/test_fake.py`, `test_bedrock.py`, `test_generation_config.py`, `test_bedrock_smoke.py` (opt-in), plus `conftest.py` (autouse fixture removing `AWS_*`, `W2A_BEDROCK*`, `W2A_RUN_BEDROCK_SMOKE`) and `support.py` (shared block/prompt helpers).
- SDK facts used (Spec rule: from documentation, not memory). Pages read 2026-11-07: https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock, https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python, https://platform.claude.com/docs/en/build-with-claude/structured-outputs, https://platform.claude.com/docs/en/build-with-claude/effort.
  - Clients: `AnthropicBedrock` (InvokeModel, `endpoint: runtime`) and `AnthropicBedrockMantle` (Messages API, `endpoint: mantle`), both with `aws_region=` and `max_retries=`; default AWS credential chain.
  - SDK version: 2.0.0 is the first release on API version `2026-10-21`; the extra is pinned `>=2.0.0,<3`. The resolved lock version is 2.6.0 (not installed in the venv; no test needs it).
  - Per-attempt timeout via `client.with_options(timeout=...)`; request fields `model`, `max_tokens`, `system`, `messages`, `output_config={"format": {"type": "json_schema", "schema": ...}, "effort": ...}`; error classes `APIConnectionError`, `APITimeoutError`, `APIStatusError` (`status_code`, `response.headers`) with the status table from the Python SDK page.
  - Docs say Mumbai (`ap-south-1`) is a Global-endpoint region for the Messages-API (mantle) Bedrock page; the runtime (InvokeModel) availability for Sonnet 5.5 and Haiku 5.5 in `ap-south-1` is not stated there. The user-owned smoke test settles both endpoints.
- Verification run:
  - iteration: `pytest packages/rag/tests/generation` → 128 passed, 1 skipped (the smoke test); `make lint typecheck` clean (0 pyright errors);
  - `HF_HUB_OFFLINE=1 HF_HOME=$(mktemp -d) make verify` (second and final run) → 1623 passed, 4 skipped;
  - `git status --porcelain -- evaluation knowledge config` → `?? config/generation.yaml` only (`config/prompts/` is committed from T2).
  - Not run: `make test-integration` (T3 does not require it); the smoke test (user-owned, never run by agents).
- Notes:
  - First `make verify` run stopped at `skills-check`: the local, untracked `workflow-reviewer` mirrors under `.claude/`, `.agents/`, `.kiro/` differed from `agent-skills/` (not part of this task). `make skills-sync` regenerated them (git-ignored; no tracked file changed); the second run passed. This is the same condition the T2 review recorded.
  - Classification is by exception **type name** through the MRO (`APITimeoutError`, `APIConnectionError`, `APIStatusError` plus `status_code`; botocore credential and region error names), so no SDK import is needed to classify and the tests use stand-in classes with the SDK's names. A wrapped error is classified only through the explicit `__cause__` chain (depth 4); `__context__` is ignored (tested).
  - `retry-after` within the deadline raises the delay to that value; one that does not leave more than 1 s before the deadline stops the loop with `DEADLINE` without sleeping (the spec text "honoured only if it fits" leaves the not-fit action open; this choice avoids retrying earlier than the server asked).
  - Credential failures raised while building or calling the client become `GeneratorConfigurationError`; messages carry the exception class name and HTTP status only.
  - `load_generation_config` takes an optional `repo_root` (default: the repository containing the package) to find `config/retrieval.yaml` and `config/prompts/` for the `top_k` and prompt-pair checks. `ContextConfig` stays in `generation/config.py` (T1).
  - `build_generator` takes `model_id_override_source` (`cli` default, `env` for the smoke test) so the identity records where the model ID came from.
  - FakeGenerator hooks are a `FakeMode` enum plus `citations=`, `unavailable=`, `record=`; `marker_mismatch` lists IDs with no marker in the text.
- Usage: (orchestrator)

### Review
- Model: claude-opus-5-5 (Opus 5.5), run as a subagent in a fresh session; intended tier BEST (Claude Code `Opus`) matches; different model from the implementer (Sonnet 5.5).
- Verdict: PASS
- Commands: `uv run pytest packages/rag/tests/generation -q` → 128 passed, 1 skipped (the opt-in smoke test). `HF_HUB_OFFLINE=1 HF_HOME=$(mktemp -d) make verify` (one run) → pass (exit 0): ruff check passed, ruff format clean, pyright 0 errors, skills-check 6 skills, validate-knowledge OK, validate-evaluation OK, pytest 1623 passed, 4 skipped. `git status --porcelain -- evaluation knowledge config` → `?? config/generation.yaml` only (matches "Allowed protected-path changes"). `make test-integration` not required by T3, not run. Smoke test not run (user-owned).
- SDK facts checked against the cited pages (read 2026-11-07): `AnthropicBedrock` (bedrock-runtime / InvokeModel path) and `AnthropicBedrockMantle` with `aws_region=`; `max_retries=0` at construction; `client.with_options(timeout=...)` per request raising `APITimeoutError`; `APIConnectionError`, `APIStatusError.status_code` / `.response`; `output_config.format` `{type: json_schema, schema}` and `output_config.effort`; `stop_reason` `refusal` / `max_tokens`; 2.0.0 is the first SDK release on API version `2026-10-21` (extra `>=2.0.0,<3`; lock 2.6.0). `uv.lock` only adds packages; no existing version changed.
- Other checks: D-B table matches the design exactly (408/429/500/502/503/504/529 eligible; 400/401/403/404 and credential errors → configuration error; others propagate; `__cause__` only, `__context__` ignored, tested). Deadline: no attempt starts with ≤ 1 s left; per-attempt timeout `min(request_timeout_s, remaining)`; `DEADLINE` raised mid-retry (traced the 25 s + 3.5 s test by hand). Committed config has `default_generator`, `bedrock.model_id`, `inference_profile` and pricing null, read from the file in a test. No retrieval, rerank, lexical, ingestion or `apps/api/` file changed. No language literal added in `generation/`.
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R5] A `retry-after` that does not fit before the deadline stops at once with sub-reason `deadline`, although the deadline has not been reached and the cause was throttling (`bedrock.py` `generate`). The design leaves the not-fit action open, and the hand-off records the choice, but T6's `generator_unavailable` counts by sub-reason will report these as `deadline`, not `throttled`. → Either raise the last error's reason (`throttled`) here, or keep it and record the choice in the design As-built notes (T7).
  - F2 [MINOR, IMPLEMENTATION, R5] `test_importing_generation_modules_does_not_import_the_sdk` cannot fail in the default environment: `anthropic`, `boto3` and `botocore` are not installed, so they can never be in `sys.modules`. It only guards the rule after `make setup-bedrock`. → A meta-path finder in the subprocess that records any attempt to import those names would make it effective without the extra.
- Summary for user (PASS only):
  - Changed: T3 adds the `Generator` Protocol and `GeneratorOutput` (`generation/base.py`), the error types (`errors.py`), a deterministic `FakeGenerator` with every R4 hook (`fake.py`), `BedrockGenerator` with its own retry and deadline loop and the D-B error table (`bedrock.py`), `build_generator` (`build.py`), the full `GenerationConfig` loader (`config.py`) and the committed `config/generation.yaml` (no default generator, model or pricing, per D-C). The `bedrock` extra (`anthropic[bedrock]>=2.0.0,<3`) and `make setup-bedrock` are new; `make setup` still drops it.
  - Verified by: `make verify` once (1623 passed, 4 skipped; ruff and pyright clean), 128 generation tests; SDK names checked against the Anthropic docs pages.
  - Worth your attention: (1) Smoke test before T6: `make setup-bedrock`, then `W2A_RUN_BEDROCK_SMOKE=1 W2A_BEDROCK_MODEL_ID=<id> uv run pytest packages/rag/tests/generation/test_bedrock_smoke.py -s` per model. It uses the committed `endpoint: runtime`; trying `mantle` means editing `config/generation.yaml` locally for that run. The Bedrock docs page says `ap-south-1` is Global-endpoint only for the Messages API (mantle), and documents InvokeModel on a separate page titled "Opus 4.6 and earlier", so check early whether Sonnet 5.5 / Haiku 5.5 answer on `runtime` in Mumbai. Model IDs there take the form `anthropic.claude-sonnet-5-5`. (2) F1: a too-long `retry-after` is reported as `deadline`, not `throttled`. (3) F2: the lazy-import test only bites once the extra is installed.
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `packages/rag/src/way2australia_rag/generation/build.py` → `build_generator`: picks fake or Bedrock, refuses a missing generator or model ID (D-C).
    2. `packages/rag/src/way2australia_rag/generation/bedrock.py` → `BedrockGenerator.generate`, `classify_error`, `_parse`: attempt/deadline loop, D-B table, structured-output parsing.
    3. `packages/rag/src/way2australia_rag/generation/fake.py` → `FakeGenerator.generate`, `FakeMode`: the hooks every later test and gate uses.
    4. `packages/rag/src/way2australia_rag/generation/base.py` → `Generator`, `GeneratorOutput`, `GeneratorInfo.model_id_source`.
    5. `packages/rag/src/way2australia_rag/generation/errors.py` → `UnavailableReason` and the four error types.
    6. `packages/rag/src/way2australia_rag/generation/config.py` → `GenerationConfig`, `load_generation_config`, `_check_cross_files` (top_k vs rerank depth, prompt pair); then `config/generation.yaml`.
    7. `packages/rag/tests/generation/test_bedrock.py`: stub client, fake clock, D-B table, deadline and retry-after cases.
    8. `packages/rag/tests/generation/test_generation_config.py`, `test_fake.py`, `test_bedrock_smoke.py` (opt-in, user-owned).
    9. Supporting edits: `tests/generation/conftest.py` (removes `AWS_*`), `support.py`, `test_models.py` (new required field), `packages/rag/pyproject.toml`, `uv.lock`, `Makefile` (`setup-bedrock`).
- Usage: 181K tokens · 40 tool uses · 7:45

### User decision
- 2026-11-07: "Approve T3. Add two boxes to T4, with a dated change-log line in `requirements.md` citing the T3 review: (1) F1 … raise `GeneratorUnavailableError(verdict)` so the sub-reason stays `throttled` / `unavailable` / etc.; use `deadline` only when no error caused it. Test both cases. (2) F2: make the lazy-import test fail without the `bedrock` extra by recording import attempts of the SDK modules in its subprocess. Then commit T3 with `Spec-Task: 012/T3` and push `spec/012`."
- Applied: two boxes added to T4 and a dated change-log line in `requirements.md` (F1 and F2 of the T3 review).

### D-A smoke-test findings so far (user-run, 2026-11-07; results to follow)
- AWS principal: IAM user `w2a-dev` (Bedrock invoke/read policy only), not root.
- In `ap-south-1`, `anthropic.claude-sonnet-5-5` and `anthropic.claude-haiku-5-5` support `INFERENCE_PROFILE` only (no on-demand). The only profiles are `global.anthropic.claude-sonnet-5-5` and `global.anthropic.claude-haiku-5-5`; there is no `apac.` profile. T6 must therefore set `bedrock.inference_profile` to a `global.` profile, and the T6 decision must record that requests may be processed outside India (data-residency trade-off).
- `aws login` credentials need `botocore[crt]`, which the `bedrock` extra lacks (`MissingDependencyException`). Workaround used: `eval "$(aws configure export-credentials --format env)"`. Decide at T6/T7 whether to add `botocore[crt]` to the extra or document the workaround in `COMMANDS.md`.
- Smoke runs use the profile ID as `W2A_BEDROCK_MODEL_ID` (the adapter sends `inference_profile or model_id`).
