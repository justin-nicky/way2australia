# Graph Report - way2australia  (2026-11-02)

## Corpus Check
- 286 files · ~309,352 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 32 file(s) not represented in the graph (top: (none) 20, .jsonl 9, .mdc 1)

## Summary
- 4340 nodes · 12905 edges · 203 communities (168 shown, 35 thin omitted)
- Extraction: 80% EXTRACTED · 20% INFERRED · 0% AMBIGUOUS · INFERRED: 2614 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0bf33f95`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- DenseRetriever
- retrieval_eval.py
- open_retrieval
- test_structure.py
- test_validate.py
- test_service.py
- service.py
- test_index.py
- rrf_fuse
- evaluation/validate.py
- lexical/cli.py
- ChunkerIdentity
- HeadingChunker
- sync_agent_skills.py
- test_lexical_cli.py
- retrieval/test_cli.py
- Spec 008 retrieval fallback
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
- metrics.py
- test_strategy_eval.py
- Evaluation CLI Tests
- structure.py
- test_suite_v2.py
- test_baseline.py
- evaluation/test_cli.py
- hashing.py
- SpyIndex
- 009 — Chunking Experiments Requirements
- 008 — Retrieval Fallback Requirements
- build_security_index
- re
- open_retrieval
- typing
- test_legacy_baseline_snapshot.py
- Workflow Reviewer
- LocalDocumentRepository
- test_lexical_standalone.py
- test_cli_config.py
- test_authorization_isolation.py
- make eval-retrieval
- 007 — Hybrid Retrieval Requirements
- LocalRepositoryConfig
- HeadingChunker
- evaluation/cli.py
- FallbackRetriever
- repositories/__init__.py
- asyncio
- Development Workflow
- retrieval/test_access.py
- EvaluationSchemas
- json
- make eval-security
- build_security_repository
- Target RAG query flow (User -> FastAPI -> validation -> AccessContext -> LanguageContext -> retrieval -> RRF -> reranker -> context builder -> answerability -> prompt -> Bedrock -> citation validation)
- BgeM3Embedder
- run_security_evaluation
- build_lexical_index
- make retrieve
- Spec 007 hybrid retrieval
- security_eval.py
- Fallback (hybrid only)
- embedder
- Phase 1 RAG query pipeline
- EvaluationConfigurationError
- AccessContext
- Constitution
- Section: Next step
- Spec 007 - hybrid retrieval (verified 2026-10-28, merged 3cf70eb; 10 tasks)
- AWS target
- test_repository_contract.py
- Spec 005 dense retrieval baseline
- chunking.py
- list_eligible_documents
- Ingestion pipeline (Spec 004)
- Retrieval fallback (Spec 008, D056-D062)
- Strategy
- test_hybrid.py
- FakeEmbedder
- Backend stack
- embedder
- D023 Task-gated agent workflow
- ARCHITECTURE.md
- test_schemas.py
- list_eligible_documents
- pathlib
- baseline.py
- .search
- documents/__init__.py
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
- .bind_to
- make eval-retrieval
- dense_equivalence.py
- test_content_hash.py
- SecurityIndex
- test_violation_names_the_document_from_the_error_attribute
- pytest
- test_bm25.py
- fusion
- evaluation/cli.py
- IndexSettings
- evaluation/errors.py
- failing_client
- test_status_handling.py
- D050 SQLite FTS5 lexical store, not Qdrant sparse vectors (Spec 007)
- load_suite
- QdrantIndexStore
- Baseline runner and result JSON
- test_failed_write_removes_partial_file
- Development Workflow
- test_status_handling.py
- absent_query_languages
- Roadmap 12 - Security
- RuntimeSettings
- test_security_eval.py
- Vocabulary, flashcards and free access
- .search
- make validate-evaluation
- Spec 002 document model and repository
- Intentionally avoided choices
- Evaluation Framework Goal
- DocumentRepository
- test_collection_with_1_0_settings_still_binds
- BGE-M3 (initial embedding model)
- Way2Australia AI Platform Master Implementation Plan
- T1 — round 1
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
- test_failed_write_removes_partial_file
- lexical/ package (Spec 007)
- Orchestrator State Machine
- way2australia_api/__init__.py
- Project Context README
- Evaluation tooling
- way2australia_rag/__init__.py
- Scripted
- way2australia-core
- Phase 1 analytics event contract
- Spec-driven development workflow
- api/__init__.py
- DocumentRepository Protocol (async)
- BGE-M3 embeddings
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
- test_failed_write_removes_partial_file
- test_status_handling.py
- shutil
- test_seed_corpus.py
- R12 — Real runs (user-owned gate)
- CountingEmbedder
- metrics.py, goldens.py, baseline.py, baseline_cli.py
- test_exit_1_on_document_failure
- policy
- test_candidate_ineligible_document_is_not_unknown
- test_ineligible_document

## God Nodes (most connected - your core abstractions)
1. `DenseIndex` - 106 edges
2. `LocalDocumentRepository` - 100 edges
3. `Strategy` - 76 edges
4. `FakeEmbedder` - 67 edges
5. `run_retrieval_evaluation()` - 65 edges
6. `HeadingChunker` - 65 edges
7. `open_retrieval()` - 65 edges
8. `FakeTokenizer` - 64 edges
9. `EvaluationConfigurationError` - 63 edges
10. `IngestionConfigurationError` - 62 edges

## Surprising Connections (you probably didn't know these)
- `Implementation` --references--> `chunker_identity_for_run()`  [INFERRED]
  .kiro/specs/009-chunking-experiments/task-reviews.md → packages/rag/src/way2australia_rag/ingestion/chunker_build.py
- `Interfaces / models` --references--> `Chunk`  [INFERRED]
  .kiro/specs/009-chunking-experiments/design.md → packages/rag/src/way2australia_rag/ingestion/chunking.py
- `Acceptance criteria` --references--> `slugify()`  [INFERRED]
  .kiro/specs/009-chunking-experiments/requirements.md → packages/rag/src/way2australia_rag/ingestion/chunking.py
- `Error and failure behavior` --references--> `IngestionConfigurationError`  [INFERRED]
  .kiro/specs/009-chunking-experiments/design.md → packages/rag/src/way2australia_rag/ingestion/errors.py
- ``structure` v1 (R3)` --references--> `IngestionConfigurationError`  [INFERRED]
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

## Communities (203 total, 35 thin omitted)

### Community 0 - "DenseRetriever"
Cohesion: 0.06
Nodes (95): R10 — `eval-compare` identity rules (`compare.py`), Implementation, Review, T7 — round 1, User decision, _changed(), _chunker_text(), compare() (+87 more)

### Community 1 - "retrieval_eval.py"
Cohesion: 0.10
Nodes (25): Implementation, Review, T5 — round 1, User decision, DatasetType, LoadedSuite, active_golden_cases(), build_chunk_stats() (+17 more)

### Community 2 - "open_retrieval"
Cohesion: 0.06
Nodes (38): Interfaces / models, R3 — Standalone lexical open (`identity.py`, `lexical/store.py`), R5 — `bm25` without Qdrant or the extra (`bm25.py`), Implementation, Review, Review, T3 — round 1, User decision (+30 more)

### Community 3 - "test_structure.py"
Cohesion: 0.13
Nodes (25): assert_matches_snapshot(), assert_structure_chunks_whitespace_fidelity(), chunks_to_records(), load_snapshot(), snapshot_for_document(), structure_chunker(), test_duplicate_sibling_headings_raise(), test_fence_blocks_are_atomic_and_headings_inside_ignored() (+17 more)

### Community 4 - "test_validate.py"
Cohesion: 0.15
Nodes (29): edit_rows(), edit_suite(), root(), run(), test_active_golden_without_relevant_documents(), test_candidate_not_suggested(), test_candidate_referenced_by_suite(), test_candidate_unknown_and_ineligible_documents() (+21 more)

### Community 5 - "test_service.py"
Cohesion: 0.15
Nodes (26): DocumentFailure, RunReport, BoomChunker, doc(), Harness, test_bumped_document_version_updates(), test_changed_body_updates(), test_changed_metadata_field_updates() (+18 more)

### Community 6 - "service.py"
Cohesion: 0.13
Nodes (17): Design summary, Truncation guard (R2), T7 — Documentation, decisions, carry-over clean-ups and hand-off, Verification, Chunk, check_chunks(), ChunkTooLongError, _effective_limit() (+9 more)

### Community 7 - "test_index.py"
Cohesion: 0.06
Nodes (70): T3 — `lexical-v1` tokenizer, lexical store and `make index-lexical`, Verification, EmbedderInfo, read_index_settings(), LexicalRow, IndexBindingError, DenseIndex, raise_if_unavailable() (+62 more)

### Community 8 - "rrf_fuse"
Cohesion: 0.09
Nodes (29): 008 — Retrieval Fallback Design, Alternatives / deferred decisions, Data flow, Decisions D056-D062, Design summary, Spec 008 Retrieval Fallback Design, Error and failure behavior, Observability (+21 more)

### Community 9 - "evaluation/validate.py"
Cohesion: 0.17
Nodes (16): Review, _candidate_rules(), problem(), _describe(), _document_problems(), EvaluationProblem, _promotion_problems(), _read_rows() (+8 more)

### Community 10 - "lexical/cli.py"
Cohesion: 0.06
Nodes (43): Implementation, Implementation, Implementation, Review, Review, Review, T1 — round 1, T1 — round 2 (+35 more)

### Community 11 - "ChunkerIdentity"
Cohesion: 0.06
Nodes (33): 009 — Chunking Experiments Design, Alternatives / deferred decisions, As-built notes, Carry-over clean-ups (R11), Chunker identity, settings and configuration (R5), Components / boundaries, Cross-index comparison (R8), Data flow (+25 more)

### Community 12 - "HeadingChunker"
Cohesion: 0.12
Nodes (37): basic_suite(), build(), default_eval_extras(), fusion_config(), golden(), _LexicalStub, run(), Scripted (+29 more)

### Community 13 - "sync_agent_skills.py"
Cohesion: 0.29
Nodes (9): discover_skills(), expected_tree(), find_problems(), inject_frontmatter(), main(), managed_skills(), read_tree(), remove() (+1 more)

### Community 14 - "test_lexical_cli.py"
Cohesion: 0.09
Nodes (40): Implementation, Implementation, Review, Review, T3 — round 2, T3 — round 3, User decision, check_target_allowed() (+32 more)

### Community 15 - "retrieval/test_cli.py"
Cohesion: 0.16
Nodes (22): _advice_ok(), clean_env(), Factory, indexed(), ingest(), retrieve(), test_bad_args_exit_2_without_client(), test_bad_config_exit_2_without_client() (+14 more)

### Community 16 - "Spec 008 retrieval fallback"
Cohesion: 0.11
Nodes (26): Default retrieval strategy hybrid degrades to BM25, RetrievalUnavailableError and availability classification, FallbackRetriever and open_retrieval wiring (merged 1107b67), Current goal: Specs 001-008 complete; Spec 008 verified and merged into main (1107b67), plan next spec, Known issue: Qdrant and Hugging Face 5xx not fallback-eligible, Known issue: Qdrant client lifecycle leak on failed open, Spec 008 retro F3: post-approval amendments lacked change-log lines; resolved 2026-11-01, spec-planner added eight dated lines to requirements.md Change log, Spec 008 retro F4: duplicated standalone open wiring (+18 more)

### Community 17 - "RetrievalConfig"
Cohesion: 0.04
Nodes (67): Components / boundaries, R12 — Docker test, R1 — Suite v2, R4 — `make index-lexical` (`lexical/cli.py`), R7 — Fusion and `HybridRetriever` (`retrieval/fusion.py`, `hybrid.py`), R9 — Result format 2.1, Acceptance criteria, Decisions resolved before drafting (+59 more)

### Community 18 - "Index Binding Errors"
Cohesion: 0.09
Nodes (32): IndexSettingsMismatchError, IndexedDocument, QdrantIndexStore, client_factory(), CountingStore, client(), _keyword_indexed(), live_client() (+24 more)

### Community 19 - "Document Model Tests"
Cohesion: 0.15
Nodes (20): IndexPoint, build_client(), docs(), guest(), open_spy(), RaisingEmbedder, retriever(), test_a_network_failure_during_model_load_is_unavailable() (+12 more)

### Community 20 - "007 — Hybrid Retrieval Requirements"
Cohesion: 0.06
Nodes (34): 007 — Hybrid Retrieval Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+26 more)

### Community 21 - "test_validate_knowledge.py"
Cohesion: 0.21
Nodes (27): load(), test_bad_date_fails_loading_naming_document_and_field(), test_guest_policy_agrees_with_access_policy_config(), test_seed_corpus_still_loads(), test_valid_date_loads(), build_repo(), metadata(), problems_for() (+19 more)

### Community 22 - "Date and Policy Tests"
Cohesion: 0.06
Nodes (40): As-built notes, Package / file placement, R1 — Failure classification (`errors.py`, `availability.py`), R2 — Qdrant timeouts (`qdrant_client.py`, `config/retrieval.yaml`), T1: Hugging Face error shapes (confirmed 2026-10-29), Testing / evaluation strategy, Implementation, Review (+32 more)

### Community 23 - "BGE-M3 Adapter"
Cohesion: 0.06
Nodes (18): Model Preferences, Agent Skills README, Implementation Checklist, Spec Implementer Skill, task-reviews.md Implementation Block, Design Template, Change Log, Requirements Template (+10 more)

### Community 24 - "test_lexical_standalone.py"
Cohesion: 0.05
Nodes (33): Day-1 Usage, document_manifest.jsonl, golden_public.jsonl, Source-of-Truth Policy, chunking, overlap_tokens, strategy, target_tokens (+25 more)

### Community 25 - "Spec 004 ingestion baseline"
Cohesion: 0.10
Nodes (25): HeadingChunker heading v1 2000-char cap, Embedder Protocol, fake and BGE-M3 adapter, IngestionService change detection, make ingest and config/ingestion.yaml, 17-field PointPayload and UUIDv5 point IDs, QdrantIndexStore with companion settings collection, Heading chunking only synthetic-tested, none of 13 docs has headings, Spec 004 open review findings (T3 F1, T5 F2, T7 F1-F3, T8 F1, retro F1) (+17 more)

### Community 26 - "tokenization.py"
Cohesion: 0.09
Nodes (18): Testing / evaluation strategy, T1 — Tokenizer and truncation guard, Verification, IngestionConfigurationError, BgeM3Tokenizer, _download_hub_file(), _tokenizer_config_error(), TokenizerIdentity (+10 more)

### Community 27 - "metrics.py"
Cohesion: 0.09
Nodes (27): Implementation, Review, T2 — round 1, User decision, T2 — v2 dense baseline (user-owned gate), Verification, dedupe_sections(), section_key() (+19 more)

### Community 28 - "test_strategy_eval.py"
Cohesion: 0.10
Nodes (30): User decision, build_lexical(), eval_world(), lexical_env(), make_world(), retrieve(), retrieve_world(), run_strategy() (+22 more)

### Community 29 - "Evaluation CLI Tests"
Cohesion: 0.12
Nodes (31): assert_invalid(), document_fields(), make_document(), test_blank_required_text_is_rejected(), test_document_is_immutable(), test_duplicate_lote_languages_are_rejected(), test_effective_window_must_be_ordered(), test_empty_lote_languages_is_rejected() (+23 more)

### Community 30 - "structure.py"
Cohesion: 0.21
Nodes (12): _build_prefix(), _compose_chunk(), DuplicateSectionError, _is_list_item(), _join_blocks(), _pack_blocks(), body_fits(), _parse_blocks() (+4 more)

### Community 31 - "test_suite_v2.py"
Cohesion: 0.14
Nodes (24): committed(), edit_jsonl(), lines(), manifest(), problems(), read_lines(), root(), test_candidates_differ_only_in_promoted_as() (+16 more)

### Community 32 - "test_baseline.py"
Cohesion: 0.14
Nodes (21): case(), cli_run(), DeviceStub, _git(), run(), setup(), test_case_access_context_never_widens_access(), test_cli_release_mismatch_and_bad_args_exit_2() (+13 more)

### Community 33 - "evaluation/test_cli.py"
Cohesion: 0.18
Nodes (16): clean_env(), index_factory(), real_factory(), run(), test_bad_top_k_exits_2(), test_existing_output_exits_2_before_qdrant(), test_fake_embedder_exits_2_before_qdrant(), test_filter_carries_the_server_tenant() (+8 more)

### Community 34 - "hashing.py"
Cohesion: 0.13
Nodes (18): canonical_json(), _canonical_value(), _canonical_value_mapping(), compute_body_sha256(), compute_content_hash(), sha256_hex(), manifest_document_count(), h() (+10 more)

### Community 36 - "009 — Chunking Experiments Requirements"
Cohesion: 0.07
Nodes (28): 009 — Chunking Experiments Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+20 more)

### Community 37 - "008 — Retrieval Fallback Requirements"
Cohesion: 0.11
Nodes (32): Binding: embedder model ID, revision, vector size, normalization, fake flag and index_version must equal recorded IndexSettings, BM25Retriever(identity, lexical), BM25 statistics (IDF, avg length) computed over every row of a lexical file, build_retriever (only place a strategy name becomes a retriever), retrieval_client_factory (Qdrant client with configured timeouts), config/retrieval.yaml (default_strategy hybrid, RRF k 60, depth 50), D033-D041 retrieval decisions, D049-D055 (+24 more)

### Community 38 - "build_security_index"
Cohesion: 0.07
Nodes (20): R11 — Security gate (`security_index.py`, `security_eval.py`), build_security_index(), _forbidden_payload(), forbidden_variant(), _lexical_forbidden_entries(), require_security_base(), collection_name(), DenseIdentity (+12 more)

### Community 39 - "re"
Cohesion: 0.10
Nodes (17): _is_word_char(), _is_token_char(), QueryTerms, tokenize(), test_no_malayalam_specific_lote_languages_in_ingestion_code(), test_business_008_words_stay_whole(), test_deterministic(), test_english_punctuation_digits_and_case() (+9 more)

### Community 40 - "open_retrieval"
Cohesion: 0.09
Nodes (15): get_health(), HealthResponse, get_request_settings(), get_settings(), Settings, create_app(), isolate_settings_environment(), test_create_app_wires_settings() (+7 more)

### Community 41 - "typing"
Cohesion: 0.09
Nodes (31): 006-candidates.jsonl with 7 suggested rows, make eval-compare, make eval-retrieval, make eval-security hard gate, result 2.2 and served-strategy eval-compare, eval-security five paths, governed suite loader and schemas, make validate-evaluation (+23 more)

### Community 42 - "test_legacy_baseline_snapshot.py"
Cohesion: 0.13
Nodes (15): clean_env(), _Factory, _FixedDatetime, _record_opens(), note(), wrap_func(), inner(), wrap_method() (+7 more)

### Community 43 - "Workflow Reviewer"
Cohesion: 0.07
Nodes (25): Considered and rejected, Evidence, F1 — <title> [waste | quality risk | process slip] (confidence: high/medium/low), Findings, New features and tools (official sources, since <date>), Not measurable here, P1 — <title> (addresses F#; expected saving: ...), Proposals (+17 more)

### Community 44 - "LocalDocumentRepository"
Cohesion: 0.14
Nodes (23): LocalDocumentRepository, build(), guest_access(), real_queries(), spied(), test_a_fallback_path_that_does_not_fall_back_is_a_harness_error(), test_a_filter_dropping_index_fails_the_gate(), test_a_forbidden_hit_injected_into_a_path_fails_the_gate_naming_it() (+15 more)

### Community 45 - "test_lexical_standalone.py"
Cohesion: 0.15
Nodes (21): lexical_index_path(), rewrite_settings(), build_from(), built(), copy_repository(), expected(), first_document_id(), open_it() (+13 more)

### Community 46 - "test_cli_config.py"
Cohesion: 0.17
Nodes (18): clean_env(), _factory(), _run(), test_agrees_with_day1_baseline(), test_builds_exactly_one_embedder_per_run(), test_collection_base_comes_from_environment(), test_config_refuses_missing_or_floating_revision(), test_config_refuses_unknown_field_and_missing_file() (+10 more)

### Community 47 - "test_authorization_isolation.py"
Cohesion: 0.21
Nodes (4): client_with_forbidden(), FilterDroppingIndex, test_forbidden_points_are_never_returned(), test_store_dropping_the_filter_fails_closed()

### Community 48 - "make eval-retrieval"
Cohesion: 0.12
Nodes (23): BgeM3Embedder (optional bge-m3 extra, dense only), D025-D030, D032 ingestion decisions, DocumentRepository Protocol (get_document, list_documents), Embedder Protocol, FakeEmbedder (deterministic), GUEST_PUBLIC_POLICY, HeadingChunker (heading v1, character cap, stable section_id slugs), IndexSettings and mismatch comparison (+15 more)

### Community 49 - "007 — Hybrid Retrieval Requirements"
Cohesion: 0.09
Nodes (27): optional bge-m3 extra (sentence-transformers, PyTorch), D048 graphify tooling, make experiment CONFIG=... (target; records git commit, release, suite, chunker, embedder, strategy, metrics, latency), make format, Knowledge graph graphify (D048), /graphify . --update (user, once per spec after merge), graphify query / path / explain, graphify update . (+19 more)

### Community 50 - "LocalRepositoryConfig"
Cohesion: 0.19
Nodes (14): LocalRepositoryConfig, assert_recursive_chunks_whitespace_fidelity(), collapse_whitespace(), recursive_chunker(), test_deterministic(), test_heading_seed_snapshot_unchanged(), test_invalid_parameters_refused(), test_recursive_seed_snapshot() (+6 more)

### Community 51 - "HeadingChunker"
Cohesion: 0.14
Nodes (26): R3 — Tokenizer `lexical-v1` (`lexical/tokenizer.py`), HeadingChunker, slugify(), ids(), make_document(), test_deterministic(), test_duplicate_headings_get_unique_ids_in_order(), test_duplicate_suffix_does_not_collide_with_literal_heading() (+18 more)

### Community 52 - "evaluation/cli.py"
Cohesion: 0.07
Nodes (30): _authority_map(), _compare(), default_security_output_path(), format_security_summary(), format_summary(), main(), _retrieval(), real_embedder_factory() (+22 more)

### Community 53 - "FallbackRetriever"
Cohesion: 0.08
Nodes (29): Fallback authorization invariant (same ResolvedAccess), BM25Retriever (identity, lexical), classify_model_error, classify_qdrant_error, Qdrant client lifecycle gap, eval-compare by served strategy (mixed refused), FallbackRetriever, Hugging Face error shapes (T1 As-built) (+21 more)

### Community 54 - "repositories/__init__.py"
Cohesion: 0.09
Nodes (5): _check_language_code(), KnowledgeDocument, DocumentNotFoundError, ListRepository, IgnoresQueryRepository

### Community 55 - "asyncio"
Cohesion: 0.32
Nodes (14): _copy_seed(), seed_repository(), test_documents_outside_approved_roots_are_never_loaded(), test_get_document_by_id_and_version(), test_get_document_missing_raises_not_found(), test_invalid_document_fails_load_without_leaking_paths(), test_invalid_schema_raises_repository_error(), test_language_filter_is_data_driven_and_does_not_affect_access() (+6 more)

### Community 56 - "Development Workflow"
Cohesion: 0.10
Nodes (30): Evaluation Suite includes goldens, refusal, multilingual, security, regression, Finalized stack: Python/FastAPI, Next.js, Qdrant, SQLite FTS5, BGE-M3, Bedrock, Langfuse, CloudWatch, Terraform ap-south-1, GitHub Actions, agent-skills sync, D001 Python-first backend, D002 RAG as reusable internal package, D003 Knowledge outside RAG package, D005 Documents are truth; chunks are derived, D007 Public-only Phase 1 (+22 more)

### Community 57 - "retrieval/test_access.py"
Cohesion: 0.16
Nodes (15): clean_env(), guest(), payload(), _policy(), test_a_different_policy_changes_both_builders(), test_both_builders_cover_the_same_three_conditions(), test_check_hit_accepts_valid_payload(), test_check_hit_rejects_malformed_payload() (+7 more)

### Community 59 - "json"
Cohesion: 0.12
Nodes (16): chunker, max_chunk_chars, name, version, embedder, batch_size, fake_vector_size, model_id (+8 more)

### Community 60 - "make eval-security"
Cohesion: 0.15
Nodes (14): Security gate on throwaway w2a-sectest-<8 hex> collection with fake embedder, security_corpus.py, security_index.py, security_eval.py, D040, Throwaway collection w2a-sectest-<8 hex>, eval-security exit 0 pass, 1 violation, 2 harness or configuration error, Security fixtures poisoned_public_document.md and staff_only_canary.md, Forbidden points: staff scope, other tenant, owned, missing owner, staff-only canary; nearest neighbour of every query, Authorization hard gate (forbidden points never returned) (+6 more)

### Community 61 - "build_security_repository"
Cohesion: 0.13
Nodes (18): build_security_repository(), _fixture_files(), security_repository(), copy_fixtures(), spy_lexical_path(), wrapper(), strip_forbidden_terms(), test_cli_clause_less_lexical_store_exits_one_naming_strategies() (+10 more)

### Community 62 - "Target RAG query flow (User -> FastAPI -> validation -> AccessContext -> LanguageContext -> retrieval -> RRF -> reranker -> context builder -> answerability -> prompt -> Bedrock -> citation validation)"
Cohesion: 0.13
Nodes (20): Answerability / insufficient-evidence decision, Authorization applied inside each retriever before fusion, never after RRF, reranking or generation, Authorization filter is part of the Qdrant query so unauthorized points never leave the store, Amazon Bedrock generation, build_access_filter (the only filter builder), check_hit (fail-closed re-check, second line of defense), Citation validation, Context builder (planned) (+12 more)

### Community 63 - "BgeM3Embedder"
Cohesion: 0.09
Nodes (14): BgeM3Embedder, _group_installed(), OptionalDependencyError, group_installed(), test_constructing_does_not_load_the_model(), test_device_none_before_load_and_recorded_after(), test_missing_group_at_load_raises_optional_dependency_error(), test_missing_group_refused_at_construction() (+6 more)

### Community 64 - "run_security_evaluation"
Cohesion: 0.11
Nodes (19): Review, EvaluationHarnessError, _lexical_sanity_check(), _open_lexical_sanity(), run_security_evaluation(), _sanity_check(), security_document(), SecurityQuery (+11 more)

### Community 65 - "build_lexical_index"
Cohesion: 0.06
Nodes (55): Implementation, Review, T3 — round 1, User decision, R4 — Freshness from the repository (`lexical/freshness.py`), Acceptance criteria, What happens to existing lexical files (user request), build_lexical_index() (+47 more)

### Community 66 - "make retrieve"
Cohesion: 0.08
Nodes (30): D061 fallback marking, docker compose up -d / down (local Qdrant), Environment: QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION_BASE, W2A_TENANT_ID, eval-retrieval options (--top-k, --strategy, --retrieval-config, --suite default public-eval-v2, --release seed-v1, --output, --repo-root, --config); no --embedder or --allow-fake, Fake embedder needs throwaway QDRANT_COLLECTION_BASE, strategy: bm25 (requested: hybrid; fallback: <reason>) plus stderr WARNING, exit 0, Fallback reasons qdrant_unavailable, qdrant_timeout, model_unavailable (never exception text), Default hybrid needs lexical file; exits 2 without it; setup order make ingest then make index-lexical (+22 more)

### Community 67 - "Spec 007 hybrid retrieval"
Cohesion: 0.08
Nodes (38): make retrieval-baseline legacy frozen, build_retriever, CURRENT_STATE.md current state document, Phase 2 Knowledge Release workflow designed not implemented, Public/guest retrieval only in Phase 1; English + Malayalam, Known issue: legacy chillu sequence does not match atomic chillu in BM25, Known issue: evaluation-data gaps (ml goldens, relevant_section_ids empty), Known issue: g004 overlaps u001, keep_both (+30 more)

### Community 68 - "security_eval.py"
Cohesion: 0.07
Nodes (48): 007 — Hybrid Retrieval Design, Alternatives / deferred decisions, As-built notes, Data flow, Design summary, Error and failure behavior, Interfaces / models, Observability (+40 more)

### Community 69 - "Fallback (hybrid only)"
Cohesion: 0.21
Nodes (14): bm25 strategy, bm25 needs neither Qdrant nor the bge-m3 extra (Spec 008), config/retrieval.yaml schema 1.1 (default_strategy hybrid, qdrant.connect_timeout_s 2, query_timeout_s 3; 1.0 refused), dense strategy, --strategy dense needs no lexical file, Embedder pair from index_settings or dense_identity; fallback-only 2.2 file compares against Spec 007 bm25 file, eval-retrieval fallback: Qdrant unreachable with default hybrid is served by bm25 for every case, Fallback never applies to explicit dense or bm25 (+6 more)

### Community 70 - "embedder"
Cohesion: 0.11
Nodes (17): chunker, context_prefix, name, overlap_tokens, target_tokens, version, embedder, batch_size (+9 more)

### Community 71 - "Phase 1 RAG query pipeline"
Cohesion: 0.11
Nodes (19): Deduplication, context budgeting, evidence ordering, Roadmap 9 - Reranking + context building, Reranker failure to hybrid results, Authorization model (guest/public), Small documents and chunking strategy, Citation strategy (backend-owned validation), FAQ-aware retrieval experiment, Graceful degradation (+11 more)

### Community 72 - "EvaluationConfigurationError"
Cohesion: 0.09
Nodes (27): EvaluationConfigurationError, CaseBase, CaseStatus, DatasetRef, GoldenCase, SecurityCase, SuiteManifest, UnanswerableCase (+19 more)

### Community 73 - "AccessContext"
Cohesion: 0.13
Nodes (12): AccessContext, Role, test_blank_tenant_refused(), test_empty_tenant_refused(), test_no_language_or_scope_fields(), test_roles_match_policy_file(), test_tenant_is_stripped(), test_unknown_role_refused() (+4 more)

### Community 74 - "Constitution"
Cohesion: 0.24
Nodes (19): metadata(), record(), run(), test_duplicate_document_id_rejected(), test_duplicate_document_version_rejected(), test_frontmatter_errors(), test_frontmatter_missing_required_field(), test_frontmatter_parsing_keeps_dates_as_strings() (+11 more)

### Community 75 - "Section: Next step"
Cohesion: 0.08
Nodes (23): Way2Australia AI Platform Master Implementation Plan, Atomic publish and rollback, Phase 2 audit trail, AWS deployment architecture (ap-south-1), Controlled document-change workflow (Release Candidate), CI/CD pipeline, Phase 1 Definition of Done, Evaluation governance states (+15 more)

### Community 76 - "Spec 007 - hybrid retrieval (verified 2026-10-28, merged 3cf70eb; 10 tasks)"
Cohesion: 0.12
Nodes (19): Completion: retrospective, Spec-Review commit, merge, verified status, Spec orchestrator loop (route, role subagents, user approval, merge), GET /health endpoint, make setup, packages core/rag/observability skeletons, task-gated spec skills and skills-sync, task State lifecycle and spec/NNN branches, uv workspace and uv.lock (+11 more)

### Community 77 - "AWS target"
Cohesion: 0.10
Nodes (21): Roadmap 11 - Observability, Langfuse traces, Stage latency, model/tokens/cost, release/config IDs, AWS target, Bedrock Knowledge Bases as core RAG (avoided), Bedrock model selection criteria, Amazon CloudWatch, Derived retrieval index in Qdrant (+13 more)

### Community 78 - "test_repository_contract.py"
Cohesion: 0.17
Nodes (12): test_fusion_module_has_no_authorization_or_io_surface(), InMemoryDocumentRepository, make_document(), test_document_query_has_no_filesystem_concepts(), test_document_query_is_immutable(), test_get_document_missing_raises_not_found(), test_get_document_returns_latest_or_requested_version(), test_in_memory_repository_satisfies_protocol() (+4 more)

### Community 79 - "Spec 005 dense retrieval baseline"
Cohesion: 0.18
Nodes (15): AccessContext, Role, W2A_TENANT_ID, BGE-M3 device mps not pinned (D038), Spec 005 retrospective findings F3-F5, Spec 005 dense retrieval baseline, Spec 005 status: verified 2026-10-23 merged b33462e, AccessContext and Role, D033 AccessContext and Role live in core (Spec 005), D034 W2A_TENANT_ID is a server setting (Spec 005) (+7 more)

### Community 80 - "chunking.py"
Cohesion: 0.11
Nodes (28): Implementation, Review, Review, Review, _char_split(), _merge_pieces(), _merge_word_pieces(), split_at_sentence_ends() (+20 more)

### Community 81 - "list_eligible_documents"
Cohesion: 0.23
Nodes (15): eligible_ids(), make_document(), test_active_approved_public_document_is_eligible(), test_language_filter_narrows_eligible_documents_only(), test_language_metadata_does_not_broaden_access(), test_local_repository_applies_the_policy_query(), test_non_active_lifecycle_is_excluded(), test_non_approved_status_is_excluded() (+7 more)

### Community 82 - "Ingestion pipeline (Spec 004)"
Cohesion: 0.11
Nodes (17): default_strategy, fusion, candidate_depth, k, method, weights, qdrant, connect_timeout_s (+9 more)

### Community 83 - "Retrieval fallback (Spec 008, D056-D062)"
Cohesion: 0.12
Nodes (18): bm25 builds no embedder and no Qdrant client, classify_model_error, classify_qdrant_error, D056-D062 fallback decisions, D057 Fallback eligibility classification, D058 Fallback policy per query, D061 Marking and evaluation of fallback, D062 5xx not eligible (+10 more)

### Community 84 - "Strategy"
Cohesion: 0.07
Nodes (42): R8 — Strategy and config (`retrieval/strategy.py`, `config/retrieval.yaml`), Implementation, Implementation, Review, Review, T5 — round 1, T5 — round 2, User decision (+34 more)

### Community 85 - "test_hybrid.py"
Cohesion: 0.11
Nodes (16): chunk(), dense_pair(), ForbiddenDenseIndex, production_lexical(), pub_chunk(), real_hybrid(), stub_result(), test_any_other_leg_error_propagates_without_fallback() (+8 more)

### Community 86 - "FakeEmbedder"
Cohesion: 0.17
Nodes (10): FakeEmbedder, test_conforms_to_protocol(), test_declared_vector_size(), test_default_size_is_64(), test_fake_device_is_none(), test_info_reports_fake_identity(), test_invalid_vector_size_rejected(), test_query_and_document_methods_agree_and_are_separate() (+2 more)

### Community 87 - "Backend stack"
Cohesion: 0.12
Nodes (18): Lexical file is a derived artifact, one per collection, bound by identity and chunk digest, Source documents are truth; chunks, embeddings, sparse entries, Qdrant points and preview indexes are derived artifacts, Backend stack, FastAPI, httpx, jsonschema, Multiple vector databases (avoided), Pandas (+10 more)

### Community 88 - "embedder"
Cohesion: 0.14
Nodes (13): chunker, max_chunk_chars, name, version, embedder, batch_size, fake_vector_size, model_id (+5 more)

### Community 89 - "D023 Task-gated agent workflow"
Cohesion: 0.12
Nodes (16): allowed_scopes, current_release, default_role, implemented_roles, allowed_scopes, allowed_scopes, roles, admin (+8 more)

### Community 90 - "ARCHITECTURE.md"
Cohesion: 0.12
Nodes (19): D042-D047, D053, D054 evaluation decisions, Evaluation architecture (Evaluation Suite case types), Evaluation assets never written by evaluation code (C6); candidates suggested and human-activated, Ingestion eligibility is the only guard against synthetic/unapproved documents; poisoned_public_document is not an authorization case, Evaluation isolation and gates, models.py, suite.py (tolerant typed cases, read-only load_suite), retrieval_eval.py, slices.py, sections.py, Section-level keys <document_id>#<section_id> (+11 more)

### Community 91 - "test_schemas.py"
Cohesion: 0.17
Nodes (6): load_schemas(), test_existing_schema_is_referenced_not_copied(), test_missing_schema_is_configuration_error(), test_per_type_required_field_enforced(), test_schema_files_are_valid_draft_2020_12(), test_valid_rows_pass()

### Community 92 - "list_eligible_documents"
Cohesion: 0.15
Nodes (7): collect(), _document_ids(), collect(), DocumentQuery, EligibilityPolicy, list_eligible_documents(), test_seed_corpus_is_entirely_eligible_for_guest()

### Community 93 - "pathlib"
Cohesion: 0.13
Nodes (16): Roadmap 2 - Document model + repository, KnowledgeDocument, Manifest/schema validation, S3DocumentRepository and external storage, apps/api, apps/web, CloudWatch, Document manifest (+8 more)

### Community 94 - "baseline.py"
Cohesion: 0.14
Nodes (9): Embedder, _aggregate(), default_output_path(), _mean(), run_baseline(), _slices(), SuiteRef, random_hit_rate() (+1 more)

### Community 96 - "documents/__init__.py"
Cohesion: 0.16
Nodes (5): AccessScope, ApprovalStatus, LanguageScope, LifecycleStatus, SourceAuthority

### Community 97 - "SpyIndex"
Cohesion: 0.15
Nodes (17): Admin content management, Agent capabilities only where they solve a real product problem, Audit trail, Basic analytics, Candidate evaluation, Change impact analysis, Content hashing, Evaluation Governance (keep/modify/deprecate/replace) (+9 more)

### Community 98 - "HybridRetriever"
Cohesion: 0.09
Nodes (25): Implementation, Implementation, Implementation, Review, Review, Review, T6 — round 1, T6 — round 2 (+17 more)

### Community 99 - "CURRENT_STATE.md"
Cohesion: 0.13
Nodes (14): interval, retries, start_period, test, timeout, container_name, healthcheck, image (+6 more)

### Community 101 - "repositories/__init__.py"
Cohesion: 0.06
Nodes (31): DocumentValidationError, DuplicateDocumentError, ManifestValidationError, split_frontmatter(), _StringDateLoader, normalize_body(), document_fields(), under_root() (+23 more)

### Community 102 - "006 Evaluation Framework Tasks"
Cohesion: 0.16
Nodes (15): Local multilingual BGE reranker, BM25 via FTS5 bm25(), Derived local lexical file per collection, Fusion, Generation, Lexical store, lexical-v1 tokens (D051), make index-lexical (+7 more)

### Community 103 - "transcript_metrics.py"
Cohesion: 0.20
Nodes (10): analyse(), category(), command_kinds(), executed_text(), expand(), main(), parse_time(), render() (+2 more)

### Community 104 - "Retrieval package (Spec 005 and 007)"
Cohesion: 0.14
Nodes (12): graphify skill pointer, spec/NNN branch and Spec-Task trailers, spec-implementer skill (one task per run), spec-orchestrator skill, spec-planner skill, spec-reviewer retrospective skill, Task-gated agent workflow loop, task-reviewer skill (read-only) (+4 more)

### Community 105 - "D035 One filter builder, fail-closed re-check, same path for later fallbacks (Spec 005)"
Cohesion: 0.09
Nodes (33): DenseIndex, build_access_filter, check_hit, DenseRetriever, make retrieve guest/public CLI, Strategy Protocol, BM25Retriever, rrf_fuse, HybridRetriever, Known issue: no circuit breaker, ~3 s per query with hanging Qdrant, Spec 008 retro F1: open-time outage makes BM25 serve whole run, Next step 7: Spec 008 hand-off carry-overs for HTTP route spec (circuit breaker, startup policy, 5xx, freshness cost, async check, client lifecycle), BM25Retriever, build_access_filter (+25 more)

### Community 106 - "Qdrant (vector database)"
Cohesion: 0.14
Nodes (13): Authorization metadata (access_scope, owner_user_id, tenant_id), Engineering Conventions, IDs and versions conventions, Knowledge files with provenance, Language metadata (content_language, lote_languages), Logging and tracing hygiene, Domain naming terms, Prompts as versioned assets (+5 more)

### Community 107 - "run_security_evaluation"
Cohesion: 0.25
Nodes (4): DroppedClauseLexical, test_a_dropped_lexical_clause_names_the_four_lexical_paths(), test_a_lexical_store_without_the_clause_fails_bm25_and_hybrid(), __init__()

### Community 108 - ".bind_to"
Cohesion: 0.33
Nodes (5): T2: where the shared pieces live (2026-10-31), chunk_set_difference(), _chunker_identity_differences(), ChunkSetDifference, _differences()

### Community 109 - "make eval-retrieval"
Cohesion: 0.12
Nodes (17): --allow-fake (plumbing only, never a recorded baseline), make retrieval-baseline (legacy, frozen Spec 005 producer), BASELINE_ARGS (--embedder, --allow-fake, --top-k, --suite, --release, --output, --config), Baseline metrics HitRate@5, random expectation min(1,5/N), Recall@5, MRR, p50/p95 latency, experiments/results/retrieval-baseline-<index_version>-<UTC>.json, never overwritten, D036 binding rules, D053 result 2.1, eval-retrieval exit 0 or 2 (+9 more)

### Community 110 - "dense_equivalence.py"
Cohesion: 0.24
Nodes (4): deterministic_clock(), equivalence_suite(), chunks_per_document_dense(), unanswerable()

### Community 111 - "test_content_hash.py"
Cohesion: 0.15
Nodes (12): Approved packages, pricing and validity, Six approved packages and prices, 60-day package validity, 24-hour cancellation notice, Personal coaching package, 60-minute coaching session on Google Meet, Individual coaching and live appointments, Mock assessments, scoring, feedback and review windows (+4 more)

### Community 112 - "SecurityIndex"
Cohesion: 0.18
Nodes (7): Implementation, T8 — round 1, User decision, delete_security_index(), SecurityIndex, test_the_security_index_records_a_fake_embedder_and_is_removed(), test_server_filter_keeps_every_forbidden_point_out()

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

### Community 118 - "IndexSettings"
Cohesion: 0.15
Nodes (7): Implementation, T2 — round 1, User decision, chunker_for_result(), embedder_identity(), IndexSettings, _DenseLike

### Community 119 - "evaluation/errors.py"
Cohesion: 0.13
Nodes (13): active_registry_languages(), aggregate(), _mean(), slice_by(), source_authority_key(), row(), test_absent_languages_from_a_temp_registry(), test_missing_registry_section_is_a_configuration_error() (+5 more)

### Community 120 - "failing_client"
Cohesion: 0.18
Nodes (10): content-hash-v1 (sole change-detection signal), LocalDocumentRepository, Document manifest and JSON Schema validation, make validate-knowledge, persona_scope spec defect (F2), BgeM3Embedder (optional extra, pinned revision), Embedder Protocol and FakeEmbedder, HeadingChunker and slugify rule (+2 more)

### Community 121 - "test_status_handling.py"
Cohesion: 0.20
Nodes (8): Adding a New Language Guide, language_registry.json, Public Assistant Content Boundaries, access_scope, content_language, Knowledge Schema and Metadata, language_scope, lote_languages

### Community 122 - "D050 SQLite FTS5 lexical store, not Qdrant sparse vectors (Spec 007)"
Cohesion: 0.19
Nodes (15): make index-lexical, lexical package: lexical-v1 tokenizer, FTS5 store, builder, standalone bm25 without Qdrant or extra (IndexIdentity, freshness), Known issue: verify_fresh asyncio.run in event loop, Known issue: BM25 statistics corpus-wide per file; needs per-scope files for roles, Known issue: freshness check rereads every document, Malayalam BM25 limit: exact tokens only, no stemming, D010 Qdrant primary, SQLite FTS5 fallback (+7 more)

### Community 123 - "load_suite"
Cohesion: 0.31
Nodes (10): load_suite(), copy_suite(), test_access_context_is_loaded_but_ignored(), test_dataset_types_loaded_by_type(), test_escaping_path_refused(), test_extra_fields_tolerated(), test_malformed_line_names_file_and_line_only(), test_real_suite_loads_every_declared_case_and_is_read_only() (+2 more)

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
Cohesion: 0.09
Nodes (27): Answerability and insufficient-evidence response, Authorization regression and staff canary, Docker, Terraform, EC2, ECR, CloudWatch, IAM, Bedrock, Bedrock Runtime (roadmap), BGE-M3 (roadmap), Deferred serving concerns (circuit breaker, startup policy, Qdrant 5xx D062), Citation manipulation tests and input/cost limits, Backend-owned citation validation (+19 more)

### Community 131 - "RuntimeSettings"
Cohesion: 0.33
Nodes (9): NAATI CCL candidate rules and test-day setup, Direct first-person speech requirement, Report technical incidents within 24 hours, NAATI, Online proctoring with separate phone or tablet, Prohibited materials and tools, Recording under 20 minutes, One repeated segment per dialogue without penalty (+1 more)

### Community 132 - "test_security_eval.py"
Cohesion: 0.19
Nodes (7): live_suite_rows(), clean_env(), _lexical_work_dir(), new_base(), seed_repository(), test_builder_refuses_a_real_embedder_identity(), test_full_gate_passes_on_the_seed_corpus()

### Community 133 - "Vocabulary, flashcards and free access"
Cohesion: 0.29
Nodes (7): EligibilityPolicy / GUEST_PUBLIC_POLICY, Security fixtures (valid but ineligible), config/ingestion.yaml and RuntimeSettings, Ingestion pipeline (target vs current state diff), AccessContext and Role (core), resolve_access / ResolvedAccess, W2A_TENANT_ID server tenant setting

### Community 134 - ".search"
Cohesion: 0.25
Nodes (8): Phase 2 basic analytics, Assistant behavior rules, Product Context, English and Malayalam language scope, Future personas, Phase 1 guest-only scope, Way2Australia AI product, Source-of-truth priorities

### Community 135 - "make validate-evaluation"
Cohesion: 0.15
Nodes (13): schemas.py, validate.py (referencing registry, validate-evaluation checks), Error format ERROR <ClassName>: <message>; eval-compare refusals start with 'not comparable:', EVAL_ARGS, python -m way2australia_rag.evaluation.cli {validate,retrieval,security,compare}, make eval-generation does not exist yet, Retrieval evaluation supports Recall@5, MRR, HitRate@5 and language/category/source-authority slices, Evaluation commands (single module evaluation.cli), Suite status draft, active, deprecated, replaced (+5 more)

### Community 136 - "Spec 002 document model and repository"
Cohesion: 0.16
Nodes (15): Pydantic document models and enums, EligibilityPolicy for guest/public, LocalDocumentRepository with manifest schema validation, make validate-knowledge, Spec 002 decisions made before approval (content_hash, fixtures, validate-knowledge), Seed data status: 13 public docs, evaluation datasets, security fixtures, Spec 002 retrospective findings F1-F6, Spec 002 document model and repository (+7 more)

### Community 137 - "Intentionally avoided choices"
Cohesion: 0.18
Nodes (13): Full agent orchestration (avoided), Intentionally avoided choices, Bedrock Agents / AgentCore for Phase 1 (avoided), Containers, Docker, Docker Compose, ECR, Fine-tuning (avoided) (+5 more)

### Community 138 - "Evaluation Framework Goal"
Cohesion: 0.39
Nodes (8): NAATI CCL test format, scoring and results, NAATI CCL test, Deduction-based assessment, Begin interpreting within five seconds of chime, NAATI, CCL is not professional interpreter certification, Pass requirement 63/90 overall and 29/45 per dialogue, Results within 4-6 weeks

### Community 139 - "DocumentRepository"
Cohesion: 0.25
Nodes (3): Acceptance criteria, _eligible_document_versions(), DocumentRepository

### Community 140 - "test_collection_with_1_0_settings_still_binds"
Cohesion: 0.12
Nodes (12): Implementation, Implementation, Review, Spec 009 — Task reviews, T2 — round 1, T2 — round 2, T2 — round 3, T3 — round 1 (+4 more)

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
Nodes (27): Implementation, Review, T4 — round 1, FallbackRetriever, access(), client_at(), closed_port(), Fallback (+19 more)

### Community 150 - "test_text.py"
Cohesion: 0.24
Nodes (6): make_payload(), make_point(), test_retrieve_cli_hit_line_is_single_clean_line(), test_safe_text_keeps_malayalam_joiners(), test_safe_text_strips_bidi_controls_but_keeps_zwj_zwnj(), test_safe_text_strips_controls_and_ansi()

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
Cohesion: 0.05
Nodes (29): R4/R5 — Lexical store (`lexical/store.py`, `lexical/build.py`), _canary_points(), Chunker, legacy_chunker_max_chunk_chars(), _parse_sections(), _Section, _split_body(), _split_words() (+21 more)

### Community 156 - "test_failed_write_removes_partial_file"
Cohesion: 0.20
Nodes (3): clean_env(), seeded(), test_failed_write_removes_partial_file()

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

### Community 161 - "Evaluation tooling"
Cohesion: 0.36
Nodes (8): Custom retrieval metrics (plain Python), DeepEval (not yet a dependency), Evaluation tooling, Generation/e2e metrics (correctness, faithfulness, citations, refusal), GitHub Actions, LLM-as-judge not sole source of truth, Primary retrieval metrics (Recall@5, MRR, HitRate@5), pytest

### Community 167 - "api/__init__.py"
Cohesion: 0.67
Nodes (3): Frontend stack, Next.js, TypeScript

### Community 168 - "DocumentRepository Protocol (async)"
Cohesion: 0.33
Nodes (6): DocumentRepository Protocol (async), KnowledgeDocument model, Spec 002 retrospective round 1, Spec 002 task review log (T3-T9), Spec 002 Document model and repository (verified), Acceptance dry run on Spec 002 T3

### Community 169 - "BGE-M3 embeddings"
Cohesion: 0.33
Nodes (6): Device not pinned, recorded in results (D038), Embeddings, Deterministic fake embedder, BGE-M3 embeddings, Multilingual design (lote_languages), Technology stack

### Community 170 - "tests/evaluation/__init__.py"
Cohesion: 0.67
Nodes (3): Canonical document metadata, Chunk metadata, Source authority precedence

### Community 191 - "test_every_path_is_gated_for_every_query"
Cohesion: 0.29
Nodes (4): test_every_path_is_gated_for_every_query(), counting(), test_the_gate_runs_all_three_strategies_on_v2(), counting()

### Community 193 - "test_status_handling.py"
Cohesion: 0.57
Nodes (4): golden_count(), suite_with_statuses(), test_exclusions_counted_by_status(), test_suggested_never_returned()

### Community 194 - "shutil"
Cohesion: 0.62
Nodes (5): _copy_seed(), _load(), test_manifest_hash_mismatch_raises(), test_moving_a_file_does_not_change_content_hash(), test_raw_sha256_mismatch_alone_raises()

### Community 195 - "test_seed_corpus.py"
Cohesion: 0.48
Nodes (4): manifest_records(), seed_documents(), test_security_fixtures_are_not_in_the_production_corpus(), test_seed_ids_and_versions_are_unique()

### Community 196 - "R12 — Real runs (user-owned gate)"
Cohesion: 0.33
Nodes (6): Acceptance criteria, R12 — Real runs (user-owned gate), Spec 007 BM25 and hybrid reference results, T7 real runs: fallback-only and Qdrant-up results, T7 — Real runs (user-owned gate), Verification

### Community 198 - "metrics.py, goldens.py, baseline.py, baseline_cli.py"
Cohesion: 0.50
Nodes (4): Baseline runner (refuses fake index without --allow-fake; HitRate@k, Recall@k, MRR, p50/p95, min(1,k/N) random expectation), D037 Baseline runner decisions, make retrieval-baseline (legacy dense-only), metrics.py, goldens.py, baseline.py, baseline_cli.py

## Ambiguous Edges - Review These
- `Task-gated agent workflow loop` → `graphify skill pointer`  [AMBIGUOUS]
  .claude/CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **380 isolated node(s):** `way2australia-api`, `way2australia-core`, `way2australia-observability`, `way2australia-rag`, `way2australia` (+375 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1309 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **35 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Change log` connect `security_eval.py` to `DenseRetriever`, `run_security_evaluation`, `HybridRetriever`, `Spec 007 hybrid retrieval`, `.bind_to`, `test_lexical_cli.py`, `007 — Hybrid Retrieval Requirements`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Are the 79 inferred relationships involving `DenseIndex` (e.g. with `Design summary` and `Decisions resolved before drafting`) actually correct?**
  _`DenseIndex` has 79 INFERRED edges - model-reasoned connections that need verification._
- **What connects `way2australia-api`, `way2australia-core`, `way2australia-observability` to the rest of the system?**
  _380 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `DenseRetriever` be split into smaller, more focused modules?**
  _Cohesion score 0.06371976647206005 - nodes in this community are weakly interconnected._
- **Why does `D055 Default strategy is hybrid (Spec 007)` connect `Spec 007 hybrid retrieval` to `typing`, `D035 One filter builder, fail-closed re-check, same path for later fallbacks (Spec 005)`, `Spec 008 retrieval fallback`, `Ingestion pipeline (Spec 004)`, `Development Workflow`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Are the 35 inferred relationships involving `LocalDocumentRepository` (e.g. with `Dependencies` and `Design summary`) actually correct?**
  _`LocalDocumentRepository` has 35 INFERRED edges - model-reasoned connections that need verification._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Task-gated agent workflow loop` and `graphify skill pointer`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._