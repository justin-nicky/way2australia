# Graph Report - way2australia  (2026-11-02)

## Corpus Check
- 283 files · ~309,355 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 32 file(s) not represented in the graph (top: (none) 20, .jsonl 9, .mdc 1)

## Summary
- 4291 nodes · 12735 edges · 190 communities (157 shown, 33 thin omitted)
- Extraction: 80% EXTRACTED · 20% INFERRED · 0% AMBIGUOUS · INFERRED: 2597 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5b25d8c0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- DenseRetriever
- Strategy
- opening.py
- test_bm25.py
- test_validate.py
- test_service.py
- service.py
- test_index.py
- dense
- evaluation/validate.py
- lexical/cli.py
- ChunkerIdentity
- HeadingChunker
- sync_agent_skills.py
- test_lexical_cli.py
- retrieval/test_cli.py
- Strategy Eval Tests
- RetrievalConfig
- Index Binding Errors
- Document Model Tests
- 007 — Hybrid Retrieval Requirements
- test_validate_knowledge.py
- Date and Policy Tests
- BGE-M3 Adapter
- test_lexical_standalone.py
- Spec 004 ingestion baseline
- tokenization.py
- retrieval_eval.py
- test_strategy_eval.py
- Evaluation CLI Tests
- chunking.py
- test_suite_v2.py
- test_baseline.py
- evaluation/test_cli.py
- test_content_hash.py
- .search
- 009 — Chunking Experiments Requirements
- 008 — Retrieval Fallback Requirements
- test_config_schema_11.py
- Evaluation Slices
- open_retrieval
- typing
- test_legacy_baseline_snapshot.py
- RuntimeSettings
- LocalDocumentRepository
- test_lexical_standalone.py
- LexicalIndex
- FilterDroppingIndex
- make eval-retrieval
- 007 — Hybrid Retrieval Requirements
- LocalRepositoryConfig
- HeadingChunker
- evaluation/cli.py
- FallbackRetriever
- repositories/__init__.py
- asyncio
- Development Workflow
- check_target_allowed
- EvaluationSchemas
- json
- make eval-security
- build_security_repository
- Target RAG query flow (User -> FastAPI -> validation -> AccessContext -> LanguageContext -> retrieval -> RRF -> reranker -> context builder -> answerability -> prompt -> Bedrock -> citation validation)
- BgeM3Embedder
- security_eval.py
- test_lexical_build.py
- make retrieve
- Spec 007 hybrid retrieval
- check_hit
- make index-lexical
- embedder
- AWS target
- EvaluationConfigurationError
- AccessContext
- Constitution
- Section: Next step
- Spec 007 - hybrid retrieval (verified 2026-10-28, merged 3cf70eb; 10 tasks)
- DocumentRepository
- test_repository_contract.py
- Spec 005 dense retrieval baseline
- chunking.py
- list_eligible_documents
- Ingestion pipeline (Spec 004)
- Retrieval fallback (Spec 008, D056-D062)
- IndexIdentity
- test_hybrid.py
- FakeEmbedder
- Backend stack
- embedder
- D023 Task-gated agent workflow
- Roadmap 13 - Graceful degradation
- test_schemas.py
- ingest_dense
- pathlib
- RetrievalConfigurationError
- documents/__init__.py
- SpyIndex
- HybridRetriever
- CURRENT_STATE.md
- QdrantIndexStore
- repositories/__init__.py
- 006 Evaluation Framework Tasks
- T2 — round 1
- Retrieval package (Spec 005 and 007)
- D035 One filter builder, fail-closed re-check, same path for later fallbacks (Spec 005)
- Qdrant (vector database)
- run_security_evaluation
- source_chunk_digest
- EmbedderInfo
- dense_equivalence.py
- test_content_hash.py
- SecurityIndex
- test_violation_names_the_document_from_the_error_attribute
- pytest
- test_bm25.py
- fusion
- evaluation/cli.py
- security_document
- evaluation/errors.py
- failing_client
- test_status_handling.py
- load_retrieval_config
- Spec 009 T3 — transcript extraction (facts only)
- QdrantIndexStore
- Baseline runner and result JSON
- test_failed_write_removes_partial_file
- Development Workflow
- test_status_handling.py
- absent_query_languages
- Roadmap 12 - Security
- RuntimeSettings
- Spec 009 T3 — transcript extraction (facts only)
- Vocabulary, flashcards and free access
- .search
- Roadmap 3 - Ingestion baseline
- Spec 002 document model and repository
- test_opening.py
- Evaluation Framework Goal
- build_security_index
- Spec 009 — Task reviews
- BGE-M3 (initial embedding model)
- Way2Australia AI Platform Master Implementation Plan
- T1 — round 1
- eval-compare
- Payments, account access and support boundaries
- canonical_json
- make test
- Mission
- test_fallback.py
- test_server_filter_keeps_every_forbidden_point_out
- Spec 004 retrospective round 1 (PASS)
- policy
- policy
- policy
- typing
- Way2Australia AI Platform Master Implementation Plan
- ForbiddenDenseIndex
- Orchestrator State Machine
- way2australia_api/__init__.py
- Project Context README
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
- test_every_path_is_gated_for_every_query

## God Nodes (most connected - your core abstractions)
1. `DenseIndex` - 105 edges
2. `LocalDocumentRepository` - 100 edges
3. `Strategy` - 76 edges
4. `FakeEmbedder` - 67 edges
5. `HeadingChunker` - 65 edges
6. `FakeTokenizer` - 64 edges
7. `open_retrieval()` - 64 edges
8. `IngestionConfigurationError` - 62 edges
9. `ResolvedAccess` - 62 edges
10. `DECISIONS.md architecture decision log` - 62 edges

## Surprising Connections (you probably didn't know these)
- `R10 — `eval-compare` identity rules (`compare.py`)` --references--> `_refusals()`  [INFERRED]
  .kiro/specs/007-hybrid-retrieval/design.md → packages/rag/src/way2australia_rag/evaluation/compare.py
- `Interfaces / models` --references--> `Chunk`  [INFERRED]
  .kiro/specs/009-chunking-experiments/design.md → packages/rag/src/way2australia_rag/ingestion/chunking.py
- `Acceptance criteria` --references--> `slugify()`  [INFERRED]
  .kiro/specs/009-chunking-experiments/requirements.md → packages/rag/src/way2australia_rag/ingestion/chunking.py
- `Error and failure behavior` --references--> `IngestionConfigurationError`  [INFERRED]
  .kiro/specs/009-chunking-experiments/design.md → packages/rag/src/way2australia_rag/ingestion/errors.py
- `Implementation` --references--> `_overlap_for_next_chunk()`  [INFERRED]
  .kiro/specs/009-chunking-experiments/task-reviews.md → packages/rag/src/way2australia_rag/ingestion/recursive.py

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

## Communities (190 total, 33 thin omitted)

### Community 0 - "DenseRetriever"
Cohesion: 0.07
Nodes (82): Implementation, Review, T7 — round 1, User decision, _changed(), compare(), Comparison, _delta_line() (+74 more)

### Community 1 - "Strategy"
Cohesion: 0.09
Nodes (22): Implementation, Review, Review, T6 — round 2, User decision, Acceptance criteria, R7 — Marking degraded results, document_leg_ranks() (+14 more)

### Community 2 - "opening.py"
Cohesion: 0.10
Nodes (33): Phase 2 compatibility / migration, Design summary, Phase 2 compatibility / migration, R5 — `bm25` without Qdrant or the extra (`bm25.py`), Security / authorization, Acceptance criteria, Dependencies, Implementation (+25 more)

### Community 3 - "test_bm25.py"
Cohesion: 0.13
Nodes (27): LexicalRow, DenseIndex, OddIdStore, build(), dense_fixture(), DroppedClauseIndex, guest(), pub() (+19 more)

### Community 4 - "test_validate.py"
Cohesion: 0.14
Nodes (31): edit_rows(), edit_suite(), root(), run(), test_active_golden_without_relevant_documents(), test_candidate_ineligible_document_is_not_unknown(), test_candidate_not_suggested(), test_candidate_referenced_by_suite() (+23 more)

### Community 5 - "test_service.py"
Cohesion: 0.14
Nodes (24): CountingEmbedder, doc(), Harness, test_bumped_document_version_updates(), test_changed_body_updates(), test_changed_metadata_field_updates(), test_chunk_shrink_leaves_no_orphan(), test_chunk_too_long_report_has_no_chunk_text() (+16 more)

### Community 6 - "service.py"
Cohesion: 0.12
Nodes (17): Implementation, Review, Chunk, IngestionError, check_chunks(), ChunkTooLongError, _effective_limit(), DocumentFailure (+9 more)

### Community 7 - "test_index.py"
Cohesion: 0.11
Nodes (42): IndexBindingError, bound_index(), client(), failing_client(), fake_info(), http_client(), make_settings(), open_index() (+34 more)

### Community 8 - "dense"
Cohesion: 0.08
Nodes (27): Components / boundaries, R10 — `eval-compare` identity rules (`compare.py`), R11 — Security gate (`security_index.py`, `security_eval.py`), R12 — Docker test, R1 — Suite v2, R4 — `make index-lexical` (`lexical/cli.py`), R6 — `BM25Retriever` (`retrieval/bm25.py`), R9 — Result format 2.1 (+19 more)

### Community 9 - "evaluation/validate.py"
Cohesion: 0.16
Nodes (16): Review, _candidate_rules(), problem(), _describe(), _document_problems(), EvaluationProblem, _promotion_problems(), _read_rows() (+8 more)

### Community 10 - "lexical/cli.py"
Cohesion: 0.09
Nodes (32): Implementation, Implementation, Implementation, Review, Review, T3 — round 1, T3 — round 2, User decision (+24 more)

### Community 11 - "ChunkerIdentity"
Cohesion: 0.07
Nodes (30): 009 — Chunking Experiments Design, Alternatives / deferred decisions, As-built notes, Carry-over clean-ups (R11), Chunker identity, settings and configuration (R5), Cross-index comparison (R8), Data flow, Design summary (+22 more)

### Community 12 - "HeadingChunker"
Cohesion: 0.13
Nodes (26): basic_suite(), build(), fusion_config(), run(), Scripted, scripted_run(), suite_with_unanswerable(), test_2_2_keys_on_a_plain_run() (+18 more)

### Community 13 - "sync_agent_skills.py"
Cohesion: 0.27
Nodes (9): discover_skills(), expected_tree(), find_problems(), inject_frontmatter(), main(), managed_skills(), read_tree(), remove() (+1 more)

### Community 14 - "test_lexical_cli.py"
Cohesion: 0.19
Nodes (19): lexical_dir(), _no_qdrant(), run(), test_bad_config_exits_2(), test_cased_name_cannot_write_into_the_real_repository(), test_default_embedder_identity_equals_the_bge_m3_adapter_identity(), test_env_dir_into_tracked_directory_is_refused(), test_file_holds_the_identity_and_no_chunk_text_is_printed() (+11 more)

### Community 15 - "retrieval/test_cli.py"
Cohesion: 0.16
Nodes (22): _advice_ok(), clean_env(), Factory, indexed(), ingest(), retrieve(), test_bad_args_exit_2_without_client(), test_bad_config_exit_2_without_client() (+14 more)

### Community 16 - "Strategy Eval Tests"
Cohesion: 0.08
Nodes (45): RetrievalUnavailableError and availability classification, standalone bm25 without Qdrant or extra (IndexIdentity, freshness), CURRENT_STATE.md current state document, Current goal: Specs 001-008 complete; Spec 008 verified and merged into main (1107b67), plan next spec, Evaluation Suite includes goldens, refusal, multilingual, security, regression, Phase 2 Knowledge Release workflow designed not implemented, Public/guest retrieval only in Phase 1; English + Malayalam, Known issue: Qdrant and Hugging Face 5xx not fallback-eligible (+37 more)

### Community 17 - "RetrievalConfig"
Cohesion: 0.04
Nodes (64): Decisions D056-D062, Spec 008 Retrieval Fallback Design, R2 — Qdrant timeouts (`qdrant_client.py`, `config/retrieval.yaml`), Security gate five paths, result 1.2, _UnavailableDense (harness-only fault injection), 008 — Retrieval Fallback Requirements, Acceptance criteria, Acceptance criteria (+56 more)

### Community 18 - "Index Binding Errors"
Cohesion: 0.06
Nodes (45): IndexSettingsMismatchError, compare(), IndexSettings, mismatch_message(), IndexedDocument, QdrantIndexStore, read_index_settings(), _DenseLike (+37 more)

### Community 19 - "Document Model Tests"
Cohesion: 0.10
Nodes (31): IndexPoint, DenseRetriever, client_with_forbidden(), test_forbidden_points_are_never_returned(), test_store_dropping_the_filter_fails_closed(), build_client(), docs(), guest() (+23 more)

### Community 20 - "007 — Hybrid Retrieval Requirements"
Cohesion: 0.05
Nodes (43): BM25Retriever with SQL access clause, eval-compare identity rules (R10), HybridRetriever (dense leg then BM25 leg, no single-leg fallback), lexical-v1 tokenizer (NFC, ZWJ/ZWNJ dropped, L/N/Mn/Mc token chars, 64-term cap), Result format 2.1 and security result 1.1, config/retrieval.yaml and build_retriever strategy factory, SQLite FTS5 lexical store (derived, git-ignored, bound to dense index), 007 — Hybrid Retrieval Requirements (+35 more)

### Community 21 - "test_validate_knowledge.py"
Cohesion: 0.21
Nodes (27): load(), test_bad_date_fails_loading_naming_document_and_field(), test_guest_policy_agrees_with_access_policy_config(), test_seed_corpus_still_loads(), test_valid_date_loads(), build_repo(), metadata(), problems_for() (+19 more)

### Community 22 - "Date and Policy Tests"
Cohesion: 0.08
Nodes (33): Interfaces / models, R1 — Failure classification (`errors.py`, `availability.py`), T1: Hugging Face error shapes (confirmed 2026-10-29), Testing / evaluation strategy, Review, classify_model_error(), classify_qdrant_error(), _optional_types() (+25 more)

### Community 23 - "BGE-M3 Adapter"
Cohesion: 0.06
Nodes (18): Model Preferences, Agent Skills README, Implementation Checklist, Spec Implementer Skill, task-reviews.md Implementation Block, Design Template, Change Log, Requirements Template (+10 more)

### Community 24 - "test_lexical_standalone.py"
Cohesion: 0.05
Nodes (33): Day-1 Usage, document_manifest.jsonl, golden_public.jsonl, Source-of-Truth Policy, chunking, overlap_tokens, strategy, target_tokens (+25 more)

### Community 25 - "Spec 004 ingestion baseline"
Cohesion: 0.12
Nodes (22): HeadingChunker heading v1 2000-char cap, Embedder Protocol, fake and BGE-M3 adapter, IngestionService change detection, make ingest and config/ingestion.yaml, 17-field PointPayload and UUIDv5 point IDs, QdrantIndexStore with companion settings collection, Heading chunking only synthetic-tested, none of 13 docs has headings, Spec 004 open review findings (T3 F1, T5 F2, T7 F1-F3, T8 F1, retro F1) (+14 more)

### Community 26 - "tokenization.py"
Cohesion: 0.08
Nodes (21): Components / boundaries, `recursive` v1 (R4), `structure` v1 (R3), Tokenizer (R1), Truncation guard (R2), T1 — Tokenizer and truncation guard, Verification, IngestionConfigurationError (+13 more)

### Community 27 - "retrieval_eval.py"
Cohesion: 0.05
Nodes (45): Review, T2 — v2 dense baseline (user-owned gate), Verification, Implementation, Review, T5 — round 1, User decision, Distinct-document metrics (R7) (+37 more)

### Community 28 - "test_strategy_eval.py"
Cohesion: 0.10
Nodes (28): User decision, build_lexical(), eval_world(), leg_order(), lexical_env(), make_world(), retrieve(), retrieve_world() (+20 more)

### Community 29 - "Evaluation CLI Tests"
Cohesion: 0.12
Nodes (31): assert_invalid(), document_fields(), make_document(), test_blank_required_text_is_rejected(), test_document_is_immutable(), test_duplicate_lote_languages_are_rejected(), test_effective_window_must_be_ordered(), test_empty_lote_languages_is_rejected() (+23 more)

### Community 30 - "chunking.py"
Cohesion: 0.13
Nodes (20): _char_split(), _merge_pieces(), _merge_word_pieces(), _parse_sections(), _Section, _split_body(), _split_long_unit(), split_to_token_budget() (+12 more)

### Community 31 - "test_suite_v2.py"
Cohesion: 0.14
Nodes (24): committed(), edit_jsonl(), lines(), manifest(), problems(), read_lines(), root(), test_candidates_differ_only_in_promoted_as() (+16 more)

### Community 32 - "test_baseline.py"
Cohesion: 0.10
Nodes (24): case(), clean_env(), cli_run(), DeviceStub, _git(), run(), seeded(), setup() (+16 more)

### Community 33 - "evaluation/test_cli.py"
Cohesion: 0.18
Nodes (16): clean_env(), index_factory(), real_factory(), run(), test_bad_top_k_exits_2(), test_existing_output_exits_2_before_qdrant(), test_fake_embedder_exits_2_before_qdrant(), test_filter_carries_the_server_tenant() (+8 more)

### Community 34 - "test_content_hash.py"
Cohesion: 0.19
Nodes (14): _copy_seed(), h(), _load(), test_absent_optional_fields_hash_as_null(), test_body_change_changes_content_hash(), test_content_hash_is_stable_and_pinned(), test_crlf_and_lf_bodies_hash_identically(), test_lote_languages_keep_stored_order() (+6 more)

### Community 36 - "009 — Chunking Experiments Requirements"
Cohesion: 0.07
Nodes (28): 009 — Chunking Experiments Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+20 more)

### Community 37 - "008 — Retrieval Fallback Requirements"
Cohesion: 0.09
Nodes (36): Baseline runner (refuses fake index without --allow-fake; HitRate@k, Recall@k, MRR, p50/p95, min(1,k/N) random expectation), Binding: embedder model ID, revision, vector size, normalization, fake flag and index_version must equal recorded IndexSettings, BM25Retriever(identity, lexical), BM25 statistics (IDF, avg length) computed over every row of a lexical file, build_access_filter (the only filter builder), build_retriever (only place a strategy name becomes a retriever), retrieval_client_factory (Qdrant client with configured timeouts), config/retrieval.yaml (default_strategy hybrid, RRF k 60, depth 50) (+28 more)

### Community 38 - "test_config_schema_11.py"
Cohesion: 0.08
Nodes (29): Review, load_ingestion_config(), collection_name(), default_lexical_dir(), lexical_index_path(), production_entries(), main(), _parser() (+21 more)

### Community 39 - "Evaluation Slices"
Cohesion: 0.06
Nodes (35): _is_token_char(), QueryTerms, tokenize(), clean_env(), _factory(), _run(), test_builds_exactly_one_embedder_per_run(), test_collection_base_comes_from_environment() (+27 more)

### Community 40 - "open_retrieval"
Cohesion: 0.12
Nodes (13): get_health(), HealthResponse, get_request_settings(), get_settings(), Settings, create_app(), isolate_settings_environment(), test_create_app_wires_settings() (+5 more)

### Community 41 - "typing"
Cohesion: 0.09
Nodes (34): 006-candidates.jsonl with 7 suggested rows, make eval-compare, make eval-security hard gate, result 2.2 and served-strategy eval-compare, eval-security five paths, governed suite loader and schemas, make validate-evaluation, Spec 006 retrospective findings (F1 byte-identity, eval-security not in verify) (+26 more)

### Community 42 - "test_legacy_baseline_snapshot.py"
Cohesion: 0.12
Nodes (15): clean_env(), _Factory, _FixedDatetime, _record_opens(), note(), wrap_func(), inner(), wrap_method() (+7 more)

### Community 43 - "RuntimeSettings"
Cohesion: 0.11
Nodes (11): Implementation, T1 — round 1, User decision, T3 — `bm25` without Qdrant or the `bge-m3` extra; one open path, Verification, RuntimeSettings, retrieval_client_factory(), QdrantTimeouts (+3 more)

### Community 44 - "LocalDocumentRepository"
Cohesion: 0.14
Nodes (27): LocalDocumentRepository, build(), guest_access(), new_base(), real_queries(), seed_repository(), spied(), SpyIndex (+19 more)

### Community 45 - "test_lexical_standalone.py"
Cohesion: 0.18
Nodes (19): build_from(), built(), copy_repository(), expected(), first_document_id(), open_it(), remove_document(), repo_at() (+11 more)

### Community 46 - "LexicalIndex"
Cohesion: 0.13
Nodes (14): Implementation, Lexical identity and per-document freshness (R6), _check_standalone_open(), build_lexical_index(), LexicalIndex, LexicalIndexBindingError, LexicalIndexError, LexicalSettings (+6 more)

### Community 48 - "make eval-retrieval"
Cohesion: 0.10
Nodes (28): BgeM3Embedder (optional bge-m3 extra, dense only), D025-D030, D032 ingestion decisions, DocumentRepository Protocol (get_document, list_documents), Embedder Protocol, FakeEmbedder (deterministic), GUEST_PUBLIC_POLICY, HeadingChunker (heading v1, character cap, stable section_id slugs), IndexSettings and mismatch comparison (+20 more)

### Community 49 - "007 — Hybrid Retrieval Requirements"
Cohesion: 0.09
Nodes (27): optional bge-m3 extra (sentence-transformers, PyTorch), D048 graphify tooling, make experiment CONFIG=... (target; records git commit, release, suite, chunker, embedder, strategy, metrics, latency), make format, Knowledge graph graphify (D048), /graphify . --update (user, once per spec after merge), graphify query / path / explain, graphify update . (+19 more)

### Community 50 - "LocalRepositoryConfig"
Cohesion: 0.16
Nodes (18): LocalRepositoryConfig, assert_matches_snapshot(), assert_recursive_chunks_whitespace_fidelity(), chunks_to_records(), collapse_whitespace(), load_snapshot(), snapshot_for_document(), test_agrees_with_day1_baseline() (+10 more)

### Community 51 - "HeadingChunker"
Cohesion: 0.08
Nodes (46): R3 — Tokenizer `lexical-v1` (`lexical/tokenizer.py`), HeadingChunker, _is_word_char(), slugify(), manifest_document_count(), assert_structure_chunks_whitespace_fidelity(), ids(), make_document() (+38 more)

### Community 52 - "evaluation/cli.py"
Cohesion: 0.10
Nodes (20): R8 — Result format 2.2 (`retrieval_eval.py`), _authority_map(), _compare(), default_security_output_path(), format_security_summary(), format_summary(), main(), _retrieval() (+12 more)

### Community 53 - "FallbackRetriever"
Cohesion: 0.08
Nodes (27): Fallback authorization invariant (same ResolvedAccess), BM25Retriever (identity, lexical), classify_model_error, classify_qdrant_error, Qdrant client lifecycle gap, eval-compare by served strategy (mixed refused), FallbackRetriever, Hugging Face error shapes (T1 As-built) (+19 more)

### Community 54 - "repositories/__init__.py"
Cohesion: 0.06
Nodes (12): _check_language_code(), KnowledgeDocument, collect(), _document_ids(), collect(), DocumentQuery, EligibilityPolicy, list_eligible_documents() (+4 more)

### Community 55 - "asyncio"
Cohesion: 0.21
Nodes (18): _copy_seed(), seed_repository(), test_documents_outside_approved_roots_are_never_loaded(), test_get_document_by_id_and_version(), test_get_document_missing_raises_not_found(), test_invalid_document_fails_load_without_leaking_paths(), test_invalid_schema_raises_repository_error(), test_language_filter_is_data_driven_and_does_not_affect_access() (+10 more)

### Community 56 - "Development Workflow"
Cohesion: 0.13
Nodes (25): Finalized stack: Python/FastAPI, Next.js, Qdrant, SQLite FTS5, BGE-M3, Bedrock, Langfuse, CloudWatch, Terraform ap-south-1, GitHub Actions, agent-skills sync, D001 Python-first backend, D002 RAG as reusable internal package, D003 Knowledge outside RAG package, D005 Documents are truth; chunks are derived, D007 Public-only Phase 1, D008 Language and authorization are independent (+17 more)

### Community 57 - "check_target_allowed"
Cohesion: 0.12
Nodes (18): Implementation, Review, T3 — round 3, User decision, check_target_allowed(), _inside_git_work_tree(), _is_git_ignored(), LexicalTargetRefusedError (+10 more)

### Community 59 - "json"
Cohesion: 0.08
Nodes (24): chunker, max_chunk_chars, name, version, embedder, batch_size, fake_vector_size, model_id (+16 more)

### Community 60 - "make eval-security"
Cohesion: 0.06
Nodes (37): D042-D047, D053, D054 evaluation decisions, Evaluation assets never written by evaluation code (C6); candidates suggested and human-activated, Ingestion eligibility is the only guard against synthetic/unapproved documents; poisoned_public_document is not an authorization case, Evaluation isolation and gates, models.py, suite.py (tolerant typed cases, read-only load_suite), retrieval_eval.py, slices.py, sections.py, schemas.py, validate.py (referencing registry, validate-evaluation checks), Section-level keys <document_id>#<section_id> (+29 more)

### Community 61 - "build_security_repository"
Cohesion: 0.12
Nodes (20): build_security_repository(), _fixture_files(), security_repository(), clean_env(), copy_fixtures(), _lexical_work_dir(), spy_lexical_path(), wrapper() (+12 more)

### Community 62 - "Target RAG query flow (User -> FastAPI -> validation -> AccessContext -> LanguageContext -> retrieval -> RRF -> reranker -> context builder -> answerability -> prompt -> Bedrock -> citation validation)"
Cohesion: 0.09
Nodes (27): Answerability / insufficient-evidence decision, Authorization applied inside each retriever before fusion, never after RRF, reranking or generation, Authorization filter is part of the Qdrant query so unauthorized points never leave the store, Amazon Bedrock generation, check_hit (fail-closed re-check, second line of defense), Citation validation, Context builder (planned), D035 Future fallbacks must take the same ResolvedAccess and call check_hit (+19 more)

### Community 63 - "BgeM3Embedder"
Cohesion: 0.11
Nodes (12): BgeM3Embedder, group_installed(), test_constructing_does_not_load_the_model(), test_device_none_before_load_and_recorded_after(), test_missing_group_at_load_raises_optional_dependency_error(), test_missing_group_refused_at_construction(), test_model_loaded_once_with_revision_and_batches(), fake_loader() (+4 more)

### Community 64 - "security_eval.py"
Cohesion: 0.16
Nodes (11): User decision, EvaluationHarnessError, _gate(), _lexical_sanity_check(), _open_lexical_sanity(), _sanity_check(), SecurityQuery, select_security_queries() (+3 more)

### Community 65 - "test_lexical_build.py"
Cohesion: 0.22
Nodes (16): identity(), payload(), synthetic_entries(), build(), test_atomic_replace_keeps_old_file_after_failure(), test_build_records_settings(), test_digest_is_stable_and_order_independent(), test_entry_without_identity_fields_is_refused() (+8 more)

### Community 66 - "make retrieve"
Cohesion: 0.06
Nodes (38): results.py, compare.py (reads 1.0, 2.0, 2.1; quality gate; identity refusals), make retrieve, --allow-fake (plumbing only, never a recorded baseline), make retrieval-baseline (legacy, frozen Spec 005 producer), BASELINE_ARGS (--embedder, --allow-fake, --top-k, --suite, --release, --output, --config), Baseline metrics HitRate@5, random expectation min(1,5/N), Recall@5, MRR, p50/p95 latency, experiments/results/retrieval-baseline-<index_version>-<UTC>.json, never overwritten, D053 result 2.1 (+30 more)

### Community 67 - "Spec 007 hybrid retrieval"
Cohesion: 0.08
Nodes (35): build_retriever, make index-lexical, lexical package: lexical-v1 tokenizer, FTS5 store, builder, Known issue: BM25 statistics corpus-wide per file; needs per-scope files for roles, Known issue: legacy chillu sequence does not match atomic chillu in BM25, Known issue: evaluation-data gaps (ml goldens, relevant_section_ids empty), Known issue: g004 overlaps u001, keep_both, Known issue: git_dirty true in Spec 007 BM25/hybrid result files (user-accepted) (+27 more)

### Community 68 - "check_hit"
Cohesion: 0.06
Nodes (40): 007 — Hybrid Retrieval Design, Alternatives / deferred decisions, Data flow, Error and failure behavior, Interfaces / models, Observability, Security / authorization, Testing / evaluation strategy (+32 more)

### Community 69 - "make index-lexical"
Cohesion: 0.08
Nodes (33): lexical/cli.py (make index-lexical writes only git-ignored file), lexical/ package (Spec 007), store.py (SQLite FTS5: chunks table, chunk_terms FTS5 table, settings row; LexicalIndex.open, bind_to, search), tokenizer.py (lexical-v1), make index-lexical, bm25 strategy, bm25 needs neither Qdrant nor the bge-m3 extra (Spec 008), config/retrieval.yaml schema 1.1 (default_strategy hybrid, qdrant.connect_timeout_s 2, query_timeout_s 3; 1.0 refused) (+25 more)

### Community 70 - "embedder"
Cohesion: 0.11
Nodes (17): chunker, context_prefix, name, overlap_tokens, target_tokens, version, embedder, batch_size (+9 more)

### Community 71 - "AWS target"
Cohesion: 0.06
Nodes (36): docker compose up -d / down (local Qdrant), Roadmap 11 - Observability, Langfuse traces, Stage latency, model/tokens/cost, release/config IDs, AWS target, Bedrock Knowledge Bases as core RAG (avoided), Bedrock model selection criteria, Amazon CloudWatch (+28 more)

### Community 72 - "EvaluationConfigurationError"
Cohesion: 0.08
Nodes (34): EvaluationConfigurationError, CaseBase, CaseStatus, DatasetRef, DatasetType, GoldenCase, LoadedSuite, SecurityCase (+26 more)

### Community 73 - "AccessContext"
Cohesion: 0.22
Nodes (8): AccessContext, test_blank_tenant_refused(), test_empty_tenant_refused(), test_no_language_or_scope_fields(), test_roles_match_policy_file(), test_tenant_is_stripped(), test_unknown_role_refused(), test_valid_context_is_frozen()

### Community 74 - "Constitution"
Cohesion: 0.19
Nodes (23): load_manifest(), load_schema(), validate_manifest(), metadata(), record(), run(), test_duplicate_document_id_rejected(), test_duplicate_document_version_rejected() (+15 more)

### Community 75 - "Section: Next step"
Cohesion: 0.11
Nodes (17): Atomic publish and rollback, Phase 2 audit trail, AWS deployment architecture (ap-south-1), Controlled document-change workflow (Release Candidate), CI/CD pipeline, Evaluation governance states, Evaluation slices, Evaluation Suite (public-eval-v1) (+9 more)

### Community 76 - "Spec 007 - hybrid retrieval (verified 2026-10-28, merged 3cf70eb; 10 tasks)"
Cohesion: 0.10
Nodes (21): Completion: retrospective, Spec-Review commit, merge, verified status, Spec orchestrator loop (route, role subagents, user approval, merge), GET /health endpoint, make setup, packages core/rag/observability skeletons, task-gated spec skills and skills-sync, task State lifecycle and spec/NNN branches, uv workspace and uv.lock (+13 more)

### Community 77 - "DocumentRepository"
Cohesion: 0.29
Nodes (7): Roadmap 2 - Document model + repository, KnowledgeDocument, Manifest/schema validation, S3DocumentRepository and external storage, Document manifest, DocumentRepository, LocalDocumentRepository

### Community 78 - "test_repository_contract.py"
Cohesion: 0.19
Nodes (11): InMemoryDocumentRepository, make_document(), test_document_query_has_no_filesystem_concepts(), test_document_query_is_immutable(), test_get_document_missing_raises_not_found(), test_get_document_returns_latest_or_requested_version(), test_in_memory_repository_satisfies_protocol(), test_list_documents_applies_query_filters() (+3 more)

### Community 79 - "Spec 005 dense retrieval baseline"
Cohesion: 0.16
Nodes (16): AccessContext, Role, W2A_TENANT_ID, make retrieval-baseline legacy frozen, BGE-M3 device mps not pinned (D038), Spec 005 retrospective findings F3-F5, Next step 2: real BGE-M3 baseline committed, experiments/results/retrieval-baseline-idx-v1-20261023T063534Z.json real BGE-M3 baseline, Spec 005 dense retrieval baseline, Spec 005 status: verified 2026-10-23 merged b33462e (+8 more)

### Community 80 - "chunking.py"
Cohesion: 0.08
Nodes (33): Package / file placement, Implementation, Review, Review, split_at_sentence_ends(), split_on_separator(), split_on_spaces(), _content_count() (+25 more)

### Community 81 - "list_eligible_documents"
Cohesion: 0.20
Nodes (16): eligible_ids(), make_document(), test_active_approved_public_document_is_eligible(), test_language_filter_narrows_eligible_documents_only(), test_language_metadata_does_not_broaden_access(), test_local_repository_applies_the_policy_query(), test_non_active_lifecycle_is_excluded(), test_non_approved_status_is_excluded() (+8 more)

### Community 82 - "Ingestion pipeline (Spec 004)"
Cohesion: 0.11
Nodes (18): default_strategy, fusion, candidate_depth, k, method, weights, qdrant, connect_timeout_s (+10 more)

### Community 83 - "Retrieval fallback (Spec 008, D056-D062)"
Cohesion: 0.09
Nodes (23): bm25 builds no embedder and no Qdrant client, classify_model_error, classify_qdrant_error, D056-D062 fallback decisions, D057 Fallback eligibility classification, D058 Fallback policy per query, D060 Standalone lexical freshness, D061 Marking and evaluation of fallback (+15 more)

### Community 84 - "IndexIdentity"
Cohesion: 0.11
Nodes (22): Package / file placement, Implementation, Implementation, Review, Review, T2 — round 1, T6 — round 1, User decision (+14 more)

### Community 85 - "test_hybrid.py"
Cohesion: 0.13
Nodes (14): chunk(), dense_pair(), production_lexical(), pub_chunk(), real_hybrid(), stub_result(), test_any_other_leg_error_propagates_without_fallback(), retrieve() (+6 more)

### Community 86 - "FakeEmbedder"
Cohesion: 0.18
Nodes (11): FakeEmbedder, __init__(), test_conforms_to_protocol(), test_declared_vector_size(), test_default_size_is_64(), test_fake_device_is_none(), test_info_reports_fake_identity(), test_invalid_vector_size_rejected() (+3 more)

### Community 87 - "Backend stack"
Cohesion: 0.05
Nodes (44): Lexical file is a derived artifact, one per collection, bound by identity and chunk digest, Source documents are truth; chunks, embeddings, sparse entries, Qdrant points and preview indexes are derived artifacts, Full agent orchestration (avoided), Intentionally avoided choices, Backend stack, Bedrock Agents / AgentCore for Phase 1 (avoided), Containers, Custom retrieval metrics (plain Python) (+36 more)

### Community 88 - "embedder"
Cohesion: 0.14
Nodes (13): chunker, max_chunk_chars, name, version, embedder, batch_size, fake_vector_size, model_id (+5 more)

### Community 89 - "D023 Task-gated agent workflow"
Cohesion: 0.12
Nodes (16): allowed_scopes, current_release, default_role, implemented_roles, allowed_scopes, allowed_scopes, roles, admin (+8 more)

### Community 90 - "Roadmap 13 - Graceful degradation"
Cohesion: 0.32
Nodes (8): Deferred serving concerns (circuit breaker, startup policy, Qdrant 5xx D062), Deduplication, context budgeting, evidence ordering, Dense to BM25 degradation, Roadmap 9 - Reranking + context building, Roadmap 13 - Graceful degradation, Qdrant failure to SQLite FTS5, Reranker failure to hybrid results, Spec 008 early delivery (D056)

### Community 91 - "test_schemas.py"
Cohesion: 0.15
Nodes (6): load_schemas(), test_existing_schema_is_referenced_not_copied(), test_missing_schema_is_configuration_error(), test_per_type_required_field_enforced(), test_schema_files_are_valid_draft_2020_12(), test_valid_rows_pass()

### Community 92 - "ingest_dense"
Cohesion: 0.20
Nodes (11): build_production(), ingest_dense(), open_lexical(), rewrite_settings(), test_bind_does_not_write_to_qdrant(), test_bind_refuses_chunk_set_mismatch_with_counts(), test_bind_refuses_identity_and_chunker_mismatch(), test_bind_refuses_when_qdrant_content_changed() (+3 more)

### Community 93 - "pathlib"
Cohesion: 0.25
Nodes (9): apps/api, apps/web, CloudWatch, Future multimodal mock-test evaluation, Langfuse tracing, packages/core, packages/observability, packages/rag (+1 more)

### Community 94 - "RetrievalConfigurationError"
Cohesion: 0.09
Nodes (24): default_output_path(), _mixed(), _served_strategy(), write_document(), BaselineResult, check_output_free(), format_summary(), main() (+16 more)

### Community 96 - "documents/__init__.py"
Cohesion: 0.23
Nodes (5): AccessScope, ApprovalStatus, LanguageScope, LifecycleStatus, SourceAuthority

### Community 97 - "SpyIndex"
Cohesion: 0.21
Nodes (13): Admin content management, Agent capabilities only where they solve a real product problem, Audit trail, Basic analytics, Candidate evaluation, Change impact analysis, Evaluation Governance (keep/modify/deprecate/replace), Versioned Evaluation Suite (+5 more)

### Community 98 - "HybridRetriever"
Cohesion: 0.06
Nodes (53): As-built notes, Design summary, Package / file placement, R7 — Fusion and `HybridRetriever` (`retrieval/fusion.py`, `hybrid.py`), Change log, Implementation, Implementation, Implementation (+45 more)

### Community 99 - "CURRENT_STATE.md"
Cohesion: 0.13
Nodes (14): interval, retries, start_period, test, timeout, container_name, healthcheck, image (+6 more)

### Community 101 - "repositories/__init__.py"
Cohesion: 0.06
Nodes (30): DocumentRepositoryError, DocumentValidationError, DuplicateDocumentError, ManifestValidationError, split_frontmatter(), _StringDateLoader, compute_body_sha256(), compute_content_hash() (+22 more)

### Community 102 - "006 Evaluation Framework Tasks"
Cohesion: 0.18
Nodes (14): Local multilingual BGE reranker, BM25 via FTS5 bm25(), Derived local lexical file per collection, Fusion, Lexical store, lexical-v1 tokens (D051), make index-lexical, One lexical file per access scope (future roles) (+6 more)

### Community 103 - "T2 — round 1"
Cohesion: 0.67
Nodes (3): Implementation, T2 — round 1, User decision

### Community 104 - "Retrieval package (Spec 005 and 007)"
Cohesion: 0.14
Nodes (12): graphify skill pointer, spec/NNN branch and Spec-Task trailers, spec-implementer skill (one task per run), spec-orchestrator skill, spec-planner skill, spec-reviewer retrospective skill, Task-gated agent workflow loop, task-reviewer skill (read-only) (+4 more)

### Community 105 - "D035 One filter builder, fail-closed re-check, same path for later fallbacks (Spec 005)"
Cohesion: 0.15
Nodes (21): DenseIndex, build_access_filter, check_hit, DenseRetriever, make eval-retrieval, FallbackRetriever and open_retrieval wiring (merged 1107b67), make retrieve guest/public CLI, Strategy Protocol, BM25Retriever, rrf_fuse, HybridRetriever, Spec 008 retro F4: duplicated standalone open wiring, Next step 1: real eval-retrieval and eval-compare PASS 2026-10-24, retrieval-evaluation-idx-v1-20261024T193140Z.json v1 2.0 closed baseline (+13 more)

### Community 106 - "Qdrant (vector database)"
Cohesion: 0.14
Nodes (13): Authorization metadata (access_scope, owner_user_id, tenant_id), Engineering Conventions, IDs and versions conventions, Knowledge files with provenance, Language metadata (content_language, lote_languages), Logging and tracing hygiene, Domain naming terms, Prompts as versioned assets (+5 more)

### Community 107 - "run_security_evaluation"
Cohesion: 0.17
Nodes (8): run_security_evaluation(), query_terms(), DroppedClauseLexical, test_a_dropped_lexical_clause_names_the_four_lexical_paths(), test_a_lexical_store_without_the_clause_fails_bm25_and_hybrid(), __init__(), test_security_result_1_2_has_paths_strategies_and_no_text(), test_zero_term_queries_skip_the_lexical_sanity_and_are_counted()

### Community 108 - "source_chunk_digest"
Cohesion: 0.12
Nodes (16): R4/R5 — Lexical store (`lexical/store.py`, `lexical/build.py`), Review, Review, T3 — `lexical-v1` tokenizer, lexical store and `make index-lexical`, Verification, As-built notes, R4 — Freshness from the repository (`lexical/freshness.py`), T2: where the shared pieces live (2026-10-31) (+8 more)

### Community 109 - "EmbedderInfo"
Cohesion: 0.16
Nodes (6): Implementation, T3 — round 2, _group_installed(), EmbedderInfo, OptionalDependencyError, missing()

### Community 110 - "dense_equivalence.py"
Cohesion: 0.13
Nodes (17): UnanswerableCase, deterministic_clock(), equivalence_suite(), run_equivalence(), golden(), suite_of(), test_active_golden_without_relevant_documents_is_refused(), test_case_access_context_never_widens_access() (+9 more)

### Community 111 - "test_content_hash.py"
Cohesion: 0.15
Nodes (12): Approved packages, pricing and validity, Six approved packages and prices, 60-day package validity, 24-hour cancellation notice, Personal coaching package, 60-minute coaching session on Google Meet, Individual coaching and live appointments, Mock assessments, scoring, feedback and review windows (+4 more)

### Community 112 - "SecurityIndex"
Cohesion: 0.19
Nodes (9): Implementation, Review, T8 — round 1, delete_security_index(), lexical_probe_text(), SecurityIndex, strip_forbidden_terms(), test_a_lexical_sanity_failure_is_a_harness_error() (+1 more)

### Community 113 - "test_violation_names_the_document_from_the_error_attribute"
Cohesion: 0.18
Nodes (12): AGENTS.md Project Rules, DocumentRepository Abstraction, Evaluation Governance Rules, Language Separation Rules, Phase 1 Scope, Task-gated Spec Loop, CLAUDE.md Project Instructions, graphify Knowledge Graph Rules (+4 more)

### Community 114 - "pytest"
Cohesion: 0.17
Nodes (12): AccessContext(role, tenant_id) with blank tenant refused, Future agent folders intentionally not created, apps/api (FastAPI application layer), apps/web (Next.js/TypeScript frontend: recruiter assistant, RAG Lab, engineering views), core/access.py (Role, frozen AccessContext), guest_access, Knowledge model metadata (document_id, document_version, tenant_id, access_scope, lote_languages, content_language, source_authority...), No language filter, score threshold or reranking yet (+4 more)

### Community 115 - "test_bm25.py"
Cohesion: 0.12
Nodes (19): BM25, Deterministic regression gates, FastAPI skeleton, Golden, refusal and security cases, HitRate@5, Roadmap 1 - Project foundation, Roadmap 5 - Evaluation framework, Roadmap 6 - Hybrid retrieval (+11 more)

### Community 116 - "fusion"
Cohesion: 0.20
Nodes (12): English, Malayalam and mixed queries, FAQ-aware retrieval/indexing, Roadmap 7 - Chunking experiments, Roadmap 8 - Multilingual retrieval, Language applicability handling, Parent-heading context and order-independent section_ids, Recursive chunking baseline, Optional semantic chunking (+4 more)

### Community 117 - "evaluation/cli.py"
Cohesion: 0.21
Nodes (12): Branching and commits (spec/NNN, Spec-Task trailer), Development Workflow, Multi-agent handoff, Implementation rule: BLOCKED spec issue, Phase discipline, Protected source-of-truth data, Required spec-reviewer retrospective, Agent skills (orchestrator, planner, implementer, task-reviewer, spec-reviewer) (+4 more)

### Community 118 - "security_document"
Cohesion: 0.18
Nodes (6): _path_strategy(), security_document(), SecurityReport, test_a_forbidden_hit_injected_into_a_path_fails_the_gate_naming_it(), test_result_document_has_ids_only(), test_violation_names_the_document_from_the_error_attribute()

### Community 119 - "evaluation/errors.py"
Cohesion: 0.13
Nodes (13): active_registry_languages(), aggregate(), _mean(), slice_by(), source_authority_key(), row(), test_absent_languages_from_a_temp_registry(), test_missing_registry_section_is_a_configuration_error() (+5 more)

### Community 120 - "failing_client"
Cohesion: 0.18
Nodes (10): content-hash-v1 (sole change-detection signal), LocalDocumentRepository, Document manifest and JSON Schema validation, make validate-knowledge, persona_scope spec defect (F2), BgeM3Embedder (optional extra, pinned revision), Embedder Protocol and FakeEmbedder, HeadingChunker and slugify rule (+2 more)

### Community 121 - "test_status_handling.py"
Cohesion: 0.20
Nodes (8): Adding a New Language Guide, language_registry.json, Public Assistant Content Boundaries, access_scope, content_language, Knowledge Schema and Metadata, language_scope, lote_languages

### Community 122 - "load_retrieval_config"
Cohesion: 0.28
Nodes (8): load_retrieval_config(), test_committed_config_loads(), test_good_config_loads(), test_invalid_config_is_refused_naming_the_field(), test_timeout_bounds_are_inclusive(), test_unreadable_and_non_mapping_files_are_refused(), variant(), write()

### Community 123 - "Spec 009 T3 — transcript extraction (facts only)"
Cohesion: 0.13
Nodes (14): Graphify calls (exact query + reads immediately after), Orchestrator (parent), T3-related segment (user msgs from 10:33 T2-approved through T3 handoff), Part A: Transcript locations, Part B: Step log (chronological), Part C: Per-invocation facts, Part D: Graphify facts, Part E: Verification and rework, Part F: Gaps (+6 more)

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

### Community 130 - "Roadmap 12 - Security"
Cohesion: 0.13
Nodes (15): Answerability and insufficient-evidence response, Authorization regression and staff canary, Docker, Terraform, EC2, ECR, CloudWatch, IAM, Bedrock, Bedrock Runtime (roadmap), BGE-M3 (roadmap), Citation manipulation tests and input/cost limits, Backend-owned citation validation, Roadmap 4 - Dense retrieval baseline (+7 more)

### Community 131 - "RuntimeSettings"
Cohesion: 0.33
Nodes (9): NAATI CCL candidate rules and test-day setup, Direct first-person speech requirement, Report technical incidents within 24 hours, NAATI, Online proctoring with separate phone or tablet, Prohibited materials and tools, Recording under 20 minutes, One repeated segment per dialogue without penalty (+1 more)

### Community 132 - "Spec 009 T3 — transcript extraction (facts only)"
Cohesion: 0.13
Nodes (14): Graphify calls (exact query + reads immediately after), Orchestrator (parent), T3-related segment (user msgs from 10:33 T2-approved through T3 handoff), Part A: Transcript locations, Part B: Step log (chronological), Part C: Per-invocation facts, Part D: Graphify facts, Part E: Verification and rework, Part F: Gaps (+6 more)

### Community 133 - "Vocabulary, flashcards and free access"
Cohesion: 0.29
Nodes (7): EligibilityPolicy / GUEST_PUBLIC_POLICY, Security fixtures (valid but ineligible), config/ingestion.yaml and RuntimeSettings, Ingestion pipeline (target vs current state diff), AccessContext and Role (core), resolve_access / ResolvedAccess, W2A_TENANT_ID server tenant setting

### Community 134 - ".search"
Cohesion: 0.25
Nodes (8): Phase 2 basic analytics, Assistant behavior rules, Product Context, English and Malayalam language scope, Future personas, Phase 1 guest-only scope, Way2Australia AI product, Source-of-truth priorities

### Community 135 - "Roadmap 3 - Ingestion baseline"
Cohesion: 0.67
Nodes (4): Content hashing, Idempotent ingestion, Roadmap 3 - Ingestion baseline, Preview indexing

### Community 136 - "Spec 002 document model and repository"
Cohesion: 0.16
Nodes (15): Pydantic document models and enums, EligibilityPolicy for guest/public, LocalDocumentRepository with manifest schema validation, make validate-knowledge, Spec 002 decisions made before approval (content_hash, fixtures, validate-knowledge), Seed data status: 13 public docs, evaluation datasets, security fixtures, Spec 002 retrospective findings F1-F6, Spec 002 document model and repository (+7 more)

### Community 137 - "test_opening.py"
Cohesion: 0.13
Nodes (5): Role, block_model_stack(), Raises, test_open_retrieval_bm25_builds_no_embedder_and_no_client(), test_retrieve_cli_bm25_needs_neither_qdrant_nor_the_model()

### Community 138 - "Evaluation Framework Goal"
Cohesion: 0.39
Nodes (8): NAATI CCL test format, scoring and results, NAATI CCL test, Deduction-based assessment, Begin interpreting within five seconds of chime, NAATI, CCL is not professional interpreter certification, Pass requirement 63/90 overall and 29/45 per dialogue, Results within 4-6 weeks

### Community 139 - "build_security_index"
Cohesion: 0.09
Nodes (17): Acceptance criteria, build_security_index(), _forbidden_payload(), _lexical_forbidden_entries(), require_security_base(), point_id(), build_payload(), PointPayload (+9 more)

### Community 140 - "Spec 009 — Task reviews"
Cohesion: 0.20
Nodes (9): Implementation, Spec 009 — Task reviews, T1 — round 1, T1 — round 2, T2 — round 1, T2 — round 2, T2 — round 3, User decision (+1 more)

### Community 141 - "BGE-M3 (initial embedding model)"
Cohesion: 0.38
Nodes (6): Evaluation Candidates File, Evaluation Package (evaluation/), Evaluation Suite and Case-type Schemas, validate-evaluation, T2 Schemas and validate-evaluation, T7 Candidates

### Community 142 - "Way2Australia AI Platform Master Implementation Plan"
Cohesion: 0.29
Nodes (7): eval-retrieval, Retrieval Result Document 2.0, Section-level Metrics, Slices and small_sample, Unanswerable Reporting, T3 Retrieval Runner, T4 Unanswerable Reporting

### Community 143 - "T1 — round 1"
Cohesion: 0.67
Nodes (3): Implementation, T1 — round 1, User decision

### Community 144 - "eval-compare"
Cohesion: 0.29
Nodes (7): AGENTS.md, Claude adapter, Initial specs, Phase 0 - Project bootstrap, Project context files, SDD workflow (Spec 003 task-gated agent workflow), Stable command interface

### Community 145 - "Payments, account access and support boundaries"
Cohesion: 0.29
Nodes (6): Vocabulary, flashcards and free access, Spaced-repetition flashcards, Free access allowance, 12 subject domains plus General vocabulary, Approved public learning samples, Sample neighbour-greeting dialogue

### Community 146 - "canonical_json"
Cohesion: 0.47
Nodes (4): canonical_json(), _canonical_value(), _canonical_value_mapping(), test_canonical_json_is_sorted_compact_and_keeps_unicode()

### Community 147 - "make test"
Cohesion: 0.33
Nodes (6): 006 Evaluation Framework Design, Decision Brief Q1-Q10, 006 Evaluation Framework Requirements, Evaluation Framework Goal, 006 Spec Retrospective Review, Retrospective Round 1 PASS

### Community 148 - "Mission"
Cohesion: 0.33
Nodes (5): Evaluation case_id and case_version, Versioning and Releases, document_id and document_version, Phase 2 Knowledge Release Candidates, Release seed-v1

### Community 149 - "test_fallback.py"
Cohesion: 0.11
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

### Community 156 - "Way2Australia AI Platform Master Implementation Plan"
Cohesion: 0.33
Nodes (6): Way2Australia AI Platform Master Implementation Plan, Phase 1 Definition of Done, Phase 1 Scope (public/guest RAG), Recruiter / portfolio story, Project Mission, Seven-day Phase 1 execution plan

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

### Community 168 - "DocumentRepository Protocol (async)"
Cohesion: 0.33
Nodes (6): DocumentRepository Protocol (async), KnowledgeDocument model, Spec 002 retrospective round 1, Spec 002 task review log (T3-T9), Spec 002 Document model and repository (verified), Acceptance dry run on Spec 002 T3

### Community 170 - "tests/evaluation/__init__.py"
Cohesion: 0.67
Nodes (3): Canonical document metadata, Chunk metadata, Source authority precedence

### Community 191 - "test_every_path_is_gated_for_every_query"
Cohesion: 0.29
Nodes (4): test_every_path_is_gated_for_every_query(), counting(), test_the_gate_runs_all_three_strategies_on_v2(), counting()

## Ambiguous Edges - Review These
- `Task-gated agent workflow loop` → `graphify skill pointer`  [AMBIGUOUS]
  .claude/CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **380 isolated node(s):** `way2australia-api`, `way2australia-core`, `way2australia-observability`, `way2australia-rag`, `way2australia` (+375 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1302 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **33 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Change log` connect `HybridRetriever` to `DenseRetriever`, `security_eval.py`, `Spec 007 hybrid retrieval`, `check_hit`, `run_security_evaluation`, `source_chunk_digest`, `SecurityIndex`, `Document Model Tests`, `007 — Hybrid Retrieval Requirements`, `check_target_allowed`?**
  _High betweenness centrality (0.090) - this node is a cross-community bridge._
- **Are the 78 inferred relationships involving `DenseIndex` (e.g. with `Design summary` and `Decisions resolved before drafting`) actually correct?**
  _`DenseIndex` has 78 INFERRED edges - model-reasoned connections that need verification._
- **What connects `way2australia-api`, `way2australia-core`, `way2australia-observability` to the rest of the system?**
  _380 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `DenseRetriever` be split into smaller, more focused modules?**
  _Cohesion score 0.06921944035346098 - nodes in this community are weakly interconnected._
- **Why does `D055 Default strategy is hybrid (Spec 007)` connect `Spec 007 hybrid retrieval` to `Development Workflow`, `typing`, `Ingestion pipeline (Spec 004)`, `D035 One filter builder, fail-closed re-check, same path for later fallbacks (Spec 005)`?**
  _High betweenness centrality (0.089) - this node is a cross-community bridge._
- **Are the 35 inferred relationships involving `LocalDocumentRepository` (e.g. with `Dependencies` and `Design summary`) actually correct?**
  _`LocalDocumentRepository` has 35 INFERRED edges - model-reasoned connections that need verification._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Task-gated agent workflow loop` and `graphify skill pointer`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._