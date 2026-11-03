# Graph Report - way2australia  (2026-11-03)

## Corpus Check
- 287 files · ~315,457 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 32 file(s) not represented in the graph (top: (none) 20, .jsonl 9, .mdc 1)

## Summary
- 4400 nodes · 13103 edges · 209 communities (171 shown, 38 thin omitted)
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 2689 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ab36c032`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_compare.py
- retrieval_eval.py
- open_retrieval
- pathlib
- test_validate.py
- test_service.py
- production_entries
- test_index.py
- retrieval/test_cli.py
- evaluation/validate.py
- ingestion/config.py
- test_tokenization.py
- HeadingChunker
- load_ingestion_config
- test_lexical_cli.py
- json
- CURRENT_STATE.md current state document
- test_legacy_baseline_snapshot.py
- test_store.py
- Document Model Tests
- 007 — Hybrid Retrieval Requirements
- test_validate_knowledge.py
- test_availability.py
- BGE-M3 Adapter
- test_lexical_standalone.py
- Spec 004 ingestion baseline
- FakeTokenizer
- EmbedderInfo
- test_strategy_eval.py
- Evaluation CLI Tests
- pathlib
- KnowledgeDocument
- test_baseline.py
- evaluation/test_cli.py
- make_document
- SpyIndex
- 009 — Chunking Experiments Requirements
- 008 — Retrieval Fallback Requirements
- test_open_retrieval_bm25_builds_no_embedder_and_no_client
- EvaluationHarnessError
- open_retrieval
- typing
- D055 Default strategy is hybrid (Spec 007)
- Workflow Reviewer
- LocalDocumentRepository
- test_lexical_standalone.py
- test_cli_config.py
- evaluation/cli.py
- make eval-retrieval
- 007 — Hybrid Retrieval Requirements
- asyncio
- HeadingChunker
- DocumentRepository
- FallbackRetriever
- hashing.py
- ingest_dense
- Development Workflow
- retrieval/test_access.py
- build_lexical_index
- json
- Evaluation Phase 1 framework (Spec 006)
- build_security_repository
- Target RAG query flow (User -> FastAPI -> validation -> AccessContext -> LanguageContext -> retrieval -> RRF -> reranker -> context builder -> answerability -> prompt -> Bedrock -> citation validation)
- BgeM3Embedder
- build_security_index
- structure.py
- make retrieve
- CURRENT_STATE.md current state document
- DenseRetriever
- make eval-retrieval
- embedder
- Phase 1 RAG query pipeline
- test_lexical_tokenizer.py
- AccessContext
- Constitution
- Section: Next step
- RetrievalConfigurationError
- AWS target
- embedder
- Spec 005 dense retrieval baseline
- build_tokenizer
- list_eligible_documents
- Ingestion pipeline (Spec 004)
- Retrieval fallback (Spec 008, D056-D062)
- load_retrieval_config
- DenseIndex
- Spec 001 project foundation
- Backend stack
- embedder
- D023 Task-gated agent workflow
- FakeEmbedder
- test_schemas.py
- Roadmap 10 - Grounded generation + citations
- pathlib
- baseline_cli.py
- list_eligible_documents
- test_lexical_build.py
- SpyIndex
- test_fusion.py
- CURRENT_STATE.md
- QdrantIndexStore
- repositories/__init__.py
- 006 Evaluation Framework Tasks
- transcript_metrics.py
- Retrieval package (Spec 005 and 007)
- D035 One filter builder, fail-closed re-check, same path for later fallbacks (Spec 005)
- Qdrant (vector database)
- run_security_evaluation
- LexicalIndexBindingError
- QdrantIndexStore
- test_run_retrieval_evaluation_on_multi_chunk_recursive_index
- test_content_hash.py
- test_recursive_v1_full_gate_on_docker
- test_violation_names_the_document_from_the_error_attribute
- IngestionService
- test_run_retrieval_evaluation_on_multi_chunk_recursive_index
- fusion
- evaluation/cli.py
- IndexSettings
- evaluation/errors.py
- failing_client
- test_status_handling.py
- test_store_integration.py
- load_suite
- QdrantIndexStore
- Baseline runner and result JSON
- test_failed_write_removes_partial_file
- Development Workflow
- test_status_handling.py
- absent_query_languages
- Phase 1 - Production-oriented RAG
- RuntimeSettings
- 007 — Hybrid Retrieval Tasks
- Vocabulary, flashcards and free access
- .search
- test_metrics.py
- Spec 002 document model and repository
- EvaluationConfigurationError
- Evaluation Framework Goal
- Evaluation tooling
- Roadmap 13 - Graceful degradation
- BGE-M3 (initial embedding model)
- Way2Australia AI Platform Master Implementation Plan
- R4 — Freshness check from the repository
- eval-compare
- Payments, account access and support boundaries
- make retrieve
- make test
- Mission
- test_fallback.py
- Way2Australia AI Platform Master Implementation Plan
- Ingestion pipeline (target vs current state diff)
- policy
- policy
- policy
- test_index_contract.py
- open_retrieval / OpenedRetrieval
- lexical/ package (Spec 007)
- Orchestrator State Machine
- way2australia_api/__init__.py
- Project Context README
- test_failed_write_removes_partial_file
- way2australia_rag/__init__.py
- Scripted
- way2australia-core
- Phase 1 analytics event contract
- Spec-driven development workflow
- api/__init__.py
- way2australia_core/access.py
- ChunkerIdentity
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
- Components / boundaries
- Evaluation result format 2.2
- R8 — Evaluation results for degraded runs
- R12 — Real runs (user-owned gate)
- 008 — Retrieval Fallback Requirements
- CountingEmbedder
- ShortResultEmbedder
- task-reviews.md per-spec log format
- policy
- Spec 008 Retrieval Fallback Requirements
- Scripted
- stalled_port
- test_every_path_is_gated_for_every_query
- stalled_port
- DocumentFailure

## God Nodes (most connected - your core abstractions)
1. `DenseIndex` - 107 edges
2. `LocalDocumentRepository` - 101 edges
3. `Strategy` - 76 edges
4. `FakeEmbedder` - 72 edges
5. `FakeTokenizer` - 72 edges
6. `run_retrieval_evaluation()` - 71 edges
7. `open_retrieval()` - 65 edges
8. `HeadingChunker` - 64 edges
9. `DenseRetriever` - 64 edges
10. `EvaluationConfigurationError` - 63 edges

## Surprising Connections (you probably didn't know these)
- `Change log` --references--> `run_retrieval_evaluation()`  [INFERRED]
  .kiro/specs/009-chunking-experiments/requirements.md → packages/rag/src/way2australia_rag/evaluation/retrieval_eval.py
- `T4 review follow-ups (planner amendment 2026-11-02)` --references--> `run_retrieval_evaluation()`  [INFERRED]
  .kiro/specs/009-chunking-experiments/tasks.md → packages/rag/src/way2australia_rag/evaluation/retrieval_eval.py
- `Interfaces / models` --references--> `Chunk`  [INFERRED]
  .kiro/specs/009-chunking-experiments/design.md → packages/rag/src/way2australia_rag/ingestion/chunking.py
- `Acceptance criteria` --references--> `slugify()`  [INFERRED]
  .kiro/specs/009-chunking-experiments/requirements.md → packages/rag/src/way2australia_rag/ingestion/chunking.py
- `Error and failure behavior` --references--> `IngestionConfigurationError`  [INFERRED]
  .kiro/specs/009-chunking-experiments/design.md → packages/rag/src/way2australia_rag/ingestion/errors.py

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

## Communities (209 total, 38 thin omitted)

### Community 0 - "test_compare.py"
Cohesion: 0.06
Nodes (104): R10 — `eval-compare` identity rules (`compare.py`), Implementation, Review, T7 — round 1, User decision, Implementation, Review, T5 — round 1 (+96 more)

### Community 1 - "retrieval_eval.py"
Cohesion: 0.04
Nodes (62): Implementation, Implementation, Implementation, Review, Review, Review, T2 — round 1, T6 — round 1 (+54 more)

### Community 2 - "open_retrieval"
Cohesion: 0.04
Nodes (62): 008 — Retrieval Fallback Design, As-built notes, Data flow, Decisions D056-D062, Design summary, Spec 008 Retrieval Fallback Design, Error and failure behavior, Interfaces / models (+54 more)

### Community 3 - "pathlib"
Cohesion: 0.09
Nodes (5): _parse_sections(), _Section, _split_body(), _split_words(), build_payload()

### Community 4 - "test_validate.py"
Cohesion: 0.13
Nodes (32): edit_rows(), edit_suite(), root(), run(), test_active_golden_without_relevant_documents(), test_candidate_ineligible_document_is_not_unknown(), test_candidate_not_suggested(), test_candidate_referenced_by_suite() (+24 more)

### Community 5 - "test_service.py"
Cohesion: 0.17
Nodes (25): RunReport, doc(), Harness, test_bumped_document_version_updates(), test_changed_body_updates(), test_changed_metadata_field_updates(), test_chunk_shrink_leaves_no_orphan(), test_chunk_too_long_report_has_no_chunk_text() (+17 more)

### Community 6 - "production_entries"
Cohesion: 0.10
Nodes (22): Package / file placement, Implementation, Review, T1 — round 1, T2 — Structure and recursive chunkers, Verification, Chunk, Chunker (+14 more)

### Community 7 - "test_index.py"
Cohesion: 0.14
Nodes (41): IndexBindingError, bound_index(), client(), failing_client(), fake_info(), http_client(), make_settings(), open_index() (+33 more)

### Community 8 - "retrieval/test_cli.py"
Cohesion: 0.16
Nodes (22): _advice_ok(), clean_env(), Factory, indexed(), ingest(), retrieve(), test_bad_args_exit_2_without_client(), test_bad_config_exit_2_without_client() (+14 more)

### Community 9 - "evaluation/validate.py"
Cohesion: 0.12
Nodes (16): Implementation, Review, T1 — round 1, User decision, EvaluationSchemas, _candidate_rules(), problem(), _describe() (+8 more)

### Community 10 - "ingestion/config.py"
Cohesion: 0.13
Nodes (22): Implementation, Implementation, Review, T3 — round 2, User decision, build_chunker(), chunk_token_cap(), chunker_identity() (+14 more)

### Community 11 - "test_tokenization.py"
Cohesion: 0.08
Nodes (22): Components / boundaries, `recursive` v1 (R4), `structure` v1 (R3), Tokenizer (R1), Truncation guard (R2), T1 — Tokenizer and truncation guard, Verification, IngestionConfigurationError (+14 more)

### Community 12 - "HeadingChunker"
Cohesion: 0.12
Nodes (39): basic_suite(), build(), default_eval_extras(), fusion_config(), golden(), _LexicalStub, _metric_chunk(), run() (+31 more)

### Community 13 - "load_ingestion_config"
Cohesion: 0.11
Nodes (17): build_chunker_from_config(), load_ingestion_config(), collection_name(), bge_tokenizer_fixture(), _structure_config(), test_chunker_identity_for_run_uses_selected_embedder(), test_chunker_identity_matches_built_chunker(), test_chunker_identity_matches_for_structure() (+9 more)

### Community 14 - "test_lexical_cli.py"
Cohesion: 0.09
Nodes (42): Implementation, Implementation, Review, Review, T3 — round 2, T3 — round 3, User decision, default_lexical_dir() (+34 more)

### Community 15 - "json"
Cohesion: 0.14
Nodes (24): committed(), edit_jsonl(), lines(), manifest(), problems(), read_lines(), root(), test_candidates_differ_only_in_promoted_as() (+16 more)

### Community 16 - "CURRENT_STATE.md current state document"
Cohesion: 0.13
Nodes (23): RetrievalUnavailableError and availability classification, standalone bm25 without Qdrant or extra (IndexIdentity, freshness), Current goal: Specs 001-008 complete; Spec 008 verified and merged into main (1107b67), plan next spec, Known issue: Qdrant and Hugging Face 5xx not fallback-eligible, Known issue: verify_fresh asyncio.run in event loop, Known issue: Qdrant client lifecycle leak on failed open, Known issue: freshness check rereads every document, Spec 008 retro F3: post-approval amendments lacked change-log lines; resolved 2026-11-01, spec-planner added eight dated lines to requirements.md Change log (+15 more)

### Community 17 - "test_legacy_baseline_snapshot.py"
Cohesion: 0.13
Nodes (15): clean_env(), _Factory, _FixedDatetime, _record_opens(), note(), wrap_func(), inner(), wrap_method() (+7 more)

### Community 18 - "test_store.py"
Cohesion: 0.19
Nodes (16): IndexSettingsMismatchError, client_factory(), client(), make_settings(), snapshot(), store(), test_absent_creates_both_and_writes_settings(), test_differing_settings_refuse_without_writes() (+8 more)

### Community 19 - "Document Model Tests"
Cohesion: 0.09
Nodes (26): client_with_forbidden(), FilterDroppingIndex, test_forbidden_points_are_never_returned(), test_store_dropping_the_filter_fails_closed(), test_formula_shows_the_cap_when_k_reaches_document_count(), build_client(), docs(), guest() (+18 more)

### Community 20 - "007 — Hybrid Retrieval Requirements"
Cohesion: 0.05
Nodes (43): BM25Retriever with SQL access clause, eval-compare identity rules (R10), HybridRetriever (dense leg then BM25 leg, no single-leg fallback), lexical-v1 tokenizer (NFC, ZWJ/ZWNJ dropped, L/N/Mn/Mc token chars, 64-term cap), Result format 2.1 and security result 1.1, config/retrieval.yaml and build_retriever strategy factory, Security gate over dense, bm25 and hybrid, SQLite FTS5 lexical store (derived, git-ignored, bound to dense index) (+35 more)

### Community 21 - "test_validate_knowledge.py"
Cohesion: 0.09
Nodes (49): load(), test_bad_date_fails_loading_naming_document_and_field(), test_seed_corpus_still_loads(), test_valid_date_loads(), _copy_seed(), seed_repository(), test_documents_outside_approved_roots_are_never_loaded(), test_get_document_by_id_and_version() (+41 more)

### Community 22 - "test_availability.py"
Cohesion: 0.08
Nodes (31): R1 — Failure classification (`errors.py`, `availability.py`), T1: Hugging Face error shapes (confirmed 2026-10-29), Testing / evaluation strategy, Review, classify_model_error(), classify_qdrant_error(), _optional_types(), RetrievalUnavailableError (+23 more)

### Community 23 - "BGE-M3 Adapter"
Cohesion: 0.06
Nodes (18): Model Preferences, Agent Skills README, Implementation Checklist, Spec Implementer Skill, task-reviews.md Implementation Block, Design Template, Change Log, Requirements Template (+10 more)

### Community 24 - "test_lexical_standalone.py"
Cohesion: 0.05
Nodes (33): Day-1 Usage, document_manifest.jsonl, golden_public.jsonl, Source-of-Truth Policy, chunking, overlap_tokens, strategy, target_tokens (+25 more)

### Community 25 - "Spec 004 ingestion baseline"
Cohesion: 0.11
Nodes (23): HeadingChunker heading v1 2000-char cap, Embedder Protocol, fake and BGE-M3 adapter, IngestionService change detection, make ingest and config/ingestion.yaml, 17-field PointPayload and UUIDv5 point IDs, QdrantIndexStore with companion settings collection, Heading chunking only synthetic-tested, none of 13 docs has headings, Spec 004 open review findings (T3 F1, T5 F2, T7 F1-F3, T8 F1, retro F1) (+15 more)

### Community 26 - "FakeTokenizer"
Cohesion: 0.11
Nodes (27): Implementation, Review, Review, _char_split(), _merge_pieces(), _merge_word_pieces(), split_at_sentence_ends(), _split_long_unit() (+19 more)

### Community 28 - "test_strategy_eval.py"
Cohesion: 0.14
Nodes (24): eval_world(), lexical_env(), retrieve(), retrieve_world(), run_strategy(), strategy_suite(), test_2_3_keys_for_each_strategy(), test_a_2_2_file_reads_with_strategy_and_lexical() (+16 more)

### Community 29 - "Evaluation CLI Tests"
Cohesion: 0.12
Nodes (31): assert_invalid(), document_fields(), make_document(), test_blank_required_text_is_rejected(), test_document_is_immutable(), test_duplicate_lote_languages_are_rejected(), test_effective_window_must_be_ordered(), test_empty_lote_languages_is_rejected() (+23 more)

### Community 30 - "pathlib"
Cohesion: 0.23
Nodes (10): declared_release_id(), load_suite(), test_declared_release(), test_filtering_in_temporary_suite(), test_invalid_line_names_file_and_line_only(), test_path_escaping_repo_root_refused(), test_real_suite_loads_every_golden_case_and_leaves_evaluation_unchanged(), test_release_id_mismatch_refused() (+2 more)

### Community 31 - "KnowledgeDocument"
Cohesion: 0.07
Nodes (17): AccessScope, ApprovalStatus, LanguageScope, LifecycleStatus, SourceAuthority, _check_language_code(), KnowledgeDocument, DocumentNotFoundError (+9 more)

### Community 32 - "test_baseline.py"
Cohesion: 0.09
Nodes (23): case(), clean_env(), cli_run(), DeviceStub, _git(), run(), seeded(), setup() (+15 more)

### Community 33 - "evaluation/test_cli.py"
Cohesion: 0.17
Nodes (17): load_production_ingestion_config(), clean_env(), index_factory(), real_factory(), run(), test_bad_top_k_exits_2(), test_existing_output_exits_2_before_qdrant(), test_fake_embedder_exits_2_before_qdrant() (+9 more)

### Community 34 - "make_document"
Cohesion: 0.20
Nodes (19): assert_structure_chunks_whitespace_fidelity(), make_document(), structure_chunker(), test_duplicate_sibling_headings_raise(), test_fence_blocks_are_atomic_and_headings_inside_ignored(), test_long_list_splits_only_between_items(), test_main_collision_with_heading_slug(), test_malayalam_paragraph_packs() (+11 more)

### Community 35 - "SpyIndex"
Cohesion: 0.18
Nodes (4): OddIdStore, SpyIndex, broken(), test_violation_names_the_document_from_the_error_attribute()

### Community 36 - "009 — Chunking Experiments Requirements"
Cohesion: 0.07
Nodes (28): 009 — Chunking Experiments Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+20 more)

### Community 37 - "008 — Retrieval Fallback Requirements"
Cohesion: 0.09
Nodes (36): Baseline runner (refuses fake index without --allow-fake; HitRate@k, Recall@k, MRR, p50/p95, min(1,k/N) random expectation), Binding: embedder model ID, revision, vector size, normalization, fake flag and index_version must equal recorded IndexSettings, BM25Retriever(identity, lexical), BM25 statistics (IDF, avg length) computed over every row of a lexical file, build_access_filter (the only filter builder), build_retriever (only place a strategy name becomes a retriever), retrieval_client_factory (Qdrant client with configured timeouts), config/retrieval.yaml (default_strategy hybrid, RRF k 60, depth 50) (+28 more)

### Community 38 - "test_open_retrieval_bm25_builds_no_embedder_and_no_client"
Cohesion: 0.22
Nodes (5): block_model_stack(), fake_lexical(), Raises, test_open_retrieval_bm25_builds_no_embedder_and_no_client(), test_retrieve_cli_bm25_needs_neither_qdrant_nor_the_model()

### Community 39 - "EvaluationHarnessError"
Cohesion: 0.13
Nodes (18): Implementation, Review, T8 — round 1, User decision, EvaluationHarnessError, _lexical_sanity_check(), _open_lexical_sanity(), run_security_evaluation() (+10 more)

### Community 40 - "open_retrieval"
Cohesion: 0.09
Nodes (15): get_health(), HealthResponse, get_request_settings(), get_settings(), Settings, create_app(), isolate_settings_environment(), test_create_app_wires_settings() (+7 more)

### Community 41 - "typing"
Cohesion: 0.09
Nodes (30): 006-candidates.jsonl with 7 suggested rows, make eval-compare, make eval-retrieval, make eval-security hard gate, result 2.2 and served-strategy eval-compare, eval-security five paths, governed suite loader and schemas, make validate-evaluation (+22 more)

### Community 42 - "D055 Default strategy is hybrid (Spec 007)"
Cohesion: 0.12
Nodes (18): make retrieval-baseline legacy frozen, Known issue: git_dirty true in Spec 007 BM25/hybrid result files (user-accepted), Latency hybrid p50 80.3 ms p95 103.6 ms; bm25 p50 0.19 ms, BM25 metrics: 64/69 goldens, MRR 0.7082, Hybrid metrics: 68/69 goldens, MRR 0.9094, Retrieval misses g004 g026 g061, Next step 2: real BGE-M3 baseline committed, Next step 4: Spec 007 T9 strategy comparison and hybrid default (+10 more)

### Community 43 - "Workflow Reviewer"
Cohesion: 0.07
Nodes (25): Considered and rejected, Evidence, F1 — <title> [waste | quality risk | process slip] (confidence: high/medium/low), Findings, New features and tools (official sources, since <date>), Not measurable here, P1 — <title> (addresses F#; expected saving: ...), Proposals (+17 more)

### Community 44 - "LocalDocumentRepository"
Cohesion: 0.13
Nodes (27): LocalDocumentRepository, build(), guest_access(), new_base(), real_queries(), security_result(), seed_repository(), spied() (+19 more)

### Community 45 - "test_lexical_standalone.py"
Cohesion: 0.17
Nodes (20): lexical_index_path(), build_from(), built(), copy_repository(), expected(), first_document_id(), open_it(), remove_document() (+12 more)

### Community 46 - "test_cli_config.py"
Cohesion: 0.14
Nodes (20): clean_env(), _factory(), _run(), test_agrees_with_day1_baseline(), test_builds_exactly_one_embedder_per_run(), test_collection_base_comes_from_environment(), test_config_refuses_missing_or_floating_revision(), test_config_refuses_unknown_field_and_missing_file() (+12 more)

### Community 47 - "evaluation/cli.py"
Cohesion: 0.09
Nodes (25): Implementation, Implementation, Review, Review, T4 — round 1, T5 — round 1, User decision, _authority_map() (+17 more)

### Community 48 - "make eval-retrieval"
Cohesion: 0.06
Nodes (39): AccessContext(role, tenant_id) with blank tenant refused, Future agent folders intentionally not created, apps/api (FastAPI application layer), apps/web (Next.js/TypeScript frontend: recruiter assistant, RAG Lab, engineering views), BgeM3Embedder (optional bge-m3 extra, dense only), core/access.py (Role, frozen AccessContext), D025-D030, D032 ingestion decisions, DocumentRepository Protocol (get_document, list_documents) (+31 more)

### Community 49 - "007 — Hybrid Retrieval Requirements"
Cohesion: 0.09
Nodes (27): optional bge-m3 extra (sentence-transformers, PyTorch), D048 graphify tooling, make experiment CONFIG=... (target; records git commit, release, suite, chunker, embedder, strategy, metrics, latency), make format, Knowledge graph graphify (D048), /graphify . --update (user, once per spec after merge), graphify query / path / explain, graphify update . (+19 more)

### Community 50 - "asyncio"
Cohesion: 0.10
Nodes (29): list_eligible_documents(), LocalRepositoryConfig, _corpus_problems(), manifest_document_count(), assert_matches_snapshot(), assert_recursive_chunks_whitespace_fidelity(), chunks_to_records(), collapse_whitespace() (+21 more)

### Community 51 - "HeadingChunker"
Cohesion: 0.11
Nodes (26): HeadingChunker, _is_word_char(), slugify(), ids(), test_deterministic(), test_duplicate_headings_get_unique_ids_in_order(), test_duplicate_suffix_does_not_collide_with_literal_heading(), test_headings_inside_code_fences_ignored() (+18 more)

### Community 52 - "DocumentRepository"
Cohesion: 0.29
Nodes (7): Roadmap 2 - Document model + repository, KnowledgeDocument, Manifest/schema validation, S3DocumentRepository and external storage, Document manifest, DocumentRepository, LocalDocumentRepository

### Community 53 - "FallbackRetriever"
Cohesion: 0.15
Nodes (14): Fallback authorization invariant (same ResolvedAccess), BM25Retriever (identity, lexical), classify_model_error, classify_qdrant_error, Qdrant client lifecycle gap, FallbackRetriever, Hugging Face error shapes (T1 As-built), HybridRetriever / rrf_fuse (unchanged, fail closed) (+6 more)

### Community 54 - "hashing.py"
Cohesion: 0.09
Nodes (25): build_security_repository(), _fixture_files(), canonical_json(), _canonical_value(), _canonical_value_mapping(), compute_body_sha256(), compute_content_hash(), sha256_hex() (+17 more)

### Community 55 - "ingest_dense"
Cohesion: 0.20
Nodes (11): build_production(), ingest_dense(), open_lexical(), rewrite_settings(), test_bind_does_not_write_to_qdrant(), test_bind_refuses_chunk_set_mismatch_with_counts(), test_bind_refuses_identity_and_chunker_mismatch(), test_bind_refuses_when_qdrant_content_changed() (+3 more)

### Community 56 - "Development Workflow"
Cohesion: 0.10
Nodes (31): Finalized stack: Python/FastAPI, Next.js, Qdrant, SQLite FTS5, BGE-M3, Bedrock, Langfuse, CloudWatch, Terraform ap-south-1, GitHub Actions, agent-skills sync, D001 Python-first backend, D002 RAG as reusable internal package, D003 Knowledge outside RAG package, D005 Documents are truth; chunks are derived, D007 Public-only Phase 1, D008 Language and authorization are independent (+23 more)

### Community 57 - "retrieval/test_access.py"
Cohesion: 0.16
Nodes (15): clean_env(), guest(), payload(), _policy(), test_a_different_policy_changes_both_builders(), test_both_builders_cover_the_same_three_conditions(), test_check_hit_accepts_valid_payload(), test_check_hit_rejects_malformed_payload() (+7 more)

### Community 58 - "build_lexical_index"
Cohesion: 0.10
Nodes (18): Implementation, Review, T3 — round 1, User decision, T3 — `lexical-v1` tokenizer, lexical store and `make index-lexical`, Verification, Lexical identity and per-document freshness (R6), What happens to existing lexical files (user request) (+10 more)

### Community 59 - "json"
Cohesion: 0.10
Nodes (19): chunker, context_prefix, name, overlap_tokens, target_tokens, version, embedder, batch_size (+11 more)

### Community 60 - "Evaluation Phase 1 framework (Spec 006)"
Cohesion: 0.06
Nodes (37): D042-D047, D053, D054 evaluation decisions, Evaluation assets never written by evaluation code (C6); candidates suggested and human-activated, Ingestion eligibility is the only guard against synthetic/unapproved documents; poisoned_public_document is not an authorization case, Evaluation isolation and gates, models.py, suite.py (tolerant typed cases, read-only load_suite), retrieval_eval.py, slices.py, sections.py, schemas.py, validate.py (referencing registry, validate-evaluation checks), Section-level keys <document_id>#<section_id> (+29 more)

### Community 61 - "build_security_repository"
Cohesion: 0.15
Nodes (19): SecurityIndex, clean_env(), copy_fixtures(), _lexical_work_dir(), spy_lexical_path(), wrapper(), strip_forbidden_terms(), test_cli_clause_less_lexical_store_exits_one_naming_strategies() (+11 more)

### Community 62 - "Target RAG query flow (User -> FastAPI -> validation -> AccessContext -> LanguageContext -> retrieval -> RRF -> reranker -> context builder -> answerability -> prompt -> Bedrock -> citation validation)"
Cohesion: 0.11
Nodes (24): Answerability / insufficient-evidence decision, Authorization applied inside each retriever before fusion, never after RRF, reranking or generation, Authorization filter is part of the Qdrant query so unauthorized points never leave the store, Amazon Bedrock generation, check_hit (fail-closed re-check, second line of defense), Citation validation, Context builder (planned), D035 Future fallbacks must take the same ResolvedAccess and call check_hit (+16 more)

### Community 63 - "BgeM3Embedder"
Cohesion: 0.09
Nodes (15): BgeM3Embedder, _group_installed(), OptionalDependencyError, missing(), group_installed(), test_constructing_does_not_load_the_model(), test_device_none_before_load_and_recorded_after(), test_missing_group_at_load_raises_optional_dependency_error() (+7 more)

### Community 64 - "build_security_index"
Cohesion: 0.10
Nodes (12): Acceptance criteria, R4 — Lexical index build (`make index-lexical`), build_security_index(), _canary_points(), _forbidden_payload(), _lexical_forbidden_entries(), point_id(), PointPayload (+4 more)

### Community 65 - "structure.py"
Cohesion: 0.21
Nodes (12): _build_prefix(), _compose_chunk(), DuplicateSectionError, _is_list_item(), _join_blocks(), _pack_blocks(), body_fits(), _parse_blocks() (+4 more)

### Community 66 - "make retrieve"
Cohesion: 0.10
Nodes (21): docker compose up -d / down (local Qdrant), Environment: QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION_BASE, W2A_TENANT_ID, Fake embedder needs throwaway QDRANT_COLLECTION_BASE, make index-lexical, make ingest, INGEST_ARGS (--embedder {bge_m3,fake}, --config), ingest exit codes 0 success, 1 document failed, 2 refusal, Ingest summary lines (index:, added/updated/unchanged/deleted, ERROR lines) (+13 more)

### Community 67 - "CURRENT_STATE.md current state document"
Cohesion: 0.09
Nodes (36): build_retriever, make index-lexical, lexical package: lexical-v1 tokenizer, FTS5 store, builder, CURRENT_STATE.md current state document, Evaluation Suite includes goldens, refusal, multilingual, security, regression, Phase 2 Knowledge Release workflow designed not implemented, Public/guest retrieval only in Phase 1; English + Malayalam, Known issue: BM25 statistics corpus-wide per file; needs per-scope files for roles (+28 more)

### Community 68 - "DenseRetriever"
Cohesion: 0.07
Nodes (50): 007 — Hybrid Retrieval Design, Alternatives / deferred decisions, As-built notes, Data flow, Design summary, Error and failure behavior, Interfaces / models, Observability (+42 more)

### Community 69 - "make eval-retrieval"
Cohesion: 0.12
Nodes (17): --allow-fake (plumbing only, never a recorded baseline), make retrieval-baseline (legacy, frozen Spec 005 producer), BASELINE_ARGS (--embedder, --allow-fake, --top-k, --suite, --release, --output, --config), Baseline metrics HitRate@5, random expectation min(1,5/N), Recall@5, MRR, p50/p95 latency, experiments/results/retrieval-baseline-<index_version>-<UTC>.json, never overwritten, D036 binding rules, D053 result 2.1, eval-retrieval exit 0 or 2 (+9 more)

### Community 70 - "embedder"
Cohesion: 0.11
Nodes (17): chunker, context_prefix, name, overlap_tokens, target_tokens, version, embedder, batch_size (+9 more)

### Community 71 - "Phase 1 RAG query pipeline"
Cohesion: 0.12
Nodes (16): Authorization model (guest/public), Small documents and chunking strategy, Citation strategy (backend-owned validation), FAQ-aware retrieval experiment, Graceful degradation, Hybrid retrieval (dense + BM25 + RRF), Production knowledge corpus, Poisoned public document fixture (+8 more)

### Community 72 - "test_lexical_tokenizer.py"
Cohesion: 0.12
Nodes (14): _is_token_char(), QueryTerms, tokenize(), test_business_008_words_stay_whole(), test_deterministic(), test_english_punctuation_digits_and_case(), test_golden_file_is_the_source_of_the_pins(), test_golden_queries_pin_exact_tokens() (+6 more)

### Community 73 - "AccessContext"
Cohesion: 0.13
Nodes (13): AccessContext, test_blank_tenant_refused(), test_empty_tenant_refused(), test_no_language_or_scope_fields(), test_tenant_is_stripped(), test_unknown_role_refused(), test_valid_context_is_frozen(), live_client() (+5 more)

### Community 74 - "Constitution"
Cohesion: 0.25
Nodes (19): metadata(), record(), run(), test_duplicate_document_id_rejected(), test_duplicate_document_version_rejected(), test_frontmatter_errors(), test_frontmatter_missing_required_field(), test_frontmatter_parsing_keeps_dates_as_strings() (+11 more)

### Community 75 - "Section: Next step"
Cohesion: 0.15
Nodes (12): Atomic publish and rollback, Phase 2 audit trail, Controlled document-change workflow (Release Candidate), Evaluation governance states, Evaluation slices, Evaluation Suite (public-eval-v1), Generation metrics, Evaluation impact detection (+4 more)

### Community 76 - "RetrievalConfigurationError"
Cohesion: 0.05
Nodes (60): R11 — Security gate (`security_index.py`, `security_eval.py`), R7 — Fusion and `HybridRetriever` (`retrieval/fusion.py`, `hybrid.py`), R8 — Strategy and config (`retrieval/strategy.py`, `config/retrieval.yaml`), Acceptance criteria, Implementation, Implementation, Review, Review (+52 more)

### Community 77 - "AWS target"
Cohesion: 0.08
Nodes (30): Roadmap 11 - Observability, Langfuse traces, Stage latency, model/tokens/cost, release/config IDs, Full agent orchestration (avoided), Intentionally avoided choices, AWS target, Bedrock Agents / AgentCore for Phase 1 (avoided), Bedrock Knowledge Bases as core RAG (avoided) (+22 more)

### Community 78 - "embedder"
Cohesion: 0.14
Nodes (13): chunker, max_chunk_chars, name, version, embedder, batch_size, fake_vector_size, model_id (+5 more)

### Community 79 - "Spec 005 dense retrieval baseline"
Cohesion: 0.18
Nodes (15): AccessContext, Role, W2A_TENANT_ID, BGE-M3 device mps not pinned (D038), Spec 005 retrospective findings F3-F5, Spec 005 dense retrieval baseline, Spec 005 status: verified 2026-10-23 merged b33462e, AccessContext and Role, D033 AccessContext and Role live in core (Spec 005), D034 W2A_TENANT_ID is a server setting (Spec 005) (+7 more)

### Community 80 - "build_tokenizer"
Cohesion: 0.09
Nodes (25): Implementation, Implementation, Implementation, Implementation, Implementation, Review, Review, Review (+17 more)

### Community 81 - "list_eligible_documents"
Cohesion: 0.18
Nodes (16): eligible_ids(), IgnoresQueryRepository, make_document(), test_active_approved_public_document_is_eligible(), test_language_filter_narrows_eligible_documents_only(), test_language_metadata_does_not_broaden_access(), test_local_repository_applies_the_policy_query(), test_non_active_lifecycle_is_excluded() (+8 more)

### Community 82 - "Ingestion pipeline (Spec 004)"
Cohesion: 0.11
Nodes (18): default_strategy, fusion, candidate_depth, k, method, weights, qdrant, connect_timeout_s (+10 more)

### Community 83 - "Retrieval fallback (Spec 008, D056-D062)"
Cohesion: 0.08
Nodes (35): bm25 builds no embedder and no Qdrant client, classify_model_error, classify_qdrant_error, D056-D062 fallback decisions, D057 Fallback eligibility classification, D058 Fallback policy per query, D061 Marking and evaluation of fallback, D062 5xx not eligible (+27 more)

### Community 84 - "load_retrieval_config"
Cohesion: 0.17
Nodes (17): Implementation, Review, T9 — round 1, User decision, test_roles_match_policy_file(), load_retrieval_config(), test_build_retriever_converts_a_string_value_and_refuses_unknown(), test_build_retriever_maps_each_strategy() (+9 more)

### Community 85 - "DenseIndex"
Cohesion: 0.07
Nodes (42): Decisions resolved before drafting, LexicalRow, DenseIndex, build(), dense_fixture(), DroppedClauseIndex, guest(), pub() (+34 more)

### Community 86 - "Spec 001 project foundation"
Cohesion: 0.09
Nodes (23): Local Qdrant Docker Compose service, Make command surface (setup, lint, typecheck, test, verify), Python monorepo foundation (FastAPI, uv, Makefile), Spec 001 Project Foundation (implemented), Completion: retrospective, Spec-Review commit, merge, verified status, Spec orchestrator loop (route, role subagents, user approval, merge), GET /health endpoint, make setup (+15 more)

### Community 87 - "Backend stack"
Cohesion: 0.09
Nodes (23): Lexical file is a derived artifact, one per collection, bound by identity and chunk digest, Source documents are truth; chunks, embeddings, sparse entries, Qdrant points and preview indexes are derived artifacts, Backend stack, Derived retrieval index in Qdrant, FastAPI, httpx, jsonschema, Relational metadata/workflow/audit database (+15 more)

### Community 88 - "embedder"
Cohesion: 0.14
Nodes (13): chunker, max_chunk_chars, name, version, embedder, batch_size, fake_vector_size, model_id (+5 more)

### Community 89 - "D023 Task-gated agent workflow"
Cohesion: 0.12
Nodes (16): allowed_scopes, current_release, default_role, implemented_roles, allowed_scopes, allowed_scopes, roles, admin (+8 more)

### Community 90 - "FakeEmbedder"
Cohesion: 0.15
Nodes (14): FakeEmbedder, _cosine_to_query(), _text_with_score_below(), __init__(), test_conforms_to_protocol(), test_declared_vector_size(), test_default_size_is_64(), test_fake_device_is_none() (+6 more)

### Community 91 - "test_schemas.py"
Cohesion: 0.13
Nodes (9): load_schemas(), _suite_paths(), validate_evaluation(), test_existing_schema_is_referenced_not_copied(), test_missing_schema_is_configuration_error(), test_per_type_required_field_enforced(), test_schema_files_are_valid_draft_2020_12(), test_valid_rows_pass() (+1 more)

### Community 92 - "Roadmap 10 - Grounded generation + citations"
Cohesion: 0.13
Nodes (15): Answerability and insufficient-evidence response, Authorization regression and staff canary, Docker, Terraform, EC2, ECR, CloudWatch, IAM, Bedrock, Bedrock Runtime (roadmap), BGE-M3 (roadmap), Citation manipulation tests and input/cost limits, Backend-owned citation validation, Roadmap 4 - Dense retrieval baseline (+7 more)

### Community 93 - "pathlib"
Cohesion: 0.25
Nodes (9): apps/api, apps/web, CloudWatch, Future multimodal mock-test evaluation, Langfuse tracing, packages/core, packages/observability, packages/rag (+1 more)

### Community 94 - "baseline_cli.py"
Cohesion: 0.08
Nodes (22): default_output_path(), write_document(), _parser(), IngestionError, _parser(), guest_access(), BaselineResult, check_output_free() (+14 more)

### Community 95 - "list_eligible_documents"
Cohesion: 0.10
Nodes (6): _document_ids(), collect(), _eligible_document_versions(), DocumentQuery, DocumentRepository, EligibilityPolicy

### Community 96 - "test_lexical_build.py"
Cohesion: 0.16
Nodes (22): collect(), test_verify_fresh_refuses_chunker_name_mismatch(), identity(), payload(), repository(), synthetic_entries(), build(), test_atomic_replace_keeps_old_file_after_failure() (+14 more)

### Community 97 - "SpyIndex"
Cohesion: 0.15
Nodes (17): Admin content management, Agent capabilities only where they solve a real product problem, Audit trail, Basic analytics, Candidate evaluation, Change impact analysis, Content hashing, Evaluation Governance (keep/modify/deprecate/replace) (+9 more)

### Community 98 - "test_fusion.py"
Cohesion: 0.19
Nodes (11): chunk(), test_both_legs_empty(), test_duplicate_in_a_leg_counts_best_rank_only(), test_empty_leg_keeps_the_other_order(), test_equal_scores_and_ranks_break_by_point_id(), test_first_seen_chunk_is_kept(), test_fusion_config_validation(), test_fusion_module_has_no_authorization_or_io_surface() (+3 more)

### Community 99 - "CURRENT_STATE.md"
Cohesion: 0.13
Nodes (14): interval, retries, start_period, test, timeout, container_name, healthcheck, image (+6 more)

### Community 101 - "repositories/__init__.py"
Cohesion: 0.06
Nodes (30): DocumentRepositoryError, DocumentValidationError, DuplicateDocumentError, ManifestValidationError, split_frontmatter(), _StringDateLoader, normalize_body(), document_fields() (+22 more)

### Community 102 - "006 Evaluation Framework Tasks"
Cohesion: 0.11
Nodes (20): Local multilingual BGE reranker, BM25 via FTS5 bm25(), Derived local lexical file per collection, Device not pinned, recorded in results (D038), Embeddings, Deterministic fake embedder, Fusion, Lexical store (+12 more)

### Community 103 - "transcript_metrics.py"
Cohesion: 0.20
Nodes (10): analyse(), category(), command_kinds(), executed_text(), expand(), main(), parse_time(), render() (+2 more)

### Community 104 - "Retrieval package (Spec 005 and 007)"
Cohesion: 0.17
Nodes (10): graphify skill pointer, Spec 002 task review log (T3-T9), spec/NNN branch and Spec-Task trailers, spec-implementer skill (one task per run), spec-orchestrator skill, spec-planner skill, spec-reviewer retrospective skill, Task-gated agent workflow loop (+2 more)

### Community 105 - "D035 One filter builder, fail-closed re-check, same path for later fallbacks (Spec 005)"
Cohesion: 0.13
Nodes (26): DenseIndex, build_access_filter, check_hit, DenseRetriever, FallbackRetriever and open_retrieval wiring (merged 1107b67), make retrieve guest/public CLI, Strategy Protocol, BM25Retriever, rrf_fuse, HybridRetriever, Known issue: no circuit breaker, ~3 s per query with hanging Qdrant, Spec 008 retro F1: open-time outage makes BM25 serve whole run, Spec 008 retro F4: duplicated standalone open wiring, Next step 7: Spec 008 hand-off carry-overs for HTTP route spec (circuit breaker, startup policy, 5xx, freshness cost, async check, client lifecycle) (+18 more)

### Community 106 - "Qdrant (vector database)"
Cohesion: 0.14
Nodes (13): Authorization metadata (access_scope, owner_user_id, tenant_id), Engineering Conventions, IDs and versions conventions, Knowledge files with provenance, Language metadata (content_language, lote_languages), Logging and tracing hygiene, Domain naming terms, Prompts as versioned assets (+5 more)

### Community 107 - "run_security_evaluation"
Cohesion: 0.25
Nodes (4): DroppedClauseLexical, test_a_dropped_lexical_clause_names_the_four_lexical_paths(), test_a_lexical_store_without_the_clause_fails_bm25_and_hybrid(), __init__()

### Community 108 - "LexicalIndexBindingError"
Cohesion: 0.19
Nodes (8): R4/R5 — Lexical store (`lexical/store.py`, `lexical/build.py`), R4 — Freshness from the repository (`lexical/freshness.py`), LexicalIndexBindingError, LexicalSettings, _read_only_connection(), test_lexical_1_0_fixture_refused(), test_verify_fresh_refuses_added_document(), test_document_count_honors_the_access_clause()

### Community 109 - "QdrantIndexStore"
Cohesion: 0.38
Nodes (7): QdrantIndexStore, test_replace_and_delete_flows(), make_points(), test_delete_documents(), test_read_state_paginates(), test_read_state_round_trip(), test_replace_shrinking_leaves_no_orphan()

### Community 110 - "test_run_retrieval_evaluation_on_multi_chunk_recursive_index"
Cohesion: 0.20
Nodes (8): UnanswerableCase, deterministic_clock(), equivalence_suite(), run_equivalence(), chunks_per_document_dense(), unanswerable(), unanswerable(), test_dense_2_2_equals_the_pre_change_2_0_result()

### Community 111 - "test_content_hash.py"
Cohesion: 0.15
Nodes (12): Approved packages, pricing and validity, Six approved packages and prices, 60-day package validity, 24-hour cancellation notice, Personal coaching package, 60-minute coaching session on Google Meet, Individual coaching and live appointments, Mock assessments, scoring, feedback and review windows (+4 more)

### Community 112 - "test_recursive_v1_full_gate_on_docker"
Cohesion: 0.21
Nodes (5): select_security_queries(), delete_security_index(), test_the_security_index_records_a_fake_embedder_and_is_removed(), test_recursive_v1_full_gate_on_docker(), test_server_filter_keeps_every_forbidden_point_out()

### Community 113 - "test_violation_names_the_document_from_the_error_attribute"
Cohesion: 0.18
Nodes (12): AGENTS.md Project Rules, DocumentRepository Abstraction, Evaluation Governance Rules, Language Separation Rules, Phase 1 Scope, Task-gated Spec Loop, CLAUDE.md Project Instructions, graphify Knowledge Graph Rules (+4 more)

### Community 114 - "IngestionService"
Cohesion: 0.24
Nodes (5): IngestionService, _reason(), test_collection_with_1_0_settings_still_binds(), test_recursive_ingest_and_idempotent_rerun(), test_seed_corpus_retrieval_under_guest_access()

### Community 115 - "test_run_retrieval_evaluation_on_multi_chunk_recursive_index"
Cohesion: 0.24
Nodes (8): build_index_settings(), test_run_retrieval_evaluation_on_multi_chunk_recursive_index(), build_lexical(), leg_order(), make_world(), production_chunker(), test_hybrid_leg_ranks_beyond_top_k_are_real_document_ranks(), make_payload()

### Community 116 - "fusion"
Cohesion: 0.20
Nodes (12): English, Malayalam and mixed queries, FAQ-aware retrieval/indexing, Roadmap 7 - Chunking experiments, Roadmap 8 - Multilingual retrieval, Language applicability handling, Parent-heading context and order-independent section_ids, Recursive chunking baseline, Optional semantic chunking (+4 more)

### Community 117 - "evaluation/cli.py"
Cohesion: 0.21
Nodes (12): Branching and commits (spec/NNN, Spec-Task trailer), Development Workflow, Multi-agent handoff, Implementation rule: BLOCKED spec issue, Phase discipline, Protected source-of-truth data, Required spec-reviewer retrospective, Agent skills (orchestrator, planner, implementer, task-reviewer, spec-reviewer) (+4 more)

### Community 118 - "IndexSettings"
Cohesion: 0.14
Nodes (4): chunker_for_result(), IndexSettings, read_index_settings(), test_index_settings_1_0_upgrades_in_memory()

### Community 119 - "evaluation/errors.py"
Cohesion: 0.11
Nodes (15): active_registry_languages(), aggregate(), _mean(), slice_by(), source_authority_key(), row(), test_absent_languages_from_a_temp_registry(), test_missing_registry_section_is_a_configuration_error() (+7 more)

### Community 120 - "failing_client"
Cohesion: 0.18
Nodes (8): content-hash-v1 (sole change-detection signal), LocalDocumentRepository, Document manifest and JSON Schema validation, make validate-knowledge, persona_scope spec defect (F2), PointPayload (17 fields), build_access_filter (single filter builder), check_hit (fail-closed re-check)

### Community 121 - "test_status_handling.py"
Cohesion: 0.20
Nodes (8): Adding a New Language Guide, language_registry.json, Public Assistant Content Boundaries, access_scope, content_language, Knowledge Schema and Metadata, language_scope, lote_languages

### Community 122 - "test_store_integration.py"
Cohesion: 0.36
Nodes (7): _keyword_indexed(), live_client(), store(), test_collection_has_keyword_indexes_and_cosine_dense_vector(), test_empty_without_settings_recreates_dropped_indexes(), test_repeated_create_payload_index_is_harmless(), test_settings_storage_and_refusal()

### Community 123 - "load_suite"
Cohesion: 0.19
Nodes (15): load_suite(), live_suite_rows(), golden_count(), suite_with_statuses(), test_exclusions_counted_by_status(), test_suggested_never_returned(), copy_suite(), test_access_context_is_loaded_but_ignored() (+7 more)

### Community 124 - "QdrantIndexStore"
Cohesion: 0.24
Nodes (10): BgeM3Embedder (optional extra, pinned revision), Embedder Protocol and FakeEmbedder, HeadingChunker and slugify rule, IndexSettings and mismatch refusal, IngestionService, UUIDv5 point identity (INGESTION_NAMESPACE), QdrantIndexStore, Companion -settings collection (+2 more)

### Community 125 - "Baseline runner and result JSON"
Cohesion: 0.40
Nodes (5): Baseline runner and result JSON, Read-only golden loader (stand-in for Spec 006), Document-level metrics (HitRate, Recall, MRR, random k/N), safe_text output sanitizer, Real BGE-M3 baseline (user-owned, pending)

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

### Community 132 - "007 — Hybrid Retrieval Tasks"
Cohesion: 0.22
Nodes (8): 007 — Hybrid Retrieval Tasks, Out of this spec, T1 — Evaluation Suite `public-eval-v2`, T7 — `eval-compare` identity rules, T9 — Strategy comparison and default-strategy decision (user-owned gate), Verification, Verification, Verification

### Community 133 - "Vocabulary, flashcards and free access"
Cohesion: 0.25
Nodes (7): Typed runtime Settings (Pydantic Settings), EligibilityPolicy / GUEST_PUBLIC_POLICY, Security fixtures (valid but ineligible), config/ingestion.yaml and RuntimeSettings, AccessContext and Role (core), resolve_access / ResolvedAccess, W2A_TENANT_ID server tenant setting

### Community 134 - ".search"
Cohesion: 0.25
Nodes (8): Phase 2 basic analytics, Assistant behavior rules, Product Context, English and Malayalam language scope, Future personas, Phase 1 guest-only scope, Way2Australia AI product, Source-of-truth priorities

### Community 135 - "test_metrics.py"
Cohesion: 0.25
Nodes (7): chunk(), test_dedupe_keeps_first_rank(), test_hit_rate_and_cutoff(), test_percentile_nearest_rank(), test_random_hit_rate_cap_and_minimum(), test_recall_with_several_relevant(), test_reciprocal_rank()

### Community 136 - "Spec 002 document model and repository"
Cohesion: 0.16
Nodes (15): Pydantic document models and enums, EligibilityPolicy for guest/public, LocalDocumentRepository with manifest schema validation, make validate-knowledge, Spec 002 decisions made before approval (content_hash, fixtures, validate-knowledge), Seed data status: 13 public docs, evaluation datasets, security fixtures, Spec 002 retrospective findings F1-F6, Spec 002 document model and repository (+7 more)

### Community 137 - "EvaluationConfigurationError"
Cohesion: 0.09
Nodes (22): EvaluationConfigurationError, CaseBase, CaseStatus, DatasetRef, DatasetType, GoldenCase, LoadedSuite, SecurityCase (+14 more)

### Community 138 - "Evaluation Framework Goal"
Cohesion: 0.39
Nodes (8): NAATI CCL test format, scoring and results, NAATI CCL test, Deduction-based assessment, Begin interpreting within five seconds of chime, NAATI, CCL is not professional interpreter certification, Pass requirement 63/90 overall and 29/45 per dialogue, Results within 4-6 weeks

### Community 139 - "Evaluation tooling"
Cohesion: 0.36
Nodes (8): Custom retrieval metrics (plain Python), DeepEval (not yet a dependency), Evaluation tooling, Generation/e2e metrics (correctness, faithfulness, citations, refusal), GitHub Actions, LLM-as-judge not sole source of truth, Primary retrieval metrics (Recall@5, MRR, HitRate@5), pytest

### Community 140 - "Roadmap 13 - Graceful degradation"
Cohesion: 0.32
Nodes (8): Deferred serving concerns (circuit breaker, startup policy, Qdrant 5xx D062), Deduplication, context budgeting, evidence ordering, Dense to BM25 degradation, Roadmap 9 - Reranking + context building, Roadmap 13 - Graceful degradation, Qdrant failure to SQLite FTS5, Reranker failure to hybrid results, Spec 008 early delivery (D056)

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

### Community 146 - "make retrieve"
Cohesion: 0.10
Nodes (22): results.py, compare.py (reads 1.0, 2.0, 2.1; quality gate; identity refusals), make retrieve, D061 fallback marking, eval-compare exit 0 pass, 1 gate failure, 2 refusal, WARNING flipped hit->miss / miss->hit lines (<case_id> v<case_version>), Gate: fail if more than 1 fewer hit cases or MRR drop above 1/n, Fallback path latency marked 'includes failed dense attempt' (informational), Not-comparable refusals (suite, case sets, top_k, fake, collection, index_version, embedder, lexical index, mixed served strategies) (+14 more)

### Community 147 - "make test"
Cohesion: 0.33
Nodes (6): 006 Evaluation Framework Design, Decision Brief Q1-Q10, 006 Evaluation Framework Requirements, Evaluation Framework Goal, 006 Spec Retrospective Review, Retrospective Round 1 PASS

### Community 148 - "Mission"
Cohesion: 0.33
Nodes (5): Evaluation case_id and case_version, Versioning and Releases, document_id and document_version, Phase 2 Knowledge Release Candidates, Release seed-v1

### Community 149 - "test_fallback.py"
Cohesion: 0.12
Nodes (26): Review, FallbackReason, FallbackRetriever, access(), client_at(), closed_port(), Fallback, open_hybrid() (+18 more)

### Community 150 - "Way2Australia AI Platform Master Implementation Plan"
Cohesion: 0.25
Nodes (8): Way2Australia AI Platform Master Implementation Plan, Phase 1 Definition of Done, Phase 1 Scope (public/guest RAG), Phase 2 Knowledge Operations, Recruiter / portfolio story, Project Mission, S3DocumentRepository, Seven-day Phase 1 execution plan

### Community 151 - "Ingestion pipeline (target vs current state diff)"
Cohesion: 0.22
Nodes (10): DocumentRepository Protocol (async), KnowledgeDocument model, Spec 002 retrospective round 1, Spec 002 Document model and repository (verified), Ingestion pipeline (target vs current state diff), Spec 004 retrospective round 1 (PASS), Spec 004 Ingestion baseline (verified), retrieval package (dense baseline) (+2 more)

### Community 152 - "policy"
Cohesion: 0.40
Nodes (4): eval-compare, Quality Gate (1 case, MRR 1/n), Release Candidates Need Compare-shared-cases, T6 eval-compare

### Community 153 - "policy"
Cohesion: 0.40
Nodes (4): Public contact channels, Payments, account access and support boundaries, Payments non-refundable, One active login session

### Community 154 - "policy"
Cohesion: 0.70
Nodes (5): Home Affairs credentialled community language points, 5 points for credentialled community language, Australian Department of Home Affairs, Refer to Home Affairs or migration adviser, No automatic visa eligibility from passing CCL

### Community 155 - "test_index_contract.py"
Cohesion: 0.13
Nodes (16): compare(), mismatch_message(), base_settings(), test_authorization_and_language_fields_are_separate(), test_build_index_settings_records_embedder_and_chunker(), test_build_payload_copies_document_and_chunk(), test_collection_name_derivation(), test_compare_equal_and_ignores_hash_contract() (+8 more)

### Community 156 - "open_retrieval / OpenedRetrieval"
Cohesion: 0.29
Nodes (7): open_retrieval / OpenedRetrieval, Open-time fallback lasts for the run, Qdrant connect/query timeouts (config 1.1), retrieval_client_factory, Review F1: open-time outage serves whole run, Review F4: duplicated standalone open wiring, Review F5: bind_to scroll fallback untested end to end

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

### Community 167 - "api/__init__.py"
Cohesion: 0.67
Nodes (3): Frontend stack, Next.js, TypeScript

### Community 169 - "ChunkerIdentity"
Cohesion: 0.08
Nodes (25): 009 — Chunking Experiments Design, Alternatives / deferred decisions, As-built notes, Carry-over clean-ups (R11), Chunker identity, settings and configuration (R5), Cross-index comparison (R8), Data flow, Design summary (+17 more)

### Community 170 - "tests/evaluation/__init__.py"
Cohesion: 0.67
Nodes (3): Canonical document metadata, Chunk metadata, Source authority precedence

### Community 191 - "_security"
Cohesion: 0.33
Nodes (3): security_document(), security_run_record(), SecurityReport

### Community 192 - "Components / boundaries"
Cohesion: 0.33
Nodes (6): Components / boundaries, R12 — Docker test, R1 — Suite v2, R3 — Tokenizer `lexical-v1` (`lexical/tokenizer.py`), R4 — `make index-lexical` (`lexical/cli.py`), R9 — Result format 2.1

### Community 193 - "Evaluation result format 2.2"
Cohesion: 0.33
Nodes (6): eval-compare by served strategy (mixed refused), Latency grouped by served path, Evaluation result format 2.2, RetrievalResult marking (requested_strategy, fallback_reason), Review F2: result 2.2 does not record fallback stage, T4 deviations (header only on fallback, requested_strategy by wrapper)

### Community 194 - "R8 — Evaluation results for degraded runs"
Cohesion: 0.40
Nodes (6): Acceptance criteria, Acceptance criteria, R8 — Evaluation results for degraded runs, R9 — `eval-compare` by served strategy, index_settings=None refusal rule (T3 F2), T5 Result 2.2 and eval-compare by served strategy

### Community 195 - "R12 — Real runs (user-owned gate)"
Cohesion: 0.33
Nodes (6): Acceptance criteria, R12 — Real runs (user-owned gate), Spec 007 BM25 and hybrid reference results, T7 real runs: fallback-only and Qdrant-up results, T7 — Real runs (user-owned gate), Verification

### Community 196 - "008 — Retrieval Fallback Requirements"
Cohesion: 0.12
Nodes (17): 008 — Retrieval Fallback Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Spec 008 taken ahead of roadmap 7 (chunking), Decisions resolved before drafting (+9 more)

### Community 199 - "task-reviews.md per-spec log format"
Cohesion: 0.50
Nodes (4): task-reviewer skill (read-only), task-reviews.md per-spec log format, Spec 004 task review log (T1-T9), Spec 005 task review log (T1-T7)

### Community 201 - "Spec 008 Retrieval Fallback Requirements"
Cohesion: 0.50
Nodes (4): Change log, Spec 008 Retrieval Fallback Requirements, Spec 008 Retrospective Review round 1, Review F3: missing change-log lines (resolved)

### Community 204 - "test_every_path_is_gated_for_every_query"
Cohesion: 0.29
Nodes (4): test_every_path_is_gated_for_every_query(), counting(), test_the_gate_runs_all_three_strategies_on_v2(), counting()

## Ambiguous Edges - Review These
- `Task-gated agent workflow loop` → `graphify skill pointer`  [AMBIGUOUS]
  .claude/CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **380 isolated node(s):** `way2australia-api`, `way2australia-core`, `way2australia-observability`, `way2australia-rag`, `way2australia` (+375 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1334 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **38 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Change log` connect `DenseRetriever` to `test_compare.py`, `retrieval_eval.py`, `open_retrieval`, `EvaluationHarnessError`, `D055 Default strategy is hybrid (Spec 007)`, `RetrievalConfigurationError`, `test_lexical_cli.py`, `007 — Hybrid Retrieval Requirements`?**
  _High betweenness centrality (0.086) - this node is a cross-community bridge._
- **Are the 80 inferred relationships involving `DenseIndex` (e.g. with `Design summary` and `Decisions resolved before drafting`) actually correct?**
  _`DenseIndex` has 80 INFERRED edges - model-reasoned connections that need verification._
- **What connects `way2australia-api`, `way2australia-core`, `way2australia-observability` to the rest of the system?**
  _380 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_compare.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05554802872239534 - nodes in this community are weakly interconnected._
- **Why does `D055 Default strategy is hybrid (Spec 007)` connect `D055 Default strategy is hybrid (Spec 007)` to `CURRENT_STATE.md current state document`, `typing`, `D035 One filter builder, fail-closed re-check, same path for later fallbacks (Spec 005)`, `Ingestion pipeline (Spec 004)`, `Development Workflow`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Are the 35 inferred relationships involving `LocalDocumentRepository` (e.g. with `Dependencies` and `Design summary`) actually correct?**
  _`LocalDocumentRepository` has 35 INFERRED edges - model-reasoned connections that need verification._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Task-gated agent workflow loop` and `graphify skill pointer`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._