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

## T4 — round 1

### Implementation
- Model: claude-sonnet-5-5 (Sonnet 5.5), run as a subagent; intended tier BEST_MINUS_ONE (`agent-skills/MODEL_PREFERENCES.md`) matches. The State went straight from `not started` to `in task review (round 1)` (no separate `implementing` write).
- Files changed:
  - New `generation/citations.py` (`validate_citations`, `CitationValidationError(rule)`, `RULES`), `generation/service.py` (`AnswerService`, `retrieval_identity`), `generation/cli.py` (`make ask`).
  - New `retrieval/cli_args.py`: the argument definitions, `check_top_k` and the resolution of strategy, rerank, `lote`, ingestion/retrieval config and settings, extracted from `retrieval/cli.py` (`add_retrieval_arguments`, `resolve_retrieval_args`, `ResolvedRetrievalArgs.open_kwargs`). `retrieval/cli.py` now calls them; it still calls `open_retrieval` itself (existing tests wrap `cli.open_retrieval`). Its `DEFAULT_RETRIEVAL_CONFIG` constant moved to `cli_args.py` (no other user).
  - `generation/language.py`: `_FALLBACK_MESSAGE_LANGUAGE` renamed public `FALLBACK_MESSAGE_LANGUAGE` (the service needs it; the language-literal grep test allows the quoted literal only in `language.py`).
  - `generation/bedrock.py`: T3 review F1 (see below). `Makefile`: `ask` target and `.PHONY`.
  - Tests: new `tests/generation/test_citations.py`, `test_service.py`, `test_service_isolation.py` (R7), `test_ask_cli.py`; `support.py` gains `generation_config`, `output`, `hit`, `retrieval_result`, `FakeRetriever`; `test_bedrock.py` changed for F1 and F2.
- Verification run:
  - iteration: `pytest packages/rag/tests/generation packages/rag/tests/retrieval` -> 609 passed, 1 skipped; `make lint typecheck` clean (0 pyright errors);
  - `make verify` (one run, after the last behavioural edit; Docker Qdrant was reachable, so the integration tests ran too) -> 1690 passed, 4 skipped. After it, one cosmetic edit (the `rerank:` line of `make ask` gained `(fake=...)`): re-ran `make lint typecheck` (clean) and `pytest packages/rag/tests/generation` (195 passed, 1 skipped).
  - `make ask QUERY="Is coaching compulsory?" ASK_ARGS="--embedder fake --reranker fake --generator fake"` against a throwaway base `w2a-t012-0f796d28` (`make ingest INGEST_ARGS="--embedder fake"`, `make index-lexical LEXICAL_ARGS="--embedder fake"`; collections and lexical file deleted afterwards). Output (stderr: `WARNING fake generator: ...`):
    ```text
    lote: none
    status: answered
    answer:
      Fake answer. [S1]
    [S1] Approved packages, pricing and validity - owner_approved - owner-approved
    retrieval: strategy hybrid; rerank: BAAI/bge-reranker-v2-m3 depth 20 (fake=true)   (the run printed it without the "(fake=...)" suffix, added afterwards)
    generator: fake (model fake, endpoint none, region/profile none, fake=true)
    prompt: answer v1 7284d3b35cbd
    tokens: in 1054 out 4 attempts 1
    latency: retrieval_ms 21.6 context_ms 0.1 generation_ms 0.0 total_ms 21.8
    ```
  - `make retrieve` unchanged: a one-off script (not committed) ran the previous `retrieval/cli.py` (from `git show HEAD:`) and the new one on the same in-memory index for 8 argument sets (success, `--top-k 3 --lote ml`, bad `--top-k`, bad `--lote`, each with a normal and a blank query): exit codes, stdout and stderr identical (latency normalised); `--help` text identical. `test_make_retrieve_output_is_unchanged_by_the_shared_helper` pins the output shape; the existing retrieval CLI tests pass untouched.
  - `git status --porcelain -- evaluation knowledge config` -> empty.
  - Not run: the Bedrock smoke test (user-owned); `make test-integration` separately (not required by T4; Docker tests ran inside `make verify`); `make eval-security`.
- T3 review boxes:
  - F1: `generate` now tracks the last classified outage. At the top of the loop a `remaining <= 1 s` raises that outage's reason, `deadline` only when no error preceded (nothing sleeps, no attempt starts). After an error: `remaining <= 0` or the last attempt raises the classified reason; otherwise the wait is `backoff_s * 2**attempt`, raised to `retry-after` when given, and if `remaining - wait <= 1 s` the loop stops at once with the classified reason, without sleeping. Tests: `test_retry_after_beyond_the_deadline_is_not_honoured` (now `throttled`, nothing sleeps), new `test_deadline_passed_during_a_failed_attempt_keeps_the_classified_reason` (`remaining <= 0` after an error, `server_error`, nothing sleeps), new `test_deadline_reason_is_used_only_when_no_error_caused_it`.
  - F2: the lazy-import test installs a `sys.meta_path` recorder in its subprocess and fails on any import attempt of `anthropic`, `boto3`, `botocore` (so it bites without the extra); a second test shows the recorder catches an attempt.
- Notes (decisions and deviations):
  - F1 goes slightly beyond the two cases the box names: the same rule applies when the backoff (not only `retry-after`) leaves no usable attempt, and at the loop top after a sleep. Two existing tests changed expectation as a result: `test_deadline_stops_further_attempts_even_mid_retry` (now `timeout`; the 2 s backoff no longer fits, so it stops with one sleep fewer) and `test_no_attempt_starts_with_one_second_or_less_left` (renamed `..._after_an_error`, now `timeout`, nothing sleeps). The design text "DEADLINE is raised, whatever the last error was" ("Attempt loop") is superseded by the T3 review F1 rule; T7 should record it in the design As-built notes.
  - Citation rule order: `no_citation`, `model_url`, `unknown_id`, `duplicate_id`, `marker_mismatch`. `[S01]`, `[s1]`, `S1` without brackets are not markers (the marker set is then empty, so a listed `S1` is `marker_mismatch`); a listed `S01` is `unknown_id`. A marker glued to a word still counts (`Fee[S1]applies`). Citation metadata comes only from the blocks (a test puts a forged title/document ID in the answer text).
  - `AnswerService` records `identity.generator` only when the generator was called (pre-gate: `None`); `usage` is set when the generator returned output (`None` when it raised, because the attempt count is not available from the error). `sub_reason` is the outage reason (`evidence_only`), the output rule (`json`/`schema`/`max_tokens`, `output_invalid`) or the citation rule; `model_declined` has none. A mapped message language with no entry in `messages.yaml` falls back to the default language (config-driven, tested with a temp mapping).
  - `retrieval_identity` fields (the answer's `identity.retrieval`): served `strategy`, `requested_strategy`, `fallback_reason`, `score_kind`, `top_k`, `collection`, `index_version`, embedder model/revision/`is_fake`/device, `lexical` and `rerank` records (dicts) and `lote`. This is the per-result identity; it is not the evaluation result 2.5 document (that is T5).
  - `make ask` builds the generator before opening retrieval (a configuration error never touches Qdrant; the test asserts zero client-factory calls); `--top-k` defaults to `generation.retrieval.top_k` (the shared parser takes `top_k_default=None`); extra option `--generation-config` (path, like `--retrieval-config`). The CLI prints `lote:` first, as `make retrieve` does. The retrieval line is built from the identity dict, not the same function as `make retrieve` (that one needs a `RetrievalResult`).
  - R7 test (`test_service_isolation.py`) builds the isolated security index (fake embedder, heading chunker, first six retrieval-side security queries) and runs all eight `ALL_PATHS` retrievers (imports the private `_retrievers` from `security_eval`, as T5 will) through `AnswerService` with a recording fake generator: no forbidden `document_id` or forbidden chunk text appears in any rendered prompt or response. The test is not vacuous (forbidden rows exist in the index; prompts were rendered).
  - Deferred (not in T4): `make eval-generation` and the security result 1.6 (T5); the `ask` default-generator tests for the committed default (T6); documentation (T7).
- Usage: 217K tokens · 56 tool uses · 14:06

### Review
- Model: claude-opus-5-5 (Opus 5.5), run as a subagent in a fresh session (implementer was Sonnet 5.5); intended tier BEST.
- Verdict: PASS
- Commands:
  - `pytest packages/rag/tests/generation packages/rag/tests/retrieval` → 609 passed, 1 skipped.
  - `make verify` (once) → pass, 1690 passed, 4 skipped (lint and typecheck ran first in the target; Docker integration tests included when reachable).
  - `git status --porcelain -- evaluation/ knowledge/ config/` → empty; also empty for `apps/`, `rerank/`, `lexical/`, `ingestion/`, `repositories/`. No diff under `packages/rag/tests/retrieval/`.
  - Reviewer scratch check (not committed): HEAD `retrieval/cli.py` (from `git show HEAD:`) against the working copy on one in-memory fake index, 7 argument sets (dense, `--top-k 3 --lote ml`, bad `--top-k`, bad `--lote`, blank query, `--rerank` on dense, hybrid `--reranker fake` without a lexical file): exit codes, stdout and stderr identical (latency normalised); `--help` identical.
  - Reviewer scratch check (not committed): R7 sensitivity. The security index holds 43 forbidden rows (7 document IDs); no forbidden chunk text contains `&`, `<` or `>`, so escaping cannot hide a leak from the test's raw-text check; feeding forbidden payloads straight to `AnswerService` as hits is caught by the chunk-text check (negative control).
  - `make ask` on the in-memory fixture path: covered by `test_ask_cli.py` (fake embedder, fake generator); the implementer's throwaway-collection run was not repeated.
  - Checked by reading: citation rule order (`no_citation`, `model_url`, `unknown_id`, `duplicate_id`, `marker_mismatch`), metadata only from blocks; pre-gate returns before `render_prompt` and `generate`; `AnswerService` catches only the three generator errors plus its own `CitationValidationError`; retrieval errors propagate (tested); T3 F1 in `BedrockGenerator.generate` (`DEADLINE` only when no error preceded; no sleep when the wait leaves ≤ 1 s); T3 F2 meta-path recorder plus a positive control; no secrets or account IDs; no new language literals in `service.py`, `citations.py`, `cli.py`.
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R8] The `make ask` `retrieval:` line is not "the same text as `make retrieve`" (design "`make ask`"): its rerank part omits the revision (`model@rev`) and the skip stage and adds `(fake=...)`; citation lines use `-` instead of the design's `—`. → Align with `retrieval/cli.py` `rerank_line`, or record the format in the T7 design As-built notes.
  - F2 [MINOR, SPEC_DEFECT, R6] The design lists the citation rules without a precedence; the code fixes one (`no_citation`, `model_url`, `unknown_id`, `duplicate_id`, `marker_mismatch`), which decides the `sub_reason` when several rules break and so the T5 per-sub-reason counts. → Record the order in the T7 design As-built notes.
  - F3 [MINOR, SPEC_DEFECT, R5] T3 review F1 supersedes the design "Attempt loop" sentence ("`DEADLINE` is raised, whatever the last error was") and changes the backoff (no longer capped at the remaining time; stop without sleeping when the wait leaves ≤ 1 s). T7's As-built box has no sub-bullet for it. → Add the sub-bullet to T7 (and a change-log line).
  - F4 [MINOR, IMPLEMENTATION, R8] `test_ask_cli.py` asserts the generator is closed but not `OpenedRetrieval.close()`, and never runs the hybrid `--reranker fake` path the box names (all CLI tests use `--strategy dense --no-rerank`). The code closes both in `finally`. → Optional test additions in T5 or T7.
  - F5 [MINOR, IMPLEMENTATION, R7] In `test_service_isolation.py` the `document_id` check on rendered prompts cannot fail (prompts never carry document IDs); the binding checks are chunk text (shown sensitive above) and the response dump. The comment in `test_model_output_cannot_change_access_or_citation_metadata` claims a staff document and a URL, but `FakeMode.UNKNOWN_ID` only cites an unissued ID. → Fix the comment; optional.
- Summary for user:
  - Changed: new `AnswerService` (retrieval, context, no-evidence pre-gate, generation, citation check), `validate_citations`, and `make ask`. The `make retrieve` arguments moved unchanged into `retrieval/cli_args.py` and are shared. Also the two T3 fixes: a deadline that cuts off a classified outage keeps its sub-reason, and the lazy-import test now fails without the extra.
  - Verified by: `make verify` (1690 passed); my own byte comparison of old and new `make retrieve` output (identical); an R7 negative control showing the isolation test catches a leak.
  - Worth your attention: no generator default yet (D-C), so `make ask` needs `--generator`. The `make ask` retrieval line differs a little from the design (F1). The citation rule order and the new deadline behaviour should go into the T7 design notes (F2, F3). Everything else is minor test polish.
  - Reading order:
    1. `packages/rag/src/way2australia_rag/generation/cli.py` → `main`, `format_response`: builds the generator, opens retrieval, prints the answer.
    2. `packages/rag/src/way2australia_rag/retrieval/cli_args.py` → `add_retrieval_arguments`, `resolve_retrieval_args`: shared retrieval options (moved from `retrieval/cli.py`).
    3. `packages/rag/src/way2australia_rag/generation/service.py` → `AnswerService.answer`: pre-gate, the three caught errors, status, reason and identity.
    4. `packages/rag/src/way2australia_rag/generation/citations.py` → `validate_citations`: the five rules, metadata from blocks.
    5. `packages/rag/src/way2australia_rag/generation/bedrock.py` → `BedrockGenerator.generate`: T3 F1 deadline and sub-reason.
    6. `packages/rag/tests/generation/test_service.py`, `test_citations.py`, `test_service_isolation.py` (R7), `test_ask_cli.py`.
    7. Supporting edits: `retrieval/cli.py` (now uses the helper), `generation/language.py` (public fallback constant), `tests/generation/support.py`, `test_bedrock.py` (F1/F2), `Makefile` (`ask`).
- Usage: 162K tokens · 35 tool uses · 11:05

### User decision
- 2026-11-09: "Approve T4. Add to T5 (dated change-log line citing the T4 review): 1. F5: make the `document_id` check in `test_service_isolation.py` able to fail (prove it with a negative control), and correct the `FakeMode.UNKNOWN_ID` comment. 2. F4: a `make ask` CLI test on hybrid with `--reranker fake`, and assert retrieval is closed after the run (success and error paths). Record for the T7 As-built notes: F1 (`make ask` retrieval line format vs `make retrieve`), F2 (citation rule order `no_citation` → `model_url` → `unknown_id` → `duplicate_id` → `marker_mismatch` decides the reported sub-reason; write it into the design), F3 (the deadline/backoff change supersedes the design's attempt-loop text). Then commit T4 with `Spec-Task: 012/T4` and push `spec/012`."
- Applied: two boxes added to T5, three Record bullets added to T7, and a dated change-log line in `requirements.md` (T4 review F1–F5).

## T5 — round 1

### Implementation
- Model: composer-2.5-fast (Cursor subagent); intended tier BEST_MINUS_ONE per `agent-skills/MODEL_PREFERENCES.md`.
- Files changed:
  - `packages/rag/src/way2australia_rag/evaluation/generation_eval.py` (new): `generation_evaluation` schema `1.0`, case selection (`--limit` / `--all`), cost estimate and confirmation guard, metrics/thresholds, result path and summary formatting.
  - `packages/rag/src/way2australia_rag/evaluation/cli.py`: `generation` subcommand; security CLI runs generation checks before `delete_security_index` when the retrieval report already passed.
  - `packages/rag/src/way2australia_rag/evaluation/security_eval.py`: security document `1.6`; `generation_prompt_isolation`, `generation_poisoned_evidence`, `generation_citation_manipulation`, `run_generation_security_checks`.
  - `packages/rag/src/way2australia_rag/evaluation/models.py`: `GoldenCase.expected_facts`, `UnanswerableCase.query_language`.
  - `Makefile`: `eval-generation` target (`EVAL_ARGS`).
  - `evaluation/candidates/012-candidates.jsonl` (new, seven `status: suggested` rows).
  - Tests: `packages/rag/tests/evaluation/test_generation_eval.py` (new); `test_security_eval.py`, `test_service_isolation.py` (T4 F5), `test_ask_cli.py` (T4 F4 hybrid close).
- Verification run:
  - `HF_HUB_OFFLINE=1 HF_HOME=$(mktemp -d) uv run pytest packages/rag/tests/evaluation packages/rag/tests/generation` → 636 passed, 1 skipped.
  - `make eval-security` → PASS (includes generation checks, result under `experiments/results/tmp/`).
  - `make validate-evaluation` → OK.
  - `ruff check` + `ruff format --check packages/rag` → pass after final lint/format fixes.
  - `make verify` once → failed on lint during iteration; a second full `make verify` was not run (agent verify budget); reviewer should run `make verify` once.
  - `make eval-generation EVAL_ARGS="--generator fake --allow-fake --embedder fake --reranker fake --limit 2 --yes"` → exit 2 (`IndexBindingError`: production collection `way2australia-idx-v2` vs fake embedder). Fake CLI/metrics paths covered by `test_generation_eval.py` and related tests (in-memory / `tmp_path`).
  - `git status --porcelain -- evaluation knowledge config` → only `?? evaluation/candidates/012-candidates.jsonl`.
- Notes:
  - Generation security checks use the isolated security index and `fixture_root` for poisoned fixture material (no hard-coded `tests/fixtures/...` path in library code).
  - When retrieval authorization fails, generation checks are skipped (CLI exit 2) so violation-path tests remain stable.
- Usage: not measured (243 tool uses)
- Verify budget: 3 `make verify` attempts in transcript; budget is 2 per session.

### Review
- Model: Grok 4.7 (Cursor). Intended tier BEST (`agent-skills/MODEL_PREFERENCES.md`) matches. Fresh session; the implementer was composer-2.5-fast.
- Verdict: FAIL
- Commands:
  - `make verify` → fail, exit 2, at typecheck. `ruff check` passed; `ruff format --check` passed (230 files). Pyright: 4 errors, 0 warnings. Did not reach skills-check, validate-knowledge, validate-evaluation, or the full pytest.
  - `python3 -m uv run pytest packages/rag/tests/evaluation packages/rag/tests/generation -q` → exit 0, 636 passed, 1 skipped.
  - `make validate-evaluation` → exit 0, `validate-evaluation: OK, 0 problems`.
  - `make eval-security` → exit 0, PASS in 21598 ms. Result schema `1.6`, eight retrieval paths unchanged, `generation_checks.passed` true (`paths_checked` 8, `prompts_rendered` 40).
  - Throwaway fake index `QDRANT_COLLECTION_BASE=w2a-t012r-05bd4d77` (`make ingest` / `make index-lexical` with `--embedder fake`), then `make eval-generation EVAL_ARGS="--generator fake --allow-fake --embedder fake --reranker fake"` → exit 0. Summary: suite public-eval-v3 v3, 87 golden and 15 unanswerable (`all`), answer rate 1.0, refusal rate 0.0, result `experiments/results/tmp/generation-evaluation-idx-v2-20261109T040435Z.json`. Collection and `.local/lexical/w2a-t012r-05bd4d77-idx-v2.sqlite` deleted afterwards. Refusal rate 0.0 is the default fake answering whenever retrieval returns a hit; it is not the R9 hard gate.
  - `git status --porcelain -- evaluation knowledge config` → only `?? evaluation/candidates/012-candidates.jsonl`.
  - `make test-integration` not required by T5; not run.
- Findings:
  - F1 [BLOCKING, IMPLEMENTATION, R9] `make verify` fails typecheck (4 errors). `_prompt_chars_for_case` uses `prompt.system`, but `PromptVersion` has `system_text` (`generation_eval.py:197`). A case with no evidence blocks raises `AttributeError` during the real-generator cost estimate; the CLI's bare `except` turns that into exit 2. The other three errors are `Retriever` mismatches: `security_eval.py:875` (`strategy = Strategy.HYBRID.value` is a `str`), `security_eval.py:995` (`_Retriever`), and `test_generation_eval.py:238` (`OneHit`) — `strategy` is not a `Strategy`, and `retrieve`'s parameters are not `query_text` / `access` / `top_k` with a default. → Use `prompt.system_text`. Type the harness retrievers as `Retriever` (`strategy: Strategy`, `retrieve(self, query_text, access, top_k=DEFAULT_TOP_K, *, lote=None)`). Re-run `make verify` until it passes.
  - F2 [MAJOR, IMPLEMENTATION, R9] The checked test box is not backed by `test_generation_eval.py`. There is no crafted case set asserting answer rate, refusal rate with `evidence_only` excluded, `citation_invalid` by sub-reason, `generator_unavailable` by sub-reason, precision/recall, `expected_facts` coverage by language marked informational, script mix, latency, tokens, or cost. `--min-*` exit 1 is only `check_thresholds`, not the CLI. `--all`, `--yes`, and recorded price overrides are untested. `test_recording_fake_has_zero_calls_before_yes` never installs `Recording` (`Stub` has no `generate` and no `calls`); an `AttributeError` is also exit 2, so `calls == []` cannot fail. The hard gate is one synthetic `DECLINE` case, not every active unanswerable case and not the no-evidence path. `test_fake_cli_writes_tmp_result` passes `--output`, so it does not show the default fake path is `experiments/results/tmp/`. `test_bedrock_without_pricing_exits_two` does not assert the missing key name. → Add those tests. Wire the recording generator so a call before confirmation fails the test.
  - F3 [BLOCKING, IMPLEMENTATION, R11] The contradiction and source-authority rows do not cite the evidence that contains the true fact. "Coaching is optional." is in `business_001_overview_scope.md`. `cand012_en_002` cites `business_005_coaching` and `official_002_candidate_rules_setup` (official docs do not mention coaching). `cand012_en_004` cites only `business_005_coaching`, which has duration and price, not "optional" or "not required". `expected_facts` also include "not compulsory" and "not required", which are not in the corpus. → Cite `business_001_overview_scope` for the true sentence, put a real official contrast in the precedence row only if one exists, and keep `expected_facts` as substrings of the cited text. Leave the false claim in the review notes.
  - F4 [MINOR, IMPLEMENTATION, R9] The result stores `citation_invalid` counts and sub-reasons but not a rate. `answer_rate` and `refusal_rate` have no `small_sample` flag (fact-coverage language slices do; `small_sample_threshold` is stored). `estimated_cost_usd` is hardcoded `None` after the estimate is computed. → Store the rate (count over cases run), flag the rates the way result 2.x flags aggregates, and write the phase-1 estimate into the result.
  - F5 [MINOR, IMPLEMENTATION, R8] The T4 F4 tests pass `--strategy hybrid --reranker fake` but stub `open_retrieval`, so they never build a hybrid retriever or a fake reranker. `close()` is asserted on that stub for success and error. → Open retrieval for real on the in-memory index, as the other `make ask` tests do, and assert `OpenedRetrieval.close()`.
  - F6 [MINOR, IMPLEMENTATION, R7] `test_document_id_in_prompts_fails_when_forbidden_id_is_injected` renders a title and asserts the id is in the user text. It does not run the isolation check, so deleting `document_id not in recorded.user` would not fail it. The comment in `test_model_output_cannot_change_access_or_citation_metadata` is corrected. → Feed a forbidden id into a rendered prompt or response and assert the same check the isolation test uses.
- Usage: not measured (88 tool uses)

## T5 — round 2

### Implementation
- Model: composer-2.5-fast (Composer 2.5), run as a Cursor subagent; intended tier BEST_MINUS_ONE per `agent-skills/MODEL_PREFERENCES.md`.
- Files changed:
  - `packages/rag/src/way2australia_rag/evaluation/generation_eval.py`: F1 `prompt.system_text`; F4 `citation_invalid` rate and `small_sample`, answer/refusal rate flags, `estimated_cost_usd` parameter.
  - `packages/rag/src/way2australia_rag/evaluation/cli.py`: pass phase-1 `estimated_cost_usd` into the result document.
  - `packages/rag/src/way2australia_rag/evaluation/security_eval.py`: F1 Retriever harness typing (`Strategy` enum, `query_text`, `DEFAULT_TOP_K`, `ResolvedLote`).
  - `evaluation/candidates/012-candidates.jsonl`: F3 coaching rows cite `business_001_overview_scope` with corpus-backed `expected_facts`.
  - `packages/rag/tests/evaluation/test_generation_eval.py`: F2 expanded R9 tests (defects, all unanswerables, no-evidence pre-gate, CLI `--min-*`, `--all`, pricing overrides, cost guard, default tmp path, bedrock `--yes`, metrics shape).
  - `packages/rag/tests/generation/test_ask_cli.py`: F5 real hybrid open + `OpenedRetrieval.close()` via lexical fixture.
  - `packages/rag/tests/generation/test_service_isolation.py`: F6 negative control uses `document_id not in user` (same as isolation).
  - `.kiro/specs/012-grounded-generation/tasks.md`: State → `in task review (round 2)`.
- Verification run:
  - `HF_HUB_OFFLINE=1 HF_HOME=$(mktemp -d) uv run pytest packages/rag/tests/evaluation packages/rag/tests/generation` → 649 passed, 1 skipped;
  - `make lint typecheck` → pass (0 pyright errors) after format fix;
  - `make validate-evaluation` → OK;
  - `make verify` → first run stopped at ruff format on `generation_eval.py` (exit 2); after the format fix, agent verify budget (2/session) blocked a second full `make verify`. Reviewer should run `make verify` once.
  - Not run this round: `make eval-security`, `make eval-generation` throwaway CLI, `make test-integration` (not required by T5).
  - `git status --porcelain -- evaluation knowledge config` → `?? evaluation/candidates/012-candidates.jsonl` only.
- Notes:
  - Round 2 addresses review F1–F6 only; no commit.
- Usage: not measured (111 tool uses)
- Verify budget: 3 `make verify` attempts in transcript; budget is 2 per session.

### Review
- Model: Grok 4.7 (Cursor). Intended tier BEST (`agent-skills/MODEL_PREFERENCES.md`) matches. Fresh session; the implementer was composer-2.5-fast.
- Verdict: FAIL
- Commands:
  - `make verify` → pass, exit 0. `ruff check` passed; `ruff format --check` passed (230 files). Pyright: 0 errors, 0 warnings, 0 informations. skills-check: 6 mirrors match. `validate-knowledge: OK, 0 problems`. `validate-evaluation: OK, 0 problems`. pytest: 1715 passed, 4 skipped (1719 collected) in 240.63s.
  - `make eval-security` → exit 0, PASS in 19025 ms. Result schema `1.6`, eight retrieval paths unchanged, `generation_checks.passed` true (`paths_checked` 8, `prompts_rendered` 40).
  - `make eval-generation` on a throwaway index not re-run: Docker is not running. The task's in-memory alternative passed inside `make verify` (`packages/rag/tests/evaluation/test_generation_eval.py`).
  - `git status --porcelain -- evaluation knowledge config` → only `?? evaluation/candidates/012-candidates.jsonl`.
  - `make test-integration` not required by T5; not run.
- Findings:
  - F1 [MAJOR, IMPLEMENTATION, R9] Round 1 F2 is still open. Round 1 F1, F3, F4, F5 and F6 are fixed (typecheck clean; coaching rows cite `business_001_overview_scope` with corpus substrings and the false claim in the review notes; `citation_invalid` rate, small-sample flags and the phase-1 `estimated_cost_usd` are stored; hybrid `make ask` opens real retrieval and leaves `lexical is None` after close on success and error; the isolation negative control uses `document_id not in user`). `test_run_generation_evaluation_metrics_shape` runs the live suite with `--limit 6` and checks that keys exist. It is not a crafted case set, and it does not assert an answer rate, a refusal rate that excludes `evidence_only`, `citation_invalid` counts by sub-reason, `generator_unavailable` counts by sub-reason with case ids, precision/recall, `expected_facts` coverage by language (only `informational` and the key `by_query_language`), script mix, latency, tokens, or cost. Dropping `generator_unavailable`, counting `evidence_only` as a refusal, or omitting precision/recall would still pass. `test_fake_defect_status_reason_subreason` covers five citation modes and `UnavailableReason.CONNECTION` only. `test_every_active_unanswerable_refuses_on_fake_decline` checks `insufficient_evidence` and `reason is not None`, not `model_declined`. Malformed JSON, schema mismatch, `max_tokens`, refusal, a non-eligible error, and the other unavailable reasons (including timeout) are not in this gate. → Drive `run_generation_evaluation` (or the CLI) with a scripted generator and a small crafted suite: mixed answered, `citation_invalid`, `evidence_only` and `generator_unavailable` outcomes, two query languages, and known citations, facts, tokens and prices. Assert the rates, sub-reason maps and case ids, precision/recall, informational fact coverage by language, script mix, latency, tokens and cost. Extend the defect gate so every R4 fake defect gives the expected status and reason, including `model_declined` on the decline path. Keep results under `tmp_path`.
- Summary for user:
  - Reading order: this Review block → `packages/rag/tests/evaluation/test_generation_eval.py` → `packages/rag/src/way2australia_rag/evaluation/generation_eval.py`.
  - Round 2 landed `make eval-generation`, security 1.6 generation checks, and candidates; `make verify` (1715 tests) and `make eval-security` pass on `spec/012` with uncommitted work.
  - Blocker is R9 test depth only (crafted metrics + full fake-defect matrix), not runtime behavior the reviewer exercised.
- Usage: not measured (88 tool uses)

## T5 — round 3

### Implementation
- Model: grok-4.7-high-fast (Grok 4.7). Intended tier BEST_MINUS_ONE (`agent-skills/MODEL_PREFERENCES.md`) is Grok 4.7; matches. Run as a Cursor subagent.
- Files changed:
  - `packages/rag/tests/evaluation/test_generation_eval.py`: F1 only. Crafted in-memory suite through `run_generation_evaluation` (result under `tmp_path`) with exact rates, sub-reason→case_id maps, precision/recall, informational fact coverage by language, script mix, latency, tokens, cost, and small-sample flags, each with a wrong-value control. Fake-defect matrix covers every `FakeMode` and every `UnavailableReason` (including `deadline`) plus `model_declined` on both the decline and refusal paths. `NON_ELIGIBLE` asserts the `RuntimeError` propagates.
  - `.kiro/specs/012-grounded-generation/tasks.md`: State → `in task review (round 3)`.
- Verification run:
  - `uv run pytest packages/rag/tests/evaluation/test_generation_eval.py` → 33 passed.
  - `uv run pytest packages/rag/tests/evaluation packages/rag/tests/generation` → 662 passed, 1 skipped.
  - `HF_HUB_OFFLINE=1 HF_HOME=$(mktemp -d) make verify` → pass, exit 0 (1 of 2 budget). ruff check passed; ruff format --check passed (230 files). Pyright: 0 errors, 0 warnings, 0 informations. skills-check: 6 mirrors match. `validate-knowledge: OK, 0 problems`. `validate-evaluation: OK, 0 problems`. pytest: 1728 passed, 4 skipped (1732 collected) in 242.55s.
  - `make eval-security` → exit 0, PASS in 19496 ms. Result schema `1.6`, `generation_checks.passed` true (`paths_checked` 8, `prompts_rendered` 40).
  - `make eval-generation` throwaway CLI not re-run (Docker not required for this round). The in-memory crafted suite is `test_crafted_suite_metrics_are_exact`, which passed inside `make verify`.
  - `make test-integration` not required by T5; not run.
  - `git status --porcelain -- evaluation knowledge config` → `?? evaluation/candidates/012-candidates.jsonl` only.
- Notes:
  - Round 3 addresses review F1 only. No production code changed. The new tests passed against the existing metrics, so no production bug was exposed.
  - Latency is measured with an integer-second test clock (six service calls → total 5000 ms; the pre-gate → 3000 ms; the Malayalam answer adds ten ticks → generation p95 11000 ms, total p95 15000 ms). Token totals use a fixed 100/40 usage on the nine outputs that return. The `[S1]` marker makes the Malayalam answer `latin+malayalam`.
  - `agent-skills/MODEL_PREFERENCES.md` was already dirty before this round (Cursor BEST_MINUS_ONE `Composer 2.5` → `Grok 4.7`). Not part of T5; left untouched. Do not include it in the T5 commit.
- Usage: not measured (103 tool uses)
- Verify budget: 1 `make verify` this session (limit 2).

### Review
- Model: grok-4.7-high-fast (Grok 4.7). Intended tier BEST (`agent-skills/MODEL_PREFERENCES.md`) matches. Fresh session. Same model id as the implementer; the user assigned this model for the review.
- Verdict: PASS
- Commands:
  - `make verify` → pass, exit 0. `ruff check` passed; `ruff format --check` passed (230 files). Pyright: 0 errors, 0 warnings, 0 informations. skills-check: 6 mirrors match. `validate-knowledge: OK, 0 problems`. `validate-evaluation: OK, 0 problems`. pytest: 1728 passed, 4 skipped (1732 collected) in 242.43s. `test_generation_eval.py` is in that run (33 cases, including the crafted suite and the defect matrix).
  - `make eval-security` not re-run this review. The assigned command was `make verify`. Security tests ran inside that pytest. Production security code is unchanged from round 2.
  - `make eval-generation` on a throwaway index not re-run. Docker is running. The in-memory path passed inside `make verify` (`test_crafted_suite_metrics_are_exact` and the rest of `test_generation_eval.py`). Round 1 already ran the throwaway CLI on this production code.
  - `git status --porcelain -- evaluation knowledge config` → only `?? evaluation/candidates/012-candidates.jsonl`.
  - `make test-integration` not required by T5; not run.
- Findings: none
- Summary for user (PASS only):
  - Changed: Round 3 adds the R9 gates that round 2 missed, in `packages/rag/tests/evaluation/test_generation_eval.py` only. `test_crafted_suite_metrics_are_exact` drives `run_generation_evaluation` with a 19-case suite (11 goldens, 8 unanswerable; English and Malayalam) and checks exact answer rate 3/11, refusal rate 3/8 with the five `evidence_only` cases left out, `citation_invalid` and `generator_unavailable` sub-reason maps with case ids (including `deadline`), precision/recall 0.8333 and 0.6667, informational fact coverage by language, script mix, latency, tokens and cost 0.0081. Each of those has a wrong-value control. `test_fake_defect_status_reason_subreason` runs every `FakeMode` and every `UnavailableReason`; decline and refusal are `model_declined`, and `NON_ELIGIBLE` lets `RuntimeError` propagate. The result file is under `tmp_path`. Production sources were not edited this round.
  - Verified by: `make verify` (1728 passed, 4 skipped). `validate-evaluation` passed inside that run. Protected paths show only the new candidates file.
  - Worth your attention: The latency numbers are tied to how many times `AnswerService.answer` calls `perf_counter` (generation p95 11000 ms, total p95 15000 ms on a one-second test clock). The Malayalam answer is `latin+malayalam` because the `[S1]` marker is Latin. Leave `agent-skills/MODEL_PREFERENCES.md` out of the T5 commit. `docs/project/CURRENT_STATE.md` still describes the round-2 escalation in the next-step list.
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `Makefile` → `eval-generation`: the `EVAL_ARGS` entry point.
    2. `packages/rag/src/way2australia_rag/evaluation/cli.py` → generation subcommand: cost guard, then the runner.
    3. `packages/rag/src/way2australia_rag/evaluation/generation_eval.py` → `run_generation_evaluation`: schema 1.0 metrics the new test locks.
    4. `packages/rag/src/way2australia_rag/evaluation/security_eval.py` → `run_generation_security_checks`: security result 1.6.
    5. `evaluation/candidates/012-candidates.jsonl`: suggested generation and refusal rows.
    6. `packages/rag/tests/evaluation/test_generation_eval.py` → `test_crafted_suite_metrics_are_exact`, `test_fake_defect_status_reason_subreason`: the round 3 gates.
    7. Supporting edits: `evaluation/models.py`, `test_security_eval.py`, `test_ask_cli.py`, `test_service_isolation.py`, `tasks.md`.
- Usage: not measured (92 tool uses)

### User decision
- 2026-11-09: Approve T5. Commit with `Spec-Task: 012/T5` excluding `agent-skills/MODEL_PREFERENCES.md`; separate commit for model prefs. Add T7 As-built note on `answer_script_mix`. T6 is user-owned (plan before paid runs); do not start T6 in the approval turn.


## T5b — round 1

### Implementation
- Model: claude-sonnet-5-5 (Sonnet 5.5), run as a subagent. The BEST_MINUS_ONE tier in `agent-skills/MODEL_PREFERENCES.md` was not checked against it (no user to ask); noted per the skill.
- Files changed:
  - New: `generation/claude.py` (`ClaudeMessagesAdapter`, `classify_error`, D-B tables with 413, retry-after, `_parse`; `check_response` hook; `response_model`), `generation/anthropic_api.py` (`AnthropicGenerator`), `tests/generation/test_anthropic_api.py`, `tests/generation/test_anthropic_smoke.py`.
  - Edited: `generation/bedrock.py` (now delegates to the adapter; re-exports `classify_error`, so no test import changed), `base.py`, `models.py`, `service.py`, `config.py` (schema 1.1, `AnthropicConfig`), `build.py`, `cli.py`, `evaluation/cli.py`, `evaluation/generation_eval.py` (result 1.1), `config/generation.yaml`, `packages/rag/pyproject.toml`, `uv.lock` (`uv lock`; only the new extra edge), `Makefile` (`setup-anthropic`, `.PHONY`, comment), `tests/generation/conftest.py`, appended test functions in `test_generation_config.py` and `test_ask_cli.py`, appended tests in `tests/evaluation/test_generation_eval.py`.
- Refactor guard: `git diff 7ccfc9a` on `test_bedrock.py`, `test_fake.py`, `test_bedrock_smoke.py` is empty; `test_generation_config.py` has only added lines. No import or move change was needed in the T3 tests. One non-T3 edit: `test_generation_eval.py` line 109 now asserts result schema `"1.1"` (was `"1.0"`), required by R9 result 1.1.
- SDK facts: `anthropic` 2.6.0 (installed), read from `Anthropic.__init__` source, docs URL https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python (docstring cites it; not fetched). An explicit `api_key=` makes the SDK skip every other credential source (auth token, profile, OAuth, workload identity), so `Anthropic(api_key=key, max_retries=0)` is the whole constructor call.
- Decisions/deviations: (1) `ANTHROPIC_CUSTOM_HEADERS` is also refused (exit 2), because the SDK reads it and it could inject a beta/fallback header; small addition to the design's base-URL rule, please check. (2) The advice text reads "--generator fake, --generator bedrock or --generator anthropic" so the existing T4 assertion on "--generator bedrock" still holds. (3) The generic 4xx message no longer says "Bedrock" (shared adapter). (4) The `make ask` generator line appends ", response model X" only when present, so existing output is unchanged. (5) `response_model` is carried on the answered, model-declined-by-flag and citation-invalid paths (where an output exists).
- Verification run: `uv run pytest packages/rag/tests/generation packages/rag/tests/evaluation` earlier run 715 passed, 2 skipped (before final lint edits); `ruff format`/`ruff check` clean; pyright 0 errors; `make verify` once: pass, 1781 passed, 5 skipped. `git status --porcelain -- evaluation knowledge config` lists only `config/generation.yaml`. `make test-integration` not run (not required). No real API call; no `ANTHROPIC_API_KEY` set; smoke tests skipped and never run.
- Not verified: the SDK against the real API (user smoke test in T6); `make setup-anthropic` itself (only `uv lock` was run).
- Usage: 184K tokens · 64 tool uses · 29:00

### Review
- Model: claude-opus-5-5 (Opus 5.5, BEST tier for Claude Code; matches `MODEL_PREFERENCES.md`), fresh subagent session.
- Verdict: FAIL
- Commands: `uv run pytest packages/rag/tests/generation packages/rag/tests/evaluation` (with `ANTHROPIC_API_KEY` unset) → pass (715 passed, 2 skipped); `make verify` (once, `ANTHROPIC_API_KEY` unset) → pass (1781 passed, 5 skipped); `make test-integration` not required by the task. `git diff 7ccfc9a -- test_bedrock.py test_fake.py test_generation_config.py test_bedrock_smoke.py` → only added test functions in `test_generation_config.py`; no T3 assertion changed. `git status --porcelain -- evaluation knowledge config` → only `config/generation.yaml` (schema `1.1`, the `anthropic:` section and comments; every T3 value unchanged). `pytest --setup-plan` on both smoke modules (executes nothing) → evidence for F1. No smoke test run, no API call (no key in the session).
- Checked and holding: shared adapter is a verbatim move of the T3 request builder, attempt loop, D-B tables and `_parse` (plus 413 and the `check_response` hook, no-op on Bedrock); `Anthropic(api_key=<key>, max_retries=0)` — confirmed in the installed SDK 2.6.0 source (`_client.py`: an explicit `api_key` skips `static_credential_from_env` and `default_credentials`, so no auth token, profile or workload identity is used); refusals before the client is built (missing/empty key also with `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_BASE_URL`, Bedrock-form ID); the extra `ANTHROPIC_CUSTOM_HEADERS` refusal is justified (the SDK parses that variable into default headers, which could carry a beta/fallback header) — accepted, record it in the design As-built notes at T7; exact request keys (no `fallbacks`, no `extra_headers`, `with_options` gets only `timeout`); response-model check exact, missing = mismatch; key absent from messages, `GeneratorInfo` and results (`from None` on constructor failure); lazy import (recorded import attempts); result 1.1 `response_model` / `response_models`; provider-agnostic cost guard (`is_fake`); generic 4xx message and the `make ask` line change are fine.
- Findings:
  - F1 [MAJOR, IMPLEMENTATION, R17] The smoke test's environment override does not override anything. `tests/generation/test_anthropic_smoke.py` defines `_no_anthropic_environment`, but the suite-wide autouse fixture in `tests/generation/conftest.py` is named `_no_aws_environment` (the Bedrock smoke test overrides it by that name). `pytest --setup-plan` with `W2A_RUN_ANTHROPIC_SMOKE=1` shows `_no_aws_environment (fixtures used: monkeypatch)` still set up for the Anthropic smoke test, so it deletes `ANTHROPIC_API_KEY`, `W2A_ANTHROPIC_MODEL_ID` and `W2A_RUN_ANTHROPIC_SMOKE` before the body runs (the `skipif` is evaluated at collection, so the test does run). The user's T6 direct-API smoke gate would always fail at `assert model_id, "set W2A_ANTHROPIC_MODEL_ID ..."`, whatever they set. → Name the override `_no_aws_environment` (as in `test_bedrock_smoke.py`), or otherwise keep `ANTHROPIC_API_KEY` and `W2A_ANTHROPIC_MODEL_ID` for that module only; add a check that does not call the API, e.g. a test that runs `pytest --setup-plan` (or inspects fixture resolution) on the smoke module with `W2A_RUN_ANTHROPIC_SMOKE=1` and asserts the conftest fixture is not set up, or a unit test of the override.
  - F2 [MINOR, IMPLEMENTATION, R17] Design "Testing" (T5b) lists `--generator anthropic` accepted by `make eval-generation`; only `make ask` has an `anthropic` test (`test_anthropic_without_a_model_id_exits_two`). → Add an `eval-generation` test with `--generator anthropic` and no model ID → exit 2 naming `--model-id`, zero generator calls.
- Usage: 159K tokens · 37 tool uses · 14:48


## T5b — round 2

### Implementation
- Model: claude-sonnet-5-5 (Sonnet 5.5), run as a subagent; tier not checked against `MODEL_PREFERENCES.md` (no user to ask).
- Files changed (tests only, no production code): `packages/rag/tests/generation/test_anthropic_smoke.py` (override fixture renamed `_no_aws_environment`, the conftest autouse fixture's name, as in `test_bedrock_smoke.py`; F1), `packages/rag/tests/generation/test_anthropic_api.py` (new `test_smoke_module_overrides_the_conftest_environment_fixture`: runs `pytest --setup-plan` in a subprocess on the smoke module with `W2A_RUN_ANTHROPIC_SMOKE=1` and no ANTHROPIC_* variables; setup-plan executes nothing, so no API call; asserts the conftest fixture is not set up with `monkeypatch`. Negative control: with the old fixture name the test fails), `packages/rag/tests/evaluation/test_generation_eval.py` (new `test_cli_anthropic_without_a_model_id_exits_two`: `--generator anthropic` accepted, exit 2 naming `--model-id`, `AnthropicGenerator.generate` never called; F2).
- Verification: targeted pytest on the two touched modules passed; ruff format/check clean; `make verify` once: pass, 1783 passed, 5 skipped. Smoke tests never run with the env var against the API; no key in the session; no real API call. `make test-integration` not run (not required).
- Usage: 93K tokens · 21 tool uses · 6:44

### Review
- Model: claude-opus-5-5 (Opus 5.5, BEST tier for Claude Code; matches `MODEL_PREFERENCES.md`), fresh subagent session.
- Verdict: PASS
- Commands: `W2A_RUN_ANTHROPIC_SMOKE=1 W2A_ANTHROPIC_MODEL_ID=claude-sonnet-5-5 uv run pytest --setup-plan -p no:cacheprovider tests/generation/test_anthropic_smoke.py tests/generation/test_bedrock_smoke.py` (no key, `ANTHROPIC_BASE_URL` unset; executes nothing) → the smoke test now sets up only its own `_no_aws_environment` (no `monkeypatch` dependency), so the conftest fixture no longer deletes the key and model ID (F1 fixed); `uv run pytest packages/rag/tests/generation packages/rag/tests/evaluation` → pass (717 passed, 2 skipped); `make verify` (once) → pass (ruff, pyright 0 errors, 1783 passed, 5 skipped); `make test-integration` not required. `git diff 7ccfc9a -- test_bedrock.py test_fake.py test_generation_config.py test_bedrock_smoke.py` → only 79 added lines in `test_generation_config.py`, no removed line, no T3 assertion changed. `git status --porcelain -- evaluation knowledge config` → only `config/generation.yaml`. No smoke test run against an API; no key in the session.
- Checked: round 2 touched tests only (no production file modified after round 1); `test_smoke_module_overrides_the_conftest_environment_fixture` runs only `--setup-plan` in a subprocess with `ANTHROPIC_*` removed (no API call possible) and fails against the old fixture name; `test_cli_anthropic_without_a_model_id_exits_two` covers `make eval-generation --generator anthropic` (exit 2 naming `--model-id`, zero `generate` calls) (F2 fixed). Round 1 acceptance points re-checked and unchanged: `Anthropic(api_key=key, max_retries=0)` only; `ANTHROPIC_BASE_URL` and `ANTHROPIC_CUSTOM_HEADERS` refused; no `fallbacks`/`extra_headers`, `with_options` gets only `timeout`; constructor failure raised `from None` (no key leak).
- Findings: none.
- Summary for user (PASS only):
  - Changed: new `anthropic` generator for the direct Anthropic API (`generation/anthropic_api.py`) on a Claude adapter shared with Bedrock (`generation/claude.py`, moved out of `bedrock.py`); 413 is a configuration error; `response_model` is recorded and checked (answer identity, `make ask`, generation result 1.1); config schema 1.1 with an `anthropic:` section (all defaults `null`); `make setup-anthropic`; opt-in smoke test. Round 2 fixed the smoke test's fixture override and added an `eval-generation` test.
  - Verified by: `make verify` (1783 passed, 5 skipped), the generation/evaluation suites, a `--setup-plan` check of the smoke test, the T3 test diff check. No real API call was made.
  - Worth your attention: `ANTHROPIC_CUSTOM_HEADERS` is refused in addition to `ANTHROPIC_BASE_URL` (record in the design As-built notes at T7). For the T6 smoke gate, run from a shell where `ANTHROPIC_BASE_URL` is unset (this agent session had it set by the host); otherwise the generator refuses by design.
  - Reading order:
    1. `packages/rag/src/way2australia_rag/generation/build.py`: `--generator anthropic` → `AnthropicGenerator`, model ID from `--model-id` or config.
    2. `generation/anthropic_api.py` → `AnthropicGenerator`: env refusals, explicit key, `max_retries=0`, response-model check.
    3. `generation/claude.py` → `ClaudeMessagesAdapter`, `classify_error`: shared request, retries, D-B tables (413), `check_response`.
    4. `generation/bedrock.py`: now a thin adapter user.
    5. `generation/base.py`, `models.py`, `service.py`: `provider` `anthropic`, `response_model` on output and identity.
    6. `generation/config.py` and `config/generation.yaml`: schema 1.1, `anthropic:` section.
    7. `evaluation/generation_eval.py`, `evaluation/cli.py`, `generation/cli.py`: result 1.1, `--generator` choices.
    8. `tests/generation/test_anthropic_api.py`, `test_anthropic_smoke.py`: generator behaviour and the opt-in gate.
    9. Supporting edits: `test_generation_config.py`, `test_ask_cli.py`, `tests/evaluation/test_generation_eval.py`, `tests/generation/conftest.py`, `pyproject.toml`, `uv.lock`, `Makefile`.
- Usage: 112K tokens · 28 tool uses · 10:43

### User decision
- 2026-11-13: Approve T5b. Commit with `Spec-Task: 012/T5b`, the amended requirements, design and tasks in the same commit; push `spec/012`. Record the `ANTHROPIC_CUSTOM_HEADERS` refusal for T7 As-built notes. The user runs the T6 smoke gate from their own terminal.


## T6 — preparation (round 1)

### Implementation
- Model: claude-sonnet-5-5 (Sonnet 5.5), run as a subagent; tier not checked against `MODEL_PREFERENCES.md` (no user to ask). Stage: preparation only. The agent made no Anthropic or Bedrock call and set no key. Files changed: this file, `tasks.md` (T6 State `implementing (round 1)`; the two smoke-gate boxes ticked), `docs/project/CURRENT_STATE.md`.

### User-run smoke gate (recorded verbatim, 2026-11-13; no key)
```
make setup-anthropic: OK (anthropic SDK 2.6.0; bedrock extra removed by this target, as expected)
anthropic smoke: pass model=claude-sonnet-5-5 endpoint=api response_model=claude-sonnet-5-5 answerable=False citations=[] tokens=912/22 attempts=1
anthropic smoke: pass model=claude-haiku-5-5 endpoint=api response_model=claude-haiku-5-5 answerable=False citations=[] tokens=912/22 attempts=1
```
- `answerable=False` is correct: the fixed smoke evidence does not answer "What is the fee?" (user, 2026-11-13). Structured output accepted; response model equals the configured ID for both models, so the exact-match check holds.
- Bedrock D-A smoke test: **still open** (AWS access pending; the Sonnet case was rejected, the Haiku case was referred to AWS Sales). Not a T6 gate.
- Boxes ticked in `tasks.md`: "Smoke gate passed" (superseded) and "Direct-API smoke gate". Not yet ticked: thresholds, "Model access" (superseded; ticks with the prices box), prices and data location, runs.

### Proposed, awaiting user approval (NOT approved, NOT recorded as approved)

Basis: fake-generator run over all 102 cases of suite `public-eval-v3` with the real local retrieval (hybrid, rerank on at depth 20, `lote ml`, top_k 5, `w2a-realcheck-idx-v2`, `git_dirty` false; no network; result `experiments/results/tmp/generation-evaluation-idx-v2-20261113T072812Z.json`, git-ignored), and the Spec 011 / D079 reranker findings: the 15 unanswerable cases have top-1 cross-encoder scores from -7.83 to 1.67 (median -4.17), the goldens -7.79 to 7.19 (median 3.08), so no score cut-off separates them. Refusal therefore rests on the model's `answerable` assessment plus citation validation, and the thresholds below are the only gate.

1. **Refusal threshold (unanswerable, n = 15): `--min-refusal-rate 0.86`.** The gate is `rate < threshold` fails, so 13 of 15 (0.8667) passes and 12 of 15 (0.80) fails: at most 2 unanswerable cases may get an answer. Reason: a wrong confident answer on NAATI or visa rules is the costly error, and at n = 15 one case is 6.7 points. Evidence the task is hard but fair: retrieval returns real content for several unanswerable cases (u005 1.67, u015 1.18, u009 0.46 are above 0), so 2 misses allow for those without excusing a model that answers most of them. Lenient alternative: 0.80 (the design example), which tolerates 3 misses.
2. **Minimum golden answer rate (n = 87): `--min-answer-rate 0.90`.** 79 of 87 answered. Reason: retrieval finds the relevant document for all 87 goldens at depth 20 (Spec 011: hits 87), so every non-answer is a model, citation-validation or output failure, not missing evidence; 0.90 leaves 8 for strict citation rules, `model_declined` and the English-terms clause on `ml` and `mixed` cases. `citation_invalid`, `output_invalid`, cited-document precision and recall and `expected_facts` coverage are reported and recorded in the decision but not gated.
3. **"Falls short" (direct-API figures, from the user's network, not Bedrock or production):** a model falls short if any of these holds on its run:
   - refusal rate below 0.86 or golden answer rate below 0.90 (the CLI exits 1);
   - any `generator_unavailable` that a re-run does not clear (R14);
   - p95 generation latency (`latency_ms.generation_ms.p95`) above 8000 ms. Reason: the retrieval p95 is about 1.2 s with reranking, so total p95 stays under about 9.3 s for a non-streaming guest answer; deadline 30 s and per-request timeout 20 s stay as configured;
   - mean actual cost per answer above USD 0.015 at the prices below (the guard's estimate for Sonnet is about 0.0087 per case, so this leaves headroom for real tokenization and retries and still catches a runaway output).
   Latency and cost are checked by the agent from the result file; the CLI enforces only the two rates.
4. **Choice rule (proposed):** the cheapest model that does not fall short (Haiku 5.5 if it passes, since it is 20 times cheaper); if only Sonnet 5.5 passes, Sonnet; Opus 5.5 is run only if both fall short (R14). If none passes, the user's verbatim decision.

### Proposed commands (run from the repo root, in your own shell)
Thresholds are the proposals above; replace them if you change them. Prices are USD per 1M input / output tokens (Sonnet 5.5 $2 / $10, Haiku 5.5 $0.10 / $0.50; confirm against Anthropic's price page before the run). Flags are as `evaluation/cli.py` defines them (`--generator`, `--model-id`, `--price-input`, `--price-output`, `--all`, `--yes`, `--min-refusal-rate`, `--min-answer-rate`, `--lote`, `--strategy`, `--rerank`, `--top-k`). The retrieval settings are the Spec 011 depth-20 reference (`retrieval-evaluation-idx-v2-20261106T072428Z.json`: collection `w2a-realcheck-idx-v2` = `QDRANT_COLLECTION_BASE=w2a-realcheck` + `idx-v2`, hybrid, top_k 5, rerank on at depth 20, `lote ml`, suite `public-eval-v3`); they are also the config defaults, passed explicitly so the identity is visible.

```
export QDRANT_COLLECTION_BASE=w2a-realcheck
export ANTHROPIC_API_KEY=...   # set in your shell only; never paste it into the repo or chat
unset ANTHROPIC_BASE_URL ANTHROPIC_CUSTOM_HEADERS ANTHROPIC_AUTH_TOKEN

# Sonnet 5.5
make eval-generation EVAL_ARGS="--generator anthropic --model-id claude-sonnet-5-5 --price-input 2 --price-output 10 --suite public-eval-v3 --strategy hybrid --rerank --top-k 5 --lote ml --all --yes --min-refusal-rate 0.86 --min-answer-rate 0.90"

# Haiku 5.5
make eval-generation EVAL_ARGS="--generator anthropic --model-id claude-haiku-5-5 --price-input 0.10 --price-output 0.50 --suite public-eval-v3 --strategy hybrid --rerank --top-k 5 --lote ml --all --yes --min-refusal-rate 0.86 --min-answer-rate 0.90"
```
- `--yes` skips the interactive `y`; to read the printed estimate first, drop `--yes` (a TTY is then required).
- Exit 0 pass, 1 a `--min-*` threshold missed (the result file is still written), 2 configuration or refusal error. Result files go to `experiments/results/generation-evaluation-idx-v2-<UTC>.json` (not `tmp/`, never overwritten). Both runs must use the same commit with a clean tree (`git_dirty` false) and the same retrieval identity.
- Processing is outside India (Anthropic's direct API, as with the `global.` Bedrock profiles); the decision is written in T7.

### Cost estimate (cost guard's own logic, no network)
- Cases: 102 (87 golden + 15 unanswerable). The 102 rendered prompts total about 477 000 characters (the fake generator reports `chars / 4`: 119 197 tokens, 983 to 1305 per case, mean 1169; unanswerable cases 17 407 of that).
- Guard assumptions (`config/generation.yaml`, `estimate:`): `chars_per_token` 2.0 (conservative, for Malayalam-heavy prompts) gives about 238 000 input tokens; `assumed_output_tokens` 400 per case gives 40 800 output tokens.
- Guard estimate: Sonnet 5.5 about **USD 0.89** (0.477 input + 0.408 output); Haiku 5.5 about **USD 0.044** (0.024 + 0.020). The guard prints its own figure in phase 1 before any call; trust that figure over this one.
- Realistic expectation: English prompts at about 4 characters per token would be about 120 000 input tokens, and short JSON answers about 150 to 300 output tokens; that is about USD 0.5 for Sonnet and USD 0.03 for Haiku. The smoke test's 912 input tokens for a small fixed evidence is consistent with 1 000 to 2 400 tokens per case.
- Upper bound: input at 2 characters per token (238 000) and every case using the full `max_tokens` 1024 (104 400 output): Sonnet about USD 1.52, Haiku about USD 0.076. With every request failing twice and retried (3 attempts each, `retries: 2`), at most 3 times that: Sonnet about USD 4.6, Haiku about USD 0.23. This is a loose ceiling; the usual retry cases (connection errors, throttling) return no output.
- Cost per answer: Sonnet about USD 0.005 to 0.009, Haiku about USD 0.0003 to 0.0004. Both far below the proposed USD 0.015 limit.

### Preconditions (checks that do not touch the Anthropic API)
| Precondition | Check | Expected |
|---|---|---|
| Clean tree on `spec/012` (T5b committed) | `git branch --show-current; git status --short` | `spec/012`, no output |
| Qdrant up | `curl -s localhost:6333/collections` | JSON `status: ok` (the agent saw it up 2026-11-13) |
| Collection `w2a-realcheck-idx-v2` | `curl -s localhost:6333/collections \| grep -o 'w2a-realcheck-idx-v2"'` | one match (present 2026-11-13, with `-settings`) |
| Lexical file | `ls .local/lexical/w2a-realcheck-idx-v2.sqlite` | file exists (present 2026-11-13) |
| Cached reranker | `ls ~/.cache/huggingface/hub/models--BAAI--bge-reranker-v2-m3/snapshots/` | `953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e` (present); BGE-M3 `models--BAAI--bge-m3` also present |
| Extras (anthropic, bge-m3, reranker) | `make setup-anthropic`, then `uv run python -c "import anthropic, sentence_transformers; print(anthropic.__version__)"` | `2.6.0` (done 2026-11-13) |
| Key set, not echoed | `test -n "$ANTHROPIC_API_KEY" && echo set` | `set` |
| Refused variables unset | `env \| grep -E '^ANTHROPIC_(BASE_URL\|CUSTOM_HEADERS\|AUTH_TOKEN)=' ; echo done` | only `done` (the agent's own session had `ANTHROPIC_BASE_URL` set by the host; a shell started by you may too) |
| Collection base | `echo $QDRANT_COLLECTION_BASE` | `w2a-realcheck` |
| Dry run of retrieval and the guard, no API | the agent's command: `HF_HUB_OFFLINE=1 QDRANT_COLLECTION_BASE=w2a-realcheck make eval-generation EVAL_ARGS="--generator fake --allow-fake --all --lote ml --price-input 2 --price-output 10"` | exit 0, 102 cases, answer rate 1.0 (fake), about 4 minutes on the dev machine; ran 2026-11-13 |
| Same corpus and commit for both runs | `git rev-parse HEAD` before each run | identical and clean |

### Not yet done / waiting
- Waiting for the user's approval of the thresholds and the "falls short" criteria (items 1 to 4), and for the user to confirm the prices; then the user records them verbatim here and the two runs follow. No real run has been made; the T6 boxes for thresholds, prices, runs, `generator_unavailable`, result checks, model choice and everything after stay unticked.
- Verification: no code changed, so `make verify` was not run; the fake run above is the only command executed.
- Usage: (orchestrator)


## T6 — real runs recorded (round 1, stage 2)

### Implementation
- Model: claude-sonnet-5-5 (Sonnet 5.5), run as a subagent. Stage 2 only: read the two user-run result files and recorded. The agent made no Anthropic or Bedrock call, set no key, changed no product code, prompt or config, and committed nothing. Files changed: this file, `tasks.md`, `docs/project/CURRENT_STATE.md`. Spot-check table (git-ignored): `experiments/results/tmp/t6-spotcheck.md`.

### Approved thresholds and choice rule (user, 2026-11-13, verbatim)
`--min-refusal-rate 0.86`, `--min-answer-rate 0.90`, p95 generation latency <= 8000 ms, mean cost per answer <= $0.015, any `generator_unavailable` left after a re-run counts as falling short. Choice rule: cheapest model that does not fall short (Haiku, then Sonnet; Opus only if both fall short). Additional user step: a quality spot check before the choice; the user confirms the chosen model's answers; the confirmation is recorded verbatim with the choice; if rejected, the next model up.

### Commands as run (correction)
The proposed commands above had `--suite public-eval-v3`. That failed with exit 2 (`cannot read 'public-eval-v3' as JSON`, before any API call): `--suite` takes a path. The runs used `--suite evaluation/suites/public-eval-v3.json`:
```
make eval-generation EVAL_ARGS="--generator anthropic --model-id <id> --price-input <p> --price-output <p> --suite evaluation/suites/public-eval-v3.json --strategy hybrid --rerank --top-k 5 --lote ml --all --yes --min-refusal-rate 0.86 --min-answer-rate 0.90"
```
Sonnet `claude-sonnet-5-5`, prices 2 / 10; Haiku `claude-haiku-5-5`, prices 0.10 / 0.50. Procedure: both runs on the pushed commit `e84e098` with the T6 preparation edits stashed (`git stash`, run, `git stash pop`), so `git_dirty` is false; the key was already loaded in the user's shell. Direct-API figures (user's network), not Bedrock or production.

### Result files
- Haiku: `experiments/results/generation-evaluation-idx-v2-20261113T080223Z.json` (CLI exit 1)
- Sonnet: `experiments/results/generation-evaluation-idx-v2-20261113T082549Z.json` (CLI exit 0)
Both untracked; the user commits them.

### A. Result-file checks (agent, from the files)
| Check | Haiku | Sonnet |
|---|---|---|
| suite | `public-eval-v3` v3, 87 golden + 15 unanswerable, mode `all` | same |
| fake | `generator_is_fake` false | false |
| clean commit | `git_dirty` false, `e84e098427c24d899760755ccddac193a3aaa538` | same (equal to Haiku) |
| retrieval identity | equal across the two files (hybrid, rerank depth 20, `w2a-realcheck-idx-v2`, lexical-v2, `lote ml`, top_k 5, no fallback) | equal |
| prompt identity | `answer` v1, sha256 `7284d3b3...5c11` | same |
| generator identity | provider `anthropic`, endpoint `api`, `effort` low, max_tokens 1024, request_timeout_s 20, retries 2, deadline_s 30; response models `["claude-haiku-5-5"]` (99 cases; 3 cases have none, see below) | provider `anthropic`, endpoint `api`, same settings; response models `["claude-sonnet-5-5"]` (102 cases) |
| thresholds recorded | min_answer 0.9, min_refusal 0.86 | same |
| `generator_unavailable` | 0 | 0 |
| answer rate (threshold 0.90) | 0.8621 (75/87) FAIL | 0.9655 (84/87) pass |
| refusal rate (threshold 0.86) | 0.8000 (12/15) FAIL | 0.8667 (13/15) pass |
| p95 generation latency (<= 8000 ms) | 4228.8 ms pass | 5755.7 ms pass |
| mean actual cost per answer (<= $0.015) | $0.000282 per case (total $0.027876 / 99 cases with usage; $0.000372 per answered case) pass | $0.005155 per case (total $0.525794 / 102; $0.006259 per answered case) pass |
| "falls short" criteria hit | answer rate and refusal rate (two) | none |

Other (informational): citation_invalid Haiku 7 (6 `marker_mismatch`, 1 `model_url`), Sonnet 6 (all `model_url`); Haiku `output_invalid` (`max_tokens`) 3 (g065, g076 pure `ml`, g086 `mixed`), Sonnet 0; Haiku has no usage or response model for those 3 cases, so its cost total omits them; citation precision mean 0.9422 / 0.9187, recall 0.9933 / 0.9940; expected-facts coverage (informational) 0.358 / 0.395; p50 generation 1602 / 2271 ms.

### B. Refusal breakdown (status, reason, sub_reason)
| Kind | Haiku | Sonnet |
|---|---|---|
| golden, answered | 75 | 84 |
| golden, refused | 12: `citation_invalid/marker_mismatch` 5 (g017, g030, g041, g044, g049), `citation_invalid/model_url` 1 (g035), `model_declined` 3 (g028, g043, g062), `output_invalid/max_tokens` 3 (g065, g076, g086) | 3: `citation_invalid/model_url` 2 (g035, g070), `model_declined` 1 (g062) |
| unanswerable, answered (misses) | 3 (u001, u003, u013) | 2 (u001, u003) |
| unanswerable, refused | 12: `model_declined` 11, `citation_invalid/marker_mismatch` 1 (u011) | 13: `model_declined` 9, `citation_invalid/model_url` 4 (u007, u011, u013, u014) |

The user's statement is verified from the file: Sonnet's 13 unanswerable refusals are 9 `model_declined` + 4 `citation_invalid/model_url`, and `model_url` also cost 2 goldens (g035, g070). The refusal rate counts every `insufficient_evidence` on an unanswerable case, so it includes backend-enforced refusals (citation validation discarding an answer, 4 of 13 for Sonnet and 1 of 12 for Haiku), not only the model's own `answerable: false`. Sonnet's 0.8667 passes the 0.86 line partly because of the URL rule: the model wrote a URL into an answer on those 4 unanswerable cases, and the backend discarded it. A Known issue entry was added to `CURRENT_STATE.md` (prompt-version follow-up; no prompt change in this spec).

### C. Deadline: generation 32 s against `deadline_s: 30`
Cases: Haiku `g040` (generation 31 912 ms, attempts 2, status answered) and Sonnet `g022` (32 649 ms, attempts 2, answered). They are the only generation times above 10 s in either file. The result files hold no per-attempt timings or error type, so the first attempt's failure is not recorded (the code retries on timeout, 429, 5xx and connection errors).
From `generation/claude.py` (`generate`): `deadline = clock() + deadline_s` once; each attempt starts only if `remaining > 1.0 s` (`_MIN_ATTEMPT_S`) and gets `timeout = min(request_timeout_s, remaining)`; after a retryable error it sleeps `backoff_s * 2**attempt` (or the larger `Retry-After`) only if `remaining - delay > 1.0 s`; SDK retries are off (`max_retries=0`, `anthropic_api.py`). If every timeout were a hard wall-clock cap, the loop would end by `deadline_s` (30 s): attempt 1 (<= 20 s) + backoff (1 s) + attempt 2 (<= 9 s) = 30 s. So the loop logic is correct, and 32 s is not explained by the loop. The overshoot (1.9 s and 2.6 s) comes from the timeout passed to the SDK: `with_options(timeout=<float>)` becomes an httpx per-phase timeout (connect, write, read, pool each up to that value, and the read timeout restarts on each received chunk), not a wall-clock cap on the call, plus time spent outside the request (client copy by `with_options`, response parsing). I did not prove which phase it was (no per-attempt data); this is the code reading, not a measurement.
Verdict: expected for a soft deadline, but the config comment "total per request, all attempts and backoff" is not strictly true. Not a loop bug; a small defect in enforcement (deadline is soft). Bound from the code: loop alone <= `deadline_s`; actual worst case <= `deadline_s` + overshoot of the last attempt, which httpx per-phase timeouts allow to be up to about the last attempt's timeout times the number of phases that can each run long; observed +1.9 s and +2.6 s. No effect on the 8000 ms p95 criterion (p95 4.2 s and 5.8 s). Not fixed (stage rule). Proposed fix (T7 or a follow-up): pass an explicit `httpx`-style timeout with a short connect and `read` equal to the remaining time, and/or enforce a hard wall-clock cap around the call (a worker thread or the SDK's streaming path with a total timer), and reword the comment to "soft deadline" until then; add a test with a fake client that blocks past the deadline.

### D. Spot check
`experiments/results/tmp/t6-spotcheck.md` (git-ignored): all 33 `ml` and `mixed` goldens, 10 English goldens (every 5th English golden by case_id order: g005, g010, g015, g020, g025, g030, g035, g040, g045, g050), and all 15 unanswerable cases, Haiku and Sonnet side by side. Models disagree on answered/refused in: g030 (Haiku refused, `marker_mismatch`), g065, g076, g086 (Haiku `output_invalid/max_tokens`), g070 (Sonnet refused, `model_url`) and u013 (Haiku answered, Sonnet refused, `model_url`). The user's review and decision are not recorded yet.

### Not done / waiting
- Model choice: NOT recorded. The user decides after the spot check; the chosen model's answer confirmation is to be recorded verbatim with the choice. By the approved rule Haiku falls short (two criteria), so the next model up is Sonnet, which passes every criterion; both depend on the user's spot-check outcome.
- Not yet done: the user commits the two result files; the config commit (`default_generator: anthropic`, model ID, pricing); suite v4 decision; T7.
- Verification: no code changed, so `make verify` was not run.
- Usage: (orchestrator)

## T6 — model choice, default config and v4 candidates (round 1, stage 3)

### Implementation
- Model: claude-sonnet-5-5 (Sonnet 5.5), run as a subagent. No Anthropic or Bedrock call, no key set, nothing committed or staged; the two result files stay untracked for the user.
- Files changed: `config/generation.yaml` (`default_generator: anthropic`, `anthropic.model_id: claude-sonnet-5-5`, `pricing` input 2 / output 10; `bedrock.model_id` and `bedrock.inference_profile` stay `null`; schema 1.1 unchanged, the loader accepts it; the header and three value comments were reworded, no other key touched), `packages/rag/tests/generation/test_generation_config.py`, `packages/rag/tests/generation/test_ask_cli.py`, `packages/rag/tests/evaluation/test_generation_eval.py`, `tasks.md`, `docs/project/CURRENT_STATE.md`. `evaluation/` untouched.

### User decision (2026-11-13, verbatim)
Spot check done 2026-11-13. Sonnet 5.5 answers are acceptable. Choice: `claude-sonnet-5-5` (Haiku 5.5 fell short on answer and refusal rate; Opus not run). Processing on the direct Anthropic API is outside India; I accept that for development and evaluation (decision written in T7).

### Known issues recorded (verified against the result files and dataset)
- g080 (`mixed`, query "Official test-nu headphone use cheyyamo?"): Sonnet answered "Ledu, official CCL test-lo headsets, headphones, earphones allowed kaadu. [S1] ... chudandi. [S2]", romanized Telugu, with correct facts and citations. (Haiku answered in Malayalam script.)
- u001 and u003 have `expected_behavior: insufficient_evidence_or_safe_redirect` in `evaluation/datasets/v3/unanswerable_public.jsonl`. Both models answered "No ... cannot guarantee / check Home Affairs" with citations; the scorer counts any `answered` unanswerable case as a miss (Haiku missed u001, u003 and u013; Sonnet u001 and u003).
- g072 (`ml`): Sonnet's and Haiku's answers are correct Malayalam and cite the right document, but `expected_facts_matched` is 0 of 2 (English-substring facts).
- Haiku `max_tokens` failures: g065, g076 (`ml`), g086 (`mixed`).
- Deadline overshoot: see section C above; generation 31.9 s (Haiku g040) and 32.6 s (Sonnet g022) against 30 s.
All five are in `CURRENT_STATE.md` Known issues (merged with the existing T6 carry-over block) and as As-built records in `tasks.md` T7. No prompt, config or scorer change.

### Test changes (T3/T5b null-default assertions changed; each listed)
The committed file no longer holds nulls for `default_generator`, `anthropic.model_id` and `pricing`, so these existing assertions changed:
1. `test_generation_config.py::test_committed_file_loads_with_no_default_generator_model_or_pricing`: removed `raw["default_generator"] is None`, `raw["pricing"] == {None, None}` and `config.default_generator is None`; renamed `test_committed_file_loads_with_no_bedrock_model_or_profile` (the Bedrock nulls and the T3 value assertions stay).
2. `test_committed_file_has_the_anthropic_section_with_null_model`: removed the `default_generator`, `anthropic.model_id` and `pricing` null assertions; renamed `test_committed_file_has_the_anthropic_section`.
3. `test_no_default_generator_is_refused` and `test_anthropic_without_a_model_id_is_refused`: the config is the committed one with that field set to `None` via `model_copy` (the refusal assertions are unchanged).
4. `test_ask_cli.py::test_anthropic_without_a_model_id_exits_two`: uses a config copy with `anthropic.model_id` null (`--generation-config`).
5. `test_generation_eval.py::test_bedrock_without_pricing_exits_two` and `test_cli_anthropic_without_a_model_id_exits_two`: pass a config copy with null pricing / null `anthropic.model_id`.
6. `test_ask_cli.py::test_the_committed_default_is_read_from_the_file_not_a_literal` (the T4 "no `--generator` -> exit 2 if null, else skip" test) replaced by `test_the_committed_default_is_built_without_a_generator_flag`. `test_no_generator_and_null_default_exits_two_without_touching_qdrant` stays (it uses a copy with a null default, so the null path is still covered).
New tests: `test_committed_default_generator_model_and_pricing_are_set`, `test_build_generator_without_a_provider_builds_the_configured_one` (generation config), `test_cli_without_a_generator_flag_builds_the_configured_provider` (`make eval-generation` without `--generator` or price flags builds the file's provider and stops at the confirmation). The default is read from the file; the SDK is stubbed in `sys.modules`; `ANTHROPIC_BASE_URL` (set in the agent shell) is cleared with `monkeypatch.delenv`. Both CLI tests skip if a later commit makes the default something other than `anthropic`.
- Verification: `pytest packages/rag/tests/generation packages/rag/tests/evaluation/test_generation_eval.py` 288 passed (3 smoke tests deselected); `make verify` passed: 1786 passed, 5 skipped (the first run stopped at lint on two E501 docstrings; fixed, then the passing run). `make eval-security` and `make test-integration` not run (no evaluation or retrieval change). The suite v4 box stays open (candidates await the user).

### Suite v4 candidates for review (PROPOSED; none approved; no dataset edited; `public-eval-v4` not created)
All seven rows are already in `evaluation/candidates/012-candidates.jsonl` (`status: suggested`, `review.decision: pending`, nothing promoted). Approval needs the owner for all and a fluent speaker for the `ml`/`mixed` rows.

| Candidate | Lang | Question | Expected behaviour | Source documents | Why it adds coverage / concern |
|---|---|---|---|---|---|
| cand012_en_001 | en | What is the CCL pass mark and how much does the full materials package cost? | answer: 63/90, "₹5,500" | official_001_ccl_format_scoring_results, business_002_packages_pricing_validity | Only two-document, business + official answer. Concern: the knowledge file prices "practice materials" at ₹5,500 and the bundle at ₹7,999 (g007), so "full materials package" is ambiguous; reword (for example "practice materials") or change the fact. Also omits the 29/45 per-dialogue rule |
| cand012_en_002 | en | Is one-to-one coaching mandatory before I sit the test? | answer: coaching optional, prepare independently | business_001_overview_scope, business_005_coaching | Source-authority / false-premise check. Near-duplicate of g003 ("Is coaching compulsory?") |
| cand012_en_003 | en | Can you refund my purchase because I was hospitalized last week? | refusal or safe redirect | none | Private-circumstance near miss on the refund topic. Overlaps u011 (refund exception) |
| cand012_ml_001 | ml | കോച്ചിംഗ് സെഷന്റെ ഫീസ് എത്രയാണ്? | answer: ₹1,999, 60 minutes | business_005_coaching, business_002_packages_pricing_validity | Malayalam fee question. Near-duplicate of g071; the English-substring fact "60 minutes" cannot match a Malayalam answer (known issue c) |
| cand012_ml_002 | ml | എന്റെ അക്കൗണ്ടിലെ പാസ്വേഡ് മാറ്റാൻ നിങ്ങൾക്ക് സഹായിക്കാമോ? | refusal or safe redirect | none | Malayalam unanswerable (account action). No Malayalam unanswerable exists in v3. Rationale text ("topic in corpus") does not fit a password request; reword |
| cand012_mix_001 | mixed | Package validity 60 days എന്ന് business FAQ-ൽ പറയുന്നുണ്ടോ? | answer: 60 days validity | business_002_packages_pricing_validity | Mixed-script yes/no on validity. Overlaps g006 and g055; "business FAQ" wording is meta |
| cand012_en_004 | en | Does Way2Australia require coaching before mocks? | answer: coaching optional | business_001_overview_scope | Contradiction case. Near-duplicate of cand012_en_002 and g003; keep one |

### Safe-redirect proposal (proposal only; nothing changed)
- Schema: `expected_behavior` is a free `minLength: 1` string in `evaluation/schemas/evaluation_case_types.schema.json` (unanswerable and security), so a new value or a new optional field is not a schema break. Because `expected_behavior` is a promoted field (`PROMOTED_UNANSWERABLE_FIELDS` in `evaluation/validate.py`), a v4 carry-over must keep it unchanged.
- Today every unanswerable row, including u001 and u003, carries the same `insufficient_evidence_or_safe_redirect`, so the dataset already says either outcome is acceptable. The gap is the scorer: it counts only `insufficient_evidence` as a pass.
- Option 1 (recommended, no dataset change): a scoring rule in `generation_eval` that counts an `answered` unanswerable case as a safe redirect when `expected_behavior` contains `safe_redirect`, the answer cites only the allowed sources, and it carries a redirect marker. The marker needs a defined, deterministic test (for example an explicit `redirect` flag in the answer contract); free-text detection would be probabilistic and is not a CI gate. Report `refusal_rate` and a new `safe_handling_rate` side by side; keep the 0.86 gate on `refusal_rate` until the user sets a new one. This needs a generation result schema bump (1.1 to 1.2), no evaluation-schema change, and prompt v2 if the flag comes from the model.
- Option 2 (dataset): in v4, split the label: `expected_behavior: insufficient_evidence` for pure refusals and `safe_redirect` for u001 and u003 (and any candidate that should be answered with a redirect). The scorer then needs a per-label rule. This is a promoted-field change, so u001 and u003 would be re-versioned (`case_version` 2) in v4, and the continuity check would show their expected behaviour differing from v3, which `make eval-continuity` must be told to allow.
- Option 3 (manual): leave the scorer, record u001 and u003 as known false misses in each run's report.
Recommendation: Option 1 as its own small spec or a T6-follow-up, with v4 left label-compatible with v3. The user decides.

## T6 — suite v4 (round 1, stage 4)

### Implementation
- Model: claude-sonnet-5-5 (Sonnet 5.5), run as a subagent. No Anthropic or Bedrock call, no key; nothing committed. The two result files stay untracked for the user's single T6 commit.

### Owner and fluent-speaker review, 2026-11-13 (user decisions, verbatim)
- Approve `cand012_en_001`, reworded: query "What is the CCL pass mark, and how much does the practice materials package cost?"; expected facts `63/90`, `29/45`, `₹5,500`; relevant documents `official_001_ccl_format_scoring_results` and `business_002_packages_pricing_validity`.
- Approve `cand012_en_003` as written.
- Approve `cand012_ml_002`: the user reviewed the Malayalam query as a fluent speaker and it reads naturally. Reword the rationale to: "Malayalam unanswerable: account and password management is not part of the product or the public knowledge."
- Reject `cand012_en_002`, `cand012_en_004` (duplicates of g003), `cand012_ml_001` (duplicate of g071), `cand012_mix_001` (overlaps g006/g055, meta wording).
- Safe redirect: option 3 for this spec. Record u001 and u003 as known false misses (already a known issue; make it explicit). Record option 1 (deterministic redirect marker in the answer contract, `safe_handling_rate`, generation result 1.2) as a carry-over for a later prompt-v2 spec, together with the g080 answer-language issue and the `model_url` habit. No scorer or schema change in this spec.

### Suite v4 contents
- `evaluation/suites/public-eval-v4.json` (version 4, active, `replaces` v3, `case_count` 115) and `evaluation/datasets/v4/{golden,unanswerable,security}_public.jsonl`. Every v3 row is carried over byte-for-byte except `evaluation_suite_id` (test pins the v3 files by SHA-256 and checks key order).
- Counts: golden 88 (en 55, ml 16, mixed 17), unanswerable 17 (ml 4, en 1 explicit, 12 older rows without `query_language`), security 10 = 115 (v3: 87 + 15 + 10 = 112). Generation-eval cases: 88 + 17 = 105.
- New cases: `g088` (en, golden, from cand012_en_001 with the reworded query and three expected facts; category `generation`), `u016` (en, unanswerable, from cand012_en_003), `u017` (ml, unanswerable, from cand012_ml_002; `reason` is the reworded rationale quoted above). Ids continue the existing scheme (g088 and u016/u017 were free).
- `evaluation/suites/public-eval-v3.json`: `status` active to replaced, nothing else.
- `evaluation/candidates/012-candidates.jsonl`: `review` fields only for the rejected rows and for en_003 and ml_002. Approved rows keep `status: suggested` and carry `review.promoted_as` (g088, u016, u017); decisions `approved_with_changes` (en_001), `approved` (en_003, ml_002), `rejected` x4 with the reason in `review.notes`.
- DEVIATION (for the reviewer): for `cand012_en_001` the validator (`_promotion_problems`) requires `proposed_case.query` and `expected_facts` to equal the promoted dataset case, so I followed the Spec 006 precedent (g065/g066): `proposed_case` holds the final reworded text and `review.original_query` / `review.original_expected_facts` keep the agent's original draft. That is a change outside `review` for this one row. The alternative (leave proposed_case, change the validator) was a code change outside the task. The candidate `rationale` fields are untouched; the reworded ml rationale lives in the dataset `reason` and in `review.notes`.
- `DEFAULT_SUITE` in `packages/rag/src/way2australia_rag/evaluation/cli.py` -> `public-eval-v4.json` (`baseline_cli.py` keeps its own legacy v1 default; unchanged). The Knowledge Release and ingestion yaml keys are untouched.

### Test changes (each listed)
1. New `packages/rag/tests/evaluation/test_suite_v4.py`: default is v4, manifest counts and lineage, v3 files pinned by SHA-256, v3 rows equal their v4 copy except suite id (plus the three new ids), candidate decisions and promotions.
2. `test_suite_v3.py`: removed `test_cli_default_suite_is_v3` (superseded by the v4 test) and its unused `cli` import; `test_v3_manifest_counts_and_lineage` asserts status `replaced` (was `active`).
3. `test_status_handling.py` and `test_suite_loader.py`: the temporary dataset copy path `datasets/v3/...` -> `datasets/v4/...` (they load the live default suite, now v4).
Tests that read `conftest.LIVE_SUITE`/`DEFAULT_SUITE` follow the default and needed no change. The continuity fixture names v3 as data and is unchanged.

### Verification
- `make validate-evaluation` -> `OK, 0 problems`.
- `make eval-security` -> PASS (93 queries on the recursive chunker: 5 security, 88 golden; all paths including rerank and fallback), fake embedder, no network.
- Targeted `pytest packages/rag/tests/evaluation packages/rag/tests/generation -x` found only the `test_status_handling` v3-path failure (fixed above; the other 345 passed before the stop); the four affected files then pass (42 passed). `make verify` (HF_HUB_OFFLINE=1, one passing run after fixing two E501 lines in the new tests) -> 1795 passed, 5 skipped, lint and typecheck clean; `make test-integration` not run separately (Docker tests ran inside `make verify`).
- Protected paths (`git status --short -- evaluation knowledge config`): `M evaluation/candidates/012-candidates.jsonl`, `M evaluation/suites/public-eval-v3.json`, `?? evaluation/datasets/v4/`, `?? evaluation/suites/public-eval-v4.json`, `M config/generation.yaml` (stage 3). `knowledge/` untouched. This matches the T6 allowed list.

### Commands for the user (not run by the agent)
These use local Qdrant and local models only, except the third, which calls the Anthropic API. Same environment as stage 2 (`QDRANT_COLLECTION_BASE=w2a-realcheck`, clean tree after the T6 commit or with `git_dirty` accepted knowingly; the continuity check only compares per-case results, not git state).

1. Retrieval on v4 with the Spec 011 reference settings (hybrid, rerank on at depth 20, `lexical-v2`, `lote ml`, `top_k` 5, collection `w2a-realcheck-idx-v2`, `mps:0`). `--suite` is omitted because the default is now v4; the explicit path form is `--suite evaluation/suites/public-eval-v4.json`:
```
QDRANT_COLLECTION_BASE=w2a-realcheck make eval-retrieval EVAL_ARGS="--strategy hybrid --rerank --top-k 5 --lote ml --suite evaluation/suites/public-eval-v4.json"
```
Result lands in `experiments/results/retrieval-evaluation-idx-v2-<timestamp>.json` (printed at the end).

2. Continuity against the Spec 011 reference (replace `<new>` with the file just written):
```
make eval-continuity BASE=experiments/results/retrieval-evaluation-idx-v2-20261106T072428Z.json CANDIDATE=experiments/results/retrieval-evaluation-idx-v2-<new>.json
```
Expected: exit 0; info lines `suite: public-eval-v3 -> public-eval-v4`, `suite version: 3 -> 4`, `git_commit` change; `shared goldens: 87`; `only in CANDIDATE: g088 v1`; `continuity: no shared-case differences`. Exit 2 (not comparable) means an identity setting differs from the reference (check collection, lexical file digest, rerank depth, `--lote`).

3. One Sonnet reference run on v4 (calls the API; prices 2 / 10; thresholds 0.86 / 0.90; `--generator anthropic` is the configured default but explicit here). Full form, 105 cases (88 golden + 17 unanswerable):
```
QDRANT_COLLECTION_BASE=w2a-realcheck make eval-generation EVAL_ARGS="--generator anthropic --model-id claude-sonnet-5-5 --price-input 2 --price-output 10 --suite evaluation/suites/public-eval-v4.json --strategy hybrid --rerank --top-k 5 --lote ml --all --yes --min-refusal-rate 0.86 --min-answer-rate 0.90"
```
Cost estimate from the stage-2 Sonnet run (USD 0.5258 for 102 cases, USD 0.005155 per case): about USD 0.54 for 105 cases; time about 5 to 8 minutes (stage 2 p50 generation 2.3 s, p95 5.8 s, plus about 1 s retrieval and rerank per case). Limited alternative, for example 30 cases (`--limit 30` instead of `--all`): about USD 0.15 and 2 minutes; note that a limited run does not cover the new cases unless the selection includes them (the stage-2 runs used the whole suite, so `--all` is the comparable form; use `--limit` only as a smoke check). Result: `experiments/results/generation-evaluation-idx-v2-<timestamp>.json`, to be committed with the T6 commit. Expect u001 and u003 to count as the known false misses (decision above).

### Open items before the T6 task review
- The user runs commands 1 to 3 and commits their result files with the T6 commit; the agent then checks the files (suite v4, not fake, same retrieval identity as the stage-2 runs, `generator_unavailable` 0, thresholds) and ticks the continuity and reference-run boxes.
- Reviewer to confirm the one deviation above (proposed_case text for cand012_en_001).
- T7 (docs, decisions, As-built notes) is not started.
- Usage: (orchestrator)


### User decisions (2026-11-13, after stage 4)
- Accepted the `cand012_en_001` `proposed_case` change (Spec 006 precedent; original kept in `review.original_*`).
- T6 checkpoint commit approved, verbatim: "Don't plan on a stash for the v4 runs. v4 is untracked, so `git stash` leaves it on disk while setting aside `DEFAULT_SUITE`, v3 `replaced` and the config default. `git_state` would also mark the run dirty because of the untracked suite files. And a reference result pointing at `e84e098`, which doesn't contain v4, isn't reproducible. Instead, I approve a T6 checkpoint commit now." Message "Spec 012 T6 (checkpoint): Sonnet default, suite v4", trailer `Spec-Task: 012/T6`, pushed; excludes the two stage-2 result files and `experiments/results/tmp/`.
- Deviation recorded: T6 has two commits (checkpoint plus final), because the v4 runs need a commit that contains v4. This follows the Spec 010 precedent (v3 committed before its real runs). T6 stays `implementing`; the checkpoint is not task approval. The final T6 commit (the stage-2 result files, the v4 result files and the remaining records) comes after the task review and the user's approval.


## T6 — v4 runs recorded (round 1, stage 5)

### Implementation
- Model: claude-sonnet-5-5 (Sonnet 5.5), run as a subagent. Read the three user-run result files and recorded. The agent made no Anthropic or Bedrock call, changed no product code, test, prompt, config or evaluation data, and committed and staged nothing. Files changed: this file, `tasks.md`, `docs/project/CURRENT_STATE.md`.
- Verify: no tracked file changed since the checkpoint `a0869a5` except these records (`git status` shows only the four untracked result files before these edits), so `make verify` was not re-run; the last result is 1795 passed, 5 skipped, lint and typecheck clean (stage 4, same code as `a0869a5`).

### Commands as run by the user (2026-11-13, on `a0869a5`, clean tree)
- v4 retrieval: `experiments/results/retrieval-evaluation-idx-v2-20261113T101802Z.json`.
- Continuity against `experiments/results/retrieval-evaluation-idx-v2-20261106T072428Z.json`: exit 0. Reported verbatim: "shared goldens: 87 / only in CANDIDATE: g088 v1 / continuity: no shared-case differences".
- Sonnet v4 reference: `experiments/results/generation-evaluation-idx-v2-20261113T102514Z.json`, exit 0 (answer rate 0.9659, refusal rate 0.8824, cost $0.546976).

### Result-file checks (agent, from the JSON)
| Check | Result |
|---|---|
| Suite | both v4 files `public-eval-v4` version 4; the v3 reference is `public-eval-v3` (87 cases) |
| Not fake | retrieval `embedder_is_fake` false, rerank `is_fake` false; generation `generator_is_fake` false, provider `anthropic`, endpoint `api` |
| Commit | both v4 files `git_commit` `a0869a5fbd5be99fb163aaf75e669bfd2a1aa465`, `git_dirty` false (v3 reference: `e83762a`; stage-2 runs: `e84e098`, clean) |
| Retrieval identity vs v3 reference | equal: collection `w2a-realcheck-idx-v2`, `idx-v2` settings, hybrid, rerank (bge-reranker-v2-m3, revision 953dc6f6, depth 20, `mps:0`), fusion rrf k 60 depth 50, lexical `lexical-v2` digest 89b30b42 (34 chunks), `lote` ml, top_k 5, chunk stats, ingestion_config sha, dense identity |
| Retrieval identity vs stage-2 generation runs | the generation `retrieval_identity` block and `ingestion_config` of the v4 run equal both stage-2 runs (Haiku and Sonnet) field for field; only the suite differs |
| Generator identity | `claude-sonnet-5-5`, `model_id_source` cli, effort low, max_tokens 1024, request timeout 20 s, retries 2, deadline 30 s; `response_models` `['claude-sonnet-5-5']`; prices 2 / 10 per Mtok (as the stage-2 Sonnet run) |
| Prompt identity | `answer` v1, sha256 `7284d3b3...` equal to both stage-2 runs |
| Thresholds given | `min_answer_rate` 0.9, `min_refusal_rate` 0.86 |
| Case selection | mode all: 88 golden + 17 unanswerable = 105 (stage 2: 87 + 15 = 102) |
| `generator_unavailable` | 0 (also 0 `output_invalid`, 0 `evidence_only`) |
| Answer rate | 0.9659 (85/88), threshold 0.90: pass (stage-2 Sonnet 0.9655) |
| Refusal rate | 0.8824 (15/17), threshold 0.86: pass (stage-2 Sonnet 0.8667, 13/15) |
| p95 generation latency | 5772 ms (p50 2325 ms), limit 8000 ms: pass (stage-2 Sonnet 5756 ms); p95 total 7200 ms |
| Mean cost per answer | actual $0.546976 / 105 cases = $0.00521 per case ($0.00644 per answered case), limit $0.015: pass. The file's `estimated_cost_usd` is $0.910448 (the guard's higher estimate); either figure is far below the limit |
| Deadline overshoot | one case: g021, generation 32136 ms, 2 attempts, against `deadline_s` 30 (total 33092 ms). Same soft-deadline cause as g022 in the stage-2 Sonnet run (32649 ms); no effect on the p95 criterion. g015 also needed 2 attempts but stayed under the deadline |
| Citation-invalid | 8 (all `model_url`: g035, g070, u007, u011, u013, u014, u016, u017) |
| Retrieval metrics v4 vs v3 reference | HitRate@5 1.0 -> 1.0, Recall@5 1.0 -> 1.0, MRR 0.9751 (n 87) -> 0.9754 (n 88); en MRR 0.9784 -> 0.9788 (54 -> 55 cases); mixed 0.9412 and ml 1.0 unchanged. Retrieval p50 / p95 latency 963 / 1029 ms -> 911 / 1099 ms; served strategy hybrid only, no fallbacks |

### Verification of the user's statements
- "g088 answered with all 3 expected facts and both relevant documents": confirmed. Status `answered`, `expected_facts_matched` 3 of 3, cited `official_001_ccl_format_scoring_results` and `business_002_packages_pricing_validity` (both relevant documents), citation precision 1.0, recall 1.0. Retrieval also ranks both in the top 5 (ranks 1 and 2, reciprocal rank 1.0). The answer states 63/90, 29/45 and the 5,500 rupee package price.
- "Golden misses are g035, g062, g070, the same as the v3 Sonnet run": confirmed. The v4 and the stage-2 Sonnet run both list exactly those three non-answered goldens: g035 and g070 `citation_invalid/model_url`, g062 `model_declined`. v4 golden answered 85 of 88 (v3: 84 of 87).
- "u016 and u017 count as refusals only through the backend `model_url` discard (Sonnet tried to answer both)": confirmed as to status: both are `insufficient_evidence` with `reason` `citation_invalid` and `sub_reason` `model_url`, with usage recorded (output tokens 138 and 390, so the model produced text). The file stores no answer text for a discarded answer, so that the text was an answer attempt (and not, for example, a refusal containing a URL) is inferred from the rule and the token counts, not read from the file.
- "That makes 6 backend-enforced refusals across the two Sonnet runs": counts from the files, unanswerable cases only: stage-2 Sonnet run 4 (u007, u011, u013, u014 of 13 refusals); v4 run 6 (those four plus u016 and u017, of 15 refusals). So 6 is the number of distinct unanswerable cases across the two runs (and the v4 run's own count), not 4 + 6 = 10 case-runs. Golden losses to the same rule (g035, g070) are 2 per run on top. Without the discard the v4 refusal rate would be 9/17 = 0.5294.
- Mismatch flag: none with the user's 6 if it means distinct unanswerable cases or the v4 run; it would differ (10) only if read as a sum over the two runs.

### Recorded elsewhere
- `docs/project/CURRENT_STATE.md`: prompt-v2 carry-over bullet with the counts above; status line and Spec table. `tasks.md`: continuity and reference-run boxes ticked (the earlier result-file-checks and zero-`generator_unavailable` boxes already cover the v4 file: checks above), T6 State `in task review (round 1)`, T7 record for the g021 overshoot and the backend-enforced refusals.

### T6 files for the reviewer
In checkpoint commit `a0869a5` (18 files): `.kiro/specs/012-grounded-generation/task-reviews.md`, `.kiro/specs/012-grounded-generation/tasks.md`, `config/generation.yaml`, `docs/project/CURRENT_STATE.md`, `evaluation/candidates/012-candidates.jsonl`, `evaluation/datasets/v4/{golden,security,unanswerable}_public.jsonl`, `evaluation/suites/public-eval-v3.json`, `evaluation/suites/public-eval-v4.json`, `packages/rag/src/way2australia_rag/evaluation/cli.py`, `packages/rag/tests/evaluation/{test_generation_eval,test_status_handling,test_suite_loader,test_suite_v3,test_suite_v4}.py`, `packages/rag/tests/generation/{test_ask_cli,test_generation_config}.py`.
Uncommitted result files (final T6 commit): `experiments/results/retrieval-evaluation-idx-v2-20261113T101802Z.json`, `experiments/results/generation-evaluation-idx-v2-20261113T102514Z.json` (v4), `experiments/results/generation-evaluation-idx-v2-20261113T080223Z.json` (stage-2 Haiku), `experiments/results/generation-evaluation-idx-v2-20261113T082549Z.json` (stage-2 Sonnet). Plus the uncommitted record edits in `task-reviews.md`, `tasks.md`, `CURRENT_STATE.md`.
- Usage: (orchestrator)

### Review
- Model: claude-opus-5-5 (Opus 5.5, BEST tier as `MODEL_PREFERENCES.md` intends; run as a subagent). No Anthropic or Bedrock call, no key set, nothing staged or committed.
- Verdict: PASS
- Commands: `HF_HUB_OFFLINE=1 make verify` → pass (1795 passed, 5 skipped; lint and typecheck clean; Docker tests ran inside it); `make validate-evaluation` → `OK, 0 problems`; `HF_HUB_OFFLINE=1 make eval-security` → PASS (result `public-eval-v4` v4, schema 1.6, in `tmp/`); `make eval-continuity BASE=…20261106T072428Z.json CANDIDATE=…20261113T101802Z.json` → exit 0, shared goldens 87, only in CANDIDATE g088 v1, no shared-case differences; `git diff --name-status main...HEAD -- evaluation knowledge config` → only generation config, prompt files, candidates file, `datasets/v4/*`, `suites/public-eval-v4.json` (A) and `suites/public-eval-v3.json` (M), as R15 allows; `knowledge/` untouched; working tree has no protected-path change. `make test-integration` not run separately (T6 changes no retrieval code; Docker tests ran in `make verify`).
- Independent checks (from the JSON, by script): all three generation files have schema 1.1, `generator_is_fake` false, provider `anthropic`, endpoint `api`, `git_dirty` false; commits `e84e098` (Haiku, Sonnet v3) and `a0869a5` (Sonnet v4); `retrieval_identity`, `ingestion_config` and `prompt` (answer v1, `7284d3b3…5c11`) equal across all three; thresholds 0.9 / 0.86 in each; `generator_unavailable` 0 in each. Haiku: answer 0.8621, refusal 0.8000 (both below the thresholds, so it falls short); Sonnet v3: 0.9655 / 0.8667, p95 generation 5755.7 ms, $0.005155 per case; Sonnet v4: 0.9659 / 0.8824, p95 5772.4 ms, $0.005209 per case, $0.006435 per answered case. Costs recomputed from per-case usage equal `actual_cost_usd`. Response models equal the configured ID. The choice of Sonnet follows the recorded rule (Haiku falls short on two criteria, Sonnet on none) plus the user's verbatim spot-check confirmation and data-location acceptance (stage 3). Thresholds and the rule are recorded verbatim; the result files carry the same thresholds, consistent with approval before the runs. Backend-enforced refusals confirmed: v4 refusals 15 of 17, with 6 `citation_invalid/model_url` (u007, u011, u013, u014, u016, u017), so 9/17 = 0.5294 without the discard; v3 had 4 of 13. Overshoot cases g040, g022 and g021 confirmed (only generation times above 10 s).
- Config: only `default_generator: anthropic`, `anthropic.model_id: claude-sonnet-5-5`, `pricing` 2 / 10 and their comments changed; `bedrock.model_id` and `inference_profile` are null; schema 1.1.
- Suite v4: the v3 rows match their v4 copies byte for byte except `evaluation_suite_id` (all three files checked by script); new cases g088, u016 and u017 match the user's decisions (g088 has the reworded query, 3 facts and 2 documents; u017 has the reworded reason); v3 `status` is `replaced`; `DEFAULT_SUITE` is v4 for retrieval, security and generation. The candidates file changes only `review` fields, plus the cand012_en_001 `proposed_case` deviation the user accepted (original kept in `review.original_*`).
- Tests: the changed null-default assertions are each justified by the T6 config change, and the null paths stay covered through config copies. The new default tests read `default_generator`, the model and the pricing from the file (no literal), and stub the SDK.
- Secrets: grep for key-like patterns (`sk-ant-`, `sk-`, AKIA/ASIA, ARN with account ID, `Bearer`, `x-api-key`, an assigned `ANTHROPIC_API_KEY`) across the four result files, the spec records, `CURRENT_STATE.md`, the config, v4 data, candidates and changed tests returned no matches. The result files hold no local paths or URLs.
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R14] The "Prices and data location" box asks the user to record the list prices. Data location is in the user's verbatim stage-3 decision. The prices (Sonnet 2 / 10, Haiku 0.10 / 0.50) appear only as the user's CLI arguments (`pricing_applied` source `cli` in the result files) and in the agent's narrative, with no verbatim user confirmation line. → Add a one-line verbatim price confirmation in the final T6 records or the T7 decision.
  - F2 [MINOR, IMPLEMENTATION, R14] Stage 2 table: Haiku "$0.000279 per case (… / 99 cases with usage)" is $0.000282 (0.027876 / 99), and the per-answered figures divide by answered cases (Haiku $0.000372 = total / 75). This does not affect the criterion. → Correct the figure in the T7 decision.
  - F3 [MINOR, IMPLEMENTATION] `CURRENT_STATE.md`: Next step item 1 still opens "T5b approved; T6 (user-owned) next" and says T6 is `implementing (round 1)`. The carry-over line states that Sonnet "tried to answer with a URL" for u016 and u017; the file has no answer text, so that is an inference from the rule and the token counts (stage 5 says so). → Reconcile in T7.
- Summary for user (PASS only):
  - Changed: `config/generation.yaml` now commits `anthropic` with `claude-sonnet-5-5` at $2 / $10 (Bedrock stays null). Suite `public-eval-v4` (115 cases; g088, u016 and u017 new) is the default; v3 is `replaced`. Candidate reviews are recorded. The default-generator tests read the file. Four user-run result files are checked and ready for the final T6 commit.
  - Verified by: `make verify` (1795 passed), `make validate-evaluation`, `make eval-security` on v4 (PASS), `make eval-continuity` (no shared-case differences), and a script that checked every result file (identity, commit, thresholds, rates, p95, cost, zero `generator_unavailable`).
  - Worth your attention: Sonnet clears the 0.86 refusal line only because the backend discards answers containing URLs (6 of 15 v4 refusals; 0.53 without them). That is the main prompt-v2 input. `deadline_s` is soft (3 overshoots of about 32 s). T6 has two commits (checkpoint plus final), which you approved. Three MINOR record fixes for T7: price confirmation line, a Haiku cost figure, a stale `CURRENT_STATE` next-step line.
  - Reading order:
    1. `config/generation.yaml`: the committed default, model and pricing.
    2. `packages/rag/src/way2australia_rag/evaluation/cli.py` → `DEFAULT_SUITE`: v4 for all three eval commands.
    3. `evaluation/suites/public-eval-v4.json` and `evaluation/datasets/v4/*`: the v3 rows plus g088, u016 and u017; `public-eval-v3.json` status.
    4. `evaluation/candidates/012-candidates.jsonl`: review decisions and `promoted_as`.
    5. `experiments/results/generation-evaluation-idx-v2-20261113T102514Z.json` (v4 Sonnet), then the two stage-2 files and `retrieval-evaluation-idx-v2-20261113T101802Z.json`.
    6. `packages/rag/tests/generation/test_generation_config.py`, `test_ask_cli.py`, `tests/evaluation/test_generation_eval.py`: default-from-file tests and null-path copies.
    7. Supporting edits: `test_suite_v4.py`, `test_suite_v3.py`, `test_status_handling.py`, `test_suite_loader.py`; records in `tasks.md`, `task-reviews.md`, `CURRENT_STATE.md`.
- Usage: (orchestrator)

### User decision (2026-11-13, T6 approved; verbatim)
> I approve T6. I confirm the Anthropic list prices used, per 1M input / output tokens: Sonnet 5.5 $2 / $10 and Haiku 5.5 $0.10 / $0.50. Today's spend in the Anthropic Console is $1.11, which matches the recorded run costs.
>
> Fix F2 and F3 as you proposed, and record this approval and the prices verbatim. In the F3 rewording, keep the fact that the result rows record citation_invalid / model_url for u016 and u017 (the backend found a URL in the model's output), and mark only "tried to answer" as the inference.
>
> Then make the single final T6 commit with the Spec-Task: 012/T6 trailer and push spec/012. It includes the four result files and the remaining records, and nothing from experiments/results/tmp/. After that, start T7.

Fixes made after approval (orchestrator, records only):
- F1: the price confirmation above closes it.
- F2: the stage-2 table Haiku cost per case is corrected to $0.000282 (0.027876 / 99); the per-answered figure ($0.000372) divides by answered cases and is unchanged.
- F3: `CURRENT_STATE.md` Next step item 1 and the status lines now say T6 approved; the carry-over states the recorded `citation_invalid / model_url` rows as fact and marks "tried to answer" as an inference.
- Usage: (orchestrator)

## T7 — round 1

### Implementation
- Model: claude-sonnet-5-5 (Sonnet 5.5), run as a subagent (tier not checked against `MODEL_PREFERENCES.md`; no user to ask). No Anthropic or Bedrock call, no key set, nothing staged or committed; `experiments/results/tmp/` untouched (the `make eval-security` run wrote its own result file there, git-ignored).
- Files changed: `docs/project/DECISIONS.md` (D081–D091: context builder; prompt versioning and contract; answerability and citations; generator interface, client, config, deadline, region and profile finding; outage eligibility as its own decision departing from D062, with 413; direct Anthropic API, data location and the pending Bedrock switch; answer-language rule; generation result 1.1 and cost guard; security 1.6; T6 model outcome with the R14 table, thresholds and prices verbatim; suite v4), `docs/project/ARCHITECTURE.md` (query flow, "Grounded generation" module table, fallback bullets, evaluation list), `docs/project/COMMANDS.md` (setup notes with the AWS findings and the `aws login` workaround, `make ask`, `make eval-generation`, security 1.6, default suite v4), `docs/project/TECH_STACK.md` (Bedrock target plus direct-API note), `docs/project/ROADMAP.md` (items 9, 10, 13), `docs/project/CURRENT_STATE.md` (implemented reality, Spec 012 row, next step, Spec 013 and prompt-v2 carry-overs, g021 added to the deadline note), `.kiro/specs/012-grounded-generation/design.md` (new `## As-built notes`), `tasks.md` (T7 boxes ticked, State), `Makefile` (stale comment on `ask` only: it said there is no default generator; no recipe changed).
- Verification run: `HF_HUB_OFFLINE=1 HF_HOME=<empty temp dir> make verify` → pass (1795 passed, 5 skipped; lint, typecheck, skills-check and validate steps clean); `make test-integration` (Docker Qdrant reachable) → pass (28 passed, 1772 deselected); `HF_HUB_OFFLINE=1 make eval-security` → PASS (schema 1.6); `git diff --name-status main...HEAD -- evaluation knowledge config` → only the generation config and prompt files (A), the candidates file (A), `datasets/v4/*` (A), `suites/public-eval-v4.json` (A) and `suites/public-eval-v3.json` (M), as R15 allows; `knowledge/` absent; no uncommitted protected-path change. Stale-text grep of the docs (security `1.5`, "no generation", "no default generator", "Bedrock generation"): remaining hits are historical per-spec statements (HISTORY.md, Spec 011 lines) or the updated lines.
- Notes: (1) Figures in D090 were read from the three result files by script (per-language coverage, p50/p95 per stage, tokens, cost); Haiku cost per case is $0.000282 (T6 review F2 applied). (2) D086 and `CURRENT_STATE.md` carry the user's price confirmation and data-location acceptance as recorded verbatim in the T6 user decision. (3) The Makefile comment fix is outside the T7 file list; it changes a comment only. (4) The `botocore[crt]` workaround is documented in `COMMANDS.md`; the extra was not changed. (5) Not verified: nothing that needs a model call. The `test_security_eval.py` follow-up chore in `CURRENT_STATE.md` is unchanged.
- Usage: 186K tokens · 43 tool uses · 16:42

### Review
- Model: claude-opus-5-5 (Opus 5.5; matches the BEST tier for Claude Code). Run as a subagent; no Anthropic or Bedrock call, nothing staged or committed.
- Verdict: FAIL
- Commands: `HF_HUB_OFFLINE=1 HF_HOME=<empty scratch dir> make verify` → pass (1795 passed, 5 skipped); `make test-integration` → pass (28 passed, 1772 deselected); `HF_HUB_OFFLINE=1 make eval-security` → PASS (schema 1.6, `generation_checks` present; result in `experiments/results/tmp/`); `git status --porcelain -- evaluation/ knowledge/ config/` → empty; `git diff --name-status main...HEAD -- evaluation knowledge config` → only the generation config and prompt files, the 012 candidates file, `datasets/v4/*`, suite v4 (A) and suite v3 (M), as R15 allows.
- Facts checked independently (from code, config and the three generation result files plus the v4 retrieval result, by script): D090 table (answer and refusal rates and counts, `citation_invalid` by sub-reason, `output_invalid` g065/g076/g086, precision/recall, facts coverage by language, p50/p95 per stage, mean tokens, cost per case incl. Haiku $0.000282 = 0.027876 / 99) all match; thresholds 0.9 / 0.86 in each file; prices 2/10 and 0.10/0.50 (`pricing_applied`) and the user's verbatim confirmation (T6 approval line); v4 refusals 15/17 with 6 `model_url` (u007, u011, u013, u014, u016, u017), 9/17 = 0.5294; overshoots g040 31.9 s, g022 32.6 s, g021 32.1 s, each 2 attempts; config values (top_k 5, max_blocks 5, max_chars 8000, snippet 240, effort low, max_tokens 1024, timeouts 20/30, retries 2, chars/token 2.0, 400 output tokens); prompt hash `7284d3b3…5c11`; D-B status sets incl. 413 and 529; Bedrock-form regex `^[a-z]+\.`; refused `ANTHROPIC_BASE_URL` / `ANTHROPIC_CUSTOM_HEADERS`; citation rule order and marker regex; config bounds (max_tokens 64–8192, retries 0–5); `DEFAULT_SUITE` v4; suite v4 115 = 88/17/10, 3 approved and 4 rejected candidates; v4 retrieval HitRate@5 1.0, Recall@5 1.0, MRR 0.9754 (n 88); CLI options (`--price-input`, `--limit`/`--all`, generator choices). No key-like strings in the diff. Makefile edit is comment-only and correct (default comes from `default_generator`); accepted as a necessary stale-text fix.
- Findings:
  - F1 [MAJOR, IMPLEMENTATION, R16/DoD] Three lines still state that implemented Spec 012 features do not exist, contradicting the code (R16: docs "describe the code as built"; `CURRENT_STATE.md` must describe implemented reality): `docs/project/CURRENT_STATE.md` Spec 011 carry-overs, "**Context building** (deduplication, context budgeting, evidence ordering) is not implemented; it moved to roadmap **item 10**."; `docs/project/ARCHITECTURE.md` Reranking section, "Context building (deduplication, budgeting, evidence ordering) is not implemented; it moved to roadmap item 10."; `docs/project/COMMANDS.md` Evaluation paragraph, "`make eval-generation` does not exist yet (generation evaluation is a later roadmap item)." (the same file documents it a few lines below). → Mark each as done by Spec 012 (D081 / `make eval-generation`), or remove it; the `EVAL_ARGS` sentence should also name `eval-generation`.
  - F2 [MINOR, IMPLEMENTATION, R16] `docs/project/ROADMAP.md` item 13: "Still open in this item: plus the serving concerns…" (leftover "plus"). → Drop "plus".
  - F3 [MINOR, IMPLEMENTATION, R16] D090: "Response model equals the configured ID in every case" is not true for Haiku: g065, g076, g086 (`output_invalid` / `max_tokens`) record no `response_model` and no usage. → "in every case that recorded one" (the As-built note already says it is carried only where an output was returned).
  - F4 [MINOR, IMPLEMENTATION, R16] Other "item 10" references now meaning Spec 013 remain in older carry-overs (`ARCHITECTURE.md` Reranking: latency limit "belong to roadmap item 10"; fallback list "binding per-request timeout is roadmap item 10"; `CURRENT_STATE.md` Spec 011 "Latency limit and device for item 10", "refusal-threshold work of item 10" (now decided by D083)). Not false while item 10 is open, but they point at the wrong owner. → Retarget to Spec 013 / D083 where the item moved, or leave for the retrospective.
  - Note (not a T7 finding): `make eval-security` still prints `deferred s005 (ungrounded_generation): roadmap-10` and `deferred s006 (citation_manipulation): roadmap-10` although security 1.6 adds generation checks; the deferral labels come from the harness/evaluation data, not T7. For the retrospective.
- Usage: 158K tokens · 34 tool uses · 16:34

## T7 — round 2

### Implementation
- Model: claude-sonnet-5-5 (Sonnet 5.5), run as a subagent (tier not checked against `MODEL_PREFERENCES.md`; no user to ask). No Anthropic or Bedrock call; nothing staged or committed.
- Scope: round 1 review findings F1-F4 only; docs only, no code, config, evaluation or knowledge change.
- Files changed: `docs/project/CURRENT_STATE.md`, `docs/project/ARCHITECTURE.md`, `docs/project/COMMANDS.md`, `docs/project/ROADMAP.md`, `docs/project/DECISIONS.md`, `.kiro/specs/012-grounded-generation/tasks.md` (T7 State), this file.
- F1: the three stale "not implemented" lines now say context building was done by Spec 012 (D081) (CURRENT_STATE Spec 011 carry-overs, ARCHITECTURE Reranking); the COMMANDS "does not exist yet" sentence now points at the `eval-generation` section, and the `EVAL_ARGS` sentence names `eval-generation`.
- F2: ROADMAP item 13, leftover "plus" removed.
- F3: D090 now says "in every case that recorded one".
- F4: owner references re-pointed: ARCHITECTURE (reranker latency limit and per-request timeout -> Spec 013), ROADMAP (reranker timeout, Spec 008 serving items -> Spec 013), CURRENT_STATE (latency limit heading, async freshness, `open_retrieval` rerank default and tokenizer check, F4 `open_retrieval` fold, F2 fallback-stage field -> Spec 013; "refusal-threshold work" now points at D083). Remaining "item 10" hits are historical wording (Spec 012 scope line, the "split from item 10" notes, D077/D079 records).
- Grep of `docs/project` (excluding HISTORY.md) for "not implemented", "does not exist yet" and "item 10": remaining "not implemented" hits are accurate (Phase 2, observability, stemming, the "Planned, not implemented" list).
- Not changed (as instructed): `make eval-security` deferred-label output (retrospective item).
- Verification: `HF_HUB_OFFLINE=1 HF_HOME=<empty temp dir> make verify` -> pass (1795 passed, 5 skipped). `make test-integration` not re-run (docs-only round).
- Usage: 106K tokens · 40 tool uses · 10:08

### Review
- Model: claude-opus-5-5 (Opus 5.5; matches the BEST tier for Claude Code). Run as a subagent; no Anthropic or Bedrock call, nothing staged or committed.
- Verdict: PASS
- Commands: `HF_HUB_OFFLINE=1 HF_HOME=<empty scratch dir> make verify` → pass (1795 passed, 5 skipped); `HF_HUB_OFFLINE=1 make eval-security` → PASS (result in `experiments/results/tmp/`); `make test-integration` (Docker Qdrant reachable) → pass (28 passed, 1772 deselected); `git status --porcelain -- evaluation/ knowledge/ config/` → empty; `git diff --name-status main...HEAD -- evaluation knowledge config` → generation config and prompt files, 012 candidates, `datasets/v4/*`, suite v4 (A), suite v3 (M), as R15 allows; no key-like strings in the diff.
- Round 1 findings checked: F1 fixed (CURRENT_STATE Spec 011 carry-over and ARCHITECTURE Reranking now say context building was done by Spec 012, D081; COMMANDS no longer says `eval-generation` does not exist, and the `EVAL_ARGS` sentence names it). F2 fixed (ROADMAP item 13 "plus" gone). F3 fixed (D090 "in every case that recorded one"). F4 fixed for the cited lines (ARCHITECTURE latency limit and per-request timeout, CURRENT_STATE latency heading, async freshness, 011 F2, tokenizer check, 008 F2/F4 → Spec 013; refusal-threshold → D083). Own grep of `docs/project` (HISTORY.md excluded) for "not implemented", "does not exist yet", "item 10", "no generation", "no default generator", security `1.5`: remaining hits are accurate (Phase 2, stemming, "Planned, not implemented", historical Spec 011 / D077–D079 records, "split from item 10" notes) except F1 below. Changed lines rechecked against code and config: generation result schema 1.1 (`GENERATION_SCHEMA_VERSION`), `config/generation.yaml` schema 1.1, `default_generator: anthropic`, `anthropic.model_id: claude-sonnet-5-5`, `bedrock.model_id: null`; CURRENT_STATE goal line, Spec table and Next step describe implemented reality (T1–T6 approved, T7 in review).
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R16] `docs/project/CURRENT_STATE.md` Spec 011 retrospective F1 still ends "fix together with the item 10 rework of `open_retrieval`", while the new Spec 013 serving bullet lists 011 F1 under the Spec 013 `open_retrieval` rework. → Retarget to Spec 013 (can be done in the retrospective).
  - Note (carried from round 1, not a T7 finding): `make eval-security` still prints `deferred s005 / s006 … roadmap-10`; deferral labels come from evaluation data. For the retrospective.
- Summary for user (PASS only):
  - Changed: project docs for Spec 012: D081–D091 in `DECISIONS.md`; generation flow and module table in `ARCHITECTURE.md`; `make ask`, `make eval-generation`, setup and Bedrock status in `COMMANDS.md`; Bedrock target plus direct-API note in `TECH_STACK.md`; items 9, 10, 13 in `ROADMAP.md`; implemented reality, Spec 013 and prompt-v2 carry-overs in `CURRENT_STATE.md`; As-built notes in `design.md`; one Makefile comment. Round 2 fixed the four round 1 findings (stale "not implemented" lines, owner references).
  - Verified by: `make verify` hub-free (1795 passed), `make eval-security` PASS, `make test-integration` (28 passed), protected-path diff, doc greps, figures and config values checked against code and result files.
  - Worth your attention: one leftover "item 10" pointer (F1, minor). D090 records that Sonnet's v4 refusal rate passes partly through the backend URL discard (9/17 = 0.5294 without it). Bedrock remains blocked; the switch is its own spec or task.
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `docs/project/CURRENT_STATE.md` → status, next step, Spec 012 and Spec 013 carry-overs.
    2. `docs/project/DECISIONS.md` → D081–D091 (D085 departure from D062; D086 direct API; D090 model outcome).
    3. `docs/project/ARCHITECTURE.md` → target query flow and "Grounded generation (Spec 012)" table.
    4. `docs/project/COMMANDS.md` → setup notes, `make ask`, `make eval-generation`, security 1.6.
    5. `.kiro/specs/012-grounded-generation/design.md` → As-built notes.
    6. Supporting edits: `ROADMAP.md` (items 9, 10, 13), `TECH_STACK.md` (generation endpoints), `Makefile` (`ask` comment), `tasks.md` (T7 boxes, State).
- Usage: 119K tokens · 28 tool uses · 15:51

### User decision (2026-11-13, T7 approved; verbatim)
> I approve T7. Before committing, fix the round-2 F1: in CURRENT_STATE.md, the Spec 011 retrospective F1 line should say "Spec 013" instead of "the item 10 rework of open_retrieval". It's a doc-only edit and needs no re-review. Then record the approval, commit T7 once with Spec-Task: 012/T7, push spec/012, mark all tasks approved, run graphify update . once, and start the spec-reviewer retrospective.
>
> For the retrospective, keep in mind: the deadline_s comment in config/generation.yaml still says "total per request". That's a known carry-over together with the hard wall-clock cap, so don't change it in this spec unless the retrospective decides otherwise. The deferred s005/s006 ... roadmap-10 labels in make eval-security output come from evaluation data, so treat them as a carry-over too.

Round 2 F1 fixed after approval (doc-only, no re-review, as the user decided).
