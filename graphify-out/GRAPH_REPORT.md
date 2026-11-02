# Graph Report - way2australia  (2026-11-02)

## Corpus Check
- 286 files · ~311,739 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 32 file(s) not represented in the graph (top: (none) 20, .jsonl 9, .mdc 1)

## Summary
- 4361 nodes · 13025 edges · 205 communities (170 shown, 35 thin omitted)
- Extraction: 79% EXTRACTED · 20% INFERRED · 0% AMBIGUOUS · INFERRED: 2670 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d89fdbc0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_compare.py
- retrieval_eval.py
- open_retrieval
- FakeTokenizer
- test_validate.py
- test_service.py
- service.py
- test_index.py
- real_hybrid
- evaluation/validate.py
- lexical/cli.py
- IndexSettings
- HeadingChunker
- test_config_schema_11.py
- test_lexical_cli.py
- retrieval/test_cli.py
- CURRENT_STATE.md current state document
- 008 — Retrieval Fallback Requirements
- Index Binding Errors
- Document Model Tests
- 007 — Hybrid Retrieval Requirements
- test_validate_knowledge.py
- test_availability.py
- BGE-M3 Adapter
- test_lexical_standalone.py
- Spec 004 ingestion baseline
- tokenization.py
- DenseIndex
- test_strategy_eval.py
- Evaluation CLI Tests
- compare.py
- KnowledgeDocument
- test_baseline.py
- evaluation/test_cli.py
- test_content_hash.py
- 009 — Chunking Experiments Requirements
- 008 — Retrieval Fallback Requirements
- conftest.py
- security_eval.py
- open_retrieval
- typing
- D055 Default strategy is hybrid (Spec 007)
- Workflow Reviewer
- LocalDocumentRepository
- test_lexical_standalone.py
- test_cli_config.py
- test_authorization_isolation.py
- make eval-retrieval
- 007 — Hybrid Retrieval Requirements
- list_eligible_documents
- HeadingChunker
- evaluation/cli.py
- FallbackRetriever
- FallbackReason
- asyncio
- Development Workflow
- retrieval/test_access.py
- build_lexical_index
- json
- make eval-security
- build_security_repository
- Target RAG query flow (User -> FastAPI -> validation -> AccessContext -> LanguageContext -> retrieval -> RRF -> reranker -> context builder -> answerability -> prompt -> Bedrock -> citation validation)
- test_legacy_baseline_snapshot.py
- build_security_index
- test_lexical_build.py
- make retrieve
- CURRENT_STATE.md current state document
- security_eval.py
- Fallback (hybrid only)
- embedder
- Phase 1 RAG query pipeline
- test_lexical_tokenizer.py
- AccessContext
- Constitution
- Section: Next step
- dense
- AWS target
- test_repository_contract.py
- Spec 005 dense retrieval baseline
- test_collection_with_1_0_settings_still_binds
- list_eligible_documents
- Ingestion pipeline (Spec 004)
- Retrieval fallback (Spec 008, D056-D062)
- strategy.py
- DenseIndex
- Spec 001 project foundation
- Backend stack
- embedder
- D023 Task-gated agent workflow
- FakeEmbedder
- test_schemas.py
- DocumentQuery
- pathlib
- RetrievalConfigurationError
- read_result
- ingest_dense
- SpyIndex
- HybridRetriever
- CURRENT_STATE.md
- QdrantIndexStore
- repositories/__init__.py
- 006 Evaluation Framework Tasks
- transcript_metrics.py
- Retrieval package (Spec 005 and 007)
- D035 One filter builder, fail-closed re-check, same path for later fallbacks (Spec 005)
- Qdrant (vector database)
- run_security_evaluation
- LexicalIndex
- make eval-retrieval
- test_run_retrieval_evaluation_on_multi_chunk_recursive_index
- test_content_hash.py
- fake_info
- test_violation_names_the_document_from_the_error_attribute
- pytest
- test_bm25.py
- fusion
- evaluation/cli.py
- make_document
- evaluation/errors.py
- failing_client
- test_status_handling.py
- ARCHITECTURE.md
- json
- QdrantIndexStore
- Baseline runner and result JSON
- test_failed_write_removes_partial_file
- Development Workflow
- test_status_handling.py
- absent_query_languages
- Phase 1 - Production-oriented RAG
- RuntimeSettings
- R1 — Failure classification (`errors.py`, `availability.py`)
- Vocabulary, flashcards and free access
- .search
- documents/__init__.py
- Spec 002 document model and repository
- suite.py
- Evaluation Framework Goal
- make validate-evaluation
- Intentionally avoided choices
- BGE-M3 (initial embedding model)
- Way2Australia AI Platform Master Implementation Plan
- R4 — Freshness check from the repository
- eval-compare
- Payments, account access and support boundaries
- make eval-compare
- make test
- Mission
- test_fallback.py
- test_text.py
- Spec 004 retrospective round 1 (PASS)
- policy
- policy
- policy
- pathlib
- build_security_repository
- lexical/ package (Spec 007)
- Orchestrator State Machine
- way2australia_api/__init__.py
- Project Context README
- D050 SQLite FTS5 lexical store, not Qdrant sparse vectors (Spec 007)
- way2australia_rag/__init__.py
- Scripted
- way2australia-core
- Phase 1 analytics event contract
- Spec-driven development workflow
- api/__init__.py
- DocumentRepository Protocol (async)
- test_a_forbidden_hit_injected_into_a_path_fails_the_gate_naming_it
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
- _security
- test_failed_write_removes_partial_file
- classify_qdrant_error
- Evaluation tooling
- BGE-M3 embeddings
- R12 — Real runs (user-owned gate)
- R8 — Evaluation results for degraded runs
- test_status_handling.py
- SpyIndex
- policy
- .search
- metrics.py, goldens.py, baseline.py, baseline_cli.py
- Scripted
- counting

## God Nodes (most connected - your core abstractions)
1. `DenseIndex` - 107 edges
2. `LocalDocumentRepository` - 101 edges
3. `Strategy` - 76 edges
4. `run_retrieval_evaluation()` - 71 edges
5. `FakeEmbedder` - 70 edges
6. `HeadingChunker` - 68 edges
7. `FakeTokenizer` - 66 edges
8. `open_retrieval()` - 65 edges
9. `DenseRetriever` - 64 edges
10. `EvaluationConfigurationError` - 63 edges

## Surprising Connections (you probably didn't know these)
- `R10 — `eval-compare` identity rules (`compare.py`)` --references--> `_refusals()`  [INFERRED]
  .kiro/specs/007-hybrid-retrieval/design.md → packages/rag/src/way2australia_rag/evaluation/compare.py
- `Change log` --references--> `run_retrieval_evaluation()`  [INFERRED]
  .kiro/specs/009-chunking-experiments/requirements.md → packages/rag/src/way2australia_rag/evaluation/retrieval_eval.py
- `T4 review follow-ups (planner amendment 2026-11-02)` --references--> `run_retrieval_evaluation()`  [INFERRED]
  .kiro/specs/009-chunking-experiments/tasks.md → packages/rag/src/way2australia_rag/evaluation/retrieval_eval.py
- `Implementation` --references--> `chunker_identity_for_run()`  [INFERRED]
  .kiro/specs/009-chunking-experiments/task-reviews.md → packages/rag/src/way2australia_rag/ingestion/chunker_build.py
- `Interfaces / models` --references--> `Chunk`  [INFERRED]
  .kiro/specs/009-chunking-experiments/design.md → packages/rag/src/way2australia_rag/ingestion/chunking.py

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

## Communities (205 total, 35 thin omitted)

### Community 0 - "test_compare.py"
Cohesion: 0.16
Nodes (44): case(), doc(), doc21(), ranked(), refusal(), run(), test_2_1_versus_2_2_dense_reads_both(), test_2_3_chunker_difference_refused_without_cross_index() (+36 more)

### Community 1 - "retrieval_eval.py"
Cohesion: 0.05
Nodes (61): Implementation, Implementation, Implementation, Implementation, Review, Review, Review, Review (+53 more)

### Community 2 - "open_retrieval"
Cohesion: 0.05
Nodes (62): 008 — Retrieval Fallback Design, Alternatives / deferred decisions, Data flow, Decisions D056-D062, Design summary, Spec 008 Retrieval Fallback Design, Error and failure behavior, Interfaces / models (+54 more)

### Community 3 - "FakeTokenizer"
Cohesion: 0.08
Nodes (34): Implementation, Review, Review, T2 — round 2, _char_split(), _merge_pieces(), _merge_word_pieces(), _parse_sections() (+26 more)

### Community 4 - "test_validate.py"
Cohesion: 0.14
Nodes (31): edit_rows(), edit_suite(), root(), run(), test_active_golden_without_relevant_documents(), test_candidate_ineligible_document_is_not_unknown(), test_candidate_not_suggested(), test_candidate_referenced_by_suite() (+23 more)

### Community 5 - "test_service.py"
Cohesion: 0.16
Nodes (24): RunReport, doc(), Harness, test_bumped_document_version_updates(), test_changed_body_updates(), test_changed_metadata_field_updates(), test_chunk_shrink_leaves_no_orphan(), test_chunk_too_long_report_has_no_chunk_text() (+16 more)

### Community 6 - "service.py"
Cohesion: 0.10
Nodes (23): T2 — Index identity, standalone lexical open and freshness check, Verification, Implementation, Review, T1 — round 1, T1 — Tokenizer and truncation guard, Verification, Chunk (+15 more)

### Community 7 - "test_index.py"
Cohesion: 0.19
Nodes (22): IndexBindingError, client(), make_settings(), open_index(), stalled_port(), test_binding_errors_are_not_mapped(), test_chunker_and_hash_contract_not_compared(), test_document_count_missing_document_id_is_a_binding_error() (+14 more)

### Community 8 - "real_hybrid"
Cohesion: 0.27
Nodes (7): dense_pair(), production_lexical(), real_hybrid(), test_empty_bm25_leg_keeps_the_dense_order(), test_fusion_receives_only_the_legs_checked_hits(), spy(), test_hybrid_result_shape()

### Community 9 - "evaluation/validate.py"
Cohesion: 0.10
Nodes (21): Implementation, Review, T1 — round 1, User decision, EvaluationSchemas, _candidate_rules(), problem(), _describe() (+13 more)

### Community 10 - "lexical/cli.py"
Cohesion: 0.08
Nodes (30): Implementation, Implementation, Review, Review, T1 — round 2, User decision, build_chunker(), chunk_token_cap() (+22 more)

### Community 11 - "IndexSettings"
Cohesion: 0.06
Nodes (38): 009 — Chunking Experiments Design, Alternatives / deferred decisions, As-built notes, Carry-over clean-ups (R11), Chunker identity, settings and configuration (R5), Cross-index comparison (R8), Data flow, Design summary (+30 more)

### Community 12 - "HeadingChunker"
Cohesion: 0.12
Nodes (40): basic_suite(), build(), default_eval_extras(), fusion_config(), golden(), _LexicalStub, _metric_chunk(), run() (+32 more)

### Community 13 - "test_config_schema_11.py"
Cohesion: 0.09
Nodes (21): build_chunker_from_config(), load_ingestion_config(), embedder_identity(), lexical_index_path(), DenseIdentity, LexicalIdentityInput, configured_lexical(), bge_tokenizer_fixture() (+13 more)

### Community 14 - "test_lexical_cli.py"
Cohesion: 0.05
Nodes (64): Implementation, Implementation, Review, T3 — round 2, T3 — round 3, User decision, check_target_allowed(), _inside_git_work_tree() (+56 more)

### Community 15 - "retrieval/test_cli.py"
Cohesion: 0.16
Nodes (22): _advice_ok(), clean_env(), Factory, indexed(), ingest(), retrieve(), test_bad_args_exit_2_without_client(), test_bad_config_exit_2_without_client() (+14 more)

### Community 16 - "CURRENT_STATE.md current state document"
Cohesion: 0.12
Nodes (26): RetrievalUnavailableError and availability classification, Current goal: Specs 001-008 complete; Spec 008 verified and merged into main (1107b67), plan next spec, Known issue: Qdrant and Hugging Face 5xx not fallback-eligible, Known issue: verify_fresh asyncio.run in event loop, Known issue: Qdrant client lifecycle leak on failed open, Known issue: freshness check rereads every document, Known issue: no circuit breaker, ~3 s per query with hanging Qdrant, Spec 008 retro F1: open-time outage makes BM25 serve whole run (+18 more)

### Community 17 - "008 — Retrieval Fallback Requirements"
Cohesion: 0.09
Nodes (26): 008 — Retrieval Fallback Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Spec 008 taken ahead of roadmap 7 (chunking), Change log (+18 more)

### Community 18 - "Index Binding Errors"
Cohesion: 0.09
Nodes (32): IndexSettingsMismatchError, IndexedDocument, QdrantIndexStore, client_factory(), CountingStore, client(), _keyword_indexed(), live_client() (+24 more)

### Community 19 - "Document Model Tests"
Cohesion: 0.15
Nodes (24): User decision, IndexPoint, DenseRetriever, build_client(), docs(), guest(), make_point(), open_spy() (+16 more)

### Community 20 - "007 — Hybrid Retrieval Requirements"
Cohesion: 0.05
Nodes (43): BM25Retriever with SQL access clause, eval-compare identity rules (R10), HybridRetriever (dense leg then BM25 leg, no single-leg fallback), lexical-v1 tokenizer (NFC, ZWJ/ZWNJ dropped, L/N/Mn/Mc token chars, 64-term cap), Result format 2.1 and security result 1.1, config/retrieval.yaml and build_retriever strategy factory, SQLite FTS5 lexical store (derived, git-ignored, bound to dense index), 007 — Hybrid Retrieval Requirements (+35 more)

### Community 21 - "test_validate_knowledge.py"
Cohesion: 0.22
Nodes (26): load(), test_bad_date_fails_loading_naming_document_and_field(), test_seed_corpus_still_loads(), test_valid_date_loads(), build_repo(), metadata(), problems_for(), run_cli() (+18 more)

### Community 22 - "test_availability.py"
Cohesion: 0.17
Nodes (11): classify_model_error(), caused_by(), handled_error(), status_error(), test_a_cause_cycle_terminates(), test_cause_chain_stops_at_the_link_limit(), test_context_without_from_is_not_eligible(), test_offline_mode_is_excluded_even_though_it_is_a_connection_error() (+3 more)

### Community 23 - "BGE-M3 Adapter"
Cohesion: 0.06
Nodes (18): Model Preferences, Agent Skills README, Implementation Checklist, Spec Implementer Skill, task-reviews.md Implementation Block, Design Template, Change Log, Requirements Template (+10 more)

### Community 24 - "test_lexical_standalone.py"
Cohesion: 0.05
Nodes (33): Day-1 Usage, document_manifest.jsonl, golden_public.jsonl, Source-of-Truth Policy, chunking, overlap_tokens, strategy, target_tokens (+25 more)

### Community 25 - "Spec 004 ingestion baseline"
Cohesion: 0.14
Nodes (18): HeadingChunker heading v1 2000-char cap, Embedder Protocol, fake and BGE-M3 adapter, IngestionService change detection, make ingest and config/ingestion.yaml, 17-field PointPayload and UUIDv5 point IDs, QdrantIndexStore with companion settings collection, Heading chunking only synthetic-tested, none of 13 docs has headings, Spec 004 open review findings (T3 F1, T5 F2, T7 F1-F3, T8 F1, retro F1) (+10 more)

### Community 26 - "tokenization.py"
Cohesion: 0.06
Nodes (31): Components / boundaries, `recursive` v1 (R4), `structure` v1 (R3), Tokenizer (R1), Truncation guard (R2), _group_installed(), IngestionConfigurationError, _build_prefix() (+23 more)

### Community 27 - "DenseIndex"
Cohesion: 0.15
Nodes (6): EmbedderInfo, DenseIndex, OddIdStore, http_client(), test_a_closed_port_is_unavailable(), test_a_stalled_open_times_out_within_the_connect_bound()

### Community 28 - "test_strategy_eval.py"
Cohesion: 0.09
Nodes (32): User decision, build_lexical(), eval_world(), leg_order(), lexical_env(), make_world(), retrieve(), retrieve_world() (+24 more)

### Community 29 - "Evaluation CLI Tests"
Cohesion: 0.12
Nodes (31): assert_invalid(), document_fields(), make_document(), test_blank_required_text_is_rejected(), test_document_is_immutable(), test_duplicate_lote_languages_are_rejected(), test_effective_window_must_be_ordered(), test_empty_lote_languages_is_rejected() (+23 more)

### Community 30 - "compare.py"
Cohesion: 0.13
Nodes (32): Implementation, Review, T7 — round 1, User decision, _changed(), _chunker_text(), compare(), Comparison (+24 more)

### Community 31 - "KnowledgeDocument"
Cohesion: 0.08
Nodes (5): _check_language_code(), KnowledgeDocument, CountingEmbedder, ListRepository, IgnoresQueryRepository

### Community 32 - "test_baseline.py"
Cohesion: 0.10
Nodes (24): case(), clean_env(), cli_run(), DeviceStub, _git(), run(), seeded(), setup() (+16 more)

### Community 33 - "evaluation/test_cli.py"
Cohesion: 0.17
Nodes (16): clean_env(), index_factory(), real_factory(), run(), test_bad_top_k_exits_2(), test_existing_output_exits_2_before_qdrant(), test_fake_embedder_exits_2_before_qdrant(), test_filter_carries_the_server_tenant() (+8 more)

### Community 34 - "test_content_hash.py"
Cohesion: 0.16
Nodes (17): canonical_json(), _canonical_value(), _canonical_value_mapping(), _copy_seed(), h(), _load(), test_absent_optional_fields_hash_as_null(), test_body_change_changes_content_hash() (+9 more)

### Community 36 - "009 — Chunking Experiments Requirements"
Cohesion: 0.07
Nodes (28): 009 — Chunking Experiments Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+20 more)

### Community 37 - "008 — Retrieval Fallback Requirements"
Cohesion: 0.11
Nodes (32): Binding: embedder model ID, revision, vector size, normalization, fake flag and index_version must equal recorded IndexSettings, BM25Retriever(identity, lexical), BM25 statistics (IDF, avg length) computed over every row of a lexical file, build_retriever (only place a strategy name becomes a retriever), retrieval_client_factory (Qdrant client with configured timeouts), config/retrieval.yaml (default_strategy hybrid, RRF k 60, depth 50), D033-D041 retrieval decisions, D049-D055 (+24 more)

### Community 38 - "conftest.py"
Cohesion: 0.20
Nodes (5): manifest_document_count(), block_model_stack(), Raises, test_open_retrieval_bm25_builds_no_embedder_and_no_client(), test_retrieve_cli_bm25_needs_neither_qdrant_nor_the_model()

### Community 39 - "security_eval.py"
Cohesion: 0.15
Nodes (16): Implementation, Review, T6 — round 1, EvaluationHarnessError, _check_standalone_open(), _gate(), _lexical_sanity_check(), _open_lexical_sanity() (+8 more)

### Community 40 - "open_retrieval"
Cohesion: 0.12
Nodes (13): get_health(), HealthResponse, get_request_settings(), get_settings(), Settings, create_app(), isolate_settings_environment(), test_create_app_wires_settings() (+5 more)

### Community 41 - "typing"
Cohesion: 0.10
Nodes (28): 006-candidates.jsonl with 7 suggested rows, make eval-compare, make eval-security hard gate, result 2.2 and served-strategy eval-compare, eval-security five paths, governed suite loader and schemas, make validate-evaluation, Spec 006 retrospective findings (F1 byte-identity, eval-security not in verify) (+20 more)

### Community 42 - "D055 Default strategy is hybrid (Spec 007)"
Cohesion: 0.12
Nodes (18): make retrieval-baseline legacy frozen, Known issue: git_dirty true in Spec 007 BM25/hybrid result files (user-accepted), Latency hybrid p50 80.3 ms p95 103.6 ms; bm25 p50 0.19 ms, BM25 metrics: 64/69 goldens, MRR 0.7082, Hybrid metrics: 68/69 goldens, MRR 0.9094, Retrieval misses g004 g026 g061, Next step 2: real BGE-M3 baseline committed, Next step 4: Spec 007 T9 strategy comparison and hybrid default (+10 more)

### Community 43 - "Workflow Reviewer"
Cohesion: 0.07
Nodes (25): Considered and rejected, Evidence, F1 — <title> [waste | quality risk | process slip] (confidence: high/medium/low), Findings, New features and tools (official sources, since <date>), Not measurable here, P1 — <title> (addresses F#; expected saving: ...), Proposals (+17 more)

### Community 44 - "LocalDocumentRepository"
Cohesion: 0.13
Nodes (39): run_security_evaluation(), query_terms(), LocalDocumentRepository, build(), guest_access(), new_base(), real_queries(), security_result() (+31 more)

### Community 45 - "test_lexical_standalone.py"
Cohesion: 0.18
Nodes (19): build_from(), built(), copy_repository(), expected(), first_document_id(), open_it(), remove_document(), repo_at() (+11 more)

### Community 46 - "test_cli_config.py"
Cohesion: 0.14
Nodes (20): clean_env(), _factory(), _run(), test_agrees_with_day1_baseline(), test_builds_exactly_one_embedder_per_run(), test_collection_base_comes_from_environment(), test_config_refuses_missing_or_floating_revision(), test_config_refuses_unknown_field_and_missing_file() (+12 more)

### Community 47 - "test_authorization_isolation.py"
Cohesion: 0.19
Nodes (4): client_with_forbidden(), FilterDroppingIndex, test_forbidden_points_are_never_returned(), test_store_dropping_the_filter_fails_closed()

### Community 48 - "make eval-retrieval"
Cohesion: 0.12
Nodes (23): BgeM3Embedder (optional bge-m3 extra, dense only), D025-D030, D032 ingestion decisions, DocumentRepository Protocol (get_document, list_documents), Embedder Protocol, FakeEmbedder (deterministic), GUEST_PUBLIC_POLICY, HeadingChunker (heading v1, character cap, stable section_id slugs), IndexSettings and mismatch comparison (+15 more)

### Community 49 - "007 — Hybrid Retrieval Requirements"
Cohesion: 0.09
Nodes (27): optional bge-m3 extra (sentence-transformers, PyTorch), D048 graphify tooling, make experiment CONFIG=... (target; records git commit, release, suite, chunker, embedder, strategy, metrics, latency), make format, Knowledge graph graphify (D048), /graphify . --update (user, once per spec after merge), graphify query / path / explain, graphify update . (+19 more)

### Community 50 - "list_eligible_documents"
Cohesion: 0.14
Nodes (21): collect(), list_eligible_documents(), assert_matches_snapshot(), assert_recursive_chunks_whitespace_fidelity(), assert_structure_chunks_whitespace_fidelity(), chunks_to_records(), collapse_whitespace(), load_snapshot() (+13 more)

### Community 51 - "HeadingChunker"
Cohesion: 0.11
Nodes (27): R3 — Tokenizer `lexical-v1` (`lexical/tokenizer.py`), HeadingChunker, _is_word_char(), slugify(), ids(), test_deterministic(), test_duplicate_headings_get_unique_ids_in_order(), test_duplicate_suffix_does_not_collide_with_literal_heading() (+19 more)

### Community 52 - "evaluation/cli.py"
Cohesion: 0.07
Nodes (29): Implementation, Review, T5 — round 1, User decision, Implementation, Review, T4 — round 1, User decision (+21 more)

### Community 53 - "FallbackRetriever"
Cohesion: 0.08
Nodes (27): Fallback authorization invariant (same ResolvedAccess), BM25Retriever (identity, lexical), classify_model_error, classify_qdrant_error, Qdrant client lifecycle gap, eval-compare by served strategy (mixed refused), FallbackRetriever, Hugging Face error shapes (T1 As-built) (+19 more)

### Community 54 - "FallbackReason"
Cohesion: 0.22
Nodes (7): FallbackReason, reason(), test_configuration_errors_fail_closed(), test_network_cause_is_eligible(), test_other_qdrant_errors_are_not_eligible(), test_transport_errors_are_eligible_bare_and_wrapped(), test_unavailable_error_message_comes_from_the_reason_only()

### Community 55 - "asyncio"
Cohesion: 0.16
Nodes (21): LocalRepositoryConfig, test_repository_content_hash_is_content_hash_v1(), test_seed_corpus_is_entirely_eligible_for_guest(), _copy_seed(), seed_repository(), test_documents_outside_approved_roots_are_never_loaded(), test_get_document_by_id_and_version(), test_get_document_missing_raises_not_found() (+13 more)

### Community 56 - "Development Workflow"
Cohesion: 0.09
Nodes (33): Evaluation Suite includes goldens, refusal, multilingual, security, regression, Finalized stack: Python/FastAPI, Next.js, Qdrant, SQLite FTS5, BGE-M3, Bedrock, Langfuse, CloudWatch, Terraform ap-south-1, GitHub Actions, Ingestion operating notes (QDRANT_COLLECTION_BASE for fake runs, make setup-bge-m3), agent-skills sync, D001 Python-first backend, D002 RAG as reusable internal package, D003 Knowledge outside RAG package, D005 Documents are truth; chunks are derived (+25 more)

### Community 57 - "retrieval/test_access.py"
Cohesion: 0.16
Nodes (16): clean_env(), guest(), payload(), _policy(), test_a_different_policy_changes_both_builders(), test_both_builders_cover_the_same_three_conditions(), test_check_hit_accepts_valid_payload(), test_check_hit_rejects_malformed_payload() (+8 more)

### Community 58 - "build_lexical_index"
Cohesion: 0.13
Nodes (16): Implementation, Review, Review, T3 — round 1, User decision, T3 — `lexical-v1` tokenizer, lexical store and `make index-lexical`, Verification, R4 — Freshness from the repository (`lexical/freshness.py`) (+8 more)

### Community 59 - "json"
Cohesion: 0.12
Nodes (16): chunker, max_chunk_chars, name, version, embedder, batch_size, fake_vector_size, model_id (+8 more)

### Community 60 - "make eval-security"
Cohesion: 0.15
Nodes (14): Security gate on throwaway w2a-sectest-<8 hex> collection with fake embedder, security_corpus.py, security_index.py, security_eval.py, D040, Throwaway collection w2a-sectest-<8 hex>, eval-security exit 0 pass, 1 violation, 2 harness or configuration error, Security fixtures poisoned_public_document.md and staff_only_canary.md, Forbidden points: staff scope, other tenant, owned, missing owner, staff-only canary; nearest neighbour of every query, Authorization hard gate (forbidden points never returned) (+6 more)

### Community 61 - "build_security_repository"
Cohesion: 0.15
Nodes (16): clean_env(), _lexical_work_dir(), spy_lexical_path(), wrapper(), SpyIndex, strip_forbidden_terms(), test_cli_clause_less_lexical_store_exits_one_naming_strategies(), test_cli_harness_error_exits_two_and_writes_nothing() (+8 more)

### Community 62 - "Target RAG query flow (User -> FastAPI -> validation -> AccessContext -> LanguageContext -> retrieval -> RRF -> reranker -> context builder -> answerability -> prompt -> Bedrock -> citation validation)"
Cohesion: 0.13
Nodes (20): Answerability / insufficient-evidence decision, Authorization applied inside each retriever before fusion, never after RRF, reranking or generation, Authorization filter is part of the Qdrant query so unauthorized points never leave the store, Amazon Bedrock generation, build_access_filter (the only filter builder), check_hit (fail-closed re-check, second line of defense), Citation validation, Context builder (planned) (+12 more)

### Community 63 - "test_legacy_baseline_snapshot.py"
Cohesion: 0.06
Nodes (27): BgeM3Embedder, group_installed(), test_constructing_does_not_load_the_model(), test_device_none_before_load_and_recorded_after(), test_missing_group_at_load_raises_optional_dependency_error(), test_missing_group_refused_at_construction(), test_model_loaded_once_with_revision_and_batches(), fake_loader() (+19 more)

### Community 64 - "build_security_index"
Cohesion: 0.10
Nodes (15): Implementation, Review, T8 — round 1, User decision, T10 — Documentation, decisions and hand-off, Verification, build_security_index(), delete_security_index() (+7 more)

### Community 65 - "test_lexical_build.py"
Cohesion: 0.20
Nodes (18): identity(), payload(), synthetic_entries(), build(), test_atomic_replace_keeps_old_file_after_failure(), test_build_production_helper_runs(), test_build_records_settings(), test_digest_is_stable_and_order_independent() (+10 more)

### Community 66 - "make retrieve"
Cohesion: 0.08
Nodes (30): D061 fallback marking, docker compose up -d / down (local Qdrant), Environment: QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION_BASE, W2A_TENANT_ID, eval-retrieval options (--top-k, --strategy, --retrieval-config, --suite default public-eval-v2, --release seed-v1, --output, --repo-root, --config); no --embedder or --allow-fake, Fake embedder needs throwaway QDRANT_COLLECTION_BASE, strategy: bm25 (requested: hybrid; fallback: <reason>) plus stderr WARNING, exit 0, Fallback reasons qdrant_unavailable, qdrant_timeout, model_unavailable (never exception text), Default hybrid needs lexical file; exits 2 without it; setup order make ingest then make index-lexical (+22 more)

### Community 67 - "CURRENT_STATE.md current state document"
Cohesion: 0.10
Nodes (29): build_retriever, make eval-retrieval, CURRENT_STATE.md current state document, Phase 2 Knowledge Release workflow designed not implemented, Public/guest retrieval only in Phase 1; English + Malayalam, Known issue: legacy chillu sequence does not match atomic chillu in BM25, Known issue: evaluation-data gaps (ml goldens, relevant_section_ids empty), Known issue: g004 overlaps u001, keep_both (+21 more)

### Community 68 - "security_eval.py"
Cohesion: 0.07
Nodes (51): 007 — Hybrid Retrieval Design, Alternatives / deferred decisions, As-built notes, Data flow, Design summary, Error and failure behavior, Interfaces / models, Observability (+43 more)

### Community 69 - "Fallback (hybrid only)"
Cohesion: 0.21
Nodes (14): bm25 strategy, bm25 needs neither Qdrant nor the bge-m3 extra (Spec 008), config/retrieval.yaml schema 1.1 (default_strategy hybrid, qdrant.connect_timeout_s 2, query_timeout_s 3; 1.0 refused), dense strategy, --strategy dense needs no lexical file, Embedder pair from index_settings or dense_identity; fallback-only 2.2 file compares against Spec 007 bm25 file, eval-retrieval fallback: Qdrant unreachable with default hybrid is served by bm25 for every case, Fallback never applies to explicit dense or bm25 (+6 more)

### Community 70 - "embedder"
Cohesion: 0.11
Nodes (17): chunker, context_prefix, name, overlap_tokens, target_tokens, version, embedder, batch_size (+9 more)

### Community 71 - "Phase 1 RAG query pipeline"
Cohesion: 0.11
Nodes (19): Deduplication, context budgeting, evidence ordering, Roadmap 9 - Reranking + context building, Reranker failure to hybrid results, Authorization model (guest/public), Small documents and chunking strategy, Citation strategy (backend-owned validation), FAQ-aware retrieval experiment, Graceful degradation (+11 more)

### Community 72 - "test_lexical_tokenizer.py"
Cohesion: 0.12
Nodes (14): _is_token_char(), QueryTerms, tokenize(), test_business_008_words_stay_whole(), test_deterministic(), test_english_punctuation_digits_and_case(), test_golden_file_is_the_source_of_the_pins(), test_golden_queries_pin_exact_tokens() (+6 more)

### Community 73 - "AccessContext"
Cohesion: 0.09
Nodes (19): AccessContext, Role, test_blank_tenant_refused(), test_empty_tenant_refused(), test_no_language_or_scope_fields(), test_roles_match_policy_file(), test_tenant_is_stripped(), test_unknown_role_refused() (+11 more)

### Community 74 - "Constitution"
Cohesion: 0.19
Nodes (23): load_manifest(), load_schema(), validate_manifest(), metadata(), record(), run(), test_duplicate_document_id_rejected(), test_duplicate_document_version_rejected() (+15 more)

### Community 75 - "Section: Next step"
Cohesion: 0.08
Nodes (23): Way2Australia AI Platform Master Implementation Plan, Atomic publish and rollback, Phase 2 audit trail, AWS deployment architecture (ap-south-1), Controlled document-change workflow (Release Candidate), CI/CD pipeline, Phase 1 Definition of Done, Evaluation governance states (+15 more)

### Community 76 - "dense"
Cohesion: 0.06
Nodes (36): Components / boundaries, R10 — `eval-compare` identity rules (`compare.py`), R11 — Security gate (`security_index.py`, `security_eval.py`), R12 — Docker test, R1 — Suite v2, R4 — `make index-lexical` (`lexical/cli.py`), R4/R5 — Lexical store (`lexical/store.py`, `lexical/build.py`), R7 — Fusion and `HybridRetriever` (`retrieval/fusion.py`, `hybrid.py`) (+28 more)

### Community 77 - "AWS target"
Cohesion: 0.10
Nodes (21): Roadmap 11 - Observability, Langfuse traces, Stage latency, model/tokens/cost, release/config IDs, AWS target, Bedrock Knowledge Bases as core RAG (avoided), Bedrock model selection criteria, Amazon CloudWatch, Derived retrieval index in Qdrant (+13 more)

### Community 78 - "test_repository_contract.py"
Cohesion: 0.26
Nodes (8): InMemoryDocumentRepository, make_document(), test_get_document_missing_raises_not_found(), test_get_document_returns_latest_or_requested_version(), test_in_memory_repository_satisfies_protocol(), test_list_documents_applies_query_filters(), test_query_matches_is_the_single_language_and_scope_rule(), use_repository()

### Community 79 - "Spec 005 dense retrieval baseline"
Cohesion: 0.18
Nodes (15): AccessContext, Role, W2A_TENANT_ID, BGE-M3 device mps not pinned (D038), Spec 005 retrospective findings F3-F5, Spec 005 dense retrieval baseline, Spec 005 status: verified 2026-10-23 merged b33462e, AccessContext and Role, D033 AccessContext and Role live in core (Spec 005), D034 W2A_TENANT_ID is a server setting (Spec 005) (+7 more)

### Community 80 - "test_collection_with_1_0_settings_still_binds"
Cohesion: 0.11
Nodes (13): Implementation, Implementation, Review, Spec 009 — Task reviews, T2 — round 1, T2 — round 3, T3 — round 1, T3 — round 2 (+5 more)

### Community 81 - "list_eligible_documents"
Cohesion: 0.23
Nodes (15): eligible_ids(), make_document(), test_active_approved_public_document_is_eligible(), test_language_filter_narrows_eligible_documents_only(), test_language_metadata_does_not_broaden_access(), test_local_repository_applies_the_policy_query(), test_non_active_lifecycle_is_excluded(), test_non_approved_status_is_excluded() (+7 more)

### Community 82 - "Ingestion pipeline (Spec 004)"
Cohesion: 0.11
Nodes (18): default_strategy, fusion, candidate_depth, k, method, weights, qdrant, connect_timeout_s (+10 more)

### Community 83 - "Retrieval fallback (Spec 008, D056-D062)"
Cohesion: 0.12
Nodes (18): bm25 builds no embedder and no Qdrant client, classify_model_error, classify_qdrant_error, D056-D062 fallback decisions, D057 Fallback eligibility classification, D058 Fallback policy per query, D061 Marking and evaluation of fallback, D062 5xx not eligible (+10 more)

### Community 84 - "strategy.py"
Cohesion: 0.25
Nodes (11): load_retrieval_config(), test_build_retriever_converts_a_string_value_and_refuses_unknown(), test_build_retriever_maps_each_strategy(), test_committed_config_loads(), test_good_config_loads(), test_invalid_config_is_refused_naming_the_field(), test_lexical_strategies_need_the_lexical_index(), test_timeout_bounds_are_inclusive() (+3 more)

### Community 85 - "DenseIndex"
Cohesion: 0.16
Nodes (25): LexicalRow, build(), dense_fixture(), DroppedClauseIndex, guest(), pub(), retriever(), _shape() (+17 more)

### Community 86 - "Spec 001 project foundation"
Cohesion: 0.09
Nodes (23): Completion: retrospective, Spec-Review commit, merge, verified status, Spec orchestrator loop (route, role subagents, user approval, merge), GET /health endpoint, make setup, packages core/rag/observability skeletons, task-gated spec skills and skills-sync, task State lifecycle and spec/NNN branches, uv workspace and uv.lock (+15 more)

### Community 87 - "Backend stack"
Cohesion: 0.12
Nodes (18): Lexical file is a derived artifact, one per collection, bound by identity and chunk digest, Source documents are truth; chunks, embeddings, sparse entries, Qdrant points and preview indexes are derived artifacts, Backend stack, FastAPI, httpx, jsonschema, Multiple vector databases (avoided), Pandas (+10 more)

### Community 88 - "embedder"
Cohesion: 0.14
Nodes (13): chunker, max_chunk_chars, name, version, embedder, batch_size, fake_vector_size, model_id (+5 more)

### Community 89 - "D023 Task-gated agent workflow"
Cohesion: 0.12
Nodes (16): allowed_scopes, current_release, default_role, implemented_roles, allowed_scopes, allowed_scopes, roles, admin (+8 more)

### Community 90 - "FakeEmbedder"
Cohesion: 0.16
Nodes (14): FakeEmbedder, _cosine_to_query(), test_run_retrieval_evaluation_on_multi_chunk_recursive_index(), _text_with_score_below(), __init__(), test_conforms_to_protocol(), test_declared_vector_size(), test_default_size_is_64() (+6 more)

### Community 91 - "test_schemas.py"
Cohesion: 0.17
Nodes (6): load_schemas(), test_existing_schema_is_referenced_not_copied(), test_missing_schema_is_configuration_error(), test_per_type_required_field_enforced(), test_schema_files_are_valid_draft_2020_12(), test_valid_rows_pass()

### Community 92 - "DocumentQuery"
Cohesion: 0.14
Nodes (3): DocumentQuery, EligibilityPolicy, test_ineligible_document()

### Community 93 - "pathlib"
Cohesion: 0.13
Nodes (16): Roadmap 2 - Document model + repository, KnowledgeDocument, Manifest/schema validation, S3DocumentRepository and external storage, apps/api, apps/web, CloudWatch, Document manifest (+8 more)

### Community 94 - "RetrievalConfigurationError"
Cohesion: 0.11
Nodes (15): guest_access(), BaselineResult, check_output_free(), format_summary(), main(), _parser(), default_output_path(), write_result() (+7 more)

### Community 95 - "read_result"
Cohesion: 0.17
Nodes (18): NotComparableError, read_result(), doc22(), doc23(), run_cross(), test_2_2_bm25_without_a_lexical_object_is_refused(), test_2_2_file_with_only_unanswerable_cases_served_differently_is_refused(), test_2_3_against_2_2_one_chunk_passes_without_cross_index() (+10 more)

### Community 96 - "ingest_dense"
Cohesion: 0.20
Nodes (11): build_production(), ingest_dense(), open_lexical(), rewrite_settings(), test_bind_does_not_write_to_qdrant(), test_bind_refuses_chunk_set_mismatch_with_counts(), test_bind_refuses_identity_and_chunker_mismatch(), test_bind_refuses_when_qdrant_content_changed() (+3 more)

### Community 97 - "SpyIndex"
Cohesion: 0.15
Nodes (17): Admin content management, Agent capabilities only where they solve a real product problem, Audit trail, Basic analytics, Candidate evaluation, Change impact analysis, Content hashing, Evaluation Governance (keep/modify/deprecate/replace) (+9 more)

### Community 98 - "HybridRetriever"
Cohesion: 0.10
Nodes (27): Change log, Implementation, Implementation, Review, Review, T5 — round 1, T5 — round 2, User decision (+19 more)

### Community 99 - "CURRENT_STATE.md"
Cohesion: 0.13
Nodes (14): interval, retries, start_period, test, timeout, container_name, healthcheck, image (+6 more)

### Community 101 - "repositories/__init__.py"
Cohesion: 0.05
Nodes (32): DocumentNotFoundError, DocumentRepositoryError, DocumentValidationError, DuplicateDocumentError, ManifestValidationError, split_frontmatter(), _StringDateLoader, compute_body_sha256() (+24 more)

### Community 102 - "006 Evaluation Framework Tasks"
Cohesion: 0.16
Nodes (15): Local multilingual BGE reranker, BM25 via FTS5 bm25(), Derived local lexical file per collection, Fusion, Generation, Lexical store, lexical-v1 tokens (D051), make index-lexical (+7 more)

### Community 103 - "transcript_metrics.py"
Cohesion: 0.12
Nodes (19): analyse(), category(), command_kinds(), executed_text(), expand(), main(), parse_time(), render() (+11 more)

### Community 104 - "Retrieval package (Spec 005 and 007)"
Cohesion: 0.14
Nodes (12): graphify skill pointer, spec/NNN branch and Spec-Task trailers, spec-implementer skill (one task per run), spec-orchestrator skill, spec-planner skill, spec-reviewer retrospective skill, Task-gated agent workflow loop, task-reviewer skill (read-only) (+4 more)

### Community 105 - "D035 One filter builder, fail-closed re-check, same path for later fallbacks (Spec 005)"
Cohesion: 0.17
Nodes (20): DenseIndex, build_access_filter, check_hit, DenseRetriever, FallbackRetriever and open_retrieval wiring (merged 1107b67), make retrieve guest/public CLI, Strategy Protocol, BM25Retriever, rrf_fuse, HybridRetriever, Spec 008 retro F4: duplicated standalone open wiring, BM25Retriever, build_access_filter, check_hit fail-closed re-check (+12 more)

### Community 106 - "Qdrant (vector database)"
Cohesion: 0.14
Nodes (13): Authorization metadata (access_scope, owner_user_id, tenant_id), Engineering Conventions, IDs and versions conventions, Knowledge files with provenance, Language metadata (content_language, lote_languages), Logging and tracing hygiene, Domain naming terms, Prompts as versioned assets (+5 more)

### Community 108 - "LexicalIndex"
Cohesion: 0.09
Nodes (22): R3 — Standalone lexical open (`identity.py`, `lexical/store.py`), T2: where the shared pieces live (2026-10-31), Implementation, Review, T2 — round 1, User decision, User decision, Verification (+14 more)

### Community 109 - "make eval-retrieval"
Cohesion: 0.12
Nodes (17): --allow-fake (plumbing only, never a recorded baseline), make retrieval-baseline (legacy, frozen Spec 005 producer), BASELINE_ARGS (--embedder, --allow-fake, --top-k, --suite, --release, --output, --config), Baseline metrics HitRate@5, random expectation min(1,5/N), Recall@5, MRR, p50/p95 latency, experiments/results/retrieval-baseline-<index_version>-<UTC>.json, never overwritten, D036 binding rules, D053 result 2.1, eval-retrieval exit 0 or 2 (+9 more)

### Community 110 - "test_run_retrieval_evaluation_on_multi_chunk_recursive_index"
Cohesion: 0.24
Nodes (6): deterministic_clock(), equivalence_suite(), run_equivalence(), chunks_per_document_dense(), unanswerable(), test_dense_2_2_equals_the_pre_change_2_0_result()

### Community 111 - "test_content_hash.py"
Cohesion: 0.15
Nodes (12): Approved packages, pricing and validity, Six approved packages and prices, 60-day package validity, 24-hour cancellation notice, Personal coaching package, 60-minute coaching session on Google Meet, Individual coaching and live appointments, Mock assessments, scoring, feedback and review windows (+4 more)

### Community 112 - "fake_info"
Cohesion: 0.22
Nodes (17): bound_index(), failing_client(), fake_info(), payload(), scope_filter(), seed(), test_a_stalled_search_times_out_within_the_query_bound(), test_dense_index_makes_no_write_calls() (+9 more)

### Community 113 - "test_violation_names_the_document_from_the_error_attribute"
Cohesion: 0.18
Nodes (12): AGENTS.md Project Rules, DocumentRepository Abstraction, Evaluation Governance Rules, Language Separation Rules, Phase 1 Scope, Task-gated Spec Loop, CLAUDE.md Project Instructions, graphify Knowledge Graph Rules (+4 more)

### Community 114 - "pytest"
Cohesion: 0.17
Nodes (12): AccessContext(role, tenant_id) with blank tenant refused, Future agent folders intentionally not created, apps/api (FastAPI application layer), apps/web (Next.js/TypeScript frontend: recruiter assistant, RAG Lab, engineering views), core/access.py (Role, frozen AccessContext), guest_access, Knowledge model metadata (document_id, document_version, tenant_id, access_scope, lote_languages, content_language, source_authority...), No language filter, score threshold or reranking yet (+4 more)

### Community 115 - "test_bm25.py"
Cohesion: 0.17
Nodes (12): BM25, Deterministic regression gates, Golden, refusal and security cases, HitRate@5, Roadmap 5 - Evaluation framework, Roadmap 6 - Hybrid retrieval, Roadmap 15 - CI/CD + regression gates, Language/domain slices (+4 more)

### Community 116 - "fusion"
Cohesion: 0.20
Nodes (12): English, Malayalam and mixed queries, FAQ-aware retrieval/indexing, Roadmap 7 - Chunking experiments, Roadmap 8 - Multilingual retrieval, Language applicability handling, Parent-heading context and order-independent section_ids, Recursive chunking baseline, Optional semantic chunking (+4 more)

### Community 117 - "evaluation/cli.py"
Cohesion: 0.21
Nodes (12): Branching and commits (spec/NNN, Spec-Task trailer), Development Workflow, Multi-agent handoff, Implementation rule: BLOCKED spec issue, Phase discipline, Protected source-of-truth data, Required spec-reviewer retrospective, Agent skills (orchestrator, planner, implementer, task-reviewer, spec-reviewer) (+4 more)

### Community 118 - "make_document"
Cohesion: 0.21
Nodes (19): make_document(), structure_chunker(), test_duplicate_sibling_headings_raise(), test_fence_blocks_are_atomic_and_headings_inside_ignored(), test_long_list_splits_only_between_items(), test_main_collision_with_heading_slug(), test_malayalam_paragraph_packs(), test_malayalam_paragraph_splits_when_over_cap() (+11 more)

### Community 119 - "evaluation/errors.py"
Cohesion: 0.09
Nodes (22): EvaluationConfigurationError, require_active_suite(), active_registry_languages(), aggregate(), _mean(), slice_by(), source_authority_key(), declared_release_id() (+14 more)

### Community 120 - "failing_client"
Cohesion: 0.18
Nodes (10): content-hash-v1 (sole change-detection signal), LocalDocumentRepository, Document manifest and JSON Schema validation, make validate-knowledge, persona_scope spec defect (F2), BgeM3Embedder (optional extra, pinned revision), Embedder Protocol and FakeEmbedder, HeadingChunker and slugify rule (+2 more)

### Community 121 - "test_status_handling.py"
Cohesion: 0.20
Nodes (8): Adding a New Language Guide, language_registry.json, Public Assistant Content Boundaries, access_scope, content_language, Knowledge Schema and Metadata, language_scope, lote_languages

### Community 122 - "ARCHITECTURE.md"
Cohesion: 0.12
Nodes (19): D042-D047, D053, D054 evaluation decisions, Evaluation architecture (Evaluation Suite case types), Evaluation assets never written by evaluation code (C6); candidates suggested and human-activated, Ingestion eligibility is the only guard against synthetic/unapproved documents; poisoned_public_document is not an authorization case, Evaluation isolation and gates, models.py, suite.py (tolerant typed cases, read-only load_suite), retrieval_eval.py, slices.py, sections.py, Section-level keys <document_id>#<section_id> (+11 more)

### Community 123 - "json"
Cohesion: 0.13
Nodes (21): load_suite(), declared_release_id(), load_suite(), live_suite_rows(), copy_suite(), test_access_context_is_loaded_but_ignored(), test_dataset_types_loaded_by_type(), test_escaping_path_refused() (+13 more)

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
Cohesion: 0.09
Nodes (27): Answerability and insufficient-evidence response, Authorization regression and staff canary, Docker, Terraform, EC2, ECR, CloudWatch, IAM, Bedrock, Bedrock Runtime (roadmap), BGE-M3 (roadmap), Deferred serving concerns (circuit breaker, startup policy, Qdrant 5xx D062), Citation manipulation tests and input/cost limits, Backend-owned citation validation (+19 more)

### Community 131 - "RuntimeSettings"
Cohesion: 0.33
Nodes (9): NAATI CCL candidate rules and test-day setup, Direct first-person speech requirement, Report technical incidents within 24 hours, NAATI, Online proctoring with separate phone or tablet, Prohibited materials and tools, Recording under 20 minutes, One repeated segment per dialogue without penalty (+1 more)

### Community 132 - "R1 — Failure classification (`errors.py`, `availability.py`)"
Cohesion: 0.22
Nodes (7): As-built notes, R1 — Failure classification (`errors.py`, `availability.py`), T1: Hugging Face error shapes (confirmed 2026-10-29), GatedRepoError, LocalEntryNotFoundError, RepositoryNotFoundError, RevisionNotFoundError

### Community 133 - "Vocabulary, flashcards and free access"
Cohesion: 0.29
Nodes (7): EligibilityPolicy / GUEST_PUBLIC_POLICY, Security fixtures (valid but ineligible), config/ingestion.yaml and RuntimeSettings, Ingestion pipeline (target vs current state diff), AccessContext and Role (core), resolve_access / ResolvedAccess, W2A_TENANT_ID server tenant setting

### Community 134 - ".search"
Cohesion: 0.25
Nodes (8): Phase 2 basic analytics, Assistant behavior rules, Product Context, English and Malayalam language scope, Future personas, Phase 1 guest-only scope, Way2Australia AI product, Source-of-truth priorities

### Community 135 - "documents/__init__.py"
Cohesion: 0.21
Nodes (6): AccessScope, ApprovalStatus, LanguageScope, LifecycleStatus, SourceAuthority, test_guest_policy_agrees_with_access_policy_config()

### Community 136 - "Spec 002 document model and repository"
Cohesion: 0.15
Nodes (16): Pydantic document models and enums, EligibilityPolicy for guest/public, LocalDocumentRepository with manifest schema validation, make validate-knowledge, Spec 002 decisions made before approval (content_hash, fixtures, validate-knowledge), Seed data status: 13 public docs, evaluation datasets, security fixtures, Spec 002 retrospective findings F1-F6, Spec 002 document model and repository (+8 more)

### Community 137 - "suite.py"
Cohesion: 0.12
Nodes (16): CaseBase, CaseStatus, DatasetRef, DatasetType, GoldenCase, LoadedSuite, SecurityCase, SuiteManifest (+8 more)

### Community 138 - "Evaluation Framework Goal"
Cohesion: 0.39
Nodes (8): NAATI CCL test format, scoring and results, NAATI CCL test, Deduction-based assessment, Begin interpreting within five seconds of chime, NAATI, CCL is not professional interpreter certification, Pass requirement 63/90 overall and 29/45 per dialogue, Results within 4-6 weeks

### Community 139 - "make validate-evaluation"
Cohesion: 0.15
Nodes (13): schemas.py, validate.py (referencing registry, validate-evaluation checks), Error format ERROR <ClassName>: <message>; eval-compare refusals start with 'not comparable:', EVAL_ARGS, python -m way2australia_rag.evaluation.cli {validate,retrieval,security,compare}, make eval-generation does not exist yet, Retrieval evaluation supports Recall@5, MRR, HitRate@5 and language/category/source-authority slices, Evaluation commands (single module evaluation.cli), Suite status draft, active, deprecated, replaced (+5 more)

### Community 140 - "Intentionally avoided choices"
Cohesion: 0.18
Nodes (13): Full agent orchestration (avoided), Intentionally avoided choices, Bedrock Agents / AgentCore for Phase 1 (avoided), Containers, Docker, Docker Compose, ECR, Fine-tuning (avoided) (+5 more)

### Community 141 - "BGE-M3 (initial embedding model)"
Cohesion: 0.38
Nodes (6): Evaluation Candidates File, Evaluation Package (evaluation/), Evaluation Suite and Case-type Schemas, validate-evaluation, T2 Schemas and validate-evaluation, T7 Candidates

### Community 142 - "Way2Australia AI Platform Master Implementation Plan"
Cohesion: 0.29
Nodes (7): eval-retrieval, Retrieval Result Document 2.0, Section-level Metrics, Slices and small_sample, Unanswerable Reporting, T3 Retrieval Runner, T4 Unanswerable Reporting

### Community 143 - "R4 — Freshness check from the repository"
Cohesion: 0.25
Nodes (8): Acceptance criteria, Acceptance criteria, R3 — Lexical index without Qdrant, R4 — Freshness check from the repository, R5 — `bm25` without Qdrant or the `bge-m3` extra, bge_m3 import move in ingestion/cli.py (T3 F1), T1 unexplained 14-minute integration hang, T3 bm25 without Qdrant or extra; one open path

### Community 144 - "eval-compare"
Cohesion: 0.29
Nodes (7): AGENTS.md, Claude adapter, Initial specs, Phase 0 - Project bootstrap, Project context files, SDD workflow (Spec 003 task-gated agent workflow), Stable command interface

### Community 145 - "Payments, account access and support boundaries"
Cohesion: 0.29
Nodes (6): Vocabulary, flashcards and free access, Spaced-repetition flashcards, Free access allowance, 12 subject domains plus General vocabulary, Approved public learning samples, Sample neighbour-greeting dialogue

### Community 146 - "make eval-compare"
Cohesion: 0.20
Nodes (11): results.py, compare.py (reads 1.0, 2.0, 2.1; quality gate; identity refusals), eval-compare exit 0 pass, 1 gate failure, 2 refusal, WARNING flipped hit->miss / miss->hit lines (<case_id> v<case_version>), Gate: fail if more than 1 fewer hit cases or MRR drop above 1/n, Fallback path latency marked 'includes failed dense attempt' (informational), Not-comparable refusals (suite, case sets, top_k, fake, collection, index_version, embedder, lexical index, mixed served strategies), BASE and CANDIDATE variables, make eval-compare (+3 more)

### Community 147 - "make test"
Cohesion: 0.33
Nodes (6): 006 Evaluation Framework Design, Decision Brief Q1-Q10, 006 Evaluation Framework Requirements, Evaluation Framework Goal, 006 Spec Retrospective Review, Retrospective Round 1 PASS

### Community 148 - "Mission"
Cohesion: 0.33
Nodes (5): Evaluation case_id and case_version, Versioning and Releases, document_id and document_version, Phase 2 Knowledge Release Candidates, Release seed-v1

### Community 149 - "test_fallback.py"
Cohesion: 0.12
Nodes (23): access(), client_at(), closed_port(), Fallback, open_hybrid(), Primary, run_cli(), stalled_port() (+15 more)

### Community 150 - "test_text.py"
Cohesion: 0.15
Nodes (5): settings(), test_factory_sets_the_connect_timeout_and_disables_the_version_check(), test_safe_text_keeps_malayalam_joiners(), test_safe_text_strips_bidi_controls_but_keeps_zwj_zwnj(), test_safe_text_strips_controls_and_ansi()

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

### Community 155 - "pathlib"
Cohesion: 0.06
Nodes (31): Acceptance criteria, T7 — Documentation, decisions, carry-over clean-ups and hand-off, Verification, _canary_points(), Embedder, OptionalDependencyError, point_id(), build_payload() (+23 more)

### Community 156 - "build_security_repository"
Cohesion: 0.21
Nodes (7): build_security_repository(), _fixture_files(), security_repository(), copy_fixtures(), test_hidden_entries_are_ignored(), test_missing_fixture_is_refused(), test_stray_fixture_file_is_refused_before_any_copy()

### Community 157 - "lexical/ package (Spec 007)"
Cohesion: 0.22
Nodes (9): D060 Standalone lexical freshness, Standalone freshness proves lexical file matches repository, not live Qdrant (D060), lexical/cli.py (make index-lexical writes only git-ignored file), freshness.py (verify_fresh, chunk digest recomputed from repository), lexical/ package (Spec 007), store.py (SQLite FTS5: chunks table, chunk_terms FTS5 table, settings row; LexicalIndex.open, bind_to, search), tokenizer.py (lexical-v1), make index-lexical (+1 more)

### Community 158 - "Orchestrator State Machine"
Cohesion: 0.50
Nodes (4): Mission, Phase 1 public/guest vs Phase 2 Knowledge Operations, Mission purpose: grounded multilingual RAG assistant, Useful product, engineering learning, portfolio evidence

### Community 159 - "way2australia_api/__init__.py"
Cohesion: 0.50
Nodes (3): Coaching is optional, Way2Australia public offering and assistant scope, English-Malayalam CCL preparation offering

### Community 160 - "Project Context README"
Cohesion: 0.50
Nodes (4): 120+ practice dialogues, Materials and dialogue practice, Recordings stay in browser, No automatic score in ordinary practice

### Community 161 - "D050 SQLite FTS5 lexical store, not Qdrant sparse vectors (Spec 007)"
Cohesion: 0.25
Nodes (11): make index-lexical, lexical package: lexical-v1 tokenizer, FTS5 store, builder, standalone bm25 without Qdrant or extra (IndexIdentity, freshness), Known issue: BM25 statistics corpus-wide per file; needs per-scope files for roles, Malayalam BM25 limit: exact tokens only, no stemming, D010 Qdrant primary, SQLite FTS5 fallback, D050 SQLite FTS5 lexical store, not Qdrant sparse vectors (Spec 007), lexical-v1 tokenizer (+3 more)

### Community 167 - "api/__init__.py"
Cohesion: 0.67
Nodes (3): Frontend stack, Next.js, TypeScript

### Community 168 - "DocumentRepository Protocol (async)"
Cohesion: 0.33
Nodes (6): DocumentRepository Protocol (async), KnowledgeDocument model, Spec 002 retrospective round 1, Spec 002 task review log (T3-T9), Spec 002 Document model and repository (verified), Acceptance dry run on Spec 002 T3

### Community 170 - "tests/evaluation/__init__.py"
Cohesion: 0.67
Nodes (3): Canonical document metadata, Chunk metadata, Source authority precedence

### Community 191 - "_security"
Cohesion: 0.19
Nodes (9): Implementation, Review, T5 — round 1, _security(), security_document(), security_gate_chunkers(), security_run_record(), SecurityReport (+1 more)

### Community 193 - "classify_qdrant_error"
Cohesion: 0.24
Nodes (6): Review, classify_qdrant_error(), _optional_types(), raise_if_unavailable(), test_qdrant_cause_and_context_are_not_followed(), test_unrelated_error_raised_while_handling_a_network_error_is_not_eligible()

### Community 194 - "Evaluation tooling"
Cohesion: 0.36
Nodes (8): Custom retrieval metrics (plain Python), DeepEval (not yet a dependency), Evaluation tooling, Generation/e2e metrics (correctness, faithfulness, citations, refusal), GitHub Actions, LLM-as-judge not sole source of truth, Primary retrieval metrics (Recall@5, MRR, HitRate@5), pytest

### Community 195 - "BGE-M3 embeddings"
Cohesion: 0.33
Nodes (6): Device not pinned, recorded in results (D038), Embeddings, Deterministic fake embedder, BGE-M3 embeddings, Multilingual design (lote_languages), Technology stack

### Community 196 - "R12 — Real runs (user-owned gate)"
Cohesion: 0.33
Nodes (6): Acceptance criteria, R12 — Real runs (user-owned gate), Spec 007 BM25 and hybrid reference results, T7 real runs: fallback-only and Qdrant-up results, T7 — Real runs (user-owned gate), Verification

### Community 197 - "R8 — Evaluation results for degraded runs"
Cohesion: 0.40
Nodes (6): Acceptance criteria, Acceptance criteria, R8 — Evaluation results for degraded runs, R9 — `eval-compare` by served strategy, index_settings=None refusal rule (T3 F2), T5 Result 2.2 and eval-compare by served strategy

### Community 198 - "test_status_handling.py"
Cohesion: 0.57
Nodes (4): golden_count(), suite_with_statuses(), test_exclusions_counted_by_status(), test_suggested_never_returned()

### Community 202 - "metrics.py, goldens.py, baseline.py, baseline_cli.py"
Cohesion: 0.50
Nodes (4): Baseline runner (refuses fake index without --allow-fake; HitRate@k, Recall@k, MRR, p50/p95, min(1,k/N) random expectation), D037 Baseline runner decisions, make retrieval-baseline (legacy dense-only), metrics.py, goldens.py, baseline.py, baseline_cli.py

## Ambiguous Edges - Review These
- `Task-gated agent workflow loop` → `graphify skill pointer`  [AMBIGUOUS]
  .claude/CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **380 isolated node(s):** `way2australia-api`, `way2australia-core`, `way2australia-observability`, `way2australia-rag`, `way2australia` (+375 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1312 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **35 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Change log` connect `HybridRetriever` to `build_security_index`, `retrieval_eval.py`, `security_eval.py`, `security_eval.py`, `D055 Default strategy is hybrid (Spec 007)`, `LocalDocumentRepository`, `LexicalIndex`, `test_lexical_cli.py`, `Document Model Tests`, `007 — Hybrid Retrieval Requirements`, `compare.py`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Are the 80 inferred relationships involving `DenseIndex` (e.g. with `Design summary` and `Decisions resolved before drafting`) actually correct?**
  _`DenseIndex` has 80 INFERRED edges - model-reasoned connections that need verification._
- **What connects `way2australia-api`, `way2australia-core`, `way2australia-observability` to the rest of the system?**
  _380 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `retrieval_eval.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0464424616792496 - nodes in this community are weakly interconnected._
- **Why does `D055 Default strategy is hybrid (Spec 007)` connect `D055 Default strategy is hybrid (Spec 007)` to `CURRENT_STATE.md current state document`, `typing`, `D035 One filter builder, fail-closed re-check, same path for later fallbacks (Spec 005)`, `Ingestion pipeline (Spec 004)`, `Development Workflow`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Are the 35 inferred relationships involving `LocalDocumentRepository` (e.g. with `Dependencies` and `Design summary`) actually correct?**
  _`LocalDocumentRepository` has 35 INFERRED edges - model-reasoned connections that need verification._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Task-gated agent workflow loop` and `graphify skill pointer`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._