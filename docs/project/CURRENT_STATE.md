# Current State

Last updated: 2026-11-13 (Spec 012 T5b approved; T6 user-owned smoke gate next; no real model call yet)

## Current phase

Phase 1 foundation complete.

Architecture, initial public knowledge seed, evaluation seed and Phase 1/Phase 2 boundaries have been designed.

Spec 001 project foundation is complete.

## Current goal

Specs **001–011** are **verified on `main`** (last: Spec 011, merged `d40d734`, 2026-11-06). Retrieval defaults: index **`idx-v2`** (recursive 128 + title, D071), **`hybrid`** with BM25 fallback (D055, D058), **`lexical-v2`** (D072), reranking on at depth 20 (D079). Setup for a default run: `make ingest`, then `make index-lexical`; reranked runs need `make setup-bge-m3` and a cached reranker. Workflow trim **D080** is in place (hooks share one shell parser, graph rebuilt once per spec, `graphify-out/cache/` local). **Spec 012** (roadmap item 10 without the HTTP route: context building, Bedrock generation, answerability, citations) is **implementing** on `spec/012`; **T1–T5 approved** (context builder, prompts and language, generator and Bedrock adapter, answer service and `make ask`, `make eval-generation` and security 1.6). Bedrock is blocked (all quotas 0), so a 2026-11-10 amendment (approved) adds **T5b**: a direct Anthropic API generator for development and evaluation. Bedrock stays the production target. **T6**, the user-owned real-run gate, then runs on that endpoint. No real model call has been made. The HTTP route and serving policy go to **Spec 013**. Repository-based shared context keeps Codex, Claude Code, Cursor and Kiro interchangeable (D063). Closed history: `docs/project/HISTORY.md`.

## Finalized high-level decisions

- Python/FastAPI backend.
- Next.js/TypeScript frontend.
- RAG under `packages/rag/`.
- Shared domain concepts under `packages/core/`.
- Public/guest retrieval only in Phase 1.
- English + Malayalam initially; future CCL languages through metadata/config.
- `DocumentRepository` abstraction from the beginning.
- `LocalDocumentRepository` in Phase 1.
- S3-backed repository planned for Phase 2.
- Qdrant primary retrieval.
- SQLite FTS5 fallback.
- BGE-M3 initial embeddings.
- BM25 + RRF hybrid retrieval (Spec 007, merged; default strategy `hybrid`, D055); `hybrid` degrades to BM25 when Qdrant or the embedding model is unreachable (Spec 008, merged).
- multilingual reranking implemented (Spec 011): `BAAI/bge-reranker-v2-m3` cross-encoder over hybrid candidates, default on at depth 20 (D079).
- Amazon Bedrock Runtime for generation.
- Langfuse for RAG tracing.
- CloudWatch for operations.
- Terraform for AWS infrastructure.
- AWS Mumbai (`ap-south-1`) deployment target.
- GitHub Actions for CI/CD.
- Evaluation Suite includes goldens, unanswerable/refusal, multilingual, security and regression cases.
- Phase 2 Knowledge Release workflow/evaluation governance are designed but not implemented.
- Basic product analytics are Phase 2 only.

## Seed data status

Latest seed design includes:
- normalized public business knowledge;
- normalized official knowledge;
- Malayalam-specific official policy;
- structured owner-approved FAQ pairs;
- document manifest/inventory;
- document metadata schema;
- lightweight initial Knowledge Release;
- versioned evaluation datasets;
- Evaluation Suite manifest;
- evaluation schema;
- security fixtures;
- source-precedence/access/language configuration;
- Phase 2 analytics event schema.

## Current implementation status

Implemented (detail per spec: `docs/project/HISTORY.md`, the specs under `.kiro/specs/` and `DECISIONS.md`):
- Spec 001: `uv` workspace, FastAPI skeleton with `GET /health`, typed settings, pytest, Ruff, Pyright, `make verify`, local Qdrant (Docker Compose), package skeletons (`packages/core`, `packages/rag`, `packages/observability`).
- Spec 003 and D080: task-gated spec skills (`agent-skills/`, mirrored by `make skills-sync`, checked by `make skills-check`); task states and `task-reviews.md` (`WORKFLOW.md`, D023); verify-budget and graphify-guard hooks (`tools/hooks/`, D073, D080).
- Spec 002: document models, `DocumentRepository` and `LocalDocumentRepository`, `content-hash-v1`, `EligibilityPolicy`, `make validate-knowledge`.
- Spec 004: ingestion (`IngestionService`, chunkers, BGE-M3 adapter, `QdrantIndexStore`, `make ingest`).
- Spec 005: dense retrieval (`AccessContext`, access filter and fail-closed `check_hit`, `DenseRetriever`, `make retrieve`).
- Spec 006: evaluation framework (suite loader, `make validate-evaluation`, `make eval-retrieval`, `make eval-security`, `make eval-compare`).
- Spec 007: BM25 (SQLite FTS5, `make index-lexical`), RRF hybrid, default `hybrid`.
- Spec 008: retrieval fallback (`hybrid` → BM25 on Qdrant or model outage; `bm25` needs neither).
- Spec 009: `structure` and `recursive` chunkers, default `idx-v2`, `eval-compare --cross-index`.
- Spec 010: `lote` applicability on every path, `lexical-v2`, suite `public-eval-v3`, `make eval-continuity`.
- Spec 011: cross-encoder reranking on `hybrid` (`BAAI/bge-reranker-v2-m3`, depth 20), result 2.5, security 1.5.
- Spec 012 T1–T5: context builder, answer prompt v1, `AnswerService`, citation validation, Bedrock adapter (no committed default; D-C), `make ask`, `make eval-generation` (result 1.0) and security result 1.6. Real runs, the default model and suite v4 are T6; docs and decisions are T7.

Not yet implemented:
- no HTTP retrieval route (Spec 013); retrieval degradation exists only for `hybrid` (Spec 008); reranking exists on `hybrid` only (Spec 011);
- the Phase 2 "compare shared cases" mode of `eval-compare` (today any difference in the case set is refused);
- committed generation default, real-model comparison and suite v4 (Spec 012 T6); generation docs and decisions (T7);
- observability;
- CI/CD;
- Terraform deployment.

## Spec status

| Spec | Status |
|---|---|
| 001 — project foundation | implemented before the review process existed (no `review.md`) |
| 002 — document model and repository | verified 2026-10-15, merged `dca6cbd` |
| 003 — task-gated agent workflow | verified 2026-10-15 (bootstrap exception, built on `main`) |
| 004 — ingestion baseline | verified 2026-10-17, merged `dde5b35` |
| 005 — dense retrieval baseline | verified 2026-10-23, merged `b33462e` |
| 006 — evaluation framework | verified 2026-10-24, merged `ab28d89` |
| 007 — hybrid retrieval | verified 2026-10-28, merged `3cf70eb` |
| 008 — retrieval fallback | verified 2026-11-01, merged `1107b67` |
| 009 — chunking experiments | verified 2026-11-04, merged `5a6deb7` |
| 010 — multilingual retrieval | verified 2026-11-04, merged `cae06c3` |
| 011 — multilingual reranking | verified 2026-11-06, merged `d40d734` |
| 012 — grounded generation | implementing on `spec/012`; T1–T5 approved 2026-11-09; 2026-11-10 amendment (T5b, direct Anthropic API) approved; T5b approved 2026-11-13; T6 (user-owned), T7 not started |

## Next step

1. **Spec 012 T5b approved 2026-11-13; T6 (user-owned) next.** (Amendment approved 2026-11-10.) Bedrock is blocked: every quota on the account is 0, and AWS Support referred both Claude 5.5 quota requests to AWS Sales. The amendment adds R17 and task **T5b**: a separate `anthropic` generator for the direct Anthropic API (development and evaluation). It shares a Claude-only adapter with Bedrock, takes the key only from `ANTHROPIC_API_KEY`, refuses `ANTHROPIC_BASE_URL`, uses no fallbacks and checks the response model. `requirements.md` and `design.md` are approved (2026-11-10). T6 then runs on `--generator anthropic` and commits `default_generator: anthropic`. Bedrock stays the production target, and the switch back is its own spec or task. No Anthropic API or Bedrock call has been made.
2. **D-A smoke tests (user-run):** after T5b, the direct-API smoke test (`W2A_RUN_ANTHROPIC_SMOKE=1`, `W2A_ANTHROPIC_MODEL_ID` = `claude-sonnet-5-5` / `claude-haiku-5-5`) is the T6 gate. The Bedrock smoke test (`W2A_RUN_BEDROCK_SMOKE=1`, `global.` profiles, `ap-south-1`) stays open until AWS grants access. `aws login` still needs `eval "$(aws configure export-credentials --format env)"` (`botocore[crt]` is not in the bedrock extra; document or add it in T7).
3. **Follow-up chore (D080):** in `packages/rag/tests/evaluation/test_security_eval.py`, share one CLI gate run across `test_cli_lexical_file_is_removed_after_a_pass`, `test_cli_pass_writes_a_result_and_exits_zero` and `test_cli_clause_less_lexical_store_exits_one_naming_strategies` (about −38 s of `make verify`). Docker tests stay in `make verify` until CI runs `make test-integration`.
4. The trial docs re-extraction of 2026-11-07 was discarded and is not to be retried (D080); the docs part of the graph stays from the earlier extraction.
5. Open since the verify-budget chore: remove user-level verify-budget hook copies; the committed hook is `.claude/settings.json` + `tools/hooks/verify_budget.py`.

## Ingestion operating notes

- Default production index (after Spec 009 T6 promotion): **`idx-v2`**, **`recursive` v1** (128 tokens, 16 overlap, title prefix) in `config/ingestion.yaml`; collection **`way2australia-idx-v2`**. Legacy **`idx-v1`** / heading: `experiments/configs/chunking/heading-idx-v1.yaml` with `--config`.
- Use `QDRANT_COLLECTION_BASE` for every fake-embedder run. A fake run without it records the default collection for the configured `index_version` as fake, and a later real run is then refused until a new `index_version` is set in `config/ingestion.yaml`.
- After `make setup`, default runs (hybrid with reranking on, Spec 011 T5) need `make setup-bge-m3` plus a cached reranker (the first reranked run downloads the pinned model); `--strategy bm25` (and `dense`) now needs `--no-rerank`.
- `make setup` removes the optional `bge-m3` extra; use `make setup-bge-m3` before a real-embedding run (on a slow connection `UV_HTTP_TIMEOUT=600 make setup-bge-m3`). A missing extra is detected when the embedder is built (exit 2, before any Qdrant call).
- `make verify` runs the Docker integration tests too when a local Qdrant is reachable (they create and remove temporary collections); otherwise they skip.
- `INGESTION_NAMESPACE` (`533d6c5a-5ac2-4dd5-a4e6-5fbb620efba2`) is permanent: changing it changes every point ID.
- Decisions: D025 to D030 and D032 in `DECISIONS.md`.

## Known issues / deferred

These are evaluation-data gaps, deliberately deferred for now (decision 2026-10-13). Changing them requires human-approved evaluation cases (C6).
- `relevant_section_ids` is empty in every evaluation case, so `eval-retrieval` reports zero section-measurable cases (deferred by Spec 009; headed documents and suite v3 are a later spec).

Spec 009 known issues and carry-overs (documented; no remediation tasks):
- Ignored top-level `knowledge_release_id` / `evaluation_suite_id` in `config/ingestion.yaml` and `experiments/configs/chunking/recursive-128.yaml` (`evaluation_suite_id` still names the replaced `public-eval-v1`). The ingestion loader ignores them. Remove at the next `index_version`; keep this promotion's byte copy so the arm's `ingestion_config` hash stays valid (D071).
- Size vs prefix confounding: the promoted arm is recursive 128 tokens *and* title prefix together (D071). Recorded metrics belong to that pair, not either treatment alone. A later spec may split them.
- `g026` (en, `business_006_mock_assessments`) flipped hit→miss on promotion. Overall HitRate@5 stayed 0.9855 (68/69); English HitRate@5 / Recall@5 1.0 → 0.9815, MRR 0.9352 → 0.9321. R10 allowed the flip (`en`, not `ml`/`mixed`). Revisit with reranking or a size-vs-prefix split.
- FAQ pairs: `knowledge/structured/owner_approved_faq_pairs.jsonl` is not indexed (own spec).
- Semantic chunking: out of scope (roadmap 7 remainder).
- Malayalam stemming: not implemented (declined in Spec 010; roadmap carry-over).
- Spec 008 serving/API items remain open for **Spec 013 (HTTP route and serving policy; split from roadmap item 10 at Spec 012 planning)** (see Spec 008 known issues and 008 retrospective F4/F5): startup and reopen policy for a missing or stale lexical file **and** refusal when the file's recorded tokenizer disagrees with `config/retrieval.yaml` (Spec 010 T5 carry-over: `open_retrieval` does not check today; stale `lexical-v1` would serve silently after a v2 promotion); circuit breaker, Qdrant client lifecycle, async freshness (`verify_fresh` uses `asyncio.run`), freshness cost on a large corpus (D060/D067), fallback-stage observability, Qdrant 5xx eligibility (D062), API surface.
- Per-scope lexical files remain a roles-spec item (D050).
- In a shallow clone (base commit `06b1af9` absent) the Spec 007 T1 v1 byte-identity tests in `test_suite_v2.py` skip, and nothing flags it. Accepted while there is no CI; revisit in the CI spec.

Spec 008 known issues and carry-overs (documented by T8; no remediation tasks):
- Qdrant client lifecycle (T4 review): `open_retrieval` closes the Qdrant client on the fallback path but not on every open failure, and `OpenedRetrieval.close()` does not close the client. A long-running server would leak a connection pool per failed open; the CLIs exit after one run. **Spec 013** (first HTTP surface) must close the client on every open failure and in `close()`, with a test.
- `verify_fresh` uses `asyncio.run`, so it cannot run inside a running event loop; **item 10** needs an async freshness check or a check at startup outside the loop (T2 review F3).
- The standalone freshness check rereads every eligible document at each open (milliseconds for 13 documents); revisit for a large corpus (D060).
- No circuit breaker: with Qdrant hanging, each hybrid query waits about `query_timeout_s` (3 s) before BM25 serves (D058). Qdrant 5xx and a Hugging Face hub 5xx are not fallback-eligible (D062).
- The security gate's standalone `bm25` path checks identity plus "every seed chunk present" instead of `verify_fresh`, and that check is one-way (an extra non-forbidden row is not refused); see the design As-built notes (T6).

Spec 008 retrospective (`.kiro/specs/008-retrieval-fallback/review.md`, round 1), MINOR, no remediation tasks:
- F2: result 2.2 and `eval-compare` do not distinguish an open-time from a per-query fallback (same `bm25+fallback:<reason>` path; `dense_attempt` about 0 ms after an open-time fallback, yet labelled "includes failed dense attempt"). Docs corrected; a `fallback_stage`-style field is left to **roadmap item 10** or observability (item 11).
- F4: `open_retrieval`'s `bm25` branch and `_open_fallback` duplicate the standalone open and lexical `document_count` wiring; fold into one helper when **roadmap item 10** reworks `open_retrieval` (together with the client lifecycle item).
- F5: no test drives the open-time fallback from a `bind_to` scroll failure (Qdrant fails after `DenseIndex.open`) through `open_retrieval`; covered by composition (`chunk_identities` maps transport errors, T1; the `except` spans `open_bound_lexical`, T4).

Spec 011 known issues and carry-overs (documented by T6; no remediation tasks in this spec):
- **Context building** (deduplication, context budgeting, evidence ordering) is not implemented; it moved to roadmap **item 10**.
- **Latency limit and device for item 10:** depth 20 costs about 1 s per query at p95 on `mps:0` (+920.6 ms over the hybrid reference, 79 ms under the 1000 ms escalation line); there is no inference timeout (D077) and the device is not pinned. The binding per-request limit, circuit breaker, model and client lifecycle and device choice belong to the HTTP spec. The numbers are a dev-machine figure, not a production one.
- **Unanswerable cross-encoder scores** (D079): top-1 scores for the 15 unanswerable cases (median -4.17, max 1.67) overlap the golden distribution (median 3.08); three unanswerable cases score above 0, so no fixed cut-off is safe. Input for the refusal-threshold work of item 10, not a threshold.
- **Query translation / transliteration** remains the intended fix for `g067`–`g069` on BM25-only and on the hybrid fallback (reranking applies to hybrid only; on the v3 BM25-only run the `ml` misses return no BM25 candidates, so reranking the fallback cannot help).
- **Residual rank losses:** `g038` (en) and `g062` (mixed) drop from rank 1 to 2 under reranking (still hits); `g057` stays at 0.5; `g026` is back to a hit at reciprocal rank 0.333.
- **Gate coverage:** `make eval-security` runs the rerank paths at depth 50 / `top_k` 50, so the committed depth-20 cut is not itself exercised (membership is decided by the legs and re-checked; D078).
- `retrieval/availability.py` private names are imported by `rerank/errors.py` (design As-built notes); `check_applicable` is called on a partial `PointPayload` and must keep reading only `document_id` and `lote_languages` (a test guards this).
- `experiments/configs/rerank/retrieval-depth50.yaml` differs from `config/retrieval.yaml` in `rerank.enabled` and `rerank.depth`.

Spec 011 retrospective (`.kiro/specs/011-multilingual-reranking/review.md`, round 1), MINOR, no remediation tasks:
- F1: with reranking requested and a dense outage, `eval-retrieval` asks BM25 for `rerank.depth` (20) chunks instead of 50 and records `retrieval_depth` 20; top-5 distinct-document metrics are unaffected while `required_depth` (17) is at most 20. Recorded in the design As-built notes and `COMMANDS.md`; fix together with the item 10 rework of `open_retrieval` (depth per served path).
- F2: `open_retrieval(rerank=False)` is the library default; only the two CLIs resolve the effective setting from `rerank.enabled`. The item 10 HTTP route must resolve it from config too, or it serves un-reranked hybrid silently.
- F3: `top_k > rerank.depth` is refused inside the stage at query time, after the reranker was loaded at open (`make retrieve --top-k 30` loads the model, then exits 2); `eval-retrieval` refuses earlier through the distinct-document depth check, with advice that names `candidate_depth`, not `rerank.depth`. No wrong result is possible.

Spec 010 known issues and carry-overs (documented by T6; no remediation tasks in this spec):
- **Query translation / transliteration** (including Latin-script Malayalam): the intended fix for **`g067`–`g069`** on BM25-only and on the hybrid **fallback** path when dense is unavailable; out of scope for Spec 010. BM25-only `ml` MRR **0.2396** (n=16) on v3 realcheck (`…20261104T105321Z.json`).
- **`g056` / `g057`:** hybrid fusion demotes a dense rank-1 relevant document to reciprocal rank 0.5 (BM25 rank 2); inputs for **roadmap item 9** reranking, not a Spec 010 bug.
- **No Malayalam knowledge content** was added (`knowledge/` unchanged); evaluation grew via v3 cases only.
- **Malayalam stemming** and **per-script fusion weighting** were declined (requirements out of scope).
- **Script mix** uses Unicode **name** prefixes, not Scripts.txt; romanized Malayalam counts as **`latin`** (reporting only).
- **`open_retrieval`** does not compare the lexical file's recorded tokenizer to `config/retrieval.yaml` (stale `lexical-v1` would serve silently); group with roadmap **item 10** startup policy (also missing/stale file).
- Spec **009** carry-overs below remain unchanged (ignored yaml keys, `g026`, FAQ, semantic chunking, per-scope lexical files, shallow-clone test skip, etc.).

Spec 007 known issues and carry-overs (documented by T10; no remediation tasks):
- The `seed-v1` Knowledge Release still names suite `public-eval-v1` (replaced); releases are Phase 2 (D049).
- BM25 statistics (IDF, average length) are computed over every row of a lexical file, including rows the access clause excludes. Today only eligible guest/public chunks are indexed, so they reveal nothing; a future roles spec needs one lexical file per access scope (D050).
- Malayalam in BM25 matches only exact tokens (no stemming): `g067`–`g069` are lost by BM25 alone and `g064`/`g065` rank on the Latin `NAATI`/`CCL`; hybrid keeps every `ml` hit but with lower reciprocal ranks (MRR 0.9167 -> 0.7917 on a 6-case sample).
- `git_state` (shared with the legacy `make retrieval-baseline`) ignores every untracked file under `experiments/results/`, not only result JSON; a path git quotes reports dirty (fails safe). Accepted at T10 review (F3).

Spec 006 retrospective (`.kiro/specs/006-evaluation-framework/review.md`, round 1), MINOR, no remediation tasks:
- F1: the byte-identity check of `evaluation/` before and after a run is tested for the loader (`test_suite_loader.py`) and the validator (`test_validate.py`), not around the `eval-retrieval` and `eval-security` runners (the design's "each runner"). Both runners read evaluation data only through `load_suite`, and no evaluation code writes under `evaluation/`.
- Legacy `make retrieval-baseline --allow-fake` without `--output` still writes into `experiments/results/` (Spec 005 location, kept by R12/R13); only the new commands use the git-ignored `experiments/results/tmp/`. Do not commit a fake result.
- `make eval-security` is not a step of the `make verify` target; its gate runs inside `make verify` through `test_security_eval.py`.
- The security result's `access.role` is hard-coded `guest` (correct in Phase 1; change it when other roles are added).

Spec 005 retrospective (`.kiro/specs/005-dense-retrieval-baseline/review.md`, round 1), MINOR, no remediation tasks (F1 and F2 were documentation gaps, reconciled in that round):
- F4: interface sketches in `design.md` differ from the code (`retrieval/__init__.py` has no exports; `SuiteRef.golden_dataset_path`; extra `run_baseline` parameters); recorded in the design's As-built notes.
- F5: the design error table says a non-guest role is refused without Qdrant contact, but resolution runs after the read-only `DenseIndex.open` (as the design data flow and T5 say); unreachable today.

Spec 004 review findings still open (all MINOR, no remediation tasks; see `.kiro/specs/004-ingestion-baseline/task-reviews.md` and `review.md` round 1):
- T3 F1: `test_info_reports_fake_identity` uses `pytest.raises(Exception)` instead of `pydantic.ValidationError`.
- T7 F2: `QdrantIndexStore` holds both `_index_version` and `index_version`.
- T7 F5: `test_security_fixtures_never_reach_the_index` does not assert the fixtures loaded.
- T8 round 2 F1: the late `OptionalDependencyError` re-raise in `service.py` (broken installs) has no test.
- Retro F1: the `repositories/manifest.py` module docstring says "one record per document version"; the loader allows one record per `document_id` (D026, D032).
- The BGE-M3 device is recorded in retrieval results and the baseline JSON but not pinned and not an index setting (D038); the user's real run used `mps`.
- Default production index is `recursive` v1 (Spec 009 T6); `heading` v1 remains via `heading-idx-v1.yaml`. None of the 13 seed documents has headings, so heading behaviour is covered mainly by synthetic tests (D030).

Spec 002 retrospective (`.kiro/specs/002-document-model-and-repository/review.md`, round 1), MINOR, no remediation tasks (F1–F4 handled by Spec 004 as noted):
- F3: partly closed by Spec 004 T1 (`GUEST_PUBLIC_POLICY` and access scopes are tested against `config/access_policy.yaml`); source authorities are still not cross-checked against `source_precedence.yaml`.
- F4: decided by D026 (one version per `document_id`; version history is Phase 2); the `manifest.py` docstring is still stale and the "version increments on change" rule is unenforced.
- F5: `ARCHITECTURE.md` repository sketch uses `list_documents(status=...)`, not `DocumentQuery`.
- F6: loader and `validate-knowledge` validate documents on two separate paths (loader reports only the first Pydantic error, no date check).

## Important constraint

Do not begin implementing Phase 2 S3/admin/release-management functionality during Phase 1.

Only preserve the interfaces/IDs needed to add it cleanly later.
