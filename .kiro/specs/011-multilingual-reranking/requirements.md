# 011 — Multilingual Reranking Requirements

Status: approved (2026-11-04)

## Goal

Add a multilingual cross-encoder reranker to the default `hybrid` retrieval path (roadmap item 9, reranking part only). Concretely:

- a reranking stage reorders the top fused hybrid candidates by a cross-encoder score before the `top_k` cut, and every returned hit is re-checked for authorization and applicability after reranking;
- the reranker is `BAAI/bge-reranker-v2-m3` at a pinned revision, behind an optional extra, with a deterministic fake for tests;
- when the reranker model is unavailable, the query is served by un-reranked hybrid results, marked as skipped; a reranker failure never becomes a BM25 fallback;
- evaluation results, `eval-compare` and the security gate cover the reranked path and its skip paths;
- user-owned real runs on suite `public-eval-v3` at two rerank depths decide, by a rule fixed here before any run, whether reranking becomes enabled by default.

Repository facts that shape the scope (checked 2026-11-04, hybrid reference `experiments/results/retrieval-evaluation-idx-v2-20261104T105300Z.json`, suite `public-eval-v3`, 87 goldens, `w2a-realcheck-idx-v2`, `lexical-v2`, `lote: ml`, device `mps:0`):

- Hybrid overall MRR 0.9228 (86 of 87 hits); `en` (54) MRR 0.9321; `mixed` (17) MRR 0.8647; `ml` (16) MRR 0.9531. One case is 1/87 ≈ 0.0115 MRR.
- Fusion losses a reranker can address (document ranks dense / BM25 → fused reciprocal rank): `g056` 1 / 2 → 0.5 and `g057` 1 / 2 → 0.5 (`mixed`); `g061` 3 / 8 → 0.2 (`mixed`); `g026` 6 / 6 → miss (`en`, lost on the `idx-v2` promotion, D071); also `g006`, `g029`, `g042`, `g076`.
- The default index has 34 chunks over 13 documents (`max_chunks_per_document` 4). Fusion candidate depth is 50, so a rerank depth of 50 reranks every eligible chunk; gains measured here may overstate behaviour on a larger corpus.
- Hybrid latency p50 73.4 ms, p95 108.2 ms (dense leg p95 107.4 ms, BM25 leg p95 1.2 ms).
- `sentence-transformers` (already the `bge-m3` extra's dependency) provides `CrossEncoder`; no other new runtime dependency is needed.
- On the v3 BM25-only run, 10 of the 11 `ml` misses return zero BM25 candidates (only `g076` has one, at rank 7), so reranking the BM25 path cannot help Malayalam; that needs candidate generation (translation/transliteration, carry-over).

## Dependencies

- Spec 010 (verified, merged `cae06c3`): suite `public-eval-v3`, `ResolvedLote` and `check_applicable`, `LanguageApplicabilityError`, result 2.4, `eval-compare --cross-tokenizer`, `make eval-continuity`, security result 1.4 (D072).
- Spec 009: default index `idx-v2` / recursive 128 + title (D071), distinct-document metrics, `--cross-index`.
- Spec 008: `open_retrieval`, `FallbackRetriever`, `RetrievalUnavailableError` and `FallbackReason`, `classify_model_error` rules (D057, D062), five gated paths, open-time vs per-query fallback (D058, retrospective F2).
- Spec 007: `HybridRetriever`, `rrf_fuse` (D052), `Strategy`, `Retriever` Protocol, `config/retrieval.yaml`, `eval-compare` identity rules (D054), default `hybrid` (D055).
- Spec 005/006: `check_hit` fail-closed re-check (D035, D040), `safe_text`, evaluation runner, unanswerable top-1 score reporting, `small_sample`.
- Spec 004: BGE-M3 adapter pattern (lazy import, pinned revision, `main`/`latest` refused, `OptionalDependencyError`), `make setup-bge-m3`.
- Retrospective notes: `.kiro/specs/010-multilingual-retrieval/review.md` "Notes for the next spec" (`g056`/`g057` as reranking inputs; hub-free verify; `lote` stays outside `AccessContext`).
- The real runs (R10) need the extras installed, Docker Qdrant, the user's `w2a-realcheck-idx-v2` collection with its `lexical-v2` file, and a one-time model download. They are run by the user.

## Decisions resolved before drafting

Decision Brief approved by the user on 2026-11-04, with these choices and changes:

- **Name.** `011-multilingual-reranking`; branch `spec/011` from `main` (`3b81508`).
- **Scope.** Reranking only. Context building (deduplication, context budgeting, evidence ordering) is deferred to roadmap item 10.
- **Paths.** Reranking runs on `hybrid` only, never on `--strategy dense`, `--strategy bm25` or the BM25 fallback.
- **Model.** `BAAI/bge-reranker-v2-m3` through `sentence-transformers` `CrossEncoder`, pinned revision, optional extra; deterministic fake reranker for tests.
- **Reranker unavailable.** Serve un-reranked hybrid results: a missing extra is a configuration error (exit 2); only failures with a network or timeout error in the explicit `__cause__` chain are eligible (D057/D062 rules); the result records `rerank_skipped_reason` and the stage (`open` or `query`). Reranker failures have their own error type, caught inside the reranking stage, and never surface as `RetrievalUnavailableError` (user change 1).
- **Scoring.** Order by the cross-encoder score alone (no blending with RRF); RRF and leg ranks kept for diagnosis.
- **Depth.** Default rerank depth 20 fused chunks; real runs measure depth 20 and depth 50.
- **Inference timeout.** Decided in the design (a timeout, or an explicit record that there is none, as D058 did).
- **Default off.** `rerank.enabled: false` is the committed default through T1–T4; tests read it from config; only the R10 task may change it (user change 3).
- **Latency.** Report-only, with a pre-registered escalation (R10). Numbers come from `mps:0` on a development machine; the binding latency limit belongs to item 10.
- **Promotion rule** (R10), including the `en` hit→miss escalation (user change 2).
- **Result 2.5** reports truncated query–chunk pairs (user change 4) and unanswerable top-1 cross-encoder scores (user change 5).
- **Shape.** Six tasks: T1 reranker contract, adapters and config; T2 reranking stage, skip path and wiring; T3 result 2.5 and `eval-compare`; T4 security gate; T5 user-owned real runs and the promotion decision; T6 docs, decisions and hand-off.

## R1 — Reranker contract and fake

A reranker scores query–chunk pairs through an explicit interface that generic retrieval code depends on.

### Acceptance criteria

- A `Reranker` Protocol in `packages/rag/` takes a query string and an ordered sequence of candidate texts and returns one finite float score per candidate, in input order. It exposes an identity: `model_id`, `revision`, `max_length`, `is_fake`, and the device (known after load, `null` before).
- It also reports, per call, how many query–chunk pairs were truncated at `max_length` (counted with the model's own tokenizer, or deterministically by the fake).
- A deterministic fake reranker, usable without the extra, PyTorch or a download, gives the same scores for the same inputs on every run and can be configured in tests to prefer chosen candidates, to raise an unavailability failure at load or at a given call, and to return malformed output.
- The reranker receives chunk text as data only: no instruction wrapping, no prompt, and nothing in the text changes the scoring call (C-level rule: retrieved text is untrusted).
- No language code, script name or Malayalam-specific branch appears in the reranker code.

## R2 — `bge-reranker-v2-m3` adapter and optional extra

The real reranker is pinned and loaded only when asked for.

### Acceptance criteria

- An adapter runs `BAAI/bge-reranker-v2-m3` at a pinned revision (a commit hash; `main`, `latest` and empty are refused at configuration time, as for BGE-M3). The revision is recorded in config and in results.
- `sentence-transformers` is imported only inside model loading, so importing retrieval code never needs the extra. A new optional extra (`reranker`) declares the dependency; `make setup-bge-m3` installs it with `bge-m3`. `make setup` still removes optional extras.
- Without the extra, asking for reranking exits 2 with `OptionalDependencyError`-style advice naming the setup command, before any query; this is a configuration error, never a skip.
- `make verify` passes without the extra, Docker or a download, and hub-free (`HF_HUB_OFFLINE=1`, empty `HF_HOME`). An opt-in real-model smoke test (like `W2A_RUN_BGE_M3_SMOKE`) is skipped by default.

## R3 — Rerank configuration and selection

Reranking is a reviewed config value, off by default until R10 decides.

### Acceptance criteria

- `config/retrieval.yaml` gains a `rerank` block (schema version bumped): `enabled`, `model_id`, `revision`, `depth`, `max_length`, and any batch setting the design needs. Invalid values are refused at load with a message naming the key. `depth` is an integer from 1 to the fusion `candidate_depth` and at least `top_k` at request time (refused otherwise, exit 2).
- The committed value is `enabled: false` through T1–T4. Tests that depend on the default read it from the config file, never a literal. Only the R10 task may change `enabled` or `depth`.
- `make retrieve` and `make eval-retrieval` accept `--rerank` and `--no-rerank` to override the config. Asking for reranking with `--strategy dense` or `--strategy bm25` is refused (exit 2, message says reranking applies to `hybrid` only).
- With reranking off, every path returns exactly what it returned before this spec (existing tests unchanged apart from new default fields).

## R4 — Reranking stage on `hybrid`

The reranker reorders the fused candidates; authorization and applicability are re-checked afterwards.

### Acceptance criteria

- With reranking on, `hybrid` fuses as today (`rrf_fuse` and `HybridRetriever` unchanged), takes the top `depth` fused chunks (fewer if fewer exist), scores them with the reranker, orders them by cross-encoder score descending (ties broken by fused rank), and returns the first `top_k`. Scores are not blended with RRF.
- Each returned hit carries the cross-encoder score as its score, `score_kind: cross_encoder`, and keeps its fused rank and leg ranks for diagnosis.
- The stage may only reorder the candidates it received: a reranker output with the wrong count, a non-finite score, or anything else malformed fails the query with a reranker error that is not a skip and not a fallback (fail closed).
- After reranking, every returned hit passes `check_hit` and then, with a `lote`, `check_applicable` again before it is returned; a failure raises the existing `RetrievalAuthorizationError` or `LanguageApplicabilityError` (never caught by the stage or by `FallbackRetriever`).
- The same `ResolvedAccess` object, `ResolvedLote` and `top_k` reach the hybrid legs and the stage; nothing in the reranker or its output can change access or applicability.
- The reranking stage sits inside `FallbackRetriever`: when the dense side is unavailable (open time or per query), BM25 serves exactly as in Spec 008 and no reranking runs. A test pins this order.
- The result records the rerank identity, the rerank depth used, the number of truncated pairs, and a `rerank` latency leg next to the existing `dense` and `bm25` legs.

## R5 — Reranker unavailable: serve un-reranked hybrid

A reranker outage degrades to hybrid results, never to BM25, and is always visible.

### Acceptance criteria

- Reranker failures have their own error type, separate from `RetrievalUnavailableError`, with a closed set of reasons. Only a load or download failure with a network or timeout error in the explicit `__cause__` chain is eligible (D057/D062 rules; `__context__` is never followed; hub HTTP 5xx is not eligible). Any other reranker error propagates.
- The stage catches only that error type. On it, the query is served by the un-reranked hybrid result (same hits as reranking off), marked with `rerank_skipped_reason` and `rerank_stage` (`open` when loading failed when retrieval was opened, `query` when it failed during a query).
- A test shows that a query-time reranker failure serves `hybrid+rerank_skipped:<reason>` and not BM25: `FallbackRetriever` never sees the reranker failure.
- Open-time behaviour is defined in the design (for example: an open-time failure skips reranking for the whole run, like D058's open-time row, or retries per query) and tested.
- `make retrieve` prints the served path and a stderr warning only when reranking was requested and skipped.
- Whether reranker inference has a timeout is decided in the design and recorded in a decision; if it has none, the decision says so and why.

## R6 — Result 2.5 and `eval-retrieval` reporting

Evaluation results show what was reranked, what was skipped, and at what cost.

### Acceptance criteria

- `make eval-retrieval` writes result schema 2.5. Older result files (2.0–2.4) still load and read as "no reranking".
- Top-level: the requested rerank setting; the rerank identity (model, revision, `max_length`, `is_fake`, device) or `null` when off; the rerank depth; counts of skipped queries by reason and stage; the total number of truncated query–chunk pairs and the number of cases with at least one.
- Per case: the served path (`hybrid`, `hybrid+rerank`, `hybrid+rerank_skipped:<reason>`, or the existing BM25 fallback paths), the cross-encoder top-1 score when reranked, the truncated-pair count, and the fused rank of each relevant document beside its reranked rank.
- Latency: overall p50/p95, p50/p95 by served path, and p50/p95 of the `rerank` leg, plus the device.
- The warm-up (excluded from p50/p95 and reported separately, as for the embedder) includes loading the reranker model, so model load or download time never enters per-query latency or R10's latency escalation.
- Unanswerable cases: when reranked, the top-1 cross-encoder score per case and its distribution next to the golden top-1 distribution, marked informational (an input for item 10's refusal threshold, not a gate).
- A fake reranker is refused for a real evaluation run unless the existing fake allowance is given (as for the fake embedder), and the result records `is_fake`.

## R7 — `eval-compare` with reranking

Comparisons never mix reranked and un-reranked results by accident.

### Acceptance criteria

- `make eval-compare` reads 2.5 files and refuses a rerank identity difference (enabled vs off, model, revision, depth, `max_length`) unless `COMPARE_ARGS=--cross-rerank` is given; with it, the rerank lines are printed and the comparison runs on the existing gate.
- A file with any skipped query is never compared as reranked: its skipped cases are reported by served path, and a compare that treats it as a reranked candidate or base is refused (exit 2) with a message naming the skip count.
- `--cross-rerank` relaxes only rerank identity; every other identity rule (collection, `index_version`, embedder, lexical, `lote`, suite) still applies, and it combines with existing flags only as the design specifies.
- `make eval-continuity` treats rerank identity like the other identity fields (design decides refuse or report) and is tested.

## R8 — Security gate over the reranked paths

Authorization and applicability hold on every new path.

### Acceptance criteria

- `make eval-security` gates three more paths: `hybrid_rerank`, `hybrid_rerank_skip_open` and `hybrid_rerank_skip_query`, each over the three chunkers and with `lote: null` and `lote: <active code>`, on the throwaway corpus with the fake embedder and fake reranker. Security result schema 1.5.
- On `hybrid_rerank`, a fake reranker that scores forbidden and non-applicable text highest cannot surface them: they are excluded before fusion, and the post-rerank re-check holds. A test injects a stage defect (a candidate not in the fused set) and shows the re-check fails closed.
- On both skip paths, the un-reranked hybrid results pass the same re-checks, and the result shows the skip reason and stage.
- The existing five paths keep their results. `make eval-security` passes on v3.

## R9 — Unchanged behaviour and protected paths

### Acceptance criteria

- With reranking off, dense, BM25, hybrid and both fallback paths behave exactly as before; `rrf_fuse`, `HybridRetriever`, `FallbackRetriever`'s eligibility, the access and applicability builders, ingestion, the payload, chunkers, lexical files and `INGESTION_NAMESPACE` are unchanged. No new `index_version`; no re-ingestion; no lexical rebuild.
- `evaluation/` and `knowledge/` are not changed. `config/` changes only by the `rerank` block (R3) and, if R10's rule allows, its promotion.
- `lote` stays outside `AccessContext` (C4, D072).
- Agents never write to, delete or re-ingest a `w2a-realcheck-*` collection and never run the real models; tests never write under `experiments/results/` outside `tmp/`.
- No secrets in code, config, fixtures, results or docs.

## R10 — Real runs and the promotion decision (user-owned gate)

The user records real reranked results on v3; a rule fixed here decides the default.

### Acceptance criteria

- With every code task approved and committed, the user installs the extras, and runs `make eval-retrieval` on suite v3 with `lote: ml` on `w2a-realcheck-idx-v2` for two reranked arms: depth 20 and depth 50. Each is compared with the hybrid reference `…20261104T105300Z.json` by `make eval-compare COMPARE_ARGS=--cross-rerank`.
- Before the arms, a reranking-off run on the same commit equals the hybrid reference case by case (hit, reciprocal rank, ranked document IDs), checked with `make eval-continuity` or `eval-compare`; a difference stops the gate until explained.
- The result files are checked like earlier user runs (suite v3, not fake, clean commit, same collection, `index_version`, chunker, embedder, lexical file, `top_k`, `lote: ml`, no skipped queries in a reranked arm) and committed. The pinned reranker revision is recorded.
- **Promotion rule (fixed here, before any run).** An arm passes only if all hold against the hybrid reference: the `eval-compare` gate passes; no `ml` or `mixed` case flips from hit to miss; overall MRR is not lower. If the depth-20 arm passes, it is promoted; else if the depth-50 arm passes, it is promoted; else reranking stays off.
- **Escalations (not automatic).** Promotion of a passing arm comes to the user to decide, instead of happening automatically, when either holds: any `en` case flips from hit to miss; or the arm's p95 minus the reference hybrid p95 (108.2 ms) exceeds 1000 ms. The user's decision is recorded verbatim.
- On promotion, only `rerank.enabled` and `rerank.depth` change in `config/retrieval.yaml`; no Qdrant or lexical change.
- A decision in `DECISIONS.md` records the outcome with numbers: overall and `en`/`ml`/`mixed` slices for both arms, every flipped case, the ranks of `g026`, `g056`, `g057`, `g061`, `g006`, `g029`, `g042`, `g076`, p50/p95 overall and of the rerank leg with the device, how rerank latency changed from depth 20 to depth 50, truncated-pair counts, the unanswerable top-1 cross-encoder score distribution, and that the numbers are from `mps:0` on a development machine (production hardware not chosen; binding latency limit is item 10).

## R11 — Spec-wide verification

### Acceptance criteria

- `make verify` passes without the extras, Docker or a model download, and hub-free (`HF_HUB_OFFLINE=1`, empty `HF_HOME`).
- `make test-integration` passes (Docker Qdrant).
- `make eval-security` passes on v3 for all eight paths.
- `git diff --name-status main...HEAD -- evaluation knowledge config` lists only `config/retrieval.yaml`.

## R12 — Documentation and decisions

### Acceptance criteria

- New decisions (from D075) record: the reranker choice, pin and extra; the stage placement inside `FallbackRetriever` and on `hybrid` only; cross-encoder-only scoring; the post-rerank re-check; the reranker error type and skip policy (open vs query, the timeout decision); result 2.5; the `--cross-rerank` rule; security result 1.5; the R10 outcome.
- `ARCHITECTURE.md` (query flow with the rerank stage), `COMMANDS.md` (`--rerank`, `--no-rerank`, `--cross-rerank`, setup, new refusals), `TECH_STACK.md` (reranker) and `CURRENT_STATE.md` describe the code as built; `ROADMAP.md` notes that item 9's context building moved to item 10 and that item 13's reranker-failure path is done.
- Carry-overs recorded in `CURRENT_STATE.md` Known issues and the retrospective notes: context building for item 10; the binding latency limit and device choice for item 10; unanswerable cross-encoder scores as a refusal-threshold input; query translation/transliteration for `g067`–`g069`; any residual misses after reranking.

## Out of scope

- Context building: deduplication, context budgeting and evidence ordering (roadmap item 10 input).
- Reranking on `dense`, `bm25` or the BM25 fallback. Evidence: on the v3 BM25-only run, 10 of the 11 `ml` misses return zero BM25 candidates (only `g076` has one, at rank 7), so reranking the fallback cannot help Malayalam; it needs candidate generation first.
- Generation, citations, refusal thresholds and the HTTP route (roadmap item 10); a binding latency limit, circuit breaker, Qdrant client lifecycle and startup policy (item 10).
- Query translation or transliteration, including `g067`–`g069`.
- Blending cross-encoder and RRF scores, changing RRF parameters, or training/fine-tuning a reranker.
- A second reranker model or an LLM-as-reranker.
- Semantic chunking, FAQ indexing, the chunk size vs title prefix experiment, a new `index_version` or re-ingestion.
- Device pinning (D038); non-guest roles; per-scope lexical files (D050); Phase 2 release workflow.
- Changes under `evaluation/` or `knowledge/`.

## Risks

- Small sample: one case is about 0.0115 MRR; `mixed` and `ml` slices are 17 and 16 cases.
- The corpus is small (34 chunks); depth 50 reranks everything, so gains may overstate a larger corpus.
- `g026` can only be recovered if its chunk is inside the rerank depth.
- Memory: BGE-M3 plus the reranker on `mps` take about 4–5 GB together.
- The first real run needs a hub connection for a large download; `make verify` stays hub-free.
- Verify budget: the hook allows at most two `make verify` runs per agent session.

## Definition of Done

- R1–R12 satisfied and traced to approved tasks.
- R10 user-owned runs recorded, checked and committed; the rerank default set by R10's rule (or by the user's recorded escalation decision) and recorded in a decision.
- `make verify` (no extras, Docker or model; also hub-free), `make test-integration` and `make eval-security` pass.
- Protected-path check: only `config/retrieval.yaml` under `evaluation`, `knowledge` and `config`.
- `DECISIONS.md`, `ARCHITECTURE.md`, `COMMANDS.md`, `TECH_STACK.md`, `ROADMAP.md` and `CURRENT_STATE.md` match the code.
- The required `spec-reviewer` retrospective passes and the user approves the merge.

## Traceability

| Requirement | Task(s) | Verification |
|---|---|---|
| R1 | T1 | Protocol and fake reranker tests |
| R2 | T1 | adapter tests (revision refusal, lazy import, missing extra); opt-in smoke test |
| R3 | T1, T2 | config schema tests; CLI flag and refusal tests; default read from config |
| R4 | T2 | stage ordering, malformed output, re-check and composition-order tests |
| R5 | T2 | skip tests (open, query); "skip is not BM25" test; eligibility tests |
| R6 | T3 | result 2.5 key tests; truncation, warm-up load and unanswerable score tests; fake-reranker refusal |
| R7 | T3 | `test_compare.py` and continuity additions |
| R8 | T4 | `test_security_eval.py` additions; `make eval-security` (eight paths) |
| R9 | T1–T4 | existing tests unchanged; protected-path diff |
| R10 | T3, T5, T6 | depth-50 experiment config (T3); user runs, continuity and compares (T5); decision in T6 |
| R11 | T6 | `make verify` (also hub-free); `make test-integration`; `make eval-security`; protected-path diff |
| R12 | T6 | doc review against code; `DECISIONS.md` D075+ |
| Definition of Done | T6 | the commands above |

## Change log

<!-- Approved amendments only, one dated line each:
- YYYY-MM-DD — <R#/T#>: <what changed and why>. Re-opened <T#>. -->
