# Graph Report - way2australia  (2026-11-04)

## Corpus Check
- 304 files · ~338,094 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 36 file(s) not represented in the graph (top: (none) 20, .jsonl 13, .mdc 1)

## Summary
- 4670 nodes · 14140 edges · 204 communities (172 shown, 32 thin omitted)
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 3030 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `55152fd8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_compare.py
- run_baseline
- open_retrieval
- pathlib
- test_validate.py
- test_service.py
- security_eval.py
- test_index.py
- asyncio
- evaluation/validate.py
- chunker_build.py
- BgeM3Tokenizer
- HeadingChunker
- test_open_retrieval_bm25_builds_no_embedder_and_no_client
- test_lexical_cli.py
- json
- CURRENT_STATE.md current state document
- IngestionConfigurationError
- QdrantIndexStore
- test_retriever.py
- 007 — Hybrid Retrieval Requirements
- test_validate_knowledge.py
- test_availability.py
- BGE-M3 Adapter
- test_lexical_standalone.py
- Spec 004 ingestion baseline
- FakeTokenizer
- test_suite_v3.py
- test_strategy_eval.py
- Evaluation CLI Tests
- live_suite_rows
- KnowledgeDocument
- test_baseline.py
- evaluation/test_cli.py
- 010 — Multilingual Retrieval Requirements
- SpyIndex
- 009 — Chunking Experiments Requirements
- 008 — Retrieval Fallback Requirements
- ResolvedLote
- _security
- open_retrieval
- typing
- security_index.py
- Workflow Reviewer
- LocalDocumentRepository
- test_lexical_standalone.py
- test_cli_config.py
- test_repository_contract.py
- Ingestion (Phase 1 baseline, Spec 004)
- 007 — Hybrid Retrieval Requirements
- test_recursive.py
- HeadingChunker
- evaluation/cli.py
- FallbackRetriever
- hashing.py
- BgeM3Embedder
- Development Workflow
- retrieval_eval.py
- dense
- json
- Evaluation Phase 1 framework (Spec 006)
- EvaluationHarnessError
- Retrieval fallback (Spec 008, D056-D062)
- ChunkerIdentity
- test_legacy_baseline_snapshot.py
- test_index_contract.py
- make eval-retrieval
- Spec 007 hybrid retrieval
- DenseRetriever
- test_applicability.py
- embedder
- Phase 1 RAG query pipeline
- build_lexical_index
- Target repository shape (apps, packages, knowledge, sources, evaluation, tests, config, experiments, analytics, prompts, docs, infra)
- test_manifest_validation.py
- Section: Next step
- BM25Retriever
- retrieval/test_cli.py
- embedder
- repositories/__init__.py
- FakeTokenizer
- list_eligible_documents
- Ingestion pipeline (Spec 004)
- rrf_fuse
- AccessContext
- test_bm25.py
- LexicalIndex
- Backend stack
- embedder
- D023 Task-gated agent workflow
- Path
- test_schemas.py
- Roadmap 12 - Security
- pathlib
- Spec status table
- DenseIndex
- test_slices.py
- SpyIndex
- transcript_metrics.py
- CURRENT_STATE.md
- QdrantIndexStore
- D035 One filter builder, fail-closed re-check, same path for later fallbacks (Spec 005)
- AWS target
- make ingest
- Retrieval package (Spec 005 and 007)
- dense_equivalence.py
- Qdrant (vector database)
- Review
- D057 Failure classification: one fallback-eligible error (Spec 008)
- FakeEmbedder
- sync_agent_skills.py
- test_content_hash.py
- Spec 005 dense retrieval baseline
- test_violation_names_the_document_from_the_error_attribute
- test_lexical_build.py
- load_retrieval_config
- fusion
- SQLite FTS5
- Development Workflow
- EvaluationConfigurationError
- failing_client
- test_status_handling.py
- DroppedClauseLexical
- Spec 009 — Task reviews
- QdrantIndexStore
- Baseline runner and result JSON
- test_failed_write_removes_partial_file
- Development Workflow
- test_status_handling.py
- absent_query_languages
- Phase 1 - Production-oriented RAG
- RuntimeSettings
- test_goldens.py
- Vocabulary, flashcards and free access
- .search
- documents/__init__.py
- Spec 002 document model and repository
- 007 — Hybrid Retrieval Tasks
- Evaluation Framework Goal
- test_failed_write_removes_partial_file
- test_forbidden_dense_hit_fails_the_whole_query
- BGE-M3 (initial embedding model)
- Way2Australia AI Platform Master Implementation Plan
- Eligible failures: Qdrant connect/network, Qdrant timeout, model load/download failure with network __cause__
- eval-compare
- Payments, account access and support boundaries
- make eval-compare
- make test
- Mission
- test_fallback.py
- CountingStore
- Spec 004 retrospective round 1 (PASS)
- policy
- policy
- policy
- tokenizer.py
- test_failed_write_removes_partial_file
- stalled_port
- Orchestrator State Machine
- way2australia_api/__init__.py
- Project Context README
- Authorization enforced before generation
- way2australia_rag/__init__.py
- Scripted
- way2australia-core
- Phase 1 analytics event contract
- Spec-driven development workflow
- api/__init__.py
- Implementation
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
- canonical_json
- DocumentRepository
- test_run_retrieval_evaluation_on_multi_chunk_recursive_index
- git_state
- Roadmap 13 - Graceful degradation
- lexical/ package (Spec 007)
- policy
- RuntimeSettings
- failing_client
- test_every_path_is_gated_for_every_query
- Way2Australia AI Platform Master Implementation Plan
- T4 — round 1

## God Nodes (most connected - your core abstractions)
1. `DenseIndex` - 112 edges
2. `LocalDocumentRepository` - 102 edges
3. `Strategy` - 79 edges
4. `DenseRetriever` - 79 edges
5. `FakeTokenizer` - 78 edges
6. `ResolvedAccess` - 77 edges
7. `run_retrieval_evaluation()` - 74 edges
8. `FakeEmbedder` - 73 edges
9. `HeadingChunker` - 68 edges
10. `LexicalIndex` - 67 edges

## Surprising Connections (you probably didn't know these)
- `R10 — `eval-compare` identity rules (`compare.py`)` --references--> `_refusals()`  [INFERRED]
  .kiro/specs/007-hybrid-retrieval/design.md → packages/rag/src/way2australia_rag/evaluation/compare.py
- `Change log` --references--> `run_retrieval_evaluation()`  [INFERRED]
  .kiro/specs/009-chunking-experiments/requirements.md → packages/rag/src/way2australia_rag/evaluation/retrieval_eval.py
- `Acceptance criteria` --references--> `script_mix()`  [INFERRED]
  .kiro/specs/010-multilingual-retrieval/requirements.md → packages/rag/src/way2australia_rag/evaluation/script_mix.py
- `Interfaces / models` --references--> `Chunk`  [INFERRED]
  .kiro/specs/009-chunking-experiments/design.md → packages/rag/src/way2australia_rag/ingestion/chunking.py
- `Acceptance criteria` --references--> `slugify()`  [INFERRED]
  .kiro/specs/009-chunking-experiments/requirements.md → packages/rag/src/way2australia_rag/ingestion/chunking.py

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

## Communities (204 total, 32 thin omitted)

### Community 0 - "test_compare.py"
Cohesion: 0.06
Nodes (102): Implementation, Review, T7 — round 1, User decision, _changed(), _chunker_text(), compare(), Comparison (+94 more)

### Community 1 - "run_baseline"
Cohesion: 0.08
Nodes (29): Implementation, Review, T2 — round 1, User decision, T2 — v2 dense baseline (user-owned gate), Verification, Continuity command (R10), dedupe_sections() (+21 more)

### Community 2 - "open_retrieval"
Cohesion: 0.06
Nodes (53): Acceptance criteria, Decisions resolved before drafting, Implementation, Review, 008 — Retrieval Fallback Design, Alternatives / deferred decisions, Data flow, Design summary (+45 more)

### Community 3 - "pathlib"
Cohesion: 0.09
Nodes (10): load_ingestion_config(), _parser(), encode_lote_column(), test_agrees_with_day1_baseline(), test_real_config_loads_with_pinned_revision(), test_clis_load_recursive_config(), test_lexical_cli_recursive_fake_embedder_records_built_identity(), test_schema_1_0_still_loads_heading() (+2 more)

### Community 4 - "test_validate.py"
Cohesion: 0.14
Nodes (31): edit_rows(), edit_suite(), root(), run(), test_active_golden_without_relevant_documents(), test_candidate_ineligible_document_is_not_unknown(), test_candidate_not_suggested(), test_candidate_referenced_by_suite() (+23 more)

### Community 5 - "test_service.py"
Cohesion: 0.14
Nodes (26): BoomChunker, doc(), Harness, ShortResultEmbedder, test_bumped_document_version_updates(), test_changed_body_updates(), test_changed_metadata_field_updates(), test_chunk_shrink_leaves_no_orphan() (+18 more)

### Community 7 - "test_index.py"
Cohesion: 0.16
Nodes (35): IndexBindingError, client(), fake_info(), http_client(), make_settings(), open_index(), payload(), scope_filter() (+27 more)

### Community 8 - "asyncio"
Cohesion: 0.17
Nodes (20): LocalRepositoryConfig, test_seed_corpus_is_entirely_eligible_for_guest(), _copy_seed(), seed_repository(), test_documents_outside_approved_roots_are_never_loaded(), test_get_document_by_id_and_version(), test_get_document_missing_raises_not_found(), test_invalid_document_fails_load_without_leaking_paths() (+12 more)

### Community 9 - "evaluation/validate.py"
Cohesion: 0.10
Nodes (21): Implementation, Review, T1 — round 1, User decision, EvaluationSchemas, _candidate_rules(), problem(), _describe() (+13 more)

### Community 10 - "chunker_build.py"
Cohesion: 0.12
Nodes (23): Implementation, Implementation, Review, T3 — round 2, User decision, T3 — Configuration, index settings, lexical identity and per-document freshness, Verification, build_chunker() (+15 more)

### Community 11 - "BgeM3Tokenizer"
Cohesion: 0.12
Nodes (11): BgeM3Tokenizer, hub(), test_bge_m3_cache_hit_counts(), test_bge_m3_miss_offline_refused(), test_bge_m3_miss_online_download(), test_bge_m3_refuses_floating_revision(), test_bge_m3_smoke_matches_sentence_transformer_tokenizer(), test_bge_m3_wrong_revision_refused() (+3 more)

### Community 12 - "HeadingChunker"
Cohesion: 0.12
Nodes (33): basic_suite(), build(), fusion_config(), _LexicalStub, _metric_chunk(), run(), Scripted, scripted_run() (+25 more)

### Community 13 - "test_open_retrieval_bm25_builds_no_embedder_and_no_client"
Cohesion: 0.29
Nodes (4): block_model_stack(), Raises, test_open_retrieval_bm25_builds_no_embedder_and_no_client(), test_retrieve_cli_bm25_needs_neither_qdrant_nor_the_model()

### Community 14 - "test_lexical_cli.py"
Cohesion: 0.09
Nodes (41): Implementation, Implementation, Review, Review, T3 — round 2, T3 — round 3, User decision, default_lexical_dir() (+33 more)

### Community 15 - "json"
Cohesion: 0.16
Nodes (23): committed(), edit_jsonl(), lines(), problems(), read_lines(), root(), test_candidates_differ_only_in_promoted_as(), test_changed_query_is_a_problem_without_text() (+15 more)

### Community 16 - "CURRENT_STATE.md current state document"
Cohesion: 0.10
Nodes (35): standalone bm25 without Qdrant or extra (IndexIdentity, freshness), CURRENT_STATE.md current state document, Phase 2 Knowledge Release workflow designed not implemented, Public/guest retrieval only in Phase 1; English + Malayalam, Known issue: Qdrant and Hugging Face 5xx not fallback-eligible, Known issue: verify_fresh asyncio.run in event loop, Known issue: Qdrant client lifecycle leak on failed open, Known issue: freshness check rereads every document (+27 more)

### Community 17 - "IngestionConfigurationError"
Cohesion: 0.07
Nodes (24): Review, Chunk, legacy_chunker_max_chunk_chars(), _parse_sections(), _Section, _split_body(), _split_words(), format_summary() (+16 more)

### Community 18 - "QdrantIndexStore"
Cohesion: 0.09
Nodes (35): IndexSettingsMismatchError, IndexSettings, QdrantIndexStore, read_index_settings(), _DenseLike, test_index_settings_1_0_upgrades_in_memory(), client_factory(), test_collection_with_1_0_settings_still_binds() (+27 more)

### Community 19 - "test_retriever.py"
Cohesion: 0.07
Nodes (29): client_with_forbidden(), FilterDroppingIndex, test_forbidden_points_are_never_returned(), test_store_dropping_the_filter_fails_closed(), build_client(), docs(), guest(), make_point() (+21 more)

### Community 20 - "007 — Hybrid Retrieval Requirements"
Cohesion: 0.05
Nodes (44): BM25Retriever with SQL access clause, eval-compare identity rules (R10), HybridRetriever (dense leg then BM25 leg, no single-leg fallback), lexical-v1 tokenizer (NFC, ZWJ/ZWNJ dropped, L/N/Mn/Mc token chars, 64-term cap), Result format 2.1 and security result 1.1, config/retrieval.yaml and build_retriever strategy factory, Security gate over dense, bm25 and hybrid, SQLite FTS5 lexical store (derived, git-ignored, bound to dense index) (+36 more)

### Community 21 - "test_validate_knowledge.py"
Cohesion: 0.22
Nodes (26): load(), test_bad_date_fails_loading_naming_document_and_field(), test_seed_corpus_still_loads(), test_valid_date_loads(), build_repo(), metadata(), problems_for(), run_cli() (+18 more)

### Community 22 - "test_availability.py"
Cohesion: 0.07
Nodes (33): T1: Hugging Face error shapes (confirmed 2026-10-29), Repeated finding: graphify update ownership, Implementer Sonnet 5.5 / reviewer Opus 5.5 pattern, Review, T1 — round 1, User decision, classify_model_error(), classify_qdrant_error() (+25 more)

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
Cohesion: 0.07
Nodes (44): Implementation, Implementation, Implementation, Review, Review, Review, T2 — round 1, T2 — round 2 (+36 more)

### Community 27 - "test_suite_v3.py"
Cohesion: 0.12
Nodes (29): Implementation, Review, T1 — round 1, User decision, candidate_row(), candidates(), edit_jsonl(), errors() (+21 more)

### Community 28 - "test_strategy_eval.py"
Cohesion: 0.10
Nodes (34): Review, User decision, User decision, build_lexical(), eval_world(), leg_order(), lexical_env(), make_world() (+26 more)

### Community 29 - "Evaluation CLI Tests"
Cohesion: 0.12
Nodes (31): assert_invalid(), document_fields(), make_document(), test_blank_required_text_is_rejected(), test_document_is_immutable(), test_duplicate_lote_languages_are_rejected(), test_effective_window_must_be_ordered(), test_empty_lote_languages_is_rejected() (+23 more)

### Community 30 - "live_suite_rows"
Cohesion: 0.11
Nodes (20): script_mix(), load_suite(), live_suite_rows(), test_every_v3_query_letter_matches_script_fixture(), test_g062_is_latin_only(), test_non_letters_add_no_script(), test_representative_v3_queries(), golden_count() (+12 more)

### Community 31 - "KnowledgeDocument"
Cohesion: 0.06
Nodes (10): _check_language_code(), KnowledgeDocument, _document_ids(), collect(), _eligible_document_versions(), DocumentQuery, DocumentRepository, _corpus_problems() (+2 more)

### Community 32 - "test_baseline.py"
Cohesion: 0.14
Nodes (21): case(), cli_run(), DeviceStub, _git(), run(), setup(), test_case_access_context_never_widens_access(), test_cli_release_mismatch_and_bad_args_exit_2() (+13 more)

### Community 33 - "evaluation/test_cli.py"
Cohesion: 0.15
Nodes (20): load_production_ingestion_config(), clean_env(), index_factory(), real_factory(), run(), test_bad_top_k_exits_2(), test_cli_has_no_embedder_or_allow_fake_flag(), test_existing_output_exits_2_before_qdrant() (+12 more)

### Community 34 - "010 — Multilingual Retrieval Requirements"
Cohesion: 0.07
Nodes (29): 010 — Multilingual Retrieval Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+21 more)

### Community 35 - "SpyIndex"
Cohesion: 0.25
Nodes (3): OddIdStore, SpyIndex, broken()

### Community 36 - "009 — Chunking Experiments Requirements"
Cohesion: 0.07
Nodes (28): 009 — Chunking Experiments Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+20 more)

### Community 37 - "008 — Retrieval Fallback Requirements"
Cohesion: 0.09
Nodes (36): Baseline runner (refuses fake index without --allow-fake; HitRate@k, Recall@k, MRR, p50/p95, min(1,k/N) random expectation), Binding: embedder model ID, revision, vector size, normalization, fake flag and index_version must equal recorded IndexSettings, BM25Retriever(identity, lexical), BM25 statistics (IDF, avg length) computed over every row of a lexical file, build_access_filter (the only filter builder), build_retriever (only place a strategy name becomes a retriever), retrieval_client_factory (Qdrant client with configured timeouts), config/retrieval.yaml (default_strategy hybrid, RRF k 60, depth 50) (+28 more)

### Community 38 - "ResolvedLote"
Cohesion: 0.10
Nodes (30): 010 — Multilingual Retrieval Design, Applicability builders (R3), Components / boundaries, Data flow, Design summary, Error and failure behavior, Observability, Package / file placement (+22 more)

### Community 39 - "_security"
Cohesion: 0.16
Nodes (7): select_security_queries(), delete_security_index(), require_security_base(), test_the_security_index_records_a_fake_embedder_and_is_removed(), live_client(), test_recursive_v1_full_gate_on_docker(), test_server_filter_keeps_every_forbidden_point_out()

### Community 40 - "open_retrieval"
Cohesion: 0.12
Nodes (13): get_health(), HealthResponse, get_request_settings(), get_settings(), Settings, create_app(), isolate_settings_environment(), test_create_app_wires_settings() (+5 more)

### Community 41 - "typing"
Cohesion: 0.09
Nodes (30): 006-candidates.jsonl with 7 suggested rows, make eval-compare, make eval-retrieval, make eval-security hard gate, result 2.2 and served-strategy eval-compare, eval-security five paths, governed suite loader and schemas, make validate-evaluation (+22 more)

### Community 42 - "security_index.py"
Cohesion: 0.08
Nodes (17): Acceptance criteria, _canary_points(), _lexical_forbidden_entries(), Embedder, point_id(), build_payload(), PointPayload, DocumentFailure (+9 more)

### Community 43 - "Workflow Reviewer"
Cohesion: 0.07
Nodes (25): Considered and rejected, Evidence, F1 — <title> [waste | quality risk | process slip] (confidence: high/medium/low), Findings, New features and tools (official sources, since <date>), Not measurable here, P1 — <title> (addresses F#; expected saving: ...), Proposals (+17 more)

### Community 44 - "LocalDocumentRepository"
Cohesion: 0.12
Nodes (34): run_security_evaluation(), LocalDocumentRepository, match_expression(), security_repository(), build(), guest_access(), new_base(), real_queries() (+26 more)

### Community 45 - "test_lexical_standalone.py"
Cohesion: 0.17
Nodes (20): build_from(), built(), copy_repository(), expected(), first_document_id(), open_it(), remove_document(), repo_at() (+12 more)

### Community 46 - "test_cli_config.py"
Cohesion: 0.12
Nodes (21): manifest_document_count(), clean_env(), _factory(), _run(), test_builds_exactly_one_embedder_per_run(), test_collection_base_comes_from_environment(), test_config_refuses_missing_or_floating_revision(), test_config_refuses_unknown_field_and_missing_file() (+13 more)

### Community 47 - "test_repository_contract.py"
Cohesion: 0.19
Nodes (11): InMemoryDocumentRepository, make_document(), test_document_query_has_no_filesystem_concepts(), test_document_query_is_immutable(), test_get_document_missing_raises_not_found(), test_get_document_returns_latest_or_requested_version(), test_in_memory_repository_satisfies_protocol(), test_list_documents_applies_query_filters() (+3 more)

### Community 48 - "Ingestion (Phase 1 baseline, Spec 004)"
Cohesion: 0.07
Nodes (34): BgeM3Embedder (optional bge-m3 extra, dense only), D025-D030, D032 ingestion decisions, DocumentRepository Protocol (get_document, list_documents), Embedder Protocol, FakeEmbedder (deterministic), GUEST_PUBLIC_POLICY, HeadingChunker (heading v1, character cap, stable section_id slugs), IndexSettings and mismatch comparison (+26 more)

### Community 49 - "007 — Hybrid Retrieval Requirements"
Cohesion: 0.09
Nodes (27): optional bge-m3 extra (sentence-transformers, PyTorch), D048 graphify tooling, make experiment CONFIG=... (target; records git commit, release, suite, chunker, embedder, strategy, metrics, latency), make format, Knowledge graph graphify (D048), /graphify . --update (user, once per spec after merge), graphify query / path / explain, graphify update . (+19 more)

### Community 50 - "test_recursive.py"
Cohesion: 0.11
Nodes (21): _authority_map(), collect(), EligibilityPolicy, list_eligible_documents(), assert_matches_snapshot(), assert_recursive_chunks_whitespace_fidelity(), chunks_to_records(), collapse_whitespace() (+13 more)

### Community 51 - "HeadingChunker"
Cohesion: 0.09
Nodes (45): HeadingChunker, _is_word_char(), slugify(), assert_structure_chunks_whitespace_fidelity(), ids(), make_document(), test_deterministic(), test_duplicate_headings_get_unique_ids_in_order() (+37 more)

### Community 52 - "evaluation/cli.py"
Cohesion: 0.07
Nodes (31): _compare(), default_security_output_path(), format_security_summary(), format_summary(), main(), _retrieval(), _security(), _unanswerable_line() (+23 more)

### Community 53 - "FallbackRetriever"
Cohesion: 0.08
Nodes (29): Fallback authorization invariant (same ResolvedAccess), BM25Retriever (identity, lexical), classify_model_error, classify_qdrant_error, Qdrant client lifecycle gap, eval-compare by served strategy (mixed refused), FallbackRetriever, Hugging Face error shapes (T1 As-built) (+21 more)

### Community 54 - "hashing.py"
Cohesion: 0.23
Nodes (13): _copy_seed(), h(), _load(), test_absent_optional_fields_hash_as_null(), test_body_change_changes_content_hash(), test_content_hash_is_stable_and_pinned(), test_crlf_and_lf_bodies_hash_identically(), test_lote_languages_keep_stored_order() (+5 more)

### Community 55 - "BgeM3Embedder"
Cohesion: 0.08
Nodes (15): BgeM3Embedder, _group_installed(), EmbedderInfo, OptionalDependencyError, group_installed(), test_constructing_does_not_load_the_model(), test_device_none_before_load_and_recorded_after(), test_missing_group_at_load_raises_optional_dependency_error() (+7 more)

### Community 56 - "Development Workflow"
Cohesion: 0.10
Nodes (32): Evaluation Suite includes goldens, refusal, multilingual, security, regression, Finalized stack: Python/FastAPI, Next.js, Qdrant, SQLite FTS5, BGE-M3, Bedrock, Langfuse, CloudWatch, Terraform ap-south-1, GitHub Actions, agent-skills sync, D001 Python-first backend, D002 RAG as reusable internal package, D003 Knowledge outside RAG package, D005 Documents are truth; chunks are derived, D007 Public-only Phase 1 (+24 more)

### Community 57 - "retrieval_eval.py"
Cohesion: 0.07
Nodes (35): Implementation, Review, T5 — round 1, User decision, Review, T4 review follow-ups (planner amendment 2026-11-02), T5 — Security gate across chunkers, Verification (+27 more)

### Community 58 - "dense"
Cohesion: 0.04
Nodes (56): Decisions D056-D062, Spec 008 Retrieval Fallback Design, Security gate five paths, result 1.2, _UnavailableDense (harness-only fault injection), 008 — Retrieval Fallback Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria (+48 more)

### Community 59 - "json"
Cohesion: 0.10
Nodes (19): chunker, context_prefix, name, overlap_tokens, target_tokens, version, embedder, batch_size (+11 more)

### Community 60 - "Evaluation Phase 1 framework (Spec 006)"
Cohesion: 0.06
Nodes (39): D042-D047, D053, D054 evaluation decisions, Evaluation architecture (Evaluation Suite case types), Evaluation assets never written by evaluation code (C6); candidates suggested and human-activated, Ingestion eligibility is the only guard against synthetic/unapproved documents; poisoned_public_document is not an authorization case, Evaluation isolation and gates, models.py, suite.py (tolerant typed cases, read-only load_suite), retrieval_eval.py, slices.py, sections.py, schemas.py, validate.py (referencing registry, validate-evaluation checks) (+31 more)

### Community 61 - "EvaluationHarnessError"
Cohesion: 0.10
Nodes (20): R11 — Security gate (`security_index.py`, `security_eval.py`), Implementation, Review, T8 — round 1, User decision, T10 — Documentation, decisions and hand-off, Verification, EvaluationHarnessError (+12 more)

### Community 62 - "Retrieval fallback (Spec 008, D056-D062)"
Cohesion: 0.07
Nodes (34): Answerability / insufficient-evidence decision, Authorization applied inside each retriever before fusion, never after RRF, reranking or generation, Authorization filter is part of the Qdrant query so unauthorized points never leave the store, Amazon Bedrock generation, bm25 builds no embedder and no Qdrant client, check_hit (fail-closed re-check, second line of defense), Citation validation, Context builder (planned) (+26 more)

### Community 63 - "ChunkerIdentity"
Cohesion: 0.08
Nodes (25): 009 — Chunking Experiments Design, Alternatives / deferred decisions, Chunker identity, settings and configuration (R5), Components / boundaries, Data flow, Design summary, Distinct-document metrics (R7), Error and failure behavior (+17 more)

### Community 64 - "test_legacy_baseline_snapshot.py"
Cohesion: 0.12
Nodes (15): clean_env(), _Factory, _FixedDatetime, _record_opens(), note(), wrap_func(), inner(), wrap_method() (+7 more)

### Community 65 - "test_index_contract.py"
Cohesion: 0.10
Nodes (20): compare(), mismatch_message(), base_settings(), test_authorization_and_language_fields_are_separate(), test_build_index_settings_records_embedder_and_chunker(), test_build_payload_copies_document_and_chunk(), test_collection_name_derivation(), test_compare_equal_and_ignores_hash_contract() (+12 more)

### Community 66 - "make eval-retrieval"
Cohesion: 0.12
Nodes (17): --allow-fake (plumbing only, never a recorded baseline), make retrieval-baseline (legacy, frozen Spec 005 producer), BASELINE_ARGS (--embedder, --allow-fake, --top-k, --suite, --release, --output, --config), Baseline metrics HitRate@5, random expectation min(1,5/N), Recall@5, MRR, p50/p95 latency, experiments/results/retrieval-baseline-<index_version>-<UTC>.json, never overwritten, D036 binding rules, D053 result 2.1, eval-retrieval exit 0 or 2 (+9 more)

### Community 67 - "Spec 007 hybrid retrieval"
Cohesion: 0.08
Nodes (36): build_retriever, make index-lexical, lexical package: lexical-v1 tokenizer, FTS5 store, builder, Current goal: Specs 001-008 complete; Spec 008 verified and merged into main (1107b67), plan next spec, Known issue: BM25 statistics corpus-wide per file; needs per-scope files for roles, Known issue: legacy chillu sequence does not match atomic chillu in BM25, Known issue: evaluation-data gaps (ml goldens, relevant_section_ids empty), Known issue: g004 overlaps u001, keep_both (+28 more)

### Community 68 - "DenseRetriever"
Cohesion: 0.09
Nodes (42): 007 — Hybrid Retrieval Design, Alternatives / deferred decisions, Data flow, Error and failure behavior, Interfaces / models, Observability, Phase 2 compatibility / migration, Security / authorization (+34 more)

### Community 69 - "test_applicability.py"
Cohesion: 0.16
Nodes (29): active_lote_codes(), _read_only_connection(), _active_list(), resolve_lote(), build_lexical(), _doc_sets(), _dropped_lote_setup(), DroppedFilterIndex (+21 more)

### Community 70 - "embedder"
Cohesion: 0.11
Nodes (17): chunker, context_prefix, name, overlap_tokens, target_tokens, version, embedder, batch_size (+9 more)

### Community 71 - "Phase 1 RAG query pipeline"
Cohesion: 0.17
Nodes (13): Deduplication, context budgeting, evidence ordering, Roadmap 9 - Reranking + context building, Reranker failure to hybrid results, Small documents and chunking strategy, Citation strategy (backend-owned validation), FAQ-aware retrieval experiment, Hybrid retrieval (dense + BM25 + RRF), Production knowledge corpus (+5 more)

### Community 72 - "build_lexical_index"
Cohesion: 0.09
Nodes (28): Implementation, Review, embedder_identity(), build_lexical_index(), chunk_identity(), _insert(), lexical_index_path(), production_entries() (+20 more)

### Community 73 - "Target repository shape (apps, packages, knowledge, sources, evaluation, tests, config, experiments, analytics, prompts, docs, infra)"
Cohesion: 0.17
Nodes (12): AccessContext(role, tenant_id) with blank tenant refused, Future agent folders intentionally not created, apps/api (FastAPI application layer), apps/web (Next.js/TypeScript frontend: recruiter assistant, RAG Lab, engineering views), core/access.py (Role, frozen AccessContext), guest_access, Knowledge model metadata (document_id, document_version, tenant_id, access_scope, lote_languages, content_language, source_authority...), No language filter, score threshold or reranking yet (+4 more)

### Community 74 - "test_manifest_validation.py"
Cohesion: 0.25
Nodes (19): metadata(), record(), run(), test_duplicate_document_id_rejected(), test_duplicate_document_version_rejected(), test_frontmatter_errors(), test_frontmatter_missing_required_field(), test_frontmatter_parsing_keeps_dates_as_strings() (+11 more)

### Community 75 - "Section: Next step"
Cohesion: 0.11
Nodes (17): Atomic publish and rollback, Phase 2 audit trail, AWS deployment architecture (ap-south-1), Controlled document-change workflow (Release Candidate), CI/CD pipeline, Evaluation governance states, Evaluation slices, Evaluation Suite (public-eval-v1) (+9 more)

### Community 76 - "BM25Retriever"
Cohesion: 0.06
Nodes (58): As-built notes, Components / boundaries, Design summary, Package / file placement, R10 — `eval-compare` identity rules (`compare.py`), R12 — Docker test, R1 — Suite v2, R4 — `make index-lexical` (`lexical/cli.py`) (+50 more)

### Community 77 - "retrieval/test_cli.py"
Cohesion: 0.15
Nodes (23): _advice_ok(), clean_env(), Factory, indexed(), ingest(), retrieve(), test_bad_args_exit_2_without_client(), test_bad_config_exit_2_without_client() (+15 more)

### Community 78 - "embedder"
Cohesion: 0.14
Nodes (13): chunker, max_chunk_chars, name, version, embedder, batch_size, fake_vector_size, model_id (+5 more)

### Community 79 - "repositories/__init__.py"
Cohesion: 0.06
Nodes (35): DocumentNotFoundError, DocumentRepositoryError, DocumentValidationError, DuplicateDocumentError, ManifestValidationError, split_frontmatter(), _StringDateLoader, compute_body_sha256() (+27 more)

### Community 80 - "FakeTokenizer"
Cohesion: 0.06
Nodes (43): As-built notes, Carry-over clean-ups (R11), Cross-index comparison (R8), Security gate (R9), Testing / evaluation strategy, 009 — Chunking Experiments: Retrospective Review, Cross-task consistency, Deviations from the approved plan (+35 more)

### Community 81 - "list_eligible_documents"
Cohesion: 0.20
Nodes (16): eligible_ids(), IgnoresQueryRepository, make_document(), test_active_approved_public_document_is_eligible(), test_language_filter_narrows_eligible_documents_only(), test_language_metadata_does_not_broaden_access(), test_local_repository_applies_the_policy_query(), test_non_active_lifecycle_is_excluded() (+8 more)

### Community 82 - "Ingestion pipeline (Spec 004)"
Cohesion: 0.09
Nodes (22): default_strategy, fusion, candidate_depth, k, method, weights, lexical, tokenizer (+14 more)

### Community 83 - "rrf_fuse"
Cohesion: 0.24
Nodes (12): rrf_fuse(), chunk(), test_both_legs_empty(), test_duplicate_in_a_leg_counts_best_rank_only(), test_empty_leg_keeps_the_other_order(), test_equal_scores_and_ranks_break_by_point_id(), test_equal_scores_break_by_best_rank_before_point_id(), test_first_seen_chunk_is_kept() (+4 more)

### Community 84 - "AccessContext"
Cohesion: 0.08
Nodes (26): Alternatives / deferred decisions, AccessContext, Role, test_blank_tenant_refused(), test_empty_tenant_refused(), test_no_language_or_scope_fields(), test_roles_match_policy_file(), test_tenant_is_stripped() (+18 more)

### Community 85 - "test_bm25.py"
Cohesion: 0.16
Nodes (24): LexicalRow, build(), dense_fixture(), DroppedClauseIndex, guest(), pub(), retriever(), _shape() (+16 more)

### Community 86 - "LexicalIndex"
Cohesion: 0.05
Nodes (42): R4/R5 — Lexical store (`lexical/store.py`, `lexical/build.py`), Review, T3 — round 1, User decision, T3 — `lexical-v1` tokenizer, lexical store and `make index-lexical`, Verification, As-built notes, Components / boundaries (+34 more)

### Community 87 - "Backend stack"
Cohesion: 0.12
Nodes (20): Backend stack, Custom retrieval metrics (plain Python), DeepEval (not yet a dependency), Evaluation tooling, FastAPI, Generation/e2e metrics (correctness, faithfulness, citations, refusal), GitHub Actions, httpx (+12 more)

### Community 88 - "embedder"
Cohesion: 0.14
Nodes (13): chunker, max_chunk_chars, name, version, embedder, batch_size, fake_vector_size, model_id (+5 more)

### Community 89 - "D023 Task-gated agent workflow"
Cohesion: 0.12
Nodes (16): allowed_scopes, current_release, default_role, implemented_roles, allowed_scopes, allowed_scopes, roles, admin (+8 more)

### Community 90 - "Path"
Cohesion: 0.14
Nodes (18): build_security_repository(), _fixture_files(), clean_env(), copy_fixtures(), _lexical_work_dir(), spy_lexical_path(), strip_forbidden_terms(), test_cli_clause_less_lexical_store_exits_one_naming_strategies() (+10 more)

### Community 91 - "test_schemas.py"
Cohesion: 0.16
Nodes (8): load_schemas(), test_existing_schema_is_referenced_not_copied(), test_missing_schema_is_configuration_error(), test_per_type_required_field_enforced(), test_schema_files_are_valid_draft_2020_12(), test_valid_rows_pass(), manifest(), test_v1_manifest_differs_only_in_status()

### Community 92 - "Roadmap 12 - Security"
Cohesion: 0.10
Nodes (22): Answerability and insufficient-evidence response, Authorization regression and staff canary, Docker, Terraform, EC2, ECR, CloudWatch, IAM, Bedrock, Bedrock Runtime (roadmap), BGE-M3 (roadmap), Citation manipulation tests and input/cost limits, Backend-owned citation validation, FastAPI skeleton (+14 more)

### Community 93 - "pathlib"
Cohesion: 0.25
Nodes (9): apps/api, apps/web, CloudWatch, Future multimodal mock-test evaluation, Langfuse tracing, packages/core, packages/observability, packages/rag (+1 more)

### Community 94 - "Spec status table"
Cohesion: 0.12
Nodes (19): Completion: retrospective, Spec-Review commit, merge, verified status, Spec orchestrator loop (route, role subagents, user approval, merge), GET /health endpoint, make setup, packages core/rag/observability skeletons, task-gated spec skills and skills-sync, task State lifecycle and spec/NNN branches, uv workspace and uv.lock (+11 more)

### Community 95 - "DenseIndex"
Cohesion: 0.13
Nodes (8): DenseIndex, dense_pair(), production_lexical(), real_hybrid(), test_empty_bm25_leg_keeps_the_dense_order(), test_fusion_receives_only_the_legs_checked_hits(), spy(), test_hybrid_result_shape()

### Community 96 - "test_slices.py"
Cohesion: 0.13
Nodes (13): active_registry_languages(), aggregate(), _mean(), slice_by(), source_authority_key(), row(), test_absent_languages_from_a_temp_registry(), test_missing_registry_section_is_a_configuration_error() (+5 more)

### Community 97 - "SpyIndex"
Cohesion: 0.15
Nodes (17): Admin content management, Agent capabilities only where they solve a real product problem, Audit trail, Basic analytics, Candidate evaluation, Change impact analysis, Content hashing, Evaluation Governance (keep/modify/deprecate/replace) (+9 more)

### Community 98 - "transcript_metrics.py"
Cohesion: 0.17
Nodes (12): analyse(), category(), command_kinds(), executed_text(), expand(), main(), parse_time(), render() (+4 more)

### Community 99 - "CURRENT_STATE.md"
Cohesion: 0.13
Nodes (14): interval, retries, start_period, test, timeout, container_name, healthcheck, image (+6 more)

### Community 101 - "D035 One filter builder, fail-closed re-check, same path for later fallbacks (Spec 005)"
Cohesion: 0.17
Nodes (20): DenseIndex, build_access_filter, check_hit, DenseRetriever, FallbackRetriever and open_retrieval wiring (merged 1107b67), make retrieve guest/public CLI, Strategy Protocol, BM25Retriever, rrf_fuse, HybridRetriever, Spec 008 retro F4: duplicated standalone open wiring, BM25Retriever, build_access_filter, check_hit fail-closed re-check (+12 more)

### Community 102 - "AWS target"
Cohesion: 0.06
Nodes (38): Source documents are truth; chunks, embeddings, sparse entries, Qdrant points and preview indexes are derived artifacts, Roadmap 11 - Observability, Langfuse traces, Stage latency, model/tokens/cost, release/config IDs, Full agent orchestration (avoided), Intentionally avoided choices, AWS target, Bedrock Agents / AgentCore for Phase 1 (avoided) (+30 more)

### Community 103 - "make ingest"
Cohesion: 0.08
Nodes (34): bm25 strategy, bm25 needs neither Qdrant nor the bge-m3 extra (Spec 008), config/retrieval.yaml schema 1.1 (default_strategy hybrid, qdrant.connect_timeout_s 2, query_timeout_s 3; 1.0 refused), dense strategy, --strategy dense needs no lexical file, docker compose up -d / down (local Qdrant), Embedder pair from index_settings or dense_identity; fallback-only 2.2 file compares against Spec 007 bm25 file, Environment: QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION_BASE, W2A_TENANT_ID (+26 more)

### Community 104 - "Retrieval package (Spec 005 and 007)"
Cohesion: 0.14
Nodes (12): graphify skill pointer, spec/NNN branch and Spec-Task trailers, spec-implementer skill (one task per run), spec-orchestrator skill, spec-planner skill, spec-reviewer retrospective skill, Task-gated agent workflow loop, task-reviewer skill (read-only) (+4 more)

### Community 105 - "dense_equivalence.py"
Cohesion: 0.13
Nodes (17): UnanswerableCase, deterministic_clock(), equivalence_suite(), run_equivalence(), chunks_per_document_dense(), default_eval_extras(), golden(), suite_of() (+9 more)

### Community 106 - "Qdrant (vector database)"
Cohesion: 0.14
Nodes (13): Authorization metadata (access_scope, owner_user_id, tenant_id), Engineering Conventions, IDs and versions conventions, Knowledge files with provenance, Language metadata (content_language, lote_languages), Logging and tracing hygiene, Domain naming terms, Prompts as versioned assets (+5 more)

### Community 107 - "Review"
Cohesion: 0.17
Nodes (7): Review, _path_strategy(), security_document(), security_run_record(), SecurityReport, SecurityIndex, test_a_forbidden_hit_injected_into_a_path_fails_the_gate_naming_it()

### Community 108 - "D057 Failure classification: one fallback-eligible error (Spec 008)"
Cohesion: 0.32
Nodes (8): RetrievalUnavailableError and availability classification, Next step 6: Spec 008 T7 real runs 1-3, retrieval-evaluation-idx-v1-20261101T070736Z.json Qdrant-up run, T7 Run 3: bm25 on closed port works; default exits 2 OptionalDependencyError, classify_model_error, classify_qdrant_error, D057 Failure classification: one fallback-eligible error (Spec 008), RetrievalUnavailableError

### Community 109 - "FakeEmbedder"
Cohesion: 0.18
Nodes (11): FakeEmbedder, test_conforms_to_protocol(), test_declared_vector_size(), test_default_size_is_64(), test_fake_device_is_none(), test_info_reports_fake_identity(), test_invalid_vector_size_rejected(), test_no_pytorch_import() (+3 more)

### Community 110 - "sync_agent_skills.py"
Cohesion: 0.31
Nodes (9): discover_skills(), expected_tree(), find_problems(), inject_frontmatter(), main(), managed_skills(), read_tree(), remove() (+1 more)

### Community 111 - "test_content_hash.py"
Cohesion: 0.15
Nodes (12): Approved packages, pricing and validity, Six approved packages and prices, 60-day package validity, 24-hour cancellation notice, Personal coaching package, 60-minute coaching session on Google Meet, Individual coaching and live appointments, Mock assessments, scoring, feedback and review windows (+4 more)

### Community 112 - "Spec 005 dense retrieval baseline"
Cohesion: 0.14
Nodes (18): AccessContext, Role, W2A_TENANT_ID, make retrieval-baseline legacy frozen, BGE-M3 device mps not pinned (D038), Spec 005 retrospective findings F3-F5, Next step 2: real BGE-M3 baseline committed, experiments/results/retrieval-baseline-idx-v1-20261023T063534Z.json real BGE-M3 baseline, Spec 005 dense retrieval baseline, Spec 005 status: verified 2026-10-23 merged b33462e (+10 more)

### Community 113 - "test_violation_names_the_document_from_the_error_attribute"
Cohesion: 0.18
Nodes (12): AGENTS.md Project Rules, DocumentRepository Abstraction, Evaluation Governance Rules, Language Separation Rules, Phase 1 Scope, Task-gated Spec Loop, CLAUDE.md Project Instructions, graphify Knowledge Graph Rules (+4 more)

### Community 114 - "test_lexical_build.py"
Cohesion: 0.10
Nodes (29): build_production(), ingest_dense(), open_lexical(), payload(), repository(), rewrite_settings(), synthetic_entries(), test_bind_does_not_write_to_qdrant() (+21 more)

### Community 115 - "load_retrieval_config"
Cohesion: 0.27
Nodes (9): load_retrieval_config(), test_committed_config_loads(), test_good_config_loads(), test_invalid_config_is_refused_naming_the_field(), test_lexical_strategies_need_the_lexical_index(), test_timeout_bounds_are_inclusive(), test_unreadable_and_non_mapping_files_are_refused(), variant() (+1 more)

### Community 116 - "fusion"
Cohesion: 0.20
Nodes (12): English, Malayalam and mixed queries, FAQ-aware retrieval/indexing, Roadmap 7 - Chunking experiments, Roadmap 8 - Multilingual retrieval, Language applicability handling, Parent-heading context and order-independent section_ids, Recursive chunking baseline, Optional semantic chunking (+4 more)

### Community 117 - "SQLite FTS5"
Cohesion: 0.11
Nodes (20): Local multilingual BGE reranker, BM25 via FTS5 bm25(), Derived local lexical file per collection, Device not pinned, recorded in results (D038), Embeddings, Deterministic fake embedder, Fusion, Lexical store (+12 more)

### Community 118 - "Development Workflow"
Cohesion: 0.21
Nodes (12): Branching and commits (spec/NNN, Spec-Task trailer), Development Workflow, Multi-agent handoff, Implementation rule: BLOCKED spec issue, Phase discipline, Protected source-of-truth data, Required spec-reviewer retrospective, Agent skills (orchestrator, planner, implementer, task-reviewer, spec-reviewer) (+4 more)

### Community 119 - "EvaluationConfigurationError"
Cohesion: 0.13
Nodes (15): EvaluationConfigurationError, CaseBase, DatasetRef, GoldenCase, SecurityCase, SuiteManifest, declared_release_id(), inside() (+7 more)

### Community 120 - "failing_client"
Cohesion: 0.18
Nodes (10): content-hash-v1 (sole change-detection signal), LocalDocumentRepository, Document manifest and JSON Schema validation, make validate-knowledge, persona_scope spec defect (F2), BgeM3Embedder (optional extra, pinned revision), Embedder Protocol and FakeEmbedder, HeadingChunker and slugify rule (+2 more)

### Community 121 - "test_status_handling.py"
Cohesion: 0.20
Nodes (8): Adding a New Language Guide, language_registry.json, Public Assistant Content Boundaries, access_scope, content_language, Knowledge Schema and Metadata, language_scope, lote_languages

### Community 122 - "DroppedClauseLexical"
Cohesion: 0.20
Nodes (5): DroppedClauseLexical, wrapper(), test_a_dropped_lexical_clause_names_the_four_lexical_paths(), test_a_lexical_store_without_the_clause_fails_bm25_and_hybrid(), __init__()

### Community 123 - "Spec 009 — Task reviews"
Cohesion: 0.14
Nodes (13): Implementation, Implementation, Implementation, Implementation, Review, Spec 009 — Task reviews, T1 — round 1, T3 — round 1 (+5 more)

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
Cohesion: 0.17
Nodes (12): BM25, Deterministic regression gates, Golden, refusal and security cases, HitRate@5, Roadmap 5 - Evaluation framework, Roadmap 6 - Hybrid retrieval, Roadmap 15 - CI/CD + regression gates, Language/domain slices (+4 more)

### Community 131 - "RuntimeSettings"
Cohesion: 0.33
Nodes (9): NAATI CCL candidate rules and test-day setup, Direct first-person speech requirement, Report technical incidents within 24 hours, NAATI, Online proctoring with separate phone or tablet, Prohibited materials and tools, Recording under 20 minutes, One repeated segment per dialogue without penalty (+1 more)

### Community 132 - "test_goldens.py"
Cohesion: 0.19
Nodes (12): declared_release_id(), load_golden_cases(), load_suite(), SuiteRef, test_declared_release(), test_filtering_in_temporary_suite(), test_invalid_line_names_file_and_line_only(), test_path_escaping_repo_root_refused() (+4 more)

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
Cohesion: 0.16
Nodes (15): Pydantic document models and enums, EligibilityPolicy for guest/public, LocalDocumentRepository with manifest schema validation, make validate-knowledge, Spec 002 decisions made before approval (content_hash, fixtures, validate-knowledge), Seed data status: 13 public docs, evaluation datasets, security fixtures, Spec 002 retrospective findings F1-F6, Spec 002 document model and repository (+7 more)

### Community 137 - "007 — Hybrid Retrieval Tasks"
Cohesion: 0.18
Nodes (10): 007 — Hybrid Retrieval Tasks, Out of this spec, T1 — Evaluation Suite `public-eval-v2`, T7 — `eval-compare` identity rules, T8 — Security gate for BM25 and hybrid, Docker isolation test, T9 — Strategy comparison and default-strategy decision (user-owned gate), Verification, Verification (+2 more)

### Community 138 - "Evaluation Framework Goal"
Cohesion: 0.39
Nodes (8): NAATI CCL test format, scoring and results, NAATI CCL test, Deduction-based assessment, Begin interpreting within five seconds of chime, NAATI, CCL is not professional interpreter certification, Pass requirement 63/90 overall and 29/45 per dialogue, Results within 4-6 weeks

### Community 139 - "test_failed_write_removes_partial_file"
Cohesion: 0.20
Nodes (3): clean_env(), seeded(), test_failed_write_removes_partial_file()

### Community 141 - "BGE-M3 (initial embedding model)"
Cohesion: 0.38
Nodes (6): Evaluation Candidates File, Evaluation Package (evaluation/), Evaluation Suite and Case-type Schemas, validate-evaluation, T2 Schemas and validate-evaluation, T7 Candidates

### Community 142 - "Way2Australia AI Platform Master Implementation Plan"
Cohesion: 0.29
Nodes (7): eval-retrieval, Retrieval Result Document 2.0, Section-level Metrics, Slices and small_sample, Unanswerable Reporting, T3 Retrieval Runner, T4 Unanswerable Reporting

### Community 143 - "Eligible failures: Qdrant connect/network, Qdrant timeout, model load/download failure with network __cause__"
Cohesion: 0.32
Nodes (8): classify_model_error, classify_qdrant_error, D057 Fallback eligibility classification, D062 5xx not eligible, Eligible failures: Qdrant connect/network, Qdrant timeout, model load/download failure with network __cause__, FallbackReason (qdrant_unavailable, qdrant_timeout, model_unavailable), RetrievalUnavailableError(reason), Non-fallback failures exit 2 (missing extra, model failure w/o network cause, HTTP error status, missing collection, mismatch, stale lexical file, authorization error)

### Community 144 - "eval-compare"
Cohesion: 0.29
Nodes (7): AGENTS.md, Claude adapter, Initial specs, Phase 0 - Project bootstrap, Project context files, SDD workflow (Spec 003 task-gated agent workflow), Stable command interface

### Community 145 - "Payments, account access and support boundaries"
Cohesion: 0.29
Nodes (6): Vocabulary, flashcards and free access, Spaced-repetition flashcards, Free access allowance, 12 subject domains plus General vocabulary, Approved public learning samples, Sample neighbour-greeting dialogue

### Community 146 - "make eval-compare"
Cohesion: 0.15
Nodes (14): results.py, compare.py (reads 1.0, 2.0, 2.1; quality gate; identity refusals), D061 fallback marking, eval-compare exit 0 pass, 1 gate failure, 2 refusal, WARNING flipped hit->miss / miss->hit lines (<case_id> v<case_version>), Gate: fail if more than 1 fewer hit cases or MRR drop above 1/n, Fallback path latency marked 'includes failed dense attempt' (informational), Not-comparable refusals (suite, case sets, top_k, fake, collection, index_version, embedder, lexical index, mixed served strategies), BASE and CANDIDATE variables (+6 more)

### Community 147 - "make test"
Cohesion: 0.33
Nodes (6): 006 Evaluation Framework Design, Decision Brief Q1-Q10, 006 Evaluation Framework Requirements, Evaluation Framework Goal, 006 Spec Retrospective Review, Retrospective Round 1 PASS

### Community 148 - "Mission"
Cohesion: 0.33
Nodes (5): Evaluation case_id and case_version, Versioning and Releases, document_id and document_version, Phase 2 Knowledge Release Candidates, Release seed-v1

### Community 149 - "test_fallback.py"
Cohesion: 0.12
Nodes (24): access(), client_at(), closed_port(), Fallback, open_hybrid(), Primary, run_cli(), stalled_port() (+16 more)

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

### Community 155 - "tokenizer.py"
Cohesion: 0.06
Nodes (18): R3 — Tokenizer `lexical-v1` (`lexical/tokenizer.py`), _is_token_char(), LexicalTokenizer, query_terms(), _query_terms_from(), QueryTerms, replace_sequences(), tokenize() (+10 more)

### Community 158 - "Orchestrator State Machine"
Cohesion: 0.50
Nodes (4): Mission, Phase 1 public/guest vs Phase 2 Knowledge Operations, Mission purpose: grounded multilingual RAG assistant, Useful product, engineering learning, portfolio evidence

### Community 159 - "way2australia_api/__init__.py"
Cohesion: 0.50
Nodes (3): Coaching is optional, Way2Australia public offering and assistant scope, English-Malayalam CCL preparation offering

### Community 160 - "Project Context README"
Cohesion: 0.50
Nodes (4): 120+ practice dialogues, Materials and dialogue practice, Recordings stay in browser, No automatic score in ordinary practice

### Community 161 - "Authorization enforced before generation"
Cohesion: 0.29
Nodes (6): Authorization model (guest/public), Graceful degradation, Poisoned public document fixture, Security plan (threats and controls), SQLite FTS5 fallback, Staff-only canary fixture

### Community 167 - "api/__init__.py"
Cohesion: 0.67
Nodes (3): Frontend stack, Next.js, TypeScript

### Community 168 - "Implementation"
Cohesion: 0.29
Nodes (5): Implementation, Review, Spec 010 — task reviews, T2 — round 1, test_fusion_and_hybrid_are_unchanged()

### Community 169 - "DocumentRepository Protocol (async)"
Cohesion: 0.33
Nodes (6): DocumentRepository Protocol (async), KnowledgeDocument model, Spec 002 retrospective round 1, Spec 002 task review log (T3-T9), Spec 002 Document model and repository (verified), Acceptance dry run on Spec 002 T3

### Community 170 - "tests/evaluation/__init__.py"
Cohesion: 0.67
Nodes (3): Canonical document metadata, Chunk metadata, Source authority precedence

### Community 191 - "continuity.py"
Cohesion: 0.18
Nodes (16): _case_keys(), compare_continuity(), _embedder_pair_from_doc(), _fmt_key(), _identity_refusals(), _info_lines(), _load_raw(), _lote_label() (+8 more)

### Community 192 - "canonical_json"
Cohesion: 0.47
Nodes (4): canonical_json(), _canonical_value(), _canonical_value_mapping(), test_canonical_json_is_sorted_compact_and_keeps_unicode()

### Community 193 - "DocumentRepository"
Cohesion: 0.29
Nodes (7): Roadmap 2 - Document model + repository, KnowledgeDocument, Manifest/schema validation, S3DocumentRepository and external storage, Document manifest, DocumentRepository, LocalDocumentRepository

### Community 194 - "test_run_retrieval_evaluation_on_multi_chunk_recursive_index"
Cohesion: 0.67
Nodes (4): _cosine_to_query(), test_run_retrieval_evaluation_on_multi_chunk_recursive_index(), _text_with_score_below(), make_payload()

### Community 196 - "git_state"
Cohesion: 0.40
Nodes (5): Implementation, Review, T9 — round 1, User decision, git_state()

### Community 198 - "Roadmap 13 - Graceful degradation"
Cohesion: 0.60
Nodes (5): Deferred serving concerns (circuit breaker, startup policy, Qdrant 5xx D062), Dense to BM25 degradation, Roadmap 13 - Graceful degradation, Qdrant failure to SQLite FTS5, Spec 008 early delivery (D056)

### Community 199 - "lexical/ package (Spec 007)"
Cohesion: 0.20
Nodes (10): D060 Standalone lexical freshness, Standalone freshness proves lexical file matches repository, not live Qdrant (D060), lexical/cli.py (make index-lexical writes only git-ignored file), Lexical file is a derived artifact, one per collection, bound by identity and chunk digest, freshness.py (verify_fresh, chunk digest recomputed from repository), lexical/ package (Spec 007), store.py (SQLite FTS5: chunks table, chunk_terms FTS5 table, settings row; LexicalIndex.open, bind_to, search), tokenizer.py (lexical-v1) (+2 more)

### Community 201 - "RuntimeSettings"
Cohesion: 0.08
Nodes (10): Implementation, Verification, default_client_factory(), RuntimeSettings, retrieval_client_factory(), LexicalConfig, QdrantTimeouts, settings() (+2 more)

### Community 203 - "failing_client"
Cohesion: 0.44
Nodes (6): bound_index(), failing_client(), test_document_count_and_chunk_identities_map_transport_errors(), test_open_maps_transport_errors(), test_other_client_errors_are_re_raised_unchanged(), test_search_maps_transport_errors()

### Community 204 - "test_every_path_is_gated_for_every_query"
Cohesion: 0.29
Nodes (4): test_every_path_is_gated_for_every_query(), counting(), test_the_gate_runs_all_three_strategies_on_v2(), counting()

### Community 207 - "Way2Australia AI Platform Master Implementation Plan"
Cohesion: 0.33
Nodes (6): Way2Australia AI Platform Master Implementation Plan, Phase 1 Definition of Done, Phase 1 Scope (public/guest RAG), Recruiter / portfolio story, Project Mission, Seven-day Phase 1 execution plan

### Community 208 - "T4 — round 1"
Cohesion: 0.67
Nodes (3): Implementation, T4 — round 1, User decision

## Ambiguous Edges - Review These
- `Task-gated agent workflow loop` → `graphify skill pointer`  [AMBIGUOUS]
  .claude/CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **380 isolated node(s):** `way2australia-api`, `way2australia-core`, `way2australia-observability`, `way2australia-rag`, `way2australia` (+375 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1398 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **32 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Change log` connect `BM25Retriever` to `test_compare.py`, `Spec 007 hybrid retrieval`, `DenseRetriever`, `git_state`, `LocalDocumentRepository`, `test_lexical_cli.py`, `007 — Hybrid Retrieval Requirements`, `LexicalIndex`, `EvaluationHarnessError`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Are the 84 inferred relationships involving `DenseIndex` (e.g. with `Design summary` and `Decisions resolved before drafting`) actually correct?**
  _`DenseIndex` has 84 INFERRED edges - model-reasoned connections that need verification._
- **What connects `way2australia-api`, `way2australia-core`, `way2australia-observability` to the rest of the system?**
  _380 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_compare.py` be split into smaller, more focused modules?**
  _Cohesion score 0.056862745098039215 - nodes in this community are weakly interconnected._
- **Why does `D055 Default strategy is hybrid (Spec 007)` connect `Spec 007 hybrid retrieval` to `Development Workflow`, `typing`, `Ingestion pipeline (Spec 004)`, `D035 One filter builder, fail-closed re-check, same path for later fallbacks (Spec 005)`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Are the 36 inferred relationships involving `LocalDocumentRepository` (e.g. with `Dependencies` and `Design summary`) actually correct?**
  _`LocalDocumentRepository` has 36 INFERRED edges - model-reasoned connections that need verification._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Task-gated agent workflow loop` and `graphify skill pointer`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._