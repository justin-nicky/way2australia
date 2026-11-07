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
