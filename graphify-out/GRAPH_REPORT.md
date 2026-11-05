# Graph Report - way2australia  (2026-11-05)

## Corpus Check
- 327 files · ~378,215 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 36 file(s) not represented in the graph (top: (none) 20, .jsonl 13, .mdc 1)

## Summary
- 5273 nodes · 16334 edges · 218 communities (183 shown, 35 thin omitted)
- Extraction: 77% EXTRACTED · 23% INFERRED · 0% AMBIGUOUS · INFERRED: 3715 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `389c456d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_compare.py
- hashing.py
- test_fallback.py
- test_bm25.py
- test_validate.py
- RetrievalResult
- test_applicability.py
- test_index.py
- T4 — round 1
- Factory
- FakeTokenizer
- T5 — Security gate across chunkers
- HeadingChunker
- compare.py
- test_lexical_cli.py
- test_suite_v2.py
- CURRENT_STATE.md current state document
- test_availability.py
- QdrantIndexStore
- test_retriever.py
- 007 — Hybrid Retrieval Requirements
- test_validate_knowledge.py
- RerankSkipReason
- BGE-M3 Adapter
- test_lexical_standalone.py
- Spec 004 ingestion baseline
- LexicalIndex
- test_suite_v3.py
- test_strategy_eval.py
- Evaluation CLI Tests
- validate_evaluation
- way2australia_api/config.py
- IngestionConfigurationError
- evaluation/test_cli.py
- 010 — Multilingual Retrieval Requirements
- test_lexical_standalone.py
- 009 — Chunking Experiments Requirements
- 008 — Retrieval Fallback Requirements
- repositories/__init__.py
- KnowledgeDocument
- test_legacy_baseline_snapshot.py
- typing
- EvaluationConfigurationError
- Workflow Reviewer
- LocalDocumentRepository
- 011 — Multilingual Reranking Design
- test_cli_config.py
- D055 Default strategy is hybrid (Spec 007)
- Ingestion (Phase 1 baseline, Spec 004)
- 007 — Hybrid Retrieval Requirements
- test_lexical_tokenizer.py
- HeadingChunker
- retrieval_eval.py
- FallbackRetriever
- FakeReranker
- BgeM3Embedder
- Development Workflow
- LocalRepositoryConfig
- test_security_eval.py
- json
- Evaluation Phase 1 framework (Spec 006)
- SecurityIndex
- BgeRerankerV2M3
- make retrieve
- hub_offline_empty_cache
- AWS target
- make eval-retrieval
- Spec 007 hybrid retrieval
- test_manifest_validation.py
- ResolvedAccess
- embedder
- Phase 1 RAG query pipeline
- load_retrieval_config
- 008 — Retrieval Fallback Requirements
- list_eligible_documents
- Section: Next step
- test_rerank_eval.py
- test_baseline.py
- embedder
- repositories/__init__.py
- hashlib
- test_verify_budget_hook.py
- Ingestion pipeline (Spec 004)
- test_recursive.py
- pytest
- open_retrieval
- rerank
- Backend stack
- embedder
- D023 Task-gated agent workflow
- guest_access
- re
- Roadmap 13 - Graceful degradation
- pathlib
- Spec status table
- test_eligibility.py
- test_rerank_bge.py
- SpyIndex
- transcript_metrics.py
- CURRENT_STATE.md
- QdrantIndexStore
- read_result
- test_structure.py
- make ingest
- Retrieval package (Spec 005 and 007)
- DenseIndex
- Qdrant (vector database)
- 011 — Multilingual Reranking Requirements
- Development Workflow
- FakeEmbedder
- evaluation/cli.py
- test_content_hash.py
- Spec 005 dense retrieval baseline
- test_violation_names_the_document_from_the_error_attribute
- security_corpus.py
- test_repository_contract.py
- fusion
- SQLite FTS5
- SpyIndex
- Chunk
- failing_client
- test_status_handling.py
- retrieval_client_factory
- chunker_build.py
- QdrantIndexStore
- Baseline runner and result JSON
- test_failed_write_removes_partial_file
- Development Workflow
- test_status_handling.py
- absent_query_languages
- Phase 1 - Production-oriented RAG
- RuntimeSettings
- sync_agent_skills.py
- Vocabulary, flashcards and free access
- .search
- asyncio
- verify_budget.py
- Any
- Evaluation Framework Goal
- lexical/ package (Spec 007)
- Phase 1 - Production-oriented RAG
- BGE-M3 (initial embedding model)
- Way2Australia AI Platform Master Implementation Plan
- Retrieval fallback (Spec 008, D056-D062)
- eval-compare
- Payments, account access and support boundaries
- make retrieve
- make test
- Mission
- format_security_summary
- documents/__init__.py
- Spec 004 retrospective round 1 (PASS)
- policy
- policy
- policy
- ResolvedAccess
- reranked_run
- baseline.py
- Orchestrator State Machine
- way2australia_api/__init__.py
- Project Context README
- json
- way2australia_rag/__init__.py
- Scripted
- way2australia-core
- Phase 1 analytics event contract
- Spec-driven development workflow
- api/__init__.py
- test_eval_cli_bm25_needs_neither_qdrant_nor_the_embedder
- DocumentRepository Protocol (async)
- tests/evaluation/__init__.py
- tests/retrieval/__init__.py
- way2australia-api
- way2australia-observability
- stalled_port
- Retrospective verdict PASS
- way2australia-core
- .document_count
- Spec-driven development workflow
- D025 persona_scope informational
- T9 deviation: git_dirty true in BM25 and hybrid result files
- way2australia
- way2australia-api
- way2australia-observability
- continuity.py
- security_eval.py
- AccessContext
- test_failed_write_removes_partial_file
- R8 — Evaluation results for degraded runs
- test_status_handling.py
- Roadmap 11 - Observability
- test_both_lote_modes_on_every_path_and_chunker
- ShortResultEmbedder
- policy
- open_retrieval / OpenedRetrieval
- Way2Australia AI Platform Master Implementation Plan
- CountingEmbedder
- ResolvedLote
- test_a_forbidden_hit_injected_into_a_path_fails_the_gate_naming_it
- DocumentRepository
- Retrieval fallback (Spec 008, D056-D062)
- D049 Suite public-eval-v2 and the closed v1 reference (Spec 007)
- IndexIdentity
- Evaluation result format 2.2
- Review
- Scripted
- stalled_port
- _split_body
- _parse_sections
- R12 — Real runs (user-owned gate)
- Spec 008 Retrieval Fallback Requirements

## God Nodes (most connected - your core abstractions)
1. `LocalDocumentRepository` - 120 edges
2. `DenseIndex` - 113 edges
3. `Strategy` - 93 edges
4. `RetrievalConfigurationError` - 92 edges
5. `open_retrieval()` - 88 edges
6. `ResolvedAccess` - 87 edges
7. `DenseRetriever` - 83 edges
8. `run_retrieval_evaluation()` - 82 edges
9. `FakeTokenizer` - 79 edges
10. `FakeEmbedder` - 75 edges

## Surprising Connections (you probably didn't know these)
- `R10 — `eval-compare` identity rules (`compare.py`)` --references--> `_refusals()`  [INFERRED]
  .kiro/specs/007-hybrid-retrieval/design.md → packages/rag/src/way2australia_rag/evaluation/compare.py
- `Change log` --references--> `run_retrieval_evaluation()`  [INFERRED]
  .kiro/specs/009-chunking-experiments/requirements.md → packages/rag/src/way2australia_rag/evaluation/retrieval_eval.py
- `T4 review follow-ups (planner amendment 2026-11-02)` --references--> `run_retrieval_evaluation()`  [INFERRED]
  .kiro/specs/009-chunking-experiments/tasks.md → packages/rag/src/way2australia_rag/evaluation/retrieval_eval.py
- `Acceptance criteria` --references--> `script_mix()`  [INFERRED]
  .kiro/specs/010-multilingual-retrieval/requirements.md → packages/rag/src/way2australia_rag/evaluation/script_mix.py
- `T1 — Reranker contract, adapters, errors and config` --references--> `prefer()`  [INFERRED]
  .kiro/specs/011-multilingual-reranking/tasks.md → packages/rag/src/way2australia_rag/evaluation/security_eval.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Failure classification to fallback serving flow** — kiro_specs_008_retrieval_fallback_design_classify_qdrant_error, kiro_specs_008_retrieval_fallback_design_classify_model_error, kiro_specs_008_retrieval_fallback_design_retrievalunavailableerror, kiro_specs_008_retrieval_fallback_design_fallbackretriever, kiro_specs_008_retrieval_fallback_design_bm25retriever [EXTRACTED 0.85]
- **Standalone lexical open (identity then freshness, no Qdrant)** — kiro_specs_008_retrieval_fallback_design_indexidentity, kiro_specs_008_retrieval_fallback_design_open_standalone_lexical, kiro_specs_008_retrieval_fallback_design_verify_fresh, kiro_specs_008_retrieval_fallback_design_bm25retriever [EXTRACTED 0.85]
- **Authorization applied inside every retrieval leg before fusion** — docs_project_decisions_d035, docs_project_decisions_d040, kiro_specs_007_hybrid_retrieval_design_bm25_retriever, kiro_specs_007_hybrid_retrieval_design_hybrid_retriever [EXTRACTED 0.95]
- **Default strategy decision: R13 rule, T9 runs, D055** — kiro_specs_007_hybrid_retrieval_requirements_r13_default_strategy_decision, kiro_specs_007_hybrid_retrieval_tasks_t9_comparison_gate, docs_project_decisions_d055 [EXTRACTED 0.95]
- **Spec 008 task sequence T1-T8 delivering R1-R14** — kiro_specs_008_retrieval_fallback_tasks_t1_failure_classification_and_qdrant_timeouts, kiro_specs_008_retrieval_fallback_tasks_t2_index_identity_standalone_lexical_open_and_freshness_check, kiro_specs_008_retrieval_fallback_tasks_t3, kiro_specs_008_retrieval_fallback_tasks_t4_fallback_policy_for_hybrid_and_result_marking, kiro_specs_008_retrieval_fallback_tasks_t5, kiro_specs_008_retrieval_fallback_tasks_t6_security_gate_over_the_fallback_paths, kiro_specs_008_retrieval_fallback_tasks_t7_real_runs_user_owned_gate, kiro_specs_008_retrieval_fallback_tasks_t8_documentation_decisions_and_final_verification [EXTRACTED 0.95]
- **Spec 008 deliverable** — docs_project_current_state_spec008, docs_project_current_state_cap_errors, docs_project_current_state_cap_standalone, docs_project_current_state_cap_fallback, docs_project_current_state_cap_result22, docs_project_current_state_cap_security5 [EXTRACTED 1.00]
- **Authorization enforcement chain** — docs_project_decisions_d006, docs_project_decisions_d035, docs_project_decisions_d040, docs_project_decisions_d045, docs_project_decisions_build_access_filter, docs_project_decisions_check_hit [EXTRACTED 1.00]
- **Retrieval fallback stack** — docs_project_decisions_d057, docs_project_decisions_d058, docs_project_decisions_d059, docs_project_decisions_d060, docs_project_decisions_d061, docs_project_decisions_d062 [EXTRACTED 1.00]
- **Graceful degradation paths** — docs_project_roadmap_dense_to_bm25, docs_project_roadmap_reranker_failure, docs_project_roadmap_qdrant_to_fts5, docs_project_roadmap_model_failure [EXTRACTED 1.00]
- **Intentionally avoided technology choices** — docs_project_tech_stack_langgraph, docs_project_tech_stack_bedrock_knowledge_bases, docs_project_tech_stack_bedrock_agents, docs_project_tech_stack_kubernetes, docs_project_tech_stack_multiple_vector_dbs, docs_project_tech_stack_agent_orchestration, docs_project_tech_stack_fine_tuning, docs_project_tech_stack_microservices, docs_project_tech_stack_heavy_frameworks [EXTRACTED 1.00]
- **Hybrid retrieval pipeline** — docs_project_tech_stack_qdrant, way2australia_ai_platform_implementation_plan_bge_m3, docs_project_tech_stack_sqlite_fts5, docs_project_tech_stack_bm25_fts5, docs_project_tech_stack_rrf [EXTRACTED 1.00]
- **Evaluation make targets sharing the suite loader** — _kiro_specs_006_evaluation_framework_design_validate_evaluation, _kiro_specs_006_evaluation_framework_design_eval_retrieval, _kiro_specs_006_evaluation_framework_design_eval_security, _kiro_specs_006_evaluation_framework_design_eval_compare, _kiro_specs_006_evaluation_framework_design_suite_loader [EXTRACTED 1.00]
- **Guest authorization path (resolve, filter, re-check)** — _kiro_specs_005_dense_retrieval_baseline_design_accesscontext, _kiro_specs_005_dense_retrieval_baseline_design_resolve_access, _kiro_specs_005_dense_retrieval_baseline_design_build_access_filter, _kiro_specs_005_dense_retrieval_baseline_design_check_hit [EXTRACTED 1.00]
- **Ingestion pipeline components** — _kiro_specs_004_ingestion_baseline_design_ingestionservice, _kiro_specs_004_ingestion_baseline_design_headingchunker, _kiro_specs_004_ingestion_baseline_design_embedder_protocol, _kiro_specs_004_ingestion_baseline_design_qdrantindexstore [EXTRACTED 1.00]
- **Authorization hard gate construction** — _kiro_specs_006_evaluation_framework_design_eval_security, _kiro_specs_006_evaluation_framework_design_security_index, _kiro_specs_006_evaluation_framework_design_forbidden_variants, _kiro_specs_006_evaluation_framework_design_one_access_path, _kiro_specs_006_evaluation_framework_design_security_gate [EXTRACTED 1.00]
- **Task-gated spec workflow roles** — agent_skills_spec_planner_skill_spec_planner_skill, agent_skills_spec_implementer_skill_spec_implementer_skill, agent_skills_task_reviewer_skill_task_reviewer_skill, agent_skills_spec_reviewer_skill_spec_reviewer_skill [EXTRACTED 1.00]
- **Task-gated workflow roles** — _kiro_specs_003_task_gated_workflow_design_spec_orchestrator, _kiro_specs_003_task_gated_workflow_design_spec_implementer, _kiro_specs_003_task_gated_workflow_design_task_reviewer, _kiro_specs_003_task_gated_workflow_design_spec_planner, _kiro_specs_003_task_gated_workflow_design_spec_reviewer [EXTRACTED 1.00]
- **Language, access and source authority separation** — docs_knowledge_schema_and_metadata_access_scope, docs_knowledge_schema_and_metadata_lote_languages, docs_knowledge_schema_and_metadata_authorization_vs_language_independence, docs_knowledge_source_of_truth_source_precedence [INFERRED 0.75]
- **Knowledge Release composition** — way2australia_ai_platform_implementation_plan_knowledge_release, way2australia_ai_platform_implementation_plan_evaluation_suite, way2australia_ai_platform_implementation_plan_release_manifest, way2australia_ai_platform_implementation_plan_document_manifest [INFERRED 0.75]
- **Security regression controls** — way2australia_ai_platform_implementation_plan_staff_only_canary, way2australia_ai_platform_implementation_plan_poisoned_public_document, way2australia_ai_platform_implementation_plan_graceful_degradation, way2australia_ai_platform_implementation_plan_authorization_before_generation [INFERRED 0.75]
- **Retrieval fallback mechanism** — docs_project_architecture_fallback_retriever, docs_project_architecture_unavailable_error, docs_project_architecture_open_retrieval, docs_project_architecture_open_standalone_lexical [INFERRED 0.85]
- **Hybrid retrieval pipeline** — docs_project_architecture_hybrid_retriever, docs_project_architecture_bm25_retriever, docs_project_architecture_dense_retriever, docs_project_architecture_rrf_fuse [INFERRED 0.85]
- **Evaluation command suite** — docs_project_commands_validate_eval, docs_project_commands_eval_retrieval, docs_project_commands_eval_security, docs_project_commands_eval_compare [INFERRED 0.85]
- **Hybrid retrieval pipeline (dense, BM25, RRF, reranker)** — way2australia_ai_platform_implementation_plan_bge_m3, way2australia_ai_platform_implementation_plan_hybrid_rrf, way2australia_ai_platform_implementation_plan_reranker, way2australia_ai_platform_implementation_plan_qdrant [INFERRED 0.85]
- **Lexical stack: tokenizer, FTS5 store and index-lexical command** — kiro_specs_007_hybrid_retrieval_design_lexical_v1_tokenizer, kiro_specs_007_hybrid_retrieval_design_sqlite_fts5_lexical_store [INFERRED 0.85]
- **Task-gated spec workflow** — docs_project_decisions_d023, docs_project_decisions_d031, docs_project_workflow_task_gated_loop, docs_project_workflow_retrospective [INFERRED 0.85]

## Communities (218 total, 35 thin omitted)

### Community 0 - "test_compare.py"
Cohesion: 0.12
Nodes (58): case(), doc(), doc21(), doc22(), ranked(), refusal(), run(), run_cross() (+50 more)

### Community 1 - "hashing.py"
Cohesion: 0.12
Nodes (23): canonical_json(), _canonical_value(), _canonical_value_mapping(), compute_body_sha256(), compute_content_hash(), sha256_hex(), rewrite_document(), _copy_seed() (+15 more)

### Community 2 - "test_fallback.py"
Cohesion: 0.11
Nodes (26): QdrantTimeouts, access(), client_at(), closed_port(), Fallback, open_hybrid(), Primary, run_cli() (+18 more)

### Community 3 - "test_bm25.py"
Cohesion: 0.07
Nodes (50): LexicalRow, build_production(), ingest_dense(), open_lexical(), payload(), rewrite_settings(), synthetic_entries(), test_bind_does_not_write_to_qdrant() (+42 more)

### Community 4 - "test_validate.py"
Cohesion: 0.13
Nodes (32): edit_rows(), edit_suite(), root(), run(), test_active_golden_without_relevant_documents(), test_candidate_ineligible_document_is_not_unknown(), test_candidate_not_suggested(), test_candidate_referenced_by_suite() (+24 more)

### Community 5 - "RetrievalResult"
Cohesion: 0.05
Nodes (49): T4 — Distinct-document metrics, result 2.3 and cross-index compare, Verification, Acceptance criteria, Change log, Decisions resolved before drafting, R4 — Reranking stage on `hybrid`, Implementation, Review (+41 more)

### Community 6 - "test_applicability.py"
Cohesion: 0.14
Nodes (34): Review, active_lote_codes(), _active_list(), resolve_lote(), build_lexical(), _dropped_lote_setup(), DroppedFilterIndex, DroppedLoteClauseLexical (+26 more)

### Community 7 - "test_index.py"
Cohesion: 0.14
Nodes (41): IndexBindingError, bound_index(), client(), failing_client(), fake_info(), http_client(), make_settings(), open_index() (+33 more)

### Community 8 - "T4 — round 1"
Cohesion: 0.67
Nodes (3): Implementation, T4 — round 1, User decision

### Community 9 - "Factory"
Cohesion: 0.07
Nodes (45): _advice_ok(), clean_env(), Factory, indexed(), ingest(), retrieve(), test_bad_args_exit_2_without_client(), test_bad_config_exit_2_without_client() (+37 more)

### Community 10 - "FakeTokenizer"
Cohesion: 0.05
Nodes (62): Implementation, Implementation, Implementation, Implementation, Implementation, Implementation, Review, Review (+54 more)

### Community 11 - "T5 — Security gate across chunkers"
Cohesion: 0.67
Nodes (3): T4 review follow-ups (planner amendment 2026-11-02), T5 — Security gate across chunkers, Verification

### Community 12 - "HeadingChunker"
Cohesion: 0.10
Nodes (46): write_document(), equivalence_suite(), test_a_reranker_without_the_flag_or_depth_is_refused(), test_reranking_off_has_null_identity_and_no_rerank_unanswerable_keys(), test_unanswerable_rerank_distributions_are_informational(), basic_suite(), build(), default_eval_extras() (+38 more)

### Community 13 - "compare.py"
Cohesion: 0.11
Nodes (39): Implementation, Review, T7 — round 1, User decision, Review, _changed(), _chunker_text(), compare() (+31 more)

### Community 14 - "test_lexical_cli.py"
Cohesion: 0.06
Nodes (49): R3 — Tokenizer `lexical-v1` (`lexical/tokenizer.py`), Implementation, Implementation, Review, Review, T3 — round 2, T3 — round 3, User decision (+41 more)

### Community 15 - "test_suite_v2.py"
Cohesion: 0.14
Nodes (25): committed(), edit_jsonl(), lines(), manifest(), problems(), read_lines(), root(), test_candidates_differ_only_in_promoted_as() (+17 more)

### Community 16 - "CURRENT_STATE.md current state document"
Cohesion: 0.10
Nodes (36): standalone bm25 without Qdrant or extra (IndexIdentity, freshness), CURRENT_STATE.md current state document, Evaluation Suite includes goldens, refusal, multilingual, security, regression, Phase 2 Knowledge Release workflow designed not implemented, Public/guest retrieval only in Phase 1; English + Malayalam, Known issue: Qdrant and Hugging Face 5xx not fallback-eligible, Known issue: verify_fresh asyncio.run in event loop, Known issue: Qdrant client lifecycle leak on failed open (+28 more)

### Community 17 - "test_availability.py"
Cohesion: 0.08
Nodes (28): T1: Hugging Face error shapes (confirmed 2026-10-29), Review, _cause_chain(), classify_model_error(), classify_qdrant_error(), _optional_types(), FallbackReason, caused_by() (+20 more)

### Community 18 - "QdrantIndexStore"
Cohesion: 0.06
Nodes (46): IndexSettingsMismatchError, compare(), IndexSettings, mismatch_message(), IndexedDocument, QdrantIndexStore, read_index_settings(), _DenseLike (+38 more)

### Community 19 - "test_retriever.py"
Cohesion: 0.09
Nodes (26): IndexPoint, build_client(), docs(), guest(), make_payload(), make_point(), open_spy(), RaisingEmbedder (+18 more)

### Community 20 - "007 — Hybrid Retrieval Requirements"
Cohesion: 0.05
Nodes (38): BM25Retriever with SQL access clause, eval-compare identity rules (R10), HybridRetriever (dense leg then BM25 leg, no single-leg fallback), lexical-v1 tokenizer (NFC, ZWJ/ZWNJ dropped, L/N/Mn/Mc token chars, 64-term cap), Result format 2.1 and security result 1.1, config/retrieval.yaml and build_retriever strategy factory, SQLite FTS5 lexical store (derived, git-ignored, bound to dense index), 007 — Hybrid Retrieval Requirements (+30 more)

### Community 21 - "test_validate_knowledge.py"
Cohesion: 0.22
Nodes (26): load(), test_bad_date_fails_loading_naming_document_and_field(), test_seed_corpus_still_loads(), test_valid_date_loads(), build_repo(), metadata(), problems_for(), run_cli() (+18 more)

### Community 22 - "RerankSkipReason"
Cohesion: 0.20
Nodes (14): classify_reranker_error(), is_offline_not_cached(), caused_by(), hub_5xx(), reason(), test_an_existing_unavailable_error_is_returned_as_is(), test_chain_walk_is_bounded(), test_context_is_never_followed() (+6 more)

### Community 23 - "BGE-M3 Adapter"
Cohesion: 0.06
Nodes (18): Model Preferences, Agent Skills README, Implementation Checklist, Spec Implementer Skill, task-reviews.md Implementation Block, Design Template, Change Log, Requirements Template (+10 more)

### Community 24 - "test_lexical_standalone.py"
Cohesion: 0.05
Nodes (33): Day-1 Usage, document_manifest.jsonl, golden_public.jsonl, Source-of-Truth Policy, chunking, overlap_tokens, strategy, target_tokens (+25 more)

### Community 25 - "Spec 004 ingestion baseline"
Cohesion: 0.07
Nodes (40): HeadingChunker heading v1 2000-char cap, Pydantic document models and enums, EligibilityPolicy for guest/public, Embedder Protocol, fake and BGE-M3 adapter, IngestionService change detection, LocalDocumentRepository with manifest schema validation, make ingest and config/ingestion.yaml, 17-field PointPayload and UUIDv5 point IDs (+32 more)

### Community 26 - "LexicalIndex"
Cohesion: 0.10
Nodes (20): Tokenizers (R5, R6), Implementation (user-owned runs + agent wrap-up), Review, 010 — Multilingual Retrieval Tasks, T3 — `lexical-v2`, tokenizer selection, script mix, `--cross-tokenizer`, continuity command, T5 — User-owned real runs on v3 and the `lexical-v2` decision, T6 — Documentation, decisions and hand-off, Verification (+12 more)

### Community 27 - "test_suite_v3.py"
Cohesion: 0.07
Nodes (45): Implementation, Implementation, Implementation, Implementation, Review, Review, Review, Spec 010 — task reviews (+37 more)

### Community 28 - "test_strategy_eval.py"
Cohesion: 0.10
Nodes (34): User decision, chunks_per_document_dense(), build_lexical(), eval_world(), lexical_env(), make_world(), production_chunker(), retrieve() (+26 more)

### Community 29 - "Evaluation CLI Tests"
Cohesion: 0.12
Nodes (31): assert_invalid(), document_fields(), make_document(), test_blank_required_text_is_rejected(), test_document_is_immutable(), test_duplicate_lote_languages_are_rejected(), test_effective_window_must_be_ordered(), test_empty_lote_languages_is_rejected() (+23 more)

### Community 30 - "validate_evaluation"
Cohesion: 0.11
Nodes (20): Implementation, Review, T1 — round 1, User decision, _validate(), EvaluationSchemas, _candidate_rules(), problem() (+12 more)

### Community 31 - "way2australia_api/config.py"
Cohesion: 0.12
Nodes (13): get_health(), HealthResponse, get_request_settings(), get_settings(), Settings, create_app(), isolate_settings_environment(), test_create_app_wires_settings() (+5 more)

### Community 32 - "IngestionConfigurationError"
Cohesion: 0.04
Nodes (59): 009 — Chunking Experiments Design, Alternatives / deferred decisions, Chunker identity, settings and configuration (R5), Components / boundaries, Data flow, Design summary, Distinct-document metrics (R7), Error and failure behavior (+51 more)

### Community 33 - "evaluation/test_cli.py"
Cohesion: 0.17
Nodes (19): load_production_ingestion_config(), clean_env(), index_factory(), real_factory(), run(), test_bad_top_k_exits_2(), test_cli_has_no_embedder_or_allow_fake_flag(), test_existing_output_exits_2_before_qdrant() (+11 more)

### Community 34 - "010 — Multilingual Retrieval Requirements"
Cohesion: 0.07
Nodes (28): 010 — Multilingual Retrieval Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+20 more)

### Community 35 - "test_lexical_standalone.py"
Cohesion: 0.17
Nodes (18): build_from(), built(), copy_repository(), expected(), first_document_id(), open_it(), remove_document(), repo_at() (+10 more)

### Community 36 - "009 — Chunking Experiments Requirements"
Cohesion: 0.07
Nodes (28): 009 — Chunking Experiments Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+20 more)

### Community 37 - "008 — Retrieval Fallback Requirements"
Cohesion: 0.09
Nodes (36): Baseline runner (refuses fake index without --allow-fake; HitRate@k, Recall@k, MRR, p50/p95, min(1,k/N) random expectation), Binding: embedder model ID, revision, vector size, normalization, fake flag and index_version must equal recorded IndexSettings, BM25Retriever(identity, lexical), BM25 statistics (IDF, avg length) computed over every row of a lexical file, build_access_filter (the only filter builder), build_retriever (only place a strategy name becomes a retriever), retrieval_client_factory (Qdrant client with configured timeouts), config/retrieval.yaml (default_strategy hybrid, RRF k 60, depth 50) (+28 more)

### Community 38 - "repositories/__init__.py"
Cohesion: 0.08
Nodes (6): _check_language_code(), KnowledgeDocument, DocumentNotFoundError, ListRepository, IgnoresQueryRepository, test_errors_share_base_class()

### Community 39 - "KnowledgeDocument"
Cohesion: 0.18
Nodes (25): BoomChunker, doc(), Harness, test_bumped_document_version_updates(), test_changed_body_updates(), test_changed_metadata_field_updates(), test_chunk_shrink_leaves_no_orphan(), test_chunk_too_long_report_has_no_chunk_text() (+17 more)

### Community 40 - "test_legacy_baseline_snapshot.py"
Cohesion: 0.12
Nodes (16): deterministic_clock(), clean_env(), _Factory, _FixedDatetime, _record_opens(), note(), wrap_func(), inner() (+8 more)

### Community 41 - "typing"
Cohesion: 0.10
Nodes (29): 006-candidates.jsonl with 7 suggested rows, make eval-compare, make eval-retrieval, make eval-security hard gate, result 2.2 and served-strategy eval-compare, eval-security five paths, governed suite loader and schemas, make validate-evaluation (+21 more)

### Community 42 - "EvaluationConfigurationError"
Cohesion: 0.10
Nodes (20): CaseBase, CaseStatus, DatasetRef, DatasetType, GoldenCase, LoadedSuite, SecurityCase, SuiteManifest (+12 more)

### Community 43 - "Workflow Reviewer"
Cohesion: 0.07
Nodes (25): Considered and rejected, Evidence, F1 — <title> [waste | quality risk | process slip] (confidence: high/medium/low), Findings, New features and tools (official sources, since <date>), Not measurable here, P1 — <title> (addresses F#; expected saving: ...), Proposals (+17 more)

### Community 44 - "LocalDocumentRepository"
Cohesion: 0.17
Nodes (15): LocalDocumentRepository, build(), test_a_skip_path_that_records_no_skip_fails_the_gate(), test_builder_refuses_a_non_throwaway_base_before_any_write(), test_builder_refuses_an_existing_collection(), test_each_forbidden_row_type_is_in_the_lexical_file(), test_full_gate_passes_on_the_seed_corpus(), test_lexical_rows_mirror_the_forbidden_points() (+7 more)

### Community 45 - "011 — Multilingual Reranking Design"
Cohesion: 0.29
Nodes (6): 011 — Multilingual Reranking Design, Alternatives / deferred decisions, As-built notes, Latency scaling, Observability, Phase 2 compatibility / migration

### Community 46 - "test_cli_config.py"
Cohesion: 0.14
Nodes (20): clean_env(), _factory(), _run(), test_builds_exactly_one_embedder_per_run(), test_collection_base_comes_from_environment(), test_config_refuses_missing_or_floating_revision(), test_config_refuses_unknown_field_and_missing_file(), test_exit_0_then_idempotent_second_run() (+12 more)

### Community 47 - "D055 Default strategy is hybrid (Spec 007)"
Cohesion: 0.10
Nodes (23): make retrieval-baseline legacy frozen, RetrievalUnavailableError and availability classification, Known issue: git_dirty true in Spec 007 BM25/hybrid result files (user-accepted), Latency hybrid p50 80.3 ms p95 103.6 ms; bm25 p50 0.19 ms, BM25 metrics: 64/69 goldens, MRR 0.7082, Hybrid metrics: 68/69 goldens, MRR 0.9094, Retrieval misses g004 g026 g061, Next step 2: real BGE-M3 baseline committed (+15 more)

### Community 48 - "Ingestion (Phase 1 baseline, Spec 004)"
Cohesion: 0.08
Nodes (32): Authorization applied inside each retriever before fusion, never after RRF, reranking or generation, Authorization filter is part of the Qdrant query so unauthorized points never leave the store, BgeM3Embedder (optional bge-m3 extra, dense only), check_hit (fail-closed re-check, second line of defense), D025-D030, D032 ingestion decisions, D035 Future fallbacks must take the same ResolvedAccess and call check_hit, D040 Authorization per retriever, DocumentRepository Protocol (get_document, list_documents) (+24 more)

### Community 49 - "007 — Hybrid Retrieval Requirements"
Cohesion: 0.09
Nodes (27): optional bge-m3 extra (sentence-transformers, PyTorch), D048 graphify tooling, make experiment CONFIG=... (target; records git commit, release, suite, chunker, embedder, strategy, metrics, latency), make format, Knowledge graph graphify (D048), /graphify . --update (user, once per spec after merge), graphify query / path / explain, graphify update . (+19 more)

### Community 50 - "test_lexical_tokenizer.py"
Cohesion: 0.09
Nodes (13): Review, script_mix(), live_suite_rows(), test_every_v3_query_letter_matches_script_fixture(), test_g062_is_latin_only(), test_non_letters_add_no_script(), test_representative_v3_queries(), test_virama_and_vowel_sign_add_no_script() (+5 more)

### Community 51 - "HeadingChunker"
Cohesion: 0.14
Nodes (26): HeadingChunker, _is_word_char(), slugify(), ids(), make_document(), test_deterministic(), test_duplicate_headings_get_unique_ids_in_order(), test_duplicate_suffix_does_not_collide_with_literal_heading() (+18 more)

### Community 52 - "retrieval_eval.py"
Cohesion: 0.06
Nodes (43): R8 — Result format 2.2 (`retrieval_eval.py`), Implementation, Review, T5 — round 1, User decision, Review, Implementation, _compare() (+35 more)

### Community 53 - "FallbackRetriever"
Cohesion: 0.15
Nodes (14): Fallback authorization invariant (same ResolvedAccess), BM25Retriever (identity, lexical), classify_model_error, classify_qdrant_error, Qdrant client lifecycle gap, FallbackRetriever, Hugging Face error shapes (T1 As-built), HybridRetriever / rrf_fuse (unchanged, fail closed) (+6 more)

### Community 54 - "FakeReranker"
Cohesion: 0.11
Nodes (13): RerankerUnavailableError, FakeReranker, stable_score(), test_the_harness_reranker_failures_use_the_fake_reranker_switches(), _RealStubReranker, test_fail_on_call_fails_only_that_call(), test_fail_on_load(), test_it_satisfies_the_protocol_and_reports_identity() (+5 more)

### Community 55 - "BgeM3Embedder"
Cohesion: 0.10
Nodes (14): Components / boundaries, BgeM3Embedder, _group_installed(), OptionalDependencyError, group_installed(), test_constructing_does_not_load_the_model(), test_device_none_before_load_and_recorded_after(), test_missing_group_at_load_raises_optional_dependency_error() (+6 more)

### Community 56 - "Development Workflow"
Cohesion: 0.11
Nodes (29): Finalized stack: Python/FastAPI, Next.js, Qdrant, SQLite FTS5, BGE-M3, Bedrock, Langfuse, CloudWatch, Terraform ap-south-1, GitHub Actions, agent-skills sync, D001 Python-first backend, D002 RAG as reusable internal package, D003 Knowledge outside RAG package, D005 Documents are truth; chunks are derived, D007 Public-only Phase 1, D008 Language and authorization are independent (+21 more)

### Community 57 - "LocalRepositoryConfig"
Cohesion: 0.04
Nodes (65): R11 — Security gate (`security_index.py`, `security_eval.py`), R4/R5 — Lexical store (`lexical/store.py`, `lexical/build.py`), Implementation, Review, T3 — round 1, User decision, Acceptance criteria, Acceptance criteria (+57 more)

### Community 58 - "test_security_eval.py"
Cohesion: 0.14
Nodes (10): clean_env(), _lexical_work_dir(), new_base(), seed_repository(), strip_forbidden_terms(), test_a_lexical_sanity_failure_is_a_harness_error(), test_builder_refuses_a_real_embedder_identity(), __init__() (+2 more)

### Community 59 - "json"
Cohesion: 0.10
Nodes (20): chunker, context_prefix, name, overlap_tokens, target_tokens, version, embedder, batch_size (+12 more)

### Community 60 - "Evaluation Phase 1 framework (Spec 006)"
Cohesion: 0.07
Nodes (31): D042-D047, D053, D054 evaluation decisions, Evaluation assets never written by evaluation code (C6); candidates suggested and human-activated, Ingestion eligibility is the only guard against synthetic/unapproved documents; poisoned_public_document is not an authorization case, Evaluation isolation and gates, models.py, suite.py (tolerant typed cases, read-only load_suite), retrieval_eval.py, slices.py, sections.py, schemas.py, validate.py (referencing registry, validate-evaluation checks), Section-level keys <document_id>#<section_id> (+23 more)

### Community 61 - "SecurityIndex"
Cohesion: 0.15
Nodes (10): SecurityIndex, test_a_fallback_path_that_does_not_fall_back_is_a_harness_error(), test_a_plain_hybrid_path_that_falls_back_is_a_harness_error(), falling_back(), test_a_rerank_path_that_fell_back_is_a_harness_error(), test_a_rerank_path_without_a_rerank_stage_is_a_harness_error(), test_the_post_rerank_applicability_recheck_fails_closed_with_a_lote(), defective() (+2 more)

### Community 62 - "BgeRerankerV2M3"
Cohesion: 0.07
Nodes (20): Package / file placement, Implementation, Review, T1 — round 1, User decision (2026-11-05), T1 — Reranker contract, adapters, errors and config, Verification, Reranker (+12 more)

### Community 63 - "make retrieve"
Cohesion: 0.09
Nodes (22): make retrieve, --allow-fake (plumbing only, never a recorded baseline), make retrieval-baseline (legacy, frozen Spec 005 producer), BASELINE_ARGS (--embedder, --allow-fake, --top-k, --suite, --release, --output, --config), Baseline metrics HitRate@5, random expectation min(1,5/N), Recall@5, MRR, p50/p95 latency, experiments/results/retrieval-baseline-<index_version>-<UTC>.json, never overwritten, D053 result 2.1, D061 fallback marking (+14 more)

### Community 64 - "hub_offline_empty_cache"
Cohesion: 0.10
Nodes (17): Verification run, 010 — Multilingual Retrieval: Retrospective Review, Deviations from the approved plan, Documentation reconciled, Final handoff, Findings, Patterns in `task-reviews.md`, Protected-data check (+9 more)

### Community 65 - "AWS target"
Cohesion: 0.07
Nodes (35): Lexical file is a derived artifact, one per collection, bound by identity and chunk digest, Source documents are truth; chunks, embeddings, sparse entries, Qdrant points and preview indexes are derived artifacts, Full agent orchestration (avoided), Intentionally avoided choices, AWS target, Bedrock Agents / AgentCore for Phase 1 (avoided), Bedrock Knowledge Bases as core RAG (avoided), Bedrock model selection criteria (+27 more)

### Community 66 - "make eval-retrieval"
Cohesion: 0.13
Nodes (22): bm25 strategy, bm25 needs neither Qdrant nor the bge-m3 extra (Spec 008), config/retrieval.yaml schema 1.1 (default_strategy hybrid, qdrant.connect_timeout_s 2, query_timeout_s 3; 1.0 refused), D036 binding rules, dense strategy, --strategy dense needs no lexical file, Embedder pair from index_settings or dense_identity; fallback-only 2.2 file compares against Spec 007 bm25 file, eval-retrieval exit 0 or 2 (+14 more)

### Community 67 - "Spec 007 hybrid retrieval"
Cohesion: 0.12
Nodes (24): build_retriever, make index-lexical, lexical package: lexical-v1 tokenizer, FTS5 store, builder, Current goal: Specs 001-008 complete; Spec 008 verified and merged into main (1107b67), plan next spec, Known issue: BM25 statistics corpus-wide per file; needs per-scope files for roles, Known issue: legacy chillu sequence does not match atomic chillu in BM25, Known issue: evaluation-data gaps (ml goldens, relevant_section_ids empty), Known issue: g004 overlaps u001, keep_both (+16 more)

### Community 68 - "test_manifest_validation.py"
Cohesion: 0.28
Nodes (17): metadata(), record(), run(), test_duplicate_document_id_rejected(), test_duplicate_document_version_rejected(), test_frontmatter_errors(), test_frontmatter_missing_required_field(), test_frontmatter_parsing_keeps_dates_as_strings() (+9 more)

### Community 69 - "ResolvedAccess"
Cohesion: 0.05
Nodes (50): Implementation, Implementation, Implementation, Implementation, Review, Review, Review, Review (+42 more)

### Community 70 - "embedder"
Cohesion: 0.11
Nodes (17): chunker, context_prefix, name, overlap_tokens, target_tokens, version, embedder, batch_size (+9 more)

### Community 71 - "Phase 1 RAG query pipeline"
Cohesion: 0.12
Nodes (16): Authorization model (guest/public), Small documents and chunking strategy, Citation strategy (backend-owned validation), FAQ-aware retrieval experiment, Graceful degradation, Hybrid retrieval (dense + BM25 + RRF), Production knowledge corpus, Poisoned public document fixture (+8 more)

### Community 72 - "load_retrieval_config"
Cohesion: 0.13
Nodes (21): load_retrieval_config(), _model_error_text(), test_depth50_config_differs_only_in_rerank_depth(), test_1_3_loads_all_fields(), test_1_3_requires_the_block(), test_committed_file_is_1_3_with_reranking_off_and_a_pinned_revision(), test_disabled_block_may_omit_the_revision(), test_invalid_values_are_refused_naming_the_key() (+13 more)

### Community 73 - "008 — Retrieval Fallback Requirements"
Cohesion: 0.14
Nodes (15): 008 — Retrieval Fallback Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Spec 008 taken ahead of roadmap 7 (chunking), Decisions resolved before drafting, Definition of Done (+7 more)

### Community 74 - "list_eligible_documents"
Cohesion: 0.12
Nodes (9): _authority_map(), collect(), _document_ids(), collect(), _eligible_document_versions(), DocumentQuery, DocumentRepository, EligibilityPolicy (+1 more)

### Community 75 - "Section: Next step"
Cohesion: 0.11
Nodes (17): Atomic publish and rollback, Phase 2 audit trail, AWS deployment architecture (ap-south-1), Controlled document-change workflow (Release Candidate), CI/CD pipeline, Evaluation governance states, Evaluation slices, Evaluation Suite (public-eval-v1) (+9 more)

### Community 76 - "test_rerank_eval.py"
Cohesion: 0.15
Nodes (28): NotComparableError, doc23(), test_cross_index_with_2_2_side_is_refused(), _FieldSpy, go(), multi_chunk(), test_a_2_4_file_reads_as_not_reranked(), test_a_2_4_reference_compares_with_a_2_5_arm_across_index() (+20 more)

### Community 77 - "test_baseline.py"
Cohesion: 0.10
Nodes (23): case(), clean_env(), cli_run(), DeviceStub, _git(), run(), seeded(), setup() (+15 more)

### Community 78 - "embedder"
Cohesion: 0.14
Nodes (13): chunker, max_chunk_chars, name, version, embedder, batch_size, fake_vector_size, model_id (+5 more)

### Community 79 - "repositories/__init__.py"
Cohesion: 0.06
Nodes (32): DocumentRepositoryError, DocumentValidationError, DuplicateDocumentError, ManifestValidationError, split_frontmatter(), _StringDateLoader, normalize_body(), document_fields() (+24 more)

### Community 80 - "hashlib"
Cohesion: 0.23
Nodes (10): declared_release_id(), load_suite(), test_declared_release(), test_filtering_in_temporary_suite(), test_invalid_line_names_file_and_line_only(), test_path_escaping_repo_root_refused(), test_real_suite_loads_every_golden_case_and_leaves_evaluation_unchanged(), test_release_id_mismatch_refused() (+2 more)

### Community 81 - "test_verify_budget_hook.py"
Cohesion: 0.08
Nodes (7): hook_env(), _load_hook_module(), _run_settings_hook(), TestAgentAndBudget, TestRepoRoot, TestRunsBudgetedMake, TestSettingsHookCommand

### Community 82 - "Ingestion pipeline (Spec 004)"
Cohesion: 0.07
Nodes (32): default_strategy, fusion, candidate_depth, k, method, weights, lexical, tokenizer (+24 more)

### Community 83 - "test_recursive.py"
Cohesion: 0.19
Nodes (16): assert_matches_snapshot(), assert_recursive_chunks_whitespace_fidelity(), chunks_to_records(), collapse_whitespace(), load_snapshot(), snapshot_for_document(), recursive_chunker(), test_deterministic() (+8 more)

### Community 84 - "pytest"
Cohesion: 0.14
Nodes (16): Role, clean_env(), guest(), payload(), _policy(), test_a_different_policy_changes_both_builders(), test_both_builders_cover_the_same_three_conditions(), test_check_hit_accepts_valid_payload() (+8 more)

### Community 85 - "open_retrieval"
Cohesion: 0.04
Nodes (93): Acceptance criteria, Decisions resolved before drafting, 008 — Retrieval Fallback Design, Alternatives / deferred decisions, Components / boundaries, Data flow, Decisions D056-D062, Design summary (+85 more)

### Community 86 - "rerank"
Cohesion: 0.09
Nodes (22): default_strategy, fusion, candidate_depth, k, method, weights, lexical, tokenizer (+14 more)

### Community 87 - "Backend stack"
Cohesion: 0.12
Nodes (20): Backend stack, Custom retrieval metrics (plain Python), DeepEval (not yet a dependency), Evaluation tooling, FastAPI, Generation/e2e metrics (correctness, faithfulness, citations, refusal), GitHub Actions, httpx (+12 more)

### Community 88 - "embedder"
Cohesion: 0.14
Nodes (13): chunker, max_chunk_chars, name, version, embedder, batch_size, fake_vector_size, model_id (+5 more)

### Community 89 - "D023 Task-gated agent workflow"
Cohesion: 0.12
Nodes (16): allowed_scopes, current_release, default_role, implemented_roles, allowed_scopes, allowed_scopes, roles, admin (+8 more)

### Community 90 - "guest_access"
Cohesion: 0.15
Nodes (24): DroppedClauseLexical, guest_access(), real_queries(), run_gate(), security_result(), spied(), test_a_dropped_lexical_clause_names_the_four_lexical_paths(), test_a_filter_dropping_index_fails_the_gate() (+16 more)

### Community 91 - "re"
Cohesion: 0.12
Nodes (15): active_registry_languages(), aggregate(), _mean(), slice_by(), source_authority_key(), row(), test_absent_languages_from_a_temp_registry(), test_missing_registry_section_is_a_configuration_error() (+7 more)

### Community 92 - "Roadmap 13 - Graceful degradation"
Cohesion: 0.32
Nodes (8): Deferred serving concerns (circuit breaker, startup policy, Qdrant 5xx D062), Deduplication, context budgeting, evidence ordering, Dense to BM25 degradation, Roadmap 9 - Reranking + context building, Roadmap 13 - Graceful degradation, Qdrant failure to SQLite FTS5, Reranker failure to hybrid results, Spec 008 early delivery (D056)

### Community 93 - "pathlib"
Cohesion: 0.25
Nodes (9): apps/api, apps/web, CloudWatch, Future multimodal mock-test evaluation, Langfuse tracing, packages/core, packages/observability, packages/rag (+1 more)

### Community 94 - "Spec status table"
Cohesion: 0.12
Nodes (19): Completion: retrospective, Spec-Review commit, merge, verified status, Spec orchestrator loop (route, role subagents, user approval, merge), GET /health endpoint, make setup, packages core/rag/observability skeletons, task-gated spec skills and skills-sync, task State lifecycle and spec/NNN branches, uv workspace and uv.lock (+11 more)

### Community 95 - "test_eligibility.py"
Cohesion: 0.20
Nodes (16): eligible_ids(), make_document(), test_active_approved_public_document_is_eligible(), test_language_filter_narrows_eligible_documents_only(), test_language_metadata_does_not_broaden_access(), test_local_repository_applies_the_policy_query(), test_non_active_lifecycle_is_excluded(), test_non_approved_status_is_excluded() (+8 more)

### Community 96 - "test_rerank_bge.py"
Cohesion: 0.14
Nodes (10): extra_installed(), failing(), raised(), test_missing_extra_at_load(), test_missing_extra_is_refused_naming_the_setup_command(), test_network_failure_at_load_becomes_a_skip_with_the_cause_chain(), test_offline_not_cached_is_a_configuration_error_with_advice(), test_refuses_missing_or_floating_revision() (+2 more)

### Community 97 - "SpyIndex"
Cohesion: 0.15
Nodes (17): Admin content management, Agent capabilities only where they solve a real product problem, Audit trail, Basic analytics, Candidate evaluation, Change impact analysis, Content hashing, Evaluation Governance (keep/modify/deprecate/replace) (+9 more)

### Community 98 - "transcript_metrics.py"
Cohesion: 0.17
Nodes (12): analyse(), category(), command_kinds(), executed_text(), expand(), main(), parse_time(), render() (+4 more)

### Community 99 - "CURRENT_STATE.md"
Cohesion: 0.13
Nodes (14): interval, retries, start_period, test, timeout, container_name, healthcheck, image (+6 more)

### Community 101 - "read_result"
Cohesion: 0.12
Nodes (12): _build_run(), default_output_path(), _mixed(), _num(), read_result(), _rerank_fields(), _served_strategy(), _unreadable() (+4 more)

### Community 102 - "test_structure.py"
Cohesion: 0.17
Nodes (18): manifest_document_count(), assert_structure_chunks_whitespace_fidelity(), structure_chunker(), test_duplicate_sibling_headings_raise(), test_fence_blocks_are_atomic_and_headings_inside_ignored(), test_long_list_splits_only_between_items(), test_main_collision_with_heading_slug(), test_malayalam_paragraph_packs() (+10 more)

### Community 103 - "make ingest"
Cohesion: 0.12
Nodes (18): docker compose up -d / down (local Qdrant), Environment: QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION_BASE, W2A_TENANT_ID, Fake embedder needs throwaway QDRANT_COLLECTION_BASE, make index-lexical, make ingest, INGEST_ARGS (--embedder {bge_m3,fake}, --config), ingest exit codes 0 success, 1 document failed, 2 refusal, Ingest summary lines (index:, added/updated/unchanged/deleted, ERROR lines) (+10 more)

### Community 104 - "Retrieval package (Spec 005 and 007)"
Cohesion: 0.14
Nodes (12): graphify skill pointer, spec/NNN branch and Spec-Task trailers, spec-implementer skill (one task per run), spec-orchestrator skill, spec-planner skill, spec-reviewer retrospective skill, Task-gated agent workflow loop, task-reviewer skill (read-only) (+4 more)

### Community 105 - "DenseIndex"
Cohesion: 0.09
Nodes (10): T3 — `lexical-v1` tokenizer, lexical store and `make index-lexical`, Verification, EmbedderInfo, build_index_settings(), DenseIndex, test_run_retrieval_evaluation_on_multi_chunk_recursive_index(), client_with_forbidden(), FilterDroppingIndex (+2 more)

### Community 106 - "Qdrant (vector database)"
Cohesion: 0.14
Nodes (13): Authorization metadata (access_scope, owner_user_id, tenant_id), Engineering Conventions, IDs and versions conventions, Knowledge files with provenance, Language metadata (content_language, lote_languages), Logging and tracing hygiene, Domain naming terms, Prompts as versioned assets (+5 more)

### Community 107 - "011 — Multilingual Reranking Requirements"
Cohesion: 0.08
Nodes (25): 011 — Multilingual Reranking Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+17 more)

### Community 108 - "Development Workflow"
Cohesion: 0.21
Nodes (12): Branching and commits (spec/NNN, Spec-Task trailer), Development Workflow, Multi-agent handoff, Implementation rule: BLOCKED spec issue, Phase discipline, Protected source-of-truth data, Required spec-reviewer retrospective, Agent skills (orchestrator, planner, implementer, task-reviewer, spec-reviewer) (+4 more)

### Community 109 - "FakeEmbedder"
Cohesion: 0.19
Nodes (12): FakeEmbedder, _cosine_to_query(), _text_with_score_below(), test_conforms_to_protocol(), test_declared_vector_size(), test_default_size_is_64(), test_fake_device_is_none(), test_info_reports_fake_identity() (+4 more)

### Community 110 - "evaluation/cli.py"
Cohesion: 0.04
Nodes (32): Implementation, default_security_output_path(), _security(), build_security_index(), _canary_points(), delete_security_index(), _forbidden_payload(), forbidden_variant() (+24 more)

### Community 111 - "test_content_hash.py"
Cohesion: 0.15
Nodes (12): Approved packages, pricing and validity, Six approved packages and prices, 60-day package validity, 24-hour cancellation notice, Personal coaching package, 60-minute coaching session on Google Meet, Individual coaching and live appointments, Mock assessments, scoring, feedback and review windows (+4 more)

### Community 112 - "Spec 005 dense retrieval baseline"
Cohesion: 0.10
Nodes (31): AccessContext, Role, W2A_TENANT_ID, DenseIndex, build_access_filter, check_hit, DenseRetriever, make retrieve guest/public CLI, BGE-M3 device mps not pinned (D038), Spec 005 retrospective findings F3-F5, Spec 005 dense retrieval baseline, Spec 005 status: verified 2026-10-23 merged b33462e, AccessContext and Role (+23 more)

### Community 113 - "test_violation_names_the_document_from_the_error_attribute"
Cohesion: 0.18
Nodes (12): AGENTS.md Project Rules, DocumentRepository Abstraction, Evaluation Governance Rules, Language Separation Rules, Phase 1 Scope, Task-gated Spec Loop, CLAUDE.md Project Instructions, graphify Knowledge Graph Rules (+4 more)

### Community 114 - "security_corpus.py"
Cohesion: 0.14
Nodes (18): build_security_repository(), _fixture_files(), security_repository(), copy_fixtures(), spy_lexical_path(), wrapper(), test_cli_clause_less_lexical_store_exits_one_naming_strategies(), test_cli_harness_error_exits_two_and_writes_nothing() (+10 more)

### Community 115 - "test_repository_contract.py"
Cohesion: 0.21
Nodes (10): InMemoryDocumentRepository, make_document(), test_document_query_has_no_filesystem_concepts(), test_document_query_is_immutable(), test_get_document_missing_raises_not_found(), test_get_document_returns_latest_or_requested_version(), test_in_memory_repository_satisfies_protocol(), test_list_documents_applies_query_filters() (+2 more)

### Community 116 - "fusion"
Cohesion: 0.20
Nodes (12): English, Malayalam and mixed queries, FAQ-aware retrieval/indexing, Roadmap 7 - Chunking experiments, Roadmap 8 - Multilingual retrieval, Language applicability handling, Parent-heading context and order-independent section_ids, Recursive chunking baseline, Optional semantic chunking (+4 more)

### Community 117 - "SQLite FTS5"
Cohesion: 0.12
Nodes (19): Local multilingual BGE reranker, BM25 via FTS5 bm25(), Derived local lexical file per collection, Device not pinned, recorded in results (D038), Embeddings, Deterministic fake embedder, Fusion, Lexical store (+11 more)

### Community 118 - "SpyIndex"
Cohesion: 0.22
Nodes (4): OddIdStore, SpyIndex, broken(), test_violation_names_the_document_from_the_error_attribute()

### Community 119 - "Chunk"
Cohesion: 0.10
Nodes (19): Chunk, IngestionError, check_chunks(), ChunkTooLongError, _effective_limit(), build_payload(), _reason(), test_above_limit_raises_with_fields() (+11 more)

### Community 120 - "failing_client"
Cohesion: 0.18
Nodes (10): content-hash-v1 (sole change-detection signal), LocalDocumentRepository, Document manifest and JSON Schema validation, make validate-knowledge, persona_scope spec defect (F2), BgeM3Embedder (optional extra, pinned revision), Embedder Protocol and FakeEmbedder, HeadingChunker and slugify rule (+2 more)

### Community 121 - "test_status_handling.py"
Cohesion: 0.20
Nodes (8): Adding a New Language Guide, language_registry.json, Public Assistant Content Boundaries, access_scope, content_language, Knowledge Schema and Metadata, language_scope, lote_languages

### Community 122 - "retrieval_client_factory"
Cohesion: 0.12
Nodes (10): Repeated finding: graphify update ownership, Spec 008 Task Reviews, Implementation, Implementer Sonnet 5.5 / reviewer Opus 5.5 pattern, T1 — round 1, User decision, Verification, raise_if_unavailable() (+2 more)

### Community 123 - "chunker_build.py"
Cohesion: 0.05
Nodes (47): As-built notes, Carry-over clean-ups (R11), Cross-index comparison (R8), Security gate (R9), 009 — Chunking Experiments: Retrospective Review, Cross-task consistency, Documentation reconciled, Extra checks (user-requested) (+39 more)

### Community 124 - "QdrantIndexStore"
Cohesion: 0.22
Nodes (10): Local Qdrant Docker Compose service, Make command surface (setup, lint, typecheck, test, verify), Python monorepo foundation (FastAPI, uv, Makefile), Typed runtime Settings (Pydantic Settings), Spec 001 Project Foundation (implemented), IndexSettings and mismatch refusal, UUIDv5 point identity (INGESTION_NAMESPACE), QdrantIndexStore (+2 more)

### Community 125 - "Baseline runner and result JSON"
Cohesion: 0.22
Nodes (8): Baseline runner and result JSON, build_access_filter (single filter builder), check_hit (fail-closed re-check), DenseRetriever, Read-only golden loader (stand-in for Spec 006), Document-level metrics (HitRate, Recall, MRR, random k/N), safe_text output sanitizer, Real BGE-M3 baseline (user-owned, pending)

### Community 126 - "test_failed_write_removes_partial_file"
Cohesion: 0.24
Nodes (8): Legacy goldens.py Compatibility Wrapper, Legacy Baseline Snapshot Test, Governed Suite Loader, 006 Task Reviews, 006 Evaluation Framework Tasks, T1 Snapshot, Models, Loader, T8a Deferred Fixes, T8b Docs and Handoff

### Community 127 - "Development Workflow"
Cohesion: 0.29
Nodes (10): NAATI CCL booking, fees, cancellation, results and credential validity, One week advance booking, 75% refund for cancellation one hour before, CCL test fee A$814, Credential validity five years from 9 August 2022, myNAATI, Expired credential not extended, Rescheduling up to eight days before test (+2 more)

### Community 128 - "test_status_handling.py"
Cohesion: 0.25
Nodes (7): RetrievalAuthorizationError.document_id, eval-security, Forbidden Point Variants, Authorization Hard Gate, Throwaway Security Index (w2a-sectest-*), T5 Security Gate, Authorization Rules

### Community 129 - "absent_query_languages"
Cohesion: 0.22
Nodes (8): last_reviewed_at, precedence, business_information, language_specific_exam_policy, migration_points_and_visa_rules, official_exam_rules, rules, schema_version

### Community 130 - "Phase 1 - Production-oriented RAG"
Cohesion: 0.12
Nodes (19): BM25, Deterministic regression gates, FastAPI skeleton, Golden, refusal and security cases, HitRate@5, Roadmap 1 - Project foundation, Roadmap 5 - Evaluation framework, Roadmap 6 - Hybrid retrieval (+11 more)

### Community 131 - "RuntimeSettings"
Cohesion: 0.33
Nodes (9): NAATI CCL candidate rules and test-day setup, Direct first-person speech requirement, Report technical incidents within 24 hours, NAATI, Online proctoring with separate phone or tablet, Prohibited materials and tools, Recording under 20 minutes, One repeated segment per dialogue without penalty (+1 more)

### Community 132 - "sync_agent_skills.py"
Cohesion: 0.31
Nodes (9): discover_skills(), expected_tree(), find_problems(), inject_frontmatter(), main(), managed_skills(), read_tree(), remove() (+1 more)

### Community 133 - "Vocabulary, flashcards and free access"
Cohesion: 0.29
Nodes (7): EligibilityPolicy / GUEST_PUBLIC_POLICY, Security fixtures (valid but ineligible), config/ingestion.yaml and RuntimeSettings, Ingestion pipeline (target vs current state diff), AccessContext and Role (core), resolve_access / ResolvedAccess, W2A_TENANT_ID server tenant setting

### Community 134 - ".search"
Cohesion: 0.25
Nodes (8): Phase 2 basic analytics, Assistant behavior rules, Product Context, English and Malayalam language scope, Future personas, Phase 1 guest-only scope, Way2Australia AI product, Source-of-truth priorities

### Community 135 - "asyncio"
Cohesion: 0.21
Nodes (18): _copy_seed(), seed_repository(), test_documents_outside_approved_roots_are_never_loaded(), test_get_document_by_id_and_version(), test_get_document_missing_raises_not_found(), test_invalid_document_fails_load_without_leaking_paths(), test_invalid_schema_raises_repository_error(), test_language_filter_is_data_driven_and_does_not_affect_access() (+10 more)

### Community 136 - "verify_budget.py"
Cohesion: 0.13
Nodes (16): test_no_pytorch_import(), test_bm25_path_imports_neither_the_model_adapter_nor_the_model_stack(), agent_key(), _budget(), count_run(), decide(), _dedupe_window_s(), in_repo() (+8 more)

### Community 138 - "Evaluation Framework Goal"
Cohesion: 0.39
Nodes (8): NAATI CCL test format, scoring and results, NAATI CCL test, Deduction-based assessment, Begin interpreting within five seconds of chime, NAATI, CCL is not professional interpreter certification, Pass requirement 63/90 overall and 29/45 per dialogue, Results within 4-6 weeks

### Community 139 - "lexical/ package (Spec 007)"
Cohesion: 0.22
Nodes (9): D060 Standalone lexical freshness, Standalone freshness proves lexical file matches repository, not live Qdrant (D060), lexical/cli.py (make index-lexical writes only git-ignored file), freshness.py (verify_fresh, chunk digest recomputed from repository), lexical/ package (Spec 007), store.py (SQLite FTS5: chunks table, chunk_terms FTS5 table, settings row; LexicalIndex.open, bind_to, search), tokenizer.py (lexical-v1), make index-lexical (+1 more)

### Community 140 - "Phase 1 - Production-oriented RAG"
Cohesion: 0.13
Nodes (15): Answerability and insufficient-evidence response, Authorization regression and staff canary, Docker, Terraform, EC2, ECR, CloudWatch, IAM, Bedrock, Bedrock Runtime (roadmap), BGE-M3 (roadmap), Citation manipulation tests and input/cost limits, Backend-owned citation validation, Roadmap 4 - Dense retrieval baseline (+7 more)

### Community 141 - "BGE-M3 (initial embedding model)"
Cohesion: 0.38
Nodes (6): Evaluation Candidates File, Evaluation Package (evaluation/), Evaluation Suite and Case-type Schemas, validate-evaluation, T2 Schemas and validate-evaluation, T7 Candidates

### Community 142 - "Way2Australia AI Platform Master Implementation Plan"
Cohesion: 0.29
Nodes (7): eval-retrieval, Retrieval Result Document 2.0, Section-level Metrics, Slices and small_sample, Unanswerable Reporting, T3 Retrieval Runner, T4 Unanswerable Reporting

### Community 143 - "Retrieval fallback (Spec 008, D056-D062)"
Cohesion: 0.07
Nodes (31): AccessContext(role, tenant_id) with blank tenant refused, Future agent folders intentionally not created, Answerability / insufficient-evidence decision, apps/api (FastAPI application layer), apps/web (Next.js/TypeScript frontend: recruiter assistant, RAG Lab, engineering views), Amazon Bedrock generation, Citation validation, Context builder (planned) (+23 more)

### Community 144 - "eval-compare"
Cohesion: 0.29
Nodes (7): AGENTS.md, Claude adapter, Initial specs, Phase 0 - Project bootstrap, Project context files, SDD workflow (Spec 003 task-gated agent workflow), Stable command interface

### Community 145 - "Payments, account access and support boundaries"
Cohesion: 0.29
Nodes (6): Vocabulary, flashcards and free access, Spaced-repetition flashcards, Free access allowance, 12 subject domains plus General vocabulary, Approved public learning samples, Sample neighbour-greeting dialogue

### Community 146 - "make retrieve"
Cohesion: 0.12
Nodes (17): results.py, compare.py (reads 1.0, 2.0, 2.1; quality gate; identity refusals), eval-compare exit 0 pass, 1 gate failure, 2 refusal, WARNING flipped hit->miss / miss->hit lines (<case_id> v<case_version>), Gate: fail if more than 1 fewer hit cases or MRR drop above 1/n, Fallback path latency marked 'includes failed dense attempt' (informational), Not-comparable refusals (suite, case sets, top_k, fake, collection, index_version, embedder, lexical index, mixed served strategies), BASE and CANDIDATE variables, Error format ERROR <ClassName>: <message>; eval-compare refusals start with 'not comparable:' (+9 more)

### Community 147 - "make test"
Cohesion: 0.33
Nodes (6): 006 Evaluation Framework Design, Decision Brief Q1-Q10, 006 Evaluation Framework Requirements, Evaluation Framework Goal, 006 Spec Retrospective Review, Retrospective Round 1 PASS

### Community 148 - "Mission"
Cohesion: 0.33
Nodes (5): Evaluation case_id and case_version, Versioning and Releases, document_id and document_version, Phase 2 Knowledge Release Candidates, Release seed-v1

### Community 149 - "format_security_summary"
Cohesion: 0.43
Nodes (4): format_security_summary(), format_summary(), _rerank_lines(), _unanswerable_line()

### Community 150 - "documents/__init__.py"
Cohesion: 0.18
Nodes (6): AccessScope, ApprovalStatus, LanguageScope, LifecycleStatus, SourceAuthority, test_guest_policy_agrees_with_access_policy_config()

### Community 151 - "Spec 004 retrospective round 1 (PASS)"
Cohesion: 0.40
Nodes (5): Spec 004 retrospective round 1 (PASS), Spec 004 Ingestion baseline (verified), retrieval package (dense baseline), Spec 005 retrospective round 1 (PASS), Spec 005 Dense retrieval baseline (verified)

### Community 152 - "policy"
Cohesion: 0.40
Nodes (4): eval-compare, Quality Gate (1 case, MRR 1/n), Release Candidates Need Compare-shared-cases, T6 eval-compare

### Community 153 - "policy"
Cohesion: 0.40
Nodes (4): Public contact channels, Payments, account access and support boundaries, Payments non-refundable, One active login session

### Community 154 - "policy"
Cohesion: 0.70
Nodes (5): Home Affairs credentialled community language points, 5 points for credentialled community language, Australian Department of Home Affairs, Refer to Home Affairs or migration adviser, No automatic visa eligibility from passing CCL

### Community 155 - "ResolvedAccess"
Cohesion: 0.06
Nodes (69): 007 — Hybrid Retrieval Design, Alternatives / deferred decisions, As-built notes, Components / boundaries, Data flow, Design summary, Error and failure behavior, Interfaces / models (+61 more)

### Community 156 - "reranked_run"
Cohesion: 0.25
Nodes (7): Reranked, reranked_run(), test_result_2_5_keys_with_a_reranker(), test_skip_counts_by_reason_and_stage_and_path(), test_truncation_counts_cover_every_measured_query(), test_warm_up_load_joins_warmup_and_never_the_percentiles(), test_warmup_skip_is_recorded_and_not_counted_as_measured()

### Community 157 - "baseline.py"
Cohesion: 0.06
Nodes (36): Implementation, Review, T9 — round 1, User decision, dedupe_sections(), section_key(), section_report(), _aggregate() (+28 more)

### Community 158 - "Orchestrator State Machine"
Cohesion: 0.50
Nodes (4): Mission, Phase 1 public/guest vs Phase 2 Knowledge Operations, Mission purpose: grounded multilingual RAG assistant, Useful product, engineering learning, portfolio evidence

### Community 159 - "way2australia_api/__init__.py"
Cohesion: 0.50
Nodes (3): Coaching is optional, Way2Australia public offering and assistant scope, English-Malayalam CCL preparation offering

### Community 160 - "Project Context README"
Cohesion: 0.50
Nodes (4): 120+ practice dialogues, Materials and dialogue practice, Recordings stay in browser, No automatic score in ordinary practice

### Community 161 - "json"
Cohesion: 0.11
Nodes (16): load_schemas(), load_suite(), test_existing_schema_is_referenced_not_copied(), test_missing_schema_is_configuration_error(), test_per_type_required_field_enforced(), test_schema_files_are_valid_draft_2020_12(), test_valid_rows_pass(), copy_suite() (+8 more)

### Community 167 - "api/__init__.py"
Cohesion: 0.67
Nodes (3): Frontend stack, Next.js, TypeScript

### Community 168 - "test_eval_cli_bm25_needs_neither_qdrant_nor_the_embedder"
Cohesion: 0.29
Nodes (5): User decision, Implementation, Review, T7 — round 1, test_eval_cli_bm25_needs_neither_qdrant_nor_the_embedder()

### Community 169 - "DocumentRepository Protocol (async)"
Cohesion: 0.33
Nodes (6): DocumentRepository Protocol (async), KnowledgeDocument model, Spec 002 retrospective round 1, Spec 002 task review log (T3-T9), Spec 002 Document model and repository (verified), Acceptance dry run on Spec 002 T3

### Community 170 - "tests/evaluation/__init__.py"
Cohesion: 0.67
Nodes (3): Canonical document metadata, Chunk metadata, Source authority precedence

### Community 191 - "continuity.py"
Cohesion: 0.18
Nodes (17): _case_keys(), compare_continuity(), _embedder_pair_from_doc(), _fmt_key(), _info_lines(), _load_raw(), _lote_label(), main() (+9 more)

### Community 192 - "security_eval.py"
Cohesion: 0.05
Nodes (52): Change log, Review, T8 — round 1, User decision, T10 — Documentation, decisions and hand-off, Verification, Acceptance criteria, R7 — Marking degraded results (+44 more)

### Community 193 - "AccessContext"
Cohesion: 0.10
Nodes (13): Alternatives / deferred decisions, AccessContext, test_blank_tenant_refused(), test_empty_tenant_refused(), test_no_language_or_scope_fields(), test_roles_match_policy_file(), test_tenant_is_stripped(), test_unknown_role_refused() (+5 more)

### Community 195 - "R8 — Evaluation results for degraded runs"
Cohesion: 0.40
Nodes (6): Acceptance criteria, Acceptance criteria, R8 — Evaluation results for degraded runs, R9 — `eval-compare` by served strategy, index_settings=None refusal rule (T3 F2), T5 Result 2.2 and eval-compare by served strategy

### Community 196 - "test_status_handling.py"
Cohesion: 0.57
Nodes (4): golden_count(), suite_with_statuses(), test_exclusions_counted_by_status(), test_suggested_never_returned()

### Community 197 - "Roadmap 11 - Observability"
Cohesion: 0.33
Nodes (6): Roadmap 11 - Observability, Langfuse traces, Stage latency, model/tokens/cost, release/config IDs, Amazon CloudWatch, Langfuse, Observability

### Community 198 - "test_both_lote_modes_on_every_path_and_chunker"
Cohesion: 0.18
Nodes (6): test_both_lote_modes_on_every_path_and_chunker(), counting(), test_every_path_is_gated_for_every_query(), counting(), test_the_gate_runs_all_three_strategies_on_v2(), counting()

### Community 201 - "open_retrieval / OpenedRetrieval"
Cohesion: 0.18
Nodes (11): open_retrieval / OpenedRetrieval, Open-time fallback lasts for the run, Qdrant connect/query timeouts (config 1.1), retrieval_client_factory, R5 — `bm25` without Qdrant or the `bge-m3` extra, Review F1: open-time outage serves whole run, Review F4: duplicated standalone open wiring, Review F5: bind_to scroll fallback untested end to end (+3 more)

### Community 202 - "Way2Australia AI Platform Master Implementation Plan"
Cohesion: 0.33
Nodes (6): Way2Australia AI Platform Master Implementation Plan, Phase 1 Definition of Done, Phase 1 Scope (public/guest RAG), Recruiter / portfolio story, Project Mission, Seven-day Phase 1 execution plan

### Community 204 - "ResolvedLote"
Cohesion: 0.08
Nodes (37): 010 — Multilingual Retrieval Design, Applicability builders (R3), Components / boundaries, Continuity command (R10), Data flow, Design summary, Error and failure behavior, Observability (+29 more)

### Community 205 - "test_a_forbidden_hit_injected_into_a_path_fails_the_gate_naming_it"
Cohesion: 0.25
Nodes (3): test_a_forbidden_hit_injected_after_the_stage_fails_each_rerank_path(), test_a_forbidden_hit_injected_into_a_path_fails_the_gate_naming_it(), injecting()

### Community 206 - "DocumentRepository"
Cohesion: 0.29
Nodes (7): Roadmap 2 - Document model + repository, KnowledgeDocument, Manifest/schema validation, S3DocumentRepository and external storage, Document manifest, DocumentRepository, LocalDocumentRepository

### Community 207 - "Retrieval fallback (Spec 008, D056-D062)"
Cohesion: 0.12
Nodes (19): bm25 builds no embedder and no Qdrant client, classify_model_error, classify_qdrant_error, D056-D062 fallback decisions, D057 Fallback eligibility classification, D058 Fallback policy per query, D061 Marking and evaluation of fallback, D062 5xx not eligible (+11 more)

### Community 208 - "D049 Suite public-eval-v2 and the closed v1 reference (Spec 007)"
Cohesion: 0.29
Nodes (7): D049 Suite public-eval-v2 and the closed v1 reference (Spec 007), suite public-eval-v2, Acceptance criteria, R13 strategy comparison and default-strategy rule, R1 Evaluation Suite public-eval-v2 (91 cases), R2 — v2 dense baseline (user-owned gate), T9 strategy comparison and default-strategy decision

### Community 209 - "IndexIdentity"
Cohesion: 0.06
Nodes (28): As-built notes, T2: where the shared pieces live (2026-10-31), Implementation, Implementation, Review, Review, T2 — round 1, T3 — round 1 (+20 more)

### Community 210 - "Evaluation result format 2.2"
Cohesion: 0.33
Nodes (6): eval-compare by served strategy (mixed refused), Latency grouped by served path, Evaluation result format 2.2, RetrievalResult marking (requested_strategy, fallback_reason), Review F2: result 2.2 does not record fallback stage, T4 deviations (header only on fallback, requested_strategy by wrapper)

### Community 211 - "Review"
Cohesion: 0.50
Nodes (4): Implementation, Review, T2 — round 1, User decision

### Community 216 - "R12 — Real runs (user-owned gate)"
Cohesion: 0.33
Nodes (6): Acceptance criteria, R12 — Real runs (user-owned gate), Spec 007 BM25 and hybrid reference results, T7 real runs: fallback-only and Qdrant-up results, T7 — Real runs (user-owned gate), Verification

### Community 219 - "Spec 008 Retrieval Fallback Requirements"
Cohesion: 0.50
Nodes (4): Change log, Spec 008 Retrieval Fallback Requirements, Spec 008 Retrospective Review round 1, Review F3: missing change-log lines (resolved)

## Ambiguous Edges - Review These
- `Task-gated agent workflow loop` → `graphify skill pointer`  [AMBIGUOUS]
  .claude/CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **380 isolated node(s):** `way2australia-api`, `way2australia-core`, `way2australia-observability`, `way2australia-rag`, `way2australia` (+375 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1570 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **35 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `D055 Default strategy is hybrid (Spec 007)` connect `D055 Default strategy is hybrid (Spec 007)` to `Development Workflow`, `typing`, `Ingestion pipeline (Spec 004)`, `Spec 007 hybrid retrieval`?**
  _High betweenness centrality (0.098) - this node is a cross-community bridge._
- **Are the 37 inferred relationships involving `LocalDocumentRepository` (e.g. with `Dependencies` and `Design summary`) actually correct?**
  _`LocalDocumentRepository` has 37 INFERRED edges - model-reasoned connections that need verification._
- **What connects `way2australia-api`, `way2australia-core`, `way2australia-observability` to the rest of the system?**
  _380 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_compare.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11634615384615385 - nodes in this community are weakly interconnected._
- **Why does `Change log` connect `security_eval.py` to `test_security_eval.py`, `ResolvedAccess`, `compare.py`, `test_lexical_cli.py`, `D055 Default strategy is hybrid (Spec 007)`, `007 — Hybrid Retrieval Requirements`, `open_retrieval`, `LexicalIndex`, `ResolvedAccess`, `baseline.py`?**
  _High betweenness centrality (0.097) - this node is a cross-community bridge._
- **Are the 85 inferred relationships involving `DenseIndex` (e.g. with `Design summary` and `Decisions resolved before drafting`) actually correct?**
  _`DenseIndex` has 85 INFERRED edges - model-reasoned connections that need verification._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Task-gated agent workflow loop` and `graphify skill pointer`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._