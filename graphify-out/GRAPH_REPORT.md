# Graph Report - way2australia  (2026-11-03)

## Corpus Check
- 287 files · ~312,401 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 32 file(s) not represented in the graph (top: (none) 20, .jsonl 9, .mdc 1)

## Summary
- 4384 nodes · 13064 edges · 196 communities (162 shown, 34 thin omitted)
- Extraction: 80% EXTRACTED · 20% INFERRED · 0% AMBIGUOUS · INFERRED: 2670 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9d1c12c3`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_compare.py
- retrieval_eval.py
- open_retrieval
- chunking.py
- test_validate.py
- test_service.py
- Chunk
- test_index.py
- real_hybrid
- evaluation/validate.py
- IngestionConfigurationError
- 009 — Chunking Experiments Design
- HeadingChunker
- test_config_schema_11.py
- test_lexical_cli.py
- json
- CURRENT_STATE.md current state document
- test_legacy_baseline_snapshot.py
- Index Binding Errors
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
- typing
- SpyIndex
- 009 — Chunking Experiments Requirements
- 008 — Retrieval Fallback Requirements
- conftest.py
- EvaluationHarnessError
- open_retrieval
- typing
- D055 Default strategy is hybrid (Spec 007)
- Workflow Reviewer
- run_security_evaluation
- test_lexical_standalone.py
- test_cli_config.py
- FilterDroppingIndex
- make eval-retrieval
- 007 — Hybrid Retrieval Requirements
- list_eligible_documents
- HeadingChunker
- DocumentRepository
- FallbackRetriever
- build
- LocalDocumentRepository
- Development Workflow
- retrieval/test_access.py
- lexical/store.py
- json
- make eval-security
- build_security_repository
- Target RAG query flow (User -> FastAPI -> validation -> AccessContext -> LanguageContext -> retrieval -> RRF -> reranker -> context builder -> answerability -> prompt -> Bedrock -> citation validation)
- BgeM3Embedder
- security_index.py
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
- embedder
- Spec 005 dense retrieval baseline
- Spec 009 — Task reviews
- list_eligible_documents
- Ingestion pipeline (Spec 004)
- Retrieval fallback (Spec 008, D056-D062)
- security_eval.py
- DenseIndex
- Spec 001 project foundation
- Backend stack
- embedder
- D023 Task-gated agent workflow
- FakeEmbedder
- test_schemas.py
- Roadmap 10 - Grounded generation + citations
- pathlib
- evaluation/cli.py
- test_store_integration.py
- ingest_dense
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
- ChunkerIdentity
- make eval-retrieval
- test_run_retrieval_evaluation_on_multi_chunk_recursive_index
- test_content_hash.py
- CountingStore
- test_violation_names_the_document_from_the_error_attribute
- pytest
- fusion
- evaluation/cli.py
- make_document
- evaluation/errors.py
- failing_client
- test_status_handling.py
- ARCHITECTURE.md
- EvaluationConfigurationError
- QdrantIndexStore
- Baseline runner and result JSON
- test_failed_write_removes_partial_file
- Development Workflow
- test_status_handling.py
- absent_query_languages
- Phase 1 - Production-oriented RAG
- RuntimeSettings
- Vocabulary, flashcards and free access
- .search
- Spec 002 document model and repository
- suite.py
- Evaluation Framework Goal
- make validate-evaluation
- Intentionally avoided choices
- BGE-M3 (initial embedding model)
- Way2Australia AI Platform Master Implementation Plan
- eval-compare
- Payments, account access and support boundaries
- make retrieve
- make test
- Mission
- test_fallback.py
- Spec 004 retrospective round 1 (PASS)
- policy
- policy
- policy
- IndexSettings
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
- Evaluation tooling
- R12 — Real runs (user-owned gate)
- R8 — Evaluation results for degraded runs
- test_status_handling.py
- policy
- .search
- metrics.py, goldens.py, baseline.py, baseline_cli.py
- Scripted
- test_every_path_is_gated_for_every_query

## God Nodes (most connected - your core abstractions)
1. `DenseIndex` - 107 edges
2. `LocalDocumentRepository` - 101 edges
3. `Strategy` - 76 edges
4. `run_retrieval_evaluation()` - 71 edges
5. `FakeEmbedder` - 70 edges
6. `FakeTokenizer` - 67 edges
7. `open_retrieval()` - 65 edges
8. `HeadingChunker` - 64 edges
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
- `Phase 2 compatibility / migration` --references--> `ChunkerIdentity`  [INFERRED]
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

## Communities (196 total, 34 thin omitted)

### Community 0 - "test_compare.py"
Cohesion: 0.05
Nodes (105): Implementation, Review, T7 — round 1, User decision, Implementation, Review, T5 — round 1, User decision (+97 more)

### Community 1 - "retrieval_eval.py"
Cohesion: 0.04
Nodes (60): Implementation, Implementation, Implementation, Review, Review, Review, T2 — round 1, T6 — round 2 (+52 more)

### Community 2 - "open_retrieval"
Cohesion: 0.04
Nodes (66): 008 — Retrieval Fallback Design, As-built notes, Data flow, Decisions D056-D062, Design summary, Spec 008 Retrieval Fallback Design, Error and failure behavior, Interfaces / models (+58 more)

### Community 3 - "chunking.py"
Cohesion: 0.13
Nodes (17): Implementation, _char_split(), _merge_pieces(), _merge_word_pieces(), _parse_sections(), _Section, split_at_sentence_ends(), _split_body() (+9 more)

### Community 4 - "test_validate.py"
Cohesion: 0.14
Nodes (31): edit_rows(), edit_suite(), root(), run(), test_active_golden_without_relevant_documents(), test_candidate_ineligible_document_is_not_unknown(), test_candidate_not_suggested(), test_candidate_referenced_by_suite() (+23 more)

### Community 5 - "test_service.py"
Cohesion: 0.18
Nodes (23): doc(), Harness, test_bumped_document_version_updates(), test_changed_body_updates(), test_changed_metadata_field_updates(), test_chunk_shrink_leaves_no_orphan(), test_chunk_too_long_report_has_no_chunk_text(), test_chunker_exception_is_per_document_failure() (+15 more)

### Community 6 - "Chunk"
Cohesion: 0.19
Nodes (9): Interfaces / models, Package / file placement, Chunk, check_chunks(), ChunkTooLongError, _effective_limit(), test_above_limit_raises_with_fields(), test_cap_below_model_maximum() (+1 more)

### Community 7 - "test_index.py"
Cohesion: 0.12
Nodes (42): IndexBindingError, bound_index(), client(), failing_client(), fake_info(), http_client(), make_settings(), open_index() (+34 more)

### Community 8 - "real_hybrid"
Cohesion: 0.20
Nodes (8): dense_pair(), production_lexical(), real_hybrid(), test_empty_bm25_leg_keeps_the_dense_order(), test_fusion_receives_only_the_legs_checked_hits(), spy(), test_hybrid_result_shape(), test_request_validation_before_any_leg()

### Community 9 - "evaluation/validate.py"
Cohesion: 0.12
Nodes (19): Implementation, Review, T1 — round 1, User decision, EvaluationSchemas, _candidate_rules(), problem(), _describe() (+11 more)

### Community 10 - "IngestionConfigurationError"
Cohesion: 0.05
Nodes (52): Implementation, Implementation, Review, Review, Review, T1 — round 2, T3 — round 1, User decision (+44 more)

### Community 11 - "009 — Chunking Experiments Design"
Cohesion: 0.11
Nodes (17): 009 — Chunking Experiments Design, Alternatives / deferred decisions, As-built notes, Carry-over clean-ups (R11), Chunker identity, settings and configuration (R5), Components / boundaries, Cross-index comparison (R8), Data flow (+9 more)

### Community 12 - "HeadingChunker"
Cohesion: 0.12
Nodes (40): basic_suite(), build(), chunks_per_document_dense(), default_eval_extras(), fusion_config(), golden(), _LexicalStub, _metric_chunk() (+32 more)

### Community 13 - "test_config_schema_11.py"
Cohesion: 0.06
Nodes (41): Acceptance criteria, Design summary, Truncation guard (R2), Implementation, Review, T1 — round 1, load_ingestion_config(), IngestionError (+33 more)

### Community 14 - "test_lexical_cli.py"
Cohesion: 0.09
Nodes (39): Implementation, Implementation, Review, Review, T3 — round 2, T3 — round 3, User decision, default_lexical_dir() (+31 more)

### Community 15 - "json"
Cohesion: 0.14
Nodes (24): committed(), edit_jsonl(), lines(), manifest(), problems(), read_lines(), root(), test_candidates_differ_only_in_promoted_as() (+16 more)

### Community 16 - "CURRENT_STATE.md current state document"
Cohesion: 0.12
Nodes (26): RetrievalUnavailableError and availability classification, Current goal: Specs 001-008 complete; Spec 008 verified and merged into main (1107b67), plan next spec, Known issue: Qdrant and Hugging Face 5xx not fallback-eligible, Known issue: verify_fresh asyncio.run in event loop, Known issue: Qdrant client lifecycle leak on failed open, Known issue: freshness check rereads every document, Known issue: no circuit breaker, ~3 s per query with hanging Qdrant, Spec 008 retro F1: open-time outage makes BM25 serve whole run (+18 more)

### Community 17 - "test_legacy_baseline_snapshot.py"
Cohesion: 0.13
Nodes (15): clean_env(), _Factory, _FixedDatetime, _record_opens(), note(), wrap_func(), inner(), wrap_method() (+7 more)

### Community 18 - "Index Binding Errors"
Cohesion: 0.17
Nodes (22): QdrantIndexStore, client_factory(), client(), test_replace_and_delete_flows(), make_points(), make_settings(), snapshot(), store() (+14 more)

### Community 19 - "Document Model Tests"
Cohesion: 0.10
Nodes (30): IndexPoint, test_run_retrieval_evaluation_on_multi_chunk_recursive_index(), make_world(), client_with_forbidden(), test_forbidden_points_are_never_returned(), test_store_dropping_the_filter_fails_closed(), test_formula_shows_the_cap_when_k_reaches_document_count(), build_client() (+22 more)

### Community 20 - "007 — Hybrid Retrieval Requirements"
Cohesion: 0.05
Nodes (44): BM25Retriever with SQL access clause, eval-compare identity rules (R10), HybridRetriever (dense leg then BM25 leg, no single-leg fallback), lexical-v1 tokenizer (NFC, ZWJ/ZWNJ dropped, L/N/Mn/Mc token chars, 64-term cap), Result format 2.1 and security result 1.1, config/retrieval.yaml and build_retriever strategy factory, Security gate over dense, bm25 and hybrid, SQLite FTS5 lexical store (derived, git-ignored, bound to dense index) (+36 more)

### Community 21 - "test_validate_knowledge.py"
Cohesion: 0.09
Nodes (48): _copy_seed(), h(), _load(), test_absent_optional_fields_hash_as_null(), test_body_change_changes_content_hash(), test_content_hash_is_stable_and_pinned(), test_crlf_and_lf_bodies_hash_identically(), test_lote_languages_keep_stored_order() (+40 more)

### Community 22 - "test_availability.py"
Cohesion: 0.08
Nodes (30): R1 — Failure classification (`errors.py`, `availability.py`), T1: Hugging Face error shapes (confirmed 2026-10-29), Testing / evaluation strategy, Review, classify_model_error(), classify_qdrant_error(), _optional_types(), raise_if_unavailable() (+22 more)

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
Cohesion: 0.14
Nodes (22): Implementation, Review, Review, Review, T2 — round 3, User decision, _content_count(), _join_units() (+14 more)

### Community 28 - "test_strategy_eval.py"
Cohesion: 0.12
Nodes (26): eval_world(), lexical_env(), retrieve(), retrieve_world(), run_strategy(), strategy_suite(), test_2_3_keys_for_each_strategy(), test_a_2_2_file_reads_with_strategy_and_lexical() (+18 more)

### Community 29 - "Evaluation CLI Tests"
Cohesion: 0.12
Nodes (31): assert_invalid(), document_fields(), make_document(), test_blank_required_text_is_rejected(), test_document_is_immutable(), test_duplicate_lote_languages_are_rejected(), test_effective_window_must_be_ordered(), test_empty_lote_languages_is_rejected() (+23 more)

### Community 30 - "pathlib"
Cohesion: 0.17
Nodes (12): declared_release_id(), load_golden_cases(), load_suite(), SuiteRef, test_declared_release(), test_filtering_in_temporary_suite(), test_invalid_line_names_file_and_line_only(), test_path_escaping_repo_root_refused() (+4 more)

### Community 31 - "KnowledgeDocument"
Cohesion: 0.08
Nodes (16): AccessScope, ApprovalStatus, LanguageScope, LifecycleStatus, SourceAuthority, _check_language_code(), KnowledgeDocument, ListRepository (+8 more)

### Community 32 - "test_baseline.py"
Cohesion: 0.06
Nodes (45): case(), clean_env(), cli_run(), DeviceStub, _git(), run(), seeded(), setup() (+37 more)

### Community 33 - "evaluation/test_cli.py"
Cohesion: 0.15
Nodes (19): load_production_ingestion_config(), clean_env(), index_factory(), real_factory(), run(), test_bad_top_k_exits_2(), test_cli_has_no_embedder_or_allow_fake_flag(), test_existing_output_exits_2_before_qdrant() (+11 more)

### Community 34 - "typing"
Cohesion: 0.15
Nodes (5): IndexSettingsMismatchError, collection_name(), IndexedDocument, read_index_settings(), test_collection_name_derivation()

### Community 35 - "SpyIndex"
Cohesion: 0.20
Nodes (3): OddIdStore, SpyIndex, broken()

### Community 36 - "009 — Chunking Experiments Requirements"
Cohesion: 0.07
Nodes (28): 009 — Chunking Experiments Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+20 more)

### Community 37 - "008 — Retrieval Fallback Requirements"
Cohesion: 0.11
Nodes (32): Binding: embedder model ID, revision, vector size, normalization, fake flag and index_version must equal recorded IndexSettings, BM25Retriever(identity, lexical), BM25 statistics (IDF, avg length) computed over every row of a lexical file, build_access_filter (the only filter builder), build_retriever (only place a strategy name becomes a retriever), retrieval_client_factory (Qdrant client with configured timeouts), config/retrieval.yaml (default_strategy hybrid, RRF k 60, depth 50), D033-D041 retrieval decisions (+24 more)

### Community 38 - "conftest.py"
Cohesion: 0.14
Nodes (7): manifest_document_count(), security_repository(), block_model_stack(), fake_lexical(), Raises, test_open_retrieval_bm25_builds_no_embedder_and_no_client(), test_retrieve_cli_bm25_needs_neither_qdrant_nor_the_model()

### Community 39 - "EvaluationHarnessError"
Cohesion: 0.15
Nodes (14): Implementation, Review, T8 — round 1, User decision, EvaluationHarnessError, _gate(), _lexical_sanity_check(), _open_lexical_sanity() (+6 more)

### Community 40 - "open_retrieval"
Cohesion: 0.09
Nodes (15): get_health(), HealthResponse, get_request_settings(), get_settings(), Settings, create_app(), isolate_settings_environment(), test_create_app_wires_settings() (+7 more)

### Community 41 - "typing"
Cohesion: 0.11
Nodes (27): 006-candidates.jsonl with 7 suggested rows, make eval-compare, make eval-security hard gate, result 2.2 and served-strategy eval-compare, eval-security five paths, governed suite loader and schemas, make validate-evaluation, Spec 006 retrospective findings (F1 byte-identity, eval-security not in verify) (+19 more)

### Community 42 - "D055 Default strategy is hybrid (Spec 007)"
Cohesion: 0.15
Nodes (15): Known issue: git_dirty true in Spec 007 BM25/hybrid result files (user-accepted), Latency hybrid p50 80.3 ms p95 103.6 ms; bm25 p50 0.19 ms, BM25 metrics: 64/69 goldens, MRR 0.7082, Hybrid metrics: 68/69 goldens, MRR 0.9094, Retrieval misses g004 g026 g061, Next step 4: Spec 007 T9 strategy comparison and hybrid default, Next step 6: Spec 008 T7 real runs 1-3, retrieval-evaluation-idx-v1-20261028T123109Z.json BM25 (+7 more)

### Community 43 - "Workflow Reviewer"
Cohesion: 0.07
Nodes (25): Considered and rejected, Evidence, F1 — <title> [waste | quality risk | process slip] (confidence: high/medium/low), Findings, New features and tools (official sources, since <date>), Not measurable here, P1 — <title> (addresses F#; expected saving: ...), Proposals (+17 more)

### Community 44 - "run_security_evaluation"
Cohesion: 0.18
Nodes (19): run_security_evaluation(), guest_access(), real_queries(), security_result(), spied(), test_a_fallback_path_that_does_not_fall_back_is_a_harness_error(), test_a_filter_dropping_index_fails_the_gate(), test_a_plain_hybrid_path_that_falls_back_is_a_harness_error() (+11 more)

### Community 45 - "test_lexical_standalone.py"
Cohesion: 0.18
Nodes (19): build_from(), built(), copy_repository(), expected(), first_document_id(), open_it(), remove_document(), repo_at() (+11 more)

### Community 46 - "test_cli_config.py"
Cohesion: 0.14
Nodes (19): clean_env(), _factory(), _run(), test_builds_exactly_one_embedder_per_run(), test_collection_base_comes_from_environment(), test_config_refuses_missing_or_floating_revision(), test_config_refuses_unknown_field_and_missing_file(), test_exit_0_then_idempotent_second_run() (+11 more)

### Community 48 - "make eval-retrieval"
Cohesion: 0.12
Nodes (23): BgeM3Embedder (optional bge-m3 extra, dense only), D025-D030, D032 ingestion decisions, DocumentRepository Protocol (get_document, list_documents), Embedder Protocol, FakeEmbedder (deterministic), GUEST_PUBLIC_POLICY, HeadingChunker (heading v1, character cap, stable section_id slugs), IndexSettings and mismatch comparison (+15 more)

### Community 49 - "007 — Hybrid Retrieval Requirements"
Cohesion: 0.09
Nodes (27): optional bge-m3 extra (sentence-transformers, PyTorch), D048 graphify tooling, make experiment CONFIG=... (target; records git commit, release, suite, chunker, embedder, strategy, metrics, latency), make format, Knowledge graph graphify (D048), /graphify . --update (user, once per spec after merge), graphify query / path / explain, graphify update . (+19 more)

### Community 50 - "list_eligible_documents"
Cohesion: 0.20
Nodes (13): assert_matches_snapshot(), assert_recursive_chunks_whitespace_fidelity(), assert_structure_chunks_whitespace_fidelity(), chunks_to_records(), collapse_whitespace(), load_snapshot(), snapshot_for_document(), recursive_chunker() (+5 more)

### Community 51 - "HeadingChunker"
Cohesion: 0.11
Nodes (27): R3 — Tokenizer `lexical-v1` (`lexical/tokenizer.py`), HeadingChunker, _is_word_char(), slugify(), ids(), test_deterministic(), test_duplicate_headings_get_unique_ids_in_order(), test_duplicate_suffix_does_not_collide_with_literal_heading() (+19 more)

### Community 52 - "DocumentRepository"
Cohesion: 0.13
Nodes (15): Roadmap 2 - Document model + repository, KnowledgeDocument, Manifest/schema validation, S3DocumentRepository and external storage, Way2Australia AI Platform Master Implementation Plan, Phase 1 Definition of Done, Document manifest, DocumentRepository (+7 more)

### Community 53 - "FallbackRetriever"
Cohesion: 0.08
Nodes (29): Fallback authorization invariant (same ResolvedAccess), BM25Retriever (identity, lexical), classify_model_error, classify_qdrant_error, Qdrant client lifecycle gap, eval-compare by served strategy (mixed refused), FallbackRetriever, Hugging Face error shapes (T1 As-built) (+21 more)

### Community 54 - "build"
Cohesion: 0.17
Nodes (12): query_terms(), build(), new_base(), seed_repository(), test_builder_refuses_a_non_throwaway_base_before_any_write(), test_builder_refuses_a_real_embedder_identity(), test_builder_refuses_an_existing_collection(), test_each_forbidden_row_type_is_in_the_lexical_file() (+4 more)

### Community 55 - "LocalDocumentRepository"
Cohesion: 0.06
Nodes (41): _authority_map(), collect(), _document_ids(), collect(), _eligible_document_versions(), DocumentQuery, DocumentRepository, EligibilityPolicy (+33 more)

### Community 56 - "Development Workflow"
Cohesion: 0.12
Nodes (26): Evaluation Suite includes goldens, refusal, multilingual, security, regression, Finalized stack: Python/FastAPI, Next.js, Qdrant, SQLite FTS5, BGE-M3, Bedrock, Langfuse, CloudWatch, Terraform ap-south-1, GitHub Actions, agent-skills sync, D001 Python-first backend, D002 RAG as reusable internal package, D003 Knowledge outside RAG package, D005 Documents are truth; chunks are derived, D007 Public-only Phase 1 (+18 more)

### Community 57 - "retrieval/test_access.py"
Cohesion: 0.16
Nodes (15): clean_env(), guest(), payload(), _policy(), test_a_different_policy_changes_both_builders(), test_both_builders_cover_the_same_three_conditions(), test_check_hit_accepts_valid_payload(), test_check_hit_rejects_malformed_payload() (+7 more)

### Community 58 - "lexical/store.py"
Cohesion: 0.08
Nodes (20): R4/R5 — Lexical store (`lexical/store.py`, `lexical/build.py`), Implementation, Review, T3 — round 1, User decision, T3 — `lexical-v1` tokenizer, lexical store and `make index-lexical`, Verification, R4 — Freshness from the repository (`lexical/freshness.py`) (+12 more)

### Community 59 - "json"
Cohesion: 0.08
Nodes (25): chunker, context_prefix, name, overlap_tokens, target_tokens, version, embedder, batch_size (+17 more)

### Community 60 - "make eval-security"
Cohesion: 0.15
Nodes (14): Security gate on throwaway w2a-sectest-<8 hex> collection with fake embedder, security_corpus.py, security_index.py, security_eval.py, D040, Throwaway collection w2a-sectest-<8 hex>, eval-security exit 0 pass, 1 violation, 2 harness or configuration error, Security fixtures poisoned_public_document.md and staff_only_canary.md, Forbidden points: staff scope, other tenant, owned, missing owner, staff-only canary; nearest neighbour of every query, Authorization hard gate (forbidden points never returned) (+6 more)

### Community 61 - "build_security_repository"
Cohesion: 0.16
Nodes (18): clean_env(), copy_fixtures(), _lexical_work_dir(), spy_lexical_path(), wrapper(), strip_forbidden_terms(), test_a_lexical_sanity_failure_is_a_harness_error(), test_cli_clause_less_lexical_store_exits_one_naming_strategies() (+10 more)

### Community 62 - "Target RAG query flow (User -> FastAPI -> validation -> AccessContext -> LanguageContext -> retrieval -> RRF -> reranker -> context builder -> answerability -> prompt -> Bedrock -> citation validation)"
Cohesion: 0.13
Nodes (19): Answerability / insufficient-evidence decision, Authorization applied inside each retriever before fusion, never after RRF, reranking or generation, Authorization filter is part of the Qdrant query so unauthorized points never leave the store, Amazon Bedrock generation, check_hit (fail-closed re-check, second line of defense), Citation validation, Context builder (planned), D035 Future fallbacks must take the same ResolvedAccess and call check_hit (+11 more)

### Community 63 - "BgeM3Embedder"
Cohesion: 0.06
Nodes (23): BgeM3Embedder, BgeM3Tokenizer, group_installed(), test_constructing_does_not_load_the_model(), test_device_none_before_load_and_recorded_after(), test_missing_group_at_load_raises_optional_dependency_error(), test_missing_group_refused_at_construction(), test_model_loaded_once_with_revision_and_batches() (+15 more)

### Community 64 - "security_index.py"
Cohesion: 0.11
Nodes (12): Acceptance criteria, build_security_index(), _canary_points(), _forbidden_payload(), forbidden_variant(), _lexical_forbidden_entries(), require_security_base(), Chunker (+4 more)

### Community 65 - "test_lexical_build.py"
Cohesion: 0.17
Nodes (20): build_lexical_index(), LexicalIndexError, identity(), payload(), synthetic_entries(), build(), test_atomic_replace_keeps_old_file_after_failure(), test_build_production_helper_runs() (+12 more)

### Community 66 - "make retrieve"
Cohesion: 0.10
Nodes (21): docker compose up -d / down (local Qdrant), Environment: QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION_BASE, W2A_TENANT_ID, Fake embedder needs throwaway QDRANT_COLLECTION_BASE, make index-lexical, make ingest, INGEST_ARGS (--embedder {bge_m3,fake}, --config), ingest exit codes 0 success, 1 document failed, 2 refusal, Ingest summary lines (index:, added/updated/unchanged/deleted, ERROR lines) (+13 more)

### Community 67 - "CURRENT_STATE.md current state document"
Cohesion: 0.10
Nodes (29): build_retriever, make eval-retrieval, CURRENT_STATE.md current state document, Phase 2 Knowledge Release workflow designed not implemented, Public/guest retrieval only in Phase 1; English + Malayalam, Known issue: legacy chillu sequence does not match atomic chillu in BM25, Known issue: evaluation-data gaps (ml goldens, relevant_section_ids empty), Known issue: g004 overlaps u001, keep_both (+21 more)

### Community 68 - "security_eval.py"
Cohesion: 0.05
Nodes (79): 007 — Hybrid Retrieval Design, Alternatives / deferred decisions, As-built notes, Data flow, Design summary, Error and failure behavior, Interfaces / models, Observability (+71 more)

### Community 69 - "Fallback (hybrid only)"
Cohesion: 0.18
Nodes (16): bm25 strategy, bm25 needs neither Qdrant nor the bge-m3 extra (Spec 008), config/retrieval.yaml schema 1.1 (default_strategy hybrid, qdrant.connect_timeout_s 2, query_timeout_s 3; 1.0 refused), dense strategy, --strategy dense needs no lexical file, Embedder pair from index_settings or dense_identity; fallback-only 2.2 file compares against Spec 007 bm25 file, eval-retrieval fallback: Qdrant unreachable with default hybrid is served by bm25 for every case, eval-retrieval options (--top-k, --strategy, --retrieval-config, --suite default public-eval-v2, --release seed-v1, --output, --repo-root, --config); no --embedder or --allow-fake (+8 more)

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
Nodes (19): AccessContext, Role, test_blank_tenant_refused(), test_empty_tenant_refused(), test_no_language_or_scope_fields(), test_tenant_is_stripped(), test_unknown_role_refused(), test_valid_context_is_frozen() (+11 more)

### Community 74 - "Constitution"
Cohesion: 0.21
Nodes (22): load_manifest(), load_schema(), validate_manifest(), metadata(), record(), run(), test_duplicate_document_id_rejected(), test_duplicate_document_version_rejected() (+14 more)

### Community 75 - "Section: Next step"
Cohesion: 0.15
Nodes (12): Atomic publish and rollback, Phase 2 audit trail, Controlled document-change workflow (Release Candidate), Evaluation governance states, Evaluation slices, Evaluation Suite (public-eval-v1), Generation metrics, Evaluation impact detection (+4 more)

### Community 76 - "dense"
Cohesion: 0.03
Nodes (69): Components / boundaries, R10 — `eval-compare` identity rules (`compare.py`), R11 — Security gate (`security_index.py`, `security_eval.py`), R12 — Docker test, R1 — Suite v2, R4 — `make index-lexical` (`lexical/cli.py`), R9 — Result format 2.1, Decisions resolved before drafting (+61 more)

### Community 77 - "AWS target"
Cohesion: 0.11
Nodes (19): Roadmap 11 - Observability, Langfuse traces, Stage latency, model/tokens/cost, release/config IDs, AWS target, Bedrock Knowledge Bases as core RAG (avoided), Bedrock model selection criteria, Amazon CloudWatch, Docker (+11 more)

### Community 78 - "embedder"
Cohesion: 0.14
Nodes (13): chunker, max_chunk_chars, name, version, embedder, batch_size, fake_vector_size, model_id (+5 more)

### Community 79 - "Spec 005 dense retrieval baseline"
Cohesion: 0.13
Nodes (20): AccessContext, Role, W2A_TENANT_ID, make retrieval-baseline legacy frozen, EligibilityPolicy for guest/public, BGE-M3 device mps not pinned (D038), Spec 005 retrospective findings F3-F5, Next step 2: real BGE-M3 baseline committed, experiments/results/retrieval-baseline-idx-v1-20261023T063534Z.json real BGE-M3 baseline, Spec 005 dense retrieval baseline (+12 more)

### Community 80 - "Spec 009 — Task reviews"
Cohesion: 0.14
Nodes (13): Implementation, Implementation, Implementation, Implementation, Spec 009 — Task reviews, T2 — round 2, T3 — round 2, T4 — round 1 (+5 more)

### Community 81 - "list_eligible_documents"
Cohesion: 0.18
Nodes (16): eligible_ids(), IgnoresQueryRepository, make_document(), test_active_approved_public_document_is_eligible(), test_language_filter_narrows_eligible_documents_only(), test_language_metadata_does_not_broaden_access(), test_local_repository_applies_the_policy_query(), test_non_active_lifecycle_is_excluded() (+8 more)

### Community 82 - "Ingestion pipeline (Spec 004)"
Cohesion: 0.11
Nodes (18): default_strategy, fusion, candidate_depth, k, method, weights, qdrant, connect_timeout_s (+10 more)

### Community 83 - "Retrieval fallback (Spec 008, D056-D062)"
Cohesion: 0.12
Nodes (19): bm25 builds no embedder and no Qdrant client, classify_model_error, classify_qdrant_error, D056-D062 fallback decisions, D057 Fallback eligibility classification, D058 Fallback policy per query, D061 Marking and evaluation of fallback, D062 5xx not eligible (+11 more)

### Community 84 - "security_eval.py"
Cohesion: 0.07
Nodes (33): R8 — Strategy and config (`retrieval/strategy.py`, `config/retrieval.yaml`), Implementation, Review, T6 — round 1, User decision, test_roles_match_policy_file(), _check_standalone_open(), _retrievers() (+25 more)

### Community 85 - "DenseIndex"
Cohesion: 0.20
Nodes (21): LexicalRow, build(), DroppedClauseIndex, guest(), pub(), retriever(), _shape(), SpyIndex (+13 more)

### Community 86 - "Spec 001 project foundation"
Cohesion: 0.14
Nodes (16): Completion: retrospective, Spec-Review commit, merge, verified status, Spec orchestrator loop (route, role subagents, user approval, merge), task-gated spec skills and skills-sync, task State lifecycle and spec/NNN branches, D023 task state lifecycle reference, Spec 003 task-gated agent workflow, Spec 003 status: verified 2026-10-15 bootstrap exception on main, Spec status table (+8 more)

### Community 87 - "Backend stack"
Cohesion: 0.15
Nodes (14): Backend stack, FastAPI, httpx, jsonschema, Pandas, Pydantic / Pydantic Settings, Python, pyyaml (+6 more)

### Community 88 - "embedder"
Cohesion: 0.14
Nodes (13): chunker, max_chunk_chars, name, version, embedder, batch_size, fake_vector_size, model_id (+5 more)

### Community 89 - "D023 Task-gated agent workflow"
Cohesion: 0.12
Nodes (16): allowed_scopes, current_release, default_role, implemented_roles, allowed_scopes, allowed_scopes, roles, admin (+8 more)

### Community 90 - "FakeEmbedder"
Cohesion: 0.12
Nodes (15): FakeEmbedder, _cosine_to_query(), _text_with_score_below(), __init__(), test_conforms_to_protocol(), test_declared_vector_size(), test_default_size_is_64(), test_fake_device_is_none() (+7 more)

### Community 91 - "test_schemas.py"
Cohesion: 0.13
Nodes (7): EvaluationError, load_schemas(), test_existing_schema_is_referenced_not_copied(), test_missing_schema_is_configuration_error(), test_per_type_required_field_enforced(), test_schema_files_are_valid_draft_2020_12(), test_valid_rows_pass()

### Community 92 - "Roadmap 10 - Grounded generation + citations"
Cohesion: 0.20
Nodes (12): Answerability and insufficient-evidence response, Docker, Terraform, EC2, ECR, CloudWatch, IAM, Bedrock, Bedrock Runtime (roadmap), Deferred serving concerns (circuit breaker, startup policy, Qdrant 5xx D062), Dense to BM25 degradation, Roadmap 10 - Grounded generation + citations, Roadmap 13 - Graceful degradation, Roadmap 14 - AWS deployment (+4 more)

### Community 93 - "pathlib"
Cohesion: 0.25
Nodes (9): apps/api, apps/web, CloudWatch, Future multimodal mock-test evaluation, Langfuse tracing, packages/core, packages/observability, packages/rag (+1 more)

### Community 94 - "evaluation/cli.py"
Cohesion: 0.06
Nodes (36): Review, default_security_output_path(), format_security_summary(), format_summary(), main(), _retrieval(), real_embedder_factory(), _security() (+28 more)

### Community 95 - "test_store_integration.py"
Cohesion: 0.36
Nodes (7): _keyword_indexed(), live_client(), store(), test_collection_has_keyword_indexes_and_cosine_dense_vector(), test_empty_without_settings_recreates_dropped_indexes(), test_repeated_create_payload_index_is_harmless(), test_settings_storage_and_refusal()

### Community 96 - "ingest_dense"
Cohesion: 0.19
Nodes (11): build_production(), ingest_dense(), open_lexical(), rewrite_settings(), test_bind_does_not_write_to_qdrant(), test_bind_refuses_chunk_set_mismatch_with_counts(), test_bind_refuses_identity_and_chunker_mismatch(), test_bind_refuses_when_qdrant_content_changed() (+3 more)

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
Cohesion: 0.05
Nodes (37): build_security_repository(), _fixture_files(), DocumentNotFoundError, DocumentRepositoryError, DocumentValidationError, DuplicateDocumentError, ManifestValidationError, split_frontmatter() (+29 more)

### Community 102 - "006 Evaluation Framework Tasks"
Cohesion: 0.18
Nodes (14): Local multilingual BGE reranker, BM25 via FTS5 bm25(), Derived local lexical file per collection, Fusion, Lexical store, lexical-v1 tokens (D051), make index-lexical, One lexical file per access scope (future roles) (+6 more)

### Community 103 - "transcript_metrics.py"
Cohesion: 0.20
Nodes (10): analyse(), category(), command_kinds(), executed_text(), expand(), main(), parse_time(), render() (+2 more)

### Community 104 - "Retrieval package (Spec 005 and 007)"
Cohesion: 0.14
Nodes (12): graphify skill pointer, spec/NNN branch and Spec-Task trailers, spec-implementer skill (one task per run), spec-orchestrator skill, spec-planner skill, spec-reviewer retrospective skill, Task-gated agent workflow loop, task-reviewer skill (read-only) (+4 more)

### Community 105 - "D035 One filter builder, fail-closed re-check, same path for later fallbacks (Spec 005)"
Cohesion: 0.17
Nodes (20): DenseIndex, build_access_filter, check_hit, DenseRetriever, FallbackRetriever and open_retrieval wiring (merged 1107b67), make retrieve guest/public CLI, Strategy Protocol, BM25Retriever, rrf_fuse, HybridRetriever, Spec 008 retro F4: duplicated standalone open wiring, BM25Retriever, build_access_filter, check_hit fail-closed re-check (+12 more)

### Community 106 - "Qdrant (vector database)"
Cohesion: 0.14
Nodes (13): Authorization metadata (access_scope, owner_user_id, tenant_id), Engineering Conventions, IDs and versions conventions, Knowledge files with provenance, Language metadata (content_language, lote_languages), Logging and tracing hygiene, Domain naming terms, Prompts as versioned assets (+5 more)

### Community 107 - "run_security_evaluation"
Cohesion: 0.25
Nodes (4): DroppedClauseLexical, test_a_dropped_lexical_clause_names_the_four_lexical_paths(), test_a_lexical_store_without_the_clause_fails_bm25_and_hybrid(), __init__()

### Community 108 - "ChunkerIdentity"
Cohesion: 0.11
Nodes (14): Implementation, T2 — round 1, 009 — Chunking Experiments Tasks, T2 — Structure and recursive chunkers, T6 — User-owned real runs and the default index, T7 — Documentation, decisions, carry-over clean-ups and hand-off, Verification, Verification (+6 more)

### Community 109 - "make eval-retrieval"
Cohesion: 0.12
Nodes (17): --allow-fake (plumbing only, never a recorded baseline), make retrieval-baseline (legacy, frozen Spec 005 producer), BASELINE_ARGS (--embedder, --allow-fake, --top-k, --suite, --release, --output, --config), Baseline metrics HitRate@5, random expectation min(1,5/N), Recall@5, MRR, p50/p95 latency, experiments/results/retrieval-baseline-<index_version>-<UTC>.json, never overwritten, D036 binding rules, D053 result 2.1, eval-retrieval exit 0 or 2 (+9 more)

### Community 110 - "test_run_retrieval_evaluation_on_multi_chunk_recursive_index"
Cohesion: 0.24
Nodes (5): UnanswerableCase, deterministic_clock(), equivalence_suite(), unanswerable(), unanswerable()

### Community 111 - "test_content_hash.py"
Cohesion: 0.15
Nodes (12): Approved packages, pricing and validity, Six approved packages and prices, 60-day package validity, 24-hour cancellation notice, Personal coaching package, 60-minute coaching session on Google Meet, Individual coaching and live appointments, Mock assessments, scoring, feedback and review windows (+4 more)

### Community 113 - "test_violation_names_the_document_from_the_error_attribute"
Cohesion: 0.18
Nodes (12): AGENTS.md Project Rules, DocumentRepository Abstraction, Evaluation Governance Rules, Language Separation Rules, Phase 1 Scope, Task-gated Spec Loop, CLAUDE.md Project Instructions, graphify Knowledge Graph Rules (+4 more)

### Community 114 - "pytest"
Cohesion: 0.17
Nodes (12): AccessContext(role, tenant_id) with blank tenant refused, Future agent folders intentionally not created, apps/api (FastAPI application layer), apps/web (Next.js/TypeScript frontend: recruiter assistant, RAG Lab, engineering views), core/access.py (Role, frozen AccessContext), guest_access, Knowledge model metadata (document_id, document_version, tenant_id, access_scope, lote_languages, content_language, source_authority...), No language filter, score threshold or reranking yet (+4 more)

### Community 116 - "fusion"
Cohesion: 0.20
Nodes (12): English, Malayalam and mixed queries, FAQ-aware retrieval/indexing, Roadmap 7 - Chunking experiments, Roadmap 8 - Multilingual retrieval, Language applicability handling, Parent-heading context and order-independent section_ids, Recursive chunking baseline, Optional semantic chunking (+4 more)

### Community 117 - "evaluation/cli.py"
Cohesion: 0.21
Nodes (12): Branching and commits (spec/NNN, Spec-Task trailer), Development Workflow, Multi-agent handoff, Implementation rule: BLOCKED spec issue, Phase discipline, Protected source-of-truth data, Required spec-reviewer retrospective, Agent skills (orchestrator, planner, implementer, task-reviewer, spec-reviewer) (+4 more)

### Community 118 - "make_document"
Cohesion: 0.25
Nodes (17): make_document(), structure_chunker(), test_duplicate_sibling_headings_raise(), test_fence_blocks_are_atomic_and_headings_inside_ignored(), test_long_list_splits_only_between_items(), test_main_collision_with_heading_slug(), test_malayalam_paragraph_packs(), test_malayalam_paragraph_splits_when_over_cap() (+9 more)

### Community 119 - "evaluation/errors.py"
Cohesion: 0.13
Nodes (13): active_registry_languages(), aggregate(), _mean(), slice_by(), source_authority_key(), row(), test_absent_languages_from_a_temp_registry(), test_missing_registry_section_is_a_configuration_error() (+5 more)

### Community 120 - "failing_client"
Cohesion: 0.18
Nodes (10): content-hash-v1 (sole change-detection signal), LocalDocumentRepository, Document manifest and JSON Schema validation, make validate-knowledge, persona_scope spec defect (F2), BgeM3Embedder (optional extra, pinned revision), Embedder Protocol and FakeEmbedder, HeadingChunker and slugify rule (+2 more)

### Community 121 - "test_status_handling.py"
Cohesion: 0.20
Nodes (8): Adding a New Language Guide, language_registry.json, Public Assistant Content Boundaries, access_scope, content_language, Knowledge Schema and Metadata, language_scope, lote_languages

### Community 122 - "ARCHITECTURE.md"
Cohesion: 0.12
Nodes (19): D042-D047, D053, D054 evaluation decisions, Evaluation architecture (Evaluation Suite case types), Evaluation assets never written by evaluation code (C6); candidates suggested and human-activated, Ingestion eligibility is the only guard against synthetic/unapproved documents; poisoned_public_document is not an authorization case, Evaluation isolation and gates, models.py, suite.py (tolerant typed cases, read-only load_suite), retrieval_eval.py, slices.py, sections.py, Section-level keys <document_id>#<section_id> (+11 more)

### Community 123 - "EvaluationConfigurationError"
Cohesion: 0.12
Nodes (20): EvaluationConfigurationError, ingestion_config_report(), require_active_suite(), declared_release_id(), inside(), load_suite(), read_dataset(), read_json() (+12 more)

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
Cohesion: 0.08
Nodes (27): Authorization regression and staff canary, BGE-M3 (roadmap), BM25, Citation manipulation tests and input/cost limits, Backend-owned citation validation, Deterministic regression gates, FastAPI skeleton, Golden, refusal and security cases (+19 more)

### Community 131 - "RuntimeSettings"
Cohesion: 0.33
Nodes (9): NAATI CCL candidate rules and test-day setup, Direct first-person speech requirement, Report technical incidents within 24 hours, NAATI, Online proctoring with separate phone or tablet, Prohibited materials and tools, Recording under 20 minutes, One repeated segment per dialogue without penalty (+1 more)

### Community 133 - "Vocabulary, flashcards and free access"
Cohesion: 0.29
Nodes (7): EligibilityPolicy / GUEST_PUBLIC_POLICY, Security fixtures (valid but ineligible), config/ingestion.yaml and RuntimeSettings, Ingestion pipeline (target vs current state diff), AccessContext and Role (core), resolve_access / ResolvedAccess, W2A_TENANT_ID server tenant setting

### Community 134 - ".search"
Cohesion: 0.25
Nodes (8): Phase 2 basic analytics, Assistant behavior rules, Product Context, English and Malayalam language scope, Future personas, Phase 1 guest-only scope, Way2Australia AI product, Source-of-truth priorities

### Community 136 - "Spec 002 document model and repository"
Cohesion: 0.10
Nodes (23): Pydantic document models and enums, GET /health endpoint, LocalDocumentRepository with manifest schema validation, make setup, packages core/rag/observability skeletons, uv workspace and uv.lock, make validate-knowledge, make verify quality surface (Ruff, Pyright, pytest) (+15 more)

### Community 137 - "suite.py"
Cohesion: 0.14
Nodes (13): CaseBase, CaseStatus, DatasetRef, DatasetType, GoldenCase, LoadedSuite, SecurityCase, SuiteManifest (+5 more)

### Community 138 - "Evaluation Framework Goal"
Cohesion: 0.39
Nodes (8): NAATI CCL test format, scoring and results, NAATI CCL test, Deduction-based assessment, Begin interpreting within five seconds of chime, NAATI, CCL is not professional interpreter certification, Pass requirement 63/90 overall and 29/45 per dialogue, Results within 4-6 weeks

### Community 139 - "make validate-evaluation"
Cohesion: 0.15
Nodes (13): schemas.py, validate.py (referencing registry, validate-evaluation checks), Error format ERROR <ClassName>: <message>; eval-compare refusals start with 'not comparable:', EVAL_ARGS, python -m way2australia_rag.evaluation.cli {validate,retrieval,security,compare}, make eval-generation does not exist yet, Retrieval evaluation supports Recall@5, MRR, HitRate@5 and language/category/source-authority slices, Evaluation commands (single module evaluation.cli), Suite status draft, active, deprecated, replaced (+5 more)

### Community 140 - "Intentionally avoided choices"
Cohesion: 0.13
Nodes (18): Lexical file is a derived artifact, one per collection, bound by identity and chunk digest, Source documents are truth; chunks, embeddings, sparse entries, Qdrant points and preview indexes are derived artifacts, Full agent orchestration (avoided), Intentionally avoided choices, Bedrock Agents / AgentCore for Phase 1 (avoided), Containers, Derived retrieval index in Qdrant, Docker Compose (+10 more)

### Community 141 - "BGE-M3 (initial embedding model)"
Cohesion: 0.38
Nodes (6): Evaluation Candidates File, Evaluation Package (evaluation/), Evaluation Suite and Case-type Schemas, validate-evaluation, T2 Schemas and validate-evaluation, T7 Candidates

### Community 142 - "Way2Australia AI Platform Master Implementation Plan"
Cohesion: 0.29
Nodes (7): eval-retrieval, Retrieval Result Document 2.0, Section-level Metrics, Slices and small_sample, Unanswerable Reporting, T3 Retrieval Runner, T4 Unanswerable Reporting

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
Cohesion: 0.11
Nodes (28): Review, FallbackReason, FallbackRetriever, access(), client_at(), closed_port(), Fallback, open_hybrid() (+20 more)

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

### Community 155 - "IndexSettings"
Cohesion: 0.08
Nodes (22): build_payload(), PointPayload, build_index_settings(), compare(), IndexSettings, mismatch_message(), _DenseLike, test_index_settings_1_0_upgrades_in_memory() (+14 more)

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
Cohesion: 0.17
Nodes (6): _path_strategy(), security_document(), security_run_record(), SecurityReport, SecurityIndex, test_a_forbidden_hit_injected_into_a_path_fails_the_gate_naming_it()

### Community 194 - "Evaluation tooling"
Cohesion: 0.27
Nodes (10): Custom retrieval metrics (plain Python), DeepEval (not yet a dependency), Evaluation tooling, Generation/e2e metrics (correctness, faithfulness, citations, refusal), GitHub Actions, Heavyweight framework abstractions (avoided), LLM-as-judge not sole source of truth, Primary retrieval metrics (Recall@5, MRR, HitRate@5) (+2 more)

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

### Community 204 - "test_every_path_is_gated_for_every_query"
Cohesion: 0.29
Nodes (4): test_every_path_is_gated_for_every_query(), counting(), test_the_gate_runs_all_three_strategies_on_v2(), counting()

## Ambiguous Edges - Review These
- `Task-gated agent workflow loop` → `graphify skill pointer`  [AMBIGUOUS]
  .claude/CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **380 isolated node(s):** `way2australia-api`, `way2australia-core`, `way2australia-observability`, `way2australia-rag`, `way2australia` (+375 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1328 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **34 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Change log` connect `security_eval.py` to `test_compare.py`, `retrieval_eval.py`, `open_retrieval`, `EvaluationHarnessError`, `D055 Default strategy is hybrid (Spec 007)`, `run_security_evaluation`, `test_lexical_cli.py`, `007 — Hybrid Retrieval Requirements`, `build_security_repository`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Are the 80 inferred relationships involving `DenseIndex` (e.g. with `Design summary` and `Decisions resolved before drafting`) actually correct?**
  _`DenseIndex` has 80 INFERRED edges - model-reasoned connections that need verification._
- **What connects `way2australia-api`, `way2australia-core`, `way2australia-observability` to the rest of the system?**
  _380 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_compare.py` be split into smaller, more focused modules?**
  _Cohesion score 0.054550222921584055 - nodes in this community are weakly interconnected._
- **Why does `D055 Default strategy is hybrid (Spec 007)` connect `D055 Default strategy is hybrid (Spec 007)` to `CURRENT_STATE.md current state document`, `typing`, `D035 One filter builder, fail-closed re-check, same path for later fallbacks (Spec 005)`, `Ingestion pipeline (Spec 004)`, `Development Workflow`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._
- **Are the 35 inferred relationships involving `LocalDocumentRepository` (e.g. with `Dependencies` and `Design summary`) actually correct?**
  _`LocalDocumentRepository` has 35 INFERRED edges - model-reasoned connections that need verification._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Task-gated agent workflow loop` and `graphify skill pointer`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._