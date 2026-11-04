# Graph Report - way2australia  (2026-11-04)

## Corpus Check
- 304 files · ~346,244 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 36 file(s) not represented in the graph (top: (none) 20, .jsonl 13, .mdc 1)

## Summary
- 4728 nodes · 14391 edges · 218 communities (178 shown, 40 thin omitted)
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 3093 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `99d323fb`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_compare.py
- DenseIndex
- opening.py
- verify_fresh
- test_validate.py
- ingestion/config.py
- test_applicability.py
- test_index.py
- Round 1 — 2026-11-03
- IngestionConfigurationError
- build_lexical_index
- ChunkerIdentity
- HeadingChunker
- compare.py
- test_lexical_cli.py
- json
- CURRENT_STATE.md current state document
- KnowledgeDocument
- .ensure_collection
- DenseRetriever
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
- evaluation/validate.py
- CountingEmbedder
- run_retrieval_evaluation
- evaluation/test_cli.py
- 010 — Multilingual Retrieval Requirements
- BgeM3Tokenizer
- 009 — Chunking Experiments Requirements
- 008 — Retrieval Fallback Requirements
- asyncio
- test_service.py
- retrieval/test_cli.py
- typing
- tokenizer.py
- Workflow Reviewer
- LocalDocumentRepository
- suite.py
- test_cli_config.py
- test_repository_contract.py
- Ingestion (Phase 1 baseline, Spec 004)
- 007 — Hybrid Retrieval Requirements
- test_recursive.py
- HeadingChunker
- build_security_repository
- FallbackRetriever
- test_content_hash.py
- BgeM3Embedder
- Development Workflow
- ._open
- 008 — Retrieval Fallback Requirements
- json
- Evaluation Phase 1 framework (Spec 006)
- security_eval.py
- test_factory_sets_the_connect_timeout_and_disables_the_version_check
- test_index_contract.py
- test_legacy_baseline_snapshot.py
- test_structure.py
- make eval-retrieval
- Spec 007 hybrid retrieval
- RetrievalResult
- ResolvedAccess
- embedder
- Phase 1 RAG query pipeline
- security_index.py
- Target repository shape (apps, packages, knowledge, sources, evaluation, tests, config, experiments, analytics, prompts, docs, infra)
- test_manifest_validation.py
- Section: Next step
- doc22
- test_baseline.py
- embedder
- repositories/__init__.py
- RetrievalConfigurationError
- test_fallback.py
- Ingestion pipeline (Spec 004)
- build_security_index
- pytest
- LexicalIndexBindingError
- test_lexical_standalone.py
- Backend stack
- embedder
- D023 Task-gated agent workflow
- D055 Default strategy is hybrid (Spec 007)
- test_schemas.py
- Roadmap 13 - Graceful degradation
- pathlib
- Spec status table
- test_eligibility.py
- check_target_allowed
- SpyIndex
- transcript_metrics.py
- CURRENT_STATE.md
- QdrantIndexStore
- read_result
- AWS target
- make ingest
- Retrieval package (Spec 005 and 007)
- retrieval_eval.py
- Qdrant (vector database)
- Chunk
- Development Workflow
- FakeEmbedder
- evaluation/cli.py
- test_content_hash.py
- Spec 005 dense retrieval baseline
- test_violation_names_the_document_from_the_error_attribute
- Spec 009 — Task reviews
- load_retrieval_config
- fusion
- SQLite FTS5
- QdrantIndexStore
- slices.py
- failing_client
- test_status_handling.py
- dense_equivalence.py
- test_open_retrieval_bm25_builds_no_embedder_and_no_client
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
- Eligible failures: Qdrant connect/network, Qdrant timeout, model load/download failure with network __cause__
- Spec 002 document model and repository
- SecurityIndex
- Evaluation Framework Goal
- test_lexical_tokenizer.py
- Phase 1 - Production-oriented RAG
- BGE-M3 (initial embedding model)
- Way2Australia AI Platform Master Implementation Plan
- Retrieval fallback (Spec 008, D056-D062)
- eval-compare
- Payments, account access and support boundaries
- make retrieve
- make test
- Mission
- test_bm25.py
- IndexSettings
- Spec 004 retrospective round 1 (PASS)
- policy
- policy
- policy
- typing
- conftest.py
- 007 — Hybrid Retrieval Design
- Orchestrator State Machine
- way2australia_api/__init__.py
- Project Context README
- DroppedClauseLexical
- way2australia_rag/__init__.py
- Scripted
- way2australia-core
- Phase 1 analytics event contract
- Spec-driven development workflow
- api/__init__.py
- LexicalIndex
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
- sync_agent_skills.py
- DocumentRepository
- Authorization enforced before generation
- open_retrieval / OpenedRetrieval
- R8 — Evaluation results for degraded runs
- ShortResultEmbedder
- stalled_port
- Spec 010 — task reviews
- policy
- test_store_integration.py
- Evaluation tooling
- Review
- Evaluation result format 2.2
- R12 — Real runs (user-owned gate)
- Way2Australia AI Platform Master Implementation Plan
- Review
- Spec 008 Retrieval Fallback Requirements
- LexicalConfig
- score_distribution
- IndexedDocument
- counting
- counting
- group_installed
- _no_qdrant

## God Nodes (most connected - your core abstractions)
1. `DenseIndex` - 113 edges
2. `LocalDocumentRepository` - 106 edges
3. `ResolvedAccess` - 79 edges
4. `Strategy` - 79 edges
5. `DenseRetriever` - 79 edges
6. `FakeTokenizer` - 78 edges
7. `run_retrieval_evaluation()` - 74 edges
8. `FakeEmbedder` - 73 edges
9. `open_retrieval()` - 70 edges
10. `HeadingChunker` - 69 edges

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

## Communities (218 total, 40 thin omitted)

### Community 0 - "test_compare.py"
Cohesion: 0.14
Nodes (51): Review, case(), doc(), doc21(), doc22(), ranked(), refusal(), run() (+43 more)

### Community 1 - "DenseIndex"
Cohesion: 0.09
Nodes (10): DenseIndex, raise_if_unavailable(), OddIdStore, ForbiddenDenseIndex, real_hybrid(), test_empty_bm25_leg_keeps_the_dense_order(), test_forbidden_dense_hit_fails_the_whole_query(), test_fusion_receives_only_the_legs_checked_hits() (+2 more)

### Community 2 - "opening.py"
Cohesion: 0.05
Nodes (59): Decisions resolved before drafting, Decisions D056-D062, Spec 008 Retrieval Fallback Design, Interfaces / models, Phase 2 compatibility / migration, R5 — `bm25` without Qdrant or the extra (`bm25.py`), R6 — `FallbackRetriever` (`fallback.py`) and `open_retrieval` (`opening.py`), R8 — Result format 2.2 (`retrieval_eval.py`) (+51 more)

### Community 3 - "verify_fresh"
Cohesion: 0.10
Nodes (20): Acceptance criteria, Acceptance criteria, R3 — Lexical index without Qdrant, R4 — Freshness check from the repository, User decision, User decision, T2 — Index identity, standalone lexical open and freshness check, Verification (+12 more)

### Community 4 - "test_validate.py"
Cohesion: 0.13
Nodes (32): edit_rows(), edit_suite(), root(), run(), test_active_golden_without_relevant_documents(), test_candidate_ineligible_document_is_not_unknown(), test_candidate_not_suggested(), test_candidate_referenced_by_suite() (+24 more)

### Community 5 - "ingestion/config.py"
Cohesion: 0.12
Nodes (27): Implementation, Implementation, Review, Review, T3 — round 1, T3 — round 2, User decision, T3 — Configuration, index settings, lexical identity and per-document freshness (+19 more)

### Community 6 - "test_applicability.py"
Cohesion: 0.15
Nodes (28): active_lote_codes(), _active_product_support_codes(), _active_list(), resolve_lote(), build_lexical(), _dropped_lote_setup(), DroppedFilterIndex, DroppedLoteClauseLexical (+20 more)

### Community 7 - "test_index.py"
Cohesion: 0.15
Nodes (38): IndexBindingError, bound_index(), client(), failing_client(), fake_info(), make_settings(), open_index(), payload() (+30 more)

### Community 8 - "Round 1 — 2026-11-03"
Cohesion: 0.07
Nodes (33): As-built notes, Cross-index comparison (R8), Security gate (R9), 009 — Chunking Experiments: Retrospective Review, Cross-task consistency, Deviations from the approved plan, Documentation reconciled, Extra checks (user-requested) (+25 more)

### Community 9 - "IngestionConfigurationError"
Cohesion: 0.11
Nodes (20): Requirements traceability, Implementation, T2 — round 2, IngestionConfigurationError, _build_prefix(), _compose_chunk(), DuplicateSectionError, _is_list_item() (+12 more)

### Community 10 - "build_lexical_index"
Cohesion: 0.07
Nodes (27): Implementation, T3 — `lexical-v1` tokenizer, lexical store and `make index-lexical`, Verification, Carry-over clean-ups (R11), Implementation, Review, T1 — round 1, embedder_identity() (+19 more)

### Community 11 - "ChunkerIdentity"
Cohesion: 0.08
Nodes (26): 009 — Chunking Experiments Design, Alternatives / deferred decisions, Chunker identity, settings and configuration (R5), Components / boundaries, Data flow, Design summary, Distinct-document metrics (R7), Error and failure behavior (+18 more)

### Community 12 - "HeadingChunker"
Cohesion: 0.10
Nodes (38): basic_suite(), build(), default_eval_extras(), fusion_config(), golden(), _LexicalStub, run(), Scripted (+30 more)

### Community 13 - "compare.py"
Cohesion: 0.11
Nodes (38): Implementation, Review, T7 — round 1, User decision, Implementation, Review, T4 — round 1, User decision (+30 more)

### Community 14 - "test_lexical_cli.py"
Cohesion: 0.23
Nodes (19): lexical_dir(), run(), test_bad_config_exits_2(), test_cased_name_cannot_write_into_the_real_repository(), test_env_dir_into_tracked_directory_is_refused(), test_file_holds_the_identity_and_no_chunk_text_is_printed(), test_lexical_location_is_git_ignored(), test_missing_config_exits_2() (+11 more)

### Community 15 - "json"
Cohesion: 0.15
Nodes (25): committed(), edit_jsonl(), lines(), manifest(), problems(), read_lines(), root(), test_candidates_differ_only_in_promoted_as() (+17 more)

### Community 16 - "CURRENT_STATE.md current state document"
Cohesion: 0.10
Nodes (36): standalone bm25 without Qdrant or extra (IndexIdentity, freshness), CURRENT_STATE.md current state document, Current goal: Specs 001-008 complete; Spec 008 verified and merged into main (1107b67), plan next spec, Phase 2 Knowledge Release workflow designed not implemented, Public/guest retrieval only in Phase 1; English + Malayalam, Known issue: Qdrant and Hugging Face 5xx not fallback-eligible, Known issue: verify_fresh asyncio.run in event loop, Known issue: Qdrant client lifecycle leak on failed open (+28 more)

### Community 17 - "KnowledgeDocument"
Cohesion: 0.06
Nodes (11): _check_language_code(), KnowledgeDocument, collect(), _eligible_document_versions(), DocumentQuery, DocumentRepository, EligibilityPolicy, list_eligible_documents() (+3 more)

### Community 18 - ".ensure_collection"
Cohesion: 0.21
Nodes (15): IndexSettingsMismatchError, client(), make_settings(), snapshot(), store(), test_absent_creates_both_and_writes_settings(), test_differing_settings_refuse_without_writes(), test_empty_without_settings_recreates_payload_indexes() (+7 more)

### Community 19 - "DenseRetriever"
Cohesion: 0.10
Nodes (27): IndexPoint, client_with_forbidden(), build_client(), docs(), guest(), make_payload(), make_point(), open_spy() (+19 more)

### Community 20 - "007 — Hybrid Retrieval Requirements"
Cohesion: 0.05
Nodes (44): BM25Retriever with SQL access clause, eval-compare identity rules (R10), HybridRetriever (dense leg then BM25 leg, no single-leg fallback), lexical-v1 tokenizer (NFC, ZWJ/ZWNJ dropped, L/N/Mn/Mc token chars, 64-term cap), Result format 2.1 and security result 1.1, config/retrieval.yaml and build_retriever strategy factory, Security gate over dense, bm25 and hybrid, SQLite FTS5 lexical store (derived, git-ignored, bound to dense index) (+36 more)

### Community 21 - "test_validate_knowledge.py"
Cohesion: 0.22
Nodes (26): load(), test_bad_date_fails_loading_naming_document_and_field(), test_seed_corpus_still_loads(), test_valid_date_loads(), build_repo(), metadata(), problems_for(), run_cli() (+18 more)

### Community 22 - "test_availability.py"
Cohesion: 0.06
Nodes (43): 008 — Retrieval Fallback Design, As-built notes, Data flow, Error and failure behavior, Observability, Package / file placement, R1 — Failure classification (`errors.py`, `availability.py`), R7 — Marking (`models.py`, `retrieval/cli.py`) (+35 more)

### Community 23 - "BGE-M3 Adapter"
Cohesion: 0.06
Nodes (18): Model Preferences, Agent Skills README, Implementation Checklist, Spec Implementer Skill, task-reviews.md Implementation Block, Design Template, Change Log, Requirements Template (+10 more)

### Community 24 - "test_lexical_standalone.py"
Cohesion: 0.05
Nodes (33): Day-1 Usage, document_manifest.jsonl, golden_public.jsonl, Source-of-Truth Policy, chunking, overlap_tokens, strategy, target_tokens (+25 more)

### Community 25 - "Spec 004 ingestion baseline"
Cohesion: 0.14
Nodes (18): HeadingChunker heading v1 2000-char cap, Embedder Protocol, fake and BGE-M3 adapter, IngestionService change detection, make ingest and config/ingestion.yaml, 17-field PointPayload and UUIDv5 point IDs, QdrantIndexStore with companion settings collection, Heading chunking only synthetic-tested, none of 13 docs has headings, Spec 004 open review findings (T3 F1, T5 F2, T7 F1-F3, T8 F1, retro F1) (+10 more)

### Community 26 - "FakeTokenizer"
Cohesion: 0.12
Nodes (23): Review, Review, _char_split(), _merge_pieces(), _merge_word_pieces(), split_at_sentence_ends(), _split_long_unit(), split_on_separator() (+15 more)

### Community 27 - "test_suite_v3.py"
Cohesion: 0.10
Nodes (30): Implementation, Review, T1 — round 1, User decision, candidate_row(), candidates(), edit_jsonl(), errors() (+22 more)

### Community 28 - "test_strategy_eval.py"
Cohesion: 0.09
Nodes (38): Review, Strategy, build_retriever(), run_equivalence(), build_lexical(), eval_world(), leg_order(), lexical_env() (+30 more)

### Community 29 - "Evaluation CLI Tests"
Cohesion: 0.06
Nodes (44): get_health(), HealthResponse, get_request_settings(), get_settings(), Settings, create_app(), isolate_settings_environment(), test_create_app_wires_settings() (+36 more)

### Community 30 - "evaluation/validate.py"
Cohesion: 0.11
Nodes (20): Implementation, Review, T1 — round 1, User decision, EvaluationSchemas, _candidate_rules(), problem(), _describe() (+12 more)

### Community 32 - "run_retrieval_evaluation"
Cohesion: 0.10
Nodes (20): User decision, T4 review follow-ups (planner amendment 2026-11-02), T5 — Security gate across chunkers, Verification, DatasetType, LoadedSuite, active_golden_cases(), _fusion_report() (+12 more)

### Community 33 - "evaluation/test_cli.py"
Cohesion: 0.20
Nodes (18): load_production_ingestion_config(), clean_env(), index_factory(), real_factory(), run(), test_bad_top_k_exits_2(), test_existing_output_exits_2_before_qdrant(), test_fake_embedder_exits_2_before_qdrant() (+10 more)

### Community 34 - "010 — Multilingual Retrieval Requirements"
Cohesion: 0.07
Nodes (28): 010 — Multilingual Retrieval Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+20 more)

### Community 35 - "BgeM3Tokenizer"
Cohesion: 0.13
Nodes (10): BgeM3Tokenizer, hub(), test_bge_m3_cache_hit_counts(), test_bge_m3_miss_offline_refused(), test_bge_m3_miss_online_download(), test_bge_m3_refuses_floating_revision(), test_bge_m3_smoke_matches_sentence_transformer_tokenizer(), test_bge_m3_wrong_revision_refused() (+2 more)

### Community 36 - "009 — Chunking Experiments Requirements"
Cohesion: 0.07
Nodes (28): 009 — Chunking Experiments Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+20 more)

### Community 37 - "008 — Retrieval Fallback Requirements"
Cohesion: 0.09
Nodes (36): Baseline runner (refuses fake index without --allow-fake; HitRate@k, Recall@k, MRR, p50/p95, min(1,k/N) random expectation), Binding: embedder model ID, revision, vector size, normalization, fake flag and index_version must equal recorded IndexSettings, BM25Retriever(identity, lexical), BM25 statistics (IDF, avg length) computed over every row of a lexical file, build_access_filter (the only filter builder), build_retriever (only place a strategy name becomes a retriever), retrieval_client_factory (Qdrant client with configured timeouts), config/retrieval.yaml (default_strategy hybrid, RRF k 60, depth 50) (+28 more)

### Community 38 - "asyncio"
Cohesion: 0.15
Nodes (22): LocalRepositoryConfig, test_agrees_with_day1_baseline(), test_repository_content_hash_is_content_hash_v1(), test_seed_corpus_is_entirely_eligible_for_guest(), _copy_seed(), seed_repository(), test_documents_outside_approved_roots_are_never_loaded(), test_get_document_by_id_and_version() (+14 more)

### Community 39 - "test_service.py"
Cohesion: 0.19
Nodes (24): doc(), Harness, test_bumped_document_version_updates(), test_changed_body_updates(), test_changed_metadata_field_updates(), test_chunk_shrink_leaves_no_orphan(), test_chunk_too_long_report_has_no_chunk_text(), test_chunker_exception_is_per_document_failure() (+16 more)

### Community 40 - "retrieval/test_cli.py"
Cohesion: 0.15
Nodes (23): _advice_ok(), clean_env(), Factory, indexed(), ingest(), retrieve(), test_bad_args_exit_2_without_client(), test_bad_config_exit_2_without_client() (+15 more)

### Community 41 - "typing"
Cohesion: 0.10
Nodes (31): 006-candidates.jsonl with 7 suggested rows, make eval-compare, make eval-security hard gate, result 2.2 and served-strategy eval-compare, eval-security five paths, governed suite loader and schemas, make validate-evaluation, Spec 006 retrospective findings (F1 byte-identity, eval-security not in verify) (+23 more)

### Community 42 - "tokenizer.py"
Cohesion: 0.13
Nodes (14): R3 — Tokenizer `lexical-v1` (`lexical/tokenizer.py`), Review, _is_token_char(), LexicalTokenizer, query_terms(), _query_terms_from(), QueryTerms, replace_sequences() (+6 more)

### Community 43 - "Workflow Reviewer"
Cohesion: 0.07
Nodes (25): Considered and rejected, Evidence, F1 — <title> [waste | quality risk | process slip] (confidence: high/medium/low), Findings, New features and tools (official sources, since <date>), Not measurable here, P1 — <title> (addresses F#; expected saving: ...), Proposals (+17 more)

### Community 44 - "LocalDocumentRepository"
Cohesion: 0.12
Nodes (44): LocalDocumentRepository, build(), guest_access(), new_base(), real_queries(), run_gate(), security_result(), seed_repository() (+36 more)

### Community 45 - "suite.py"
Cohesion: 0.12
Nodes (23): CaseBase, DatasetRef, GoldenCase, SecurityCase, SuiteManifest, UnanswerableCase, inside(), load_suite() (+15 more)

### Community 46 - "test_cli_config.py"
Cohesion: 0.10
Nodes (25): format_summary(), main(), _parser(), RunReport, test_cli_has_no_embedder_or_allow_fake_flag(), test_eval_cli_unknown_strategy_is_a_usage_error(), clean_env(), _factory() (+17 more)

### Community 47 - "test_repository_contract.py"
Cohesion: 0.19
Nodes (12): test_fusion_module_has_no_authorization_or_io_surface(), InMemoryDocumentRepository, make_document(), test_document_query_has_no_filesystem_concepts(), test_document_query_is_immutable(), test_get_document_missing_raises_not_found(), test_get_document_returns_latest_or_requested_version(), test_in_memory_repository_satisfies_protocol() (+4 more)

### Community 48 - "Ingestion (Phase 1 baseline, Spec 004)"
Cohesion: 0.08
Nodes (32): Authorization applied inside each retriever before fusion, never after RRF, reranking or generation, Authorization filter is part of the Qdrant query so unauthorized points never leave the store, BgeM3Embedder (optional bge-m3 extra, dense only), check_hit (fail-closed re-check, second line of defense), D025-D030, D032 ingestion decisions, D035 Future fallbacks must take the same ResolvedAccess and call check_hit, D040 Authorization per retriever, DocumentRepository Protocol (get_document, list_documents) (+24 more)

### Community 49 - "007 — Hybrid Retrieval Requirements"
Cohesion: 0.09
Nodes (27): optional bge-m3 extra (sentence-transformers, PyTorch), D048 graphify tooling, make experiment CONFIG=... (target; records git commit, release, suite, chunker, embedder, strategy, metrics, latency), make format, Knowledge graph graphify (D048), /graphify . --update (user, once per spec after merge), graphify query / path / explain, graphify update . (+19 more)

### Community 50 - "test_recursive.py"
Cohesion: 0.19
Nodes (15): assert_matches_snapshot(), assert_recursive_chunks_whitespace_fidelity(), chunks_to_records(), load_snapshot(), snapshot_for_document(), recursive_chunker(), test_deterministic(), test_heading_seed_snapshot_unchanged() (+7 more)

### Community 51 - "HeadingChunker"
Cohesion: 0.11
Nodes (27): HeadingChunker, _is_word_char(), slugify(), ids(), test_deterministic(), test_duplicate_headings_get_unique_ids_in_order(), test_duplicate_suffix_does_not_collide_with_literal_heading(), test_headings_inside_code_fences_ignored() (+19 more)

### Community 52 - "build_security_repository"
Cohesion: 0.10
Nodes (22): build_security_repository(), _fixture_files(), security_repository(), clean_env(), copy_fixtures(), _lexical_work_dir(), spy_lexical_path(), wrapper() (+14 more)

### Community 53 - "FallbackRetriever"
Cohesion: 0.15
Nodes (14): Fallback authorization invariant (same ResolvedAccess), BM25Retriever (identity, lexical), classify_model_error, classify_qdrant_error, Qdrant client lifecycle gap, FallbackRetriever, Hugging Face error shapes (T1 As-built), HybridRetriever / rrf_fuse (unchanged, fail closed) (+6 more)

### Community 54 - "test_content_hash.py"
Cohesion: 0.12
Nodes (22): canonical_json(), _canonical_value(), _canonical_value_mapping(), compute_body_sha256(), compute_content_hash(), normalize_body(), sha256_hex(), _copy_seed() (+14 more)

### Community 55 - "BgeM3Embedder"
Cohesion: 0.12
Nodes (13): BgeM3Embedder, OptionalDependencyError, missing(), test_constructing_does_not_load_the_model(), test_device_none_before_load_and_recorded_after(), test_missing_group_at_load_raises_optional_dependency_error(), test_missing_group_refused_at_construction(), test_model_loaded_once_with_revision_and_batches() (+5 more)

### Community 56 - "Development Workflow"
Cohesion: 0.09
Nodes (33): Evaluation Suite includes goldens, refusal, multilingual, security, regression, Finalized stack: Python/FastAPI, Next.js, Qdrant, SQLite FTS5, BGE-M3, Bedrock, Langfuse, CloudWatch, Terraform ap-south-1, GitHub Actions, Ingestion operating notes (QDRANT_COLLECTION_BASE for fake runs, make setup-bge-m3), agent-skills sync, D001 Python-first backend, D002 RAG as reusable internal package, D003 Knowledge outside RAG package, D005 Documents are truth; chunks are derived (+25 more)

### Community 57 - "._open"
Cohesion: 0.15
Nodes (6): FilterDroppingIndex, test_forbidden_points_are_never_returned(), test_store_dropping_the_filter_fails_closed(), http_client(), test_a_closed_port_is_unavailable(), test_a_stalled_open_times_out_within_the_connect_bound()

### Community 58 - "008 — Retrieval Fallback Requirements"
Cohesion: 0.14
Nodes (15): 008 — Retrieval Fallback Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Spec 008 taken ahead of roadmap 7 (chunking), Decisions resolved before drafting, Definition of Done (+7 more)

### Community 59 - "json"
Cohesion: 0.10
Nodes (20): chunker, context_prefix, name, overlap_tokens, target_tokens, version, embedder, batch_size (+12 more)

### Community 60 - "Evaluation Phase 1 framework (Spec 006)"
Cohesion: 0.06
Nodes (39): D042-D047, D053, D054 evaluation decisions, Evaluation architecture (Evaluation Suite case types), Evaluation assets never written by evaluation code (C6); candidates suggested and human-activated, Ingestion eligibility is the only guard against synthetic/unapproved documents; poisoned_public_document is not an authorization case, Evaluation isolation and gates, models.py, suite.py (tolerant typed cases, read-only load_suite), retrieval_eval.py, slices.py, sections.py, schemas.py, validate.py (referencing registry, validate-evaluation checks) (+31 more)

### Community 61 - "security_eval.py"
Cohesion: 0.09
Nodes (30): Review, T8 — round 1, User decision, T10 — Documentation, decisions and hand-off, Verification, Implementation, Review, T4 — round 1 (+22 more)

### Community 63 - "test_index_contract.py"
Cohesion: 0.10
Nodes (18): compare(), mismatch_message(), base_settings(), test_authorization_and_language_fields_are_separate(), test_build_index_settings_records_embedder_and_chunker(), test_build_payload_copies_document_and_chunk(), test_collection_name_derivation(), test_compare_equal_and_ignores_hash_contract() (+10 more)

### Community 64 - "test_legacy_baseline_snapshot.py"
Cohesion: 0.13
Nodes (15): clean_env(), _Factory, _FixedDatetime, _record_opens(), note(), wrap_func(), inner(), wrap_method() (+7 more)

### Community 65 - "test_structure.py"
Cohesion: 0.18
Nodes (22): manifest_document_count(), assert_structure_chunks_whitespace_fidelity(), make_document(), structure_chunker(), test_duplicate_sibling_headings_raise(), test_fence_blocks_are_atomic_and_headings_inside_ignored(), test_long_list_splits_only_between_items(), test_main_collision_with_heading_slug() (+14 more)

### Community 66 - "make eval-retrieval"
Cohesion: 0.13
Nodes (22): bm25 strategy, bm25 needs neither Qdrant nor the bge-m3 extra (Spec 008), config/retrieval.yaml schema 1.1 (default_strategy hybrid, qdrant.connect_timeout_s 2, query_timeout_s 3; 1.0 refused), D036 binding rules, dense strategy, --strategy dense needs no lexical file, Embedder pair from index_settings or dense_identity; fallback-only 2.2 file compares against Spec 007 bm25 file, eval-retrieval exit 0 or 2 (+14 more)

### Community 67 - "Spec 007 hybrid retrieval"
Cohesion: 0.10
Nodes (28): build_retriever, make eval-retrieval, make index-lexical, lexical package: lexical-v1 tokenizer, FTS5 store, builder, Known issue: BM25 statistics corpus-wide per file; needs per-scope files for roles, Known issue: legacy chillu sequence does not match atomic chillu in BM25, Known issue: evaluation-data gaps (ml goldens, relevant_section_ids empty), Known issue: g004 overlaps u001, keep_both (+20 more)

### Community 68 - "RetrievalResult"
Cohesion: 0.05
Nodes (56): As-built notes, Package / file placement, R7 — Fusion and `HybridRetriever` (`retrieval/fusion.py`, `hybrid.py`), Change log, Implementation, Implementation, Implementation, Implementation (+48 more)

### Community 69 - "ResolvedAccess"
Cohesion: 0.06
Nodes (76): Alternatives / deferred decisions, Design summary, Phase 2 compatibility / migration, R6 — `BM25Retriever` (`retrieval/bm25.py`), Security / authorization, Acceptance criteria, Acceptance criteria, Acceptance criteria (+68 more)

### Community 70 - "embedder"
Cohesion: 0.11
Nodes (17): chunker, context_prefix, name, overlap_tokens, target_tokens, version, embedder, batch_size (+9 more)

### Community 71 - "Phase 1 RAG query pipeline"
Cohesion: 0.17
Nodes (13): Deduplication, context budgeting, evidence ordering, Roadmap 9 - Reranking + context building, Reranker failure to hybrid results, Small documents and chunking strategy, Citation strategy (backend-owned validation), FAQ-aware retrieval experiment, Hybrid retrieval (dense + BM25 + RRF), Production knowledge corpus (+5 more)

### Community 72 - "security_index.py"
Cohesion: 0.08
Nodes (19): Acceptance criteria, AccessScope, ApprovalStatus, LanguageScope, LifecycleStatus, SourceAuthority, _canary_points(), Chunker (+11 more)

### Community 73 - "Target repository shape (apps, packages, knowledge, sources, evaluation, tests, config, experiments, analytics, prompts, docs, infra)"
Cohesion: 0.17
Nodes (12): AccessContext(role, tenant_id) with blank tenant refused, Future agent folders intentionally not created, apps/api (FastAPI application layer), apps/web (Next.js/TypeScript frontend: recruiter assistant, RAG Lab, engineering views), core/access.py (Role, frozen AccessContext), guest_access, Knowledge model metadata (document_id, document_version, tenant_id, access_scope, lote_languages, content_language, source_authority...), No language filter, score threshold or reranking yet (+4 more)

### Community 74 - "test_manifest_validation.py"
Cohesion: 0.27
Nodes (18): metadata(), record(), run(), test_duplicate_document_id_rejected(), test_duplicate_document_version_rejected(), test_frontmatter_errors(), test_frontmatter_missing_required_field(), test_frontmatter_schema_violation_names_document_and_field() (+10 more)

### Community 75 - "Section: Next step"
Cohesion: 0.11
Nodes (17): Atomic publish and rollback, Phase 2 audit trail, AWS deployment architecture (ap-south-1), Controlled document-change workflow (Release Candidate), CI/CD pipeline, Evaluation governance states, Evaluation slices, Evaluation Suite (public-eval-v1) (+9 more)

### Community 76 - "doc22"
Cohesion: 0.31
Nodes (8): doc23(), run_cross(), test_2_3_against_2_2_one_chunk_passes_without_cross_index(), test_committed_baseline_compared_with_itself_passes(), test_cross_index_allows_index_fields(), test_cross_index_allows_lexical_digest_and_chunk_count(), test_cross_index_with_2_2_side_is_refused(), test_make_eval_compare_cross_index_prints_chunker()

### Community 77 - "test_baseline.py"
Cohesion: 0.10
Nodes (23): case(), clean_env(), cli_run(), DeviceStub, _git(), run(), seeded(), setup() (+15 more)

### Community 78 - "embedder"
Cohesion: 0.14
Nodes (13): chunker, max_chunk_chars, name, version, embedder, batch_size, fake_vector_size, model_id (+5 more)

### Community 79 - "repositories/__init__.py"
Cohesion: 0.06
Nodes (31): DocumentRepositoryError, DocumentValidationError, DuplicateDocumentError, ManifestValidationError, split_frontmatter(), _StringDateLoader, document_fields(), under_root() (+23 more)

### Community 80 - "RetrievalConfigurationError"
Cohesion: 0.15
Nodes (15): CaseStatus, declared_release_id(), RetrievalConfigurationError, declared_release_id(), load_golden_cases(), load_suite(), SuiteRef, test_declared_release() (+7 more)

### Community 81 - "test_fallback.py"
Cohesion: 0.11
Nodes (26): Review, FallbackRetriever, access(), client_at(), closed_port(), Fallback, open_hybrid(), Primary (+18 more)

### Community 82 - "Ingestion pipeline (Spec 004)"
Cohesion: 0.09
Nodes (26): default_strategy, fusion, candidate_depth, k, method, weights, lexical, tokenizer (+18 more)

### Community 83 - "build_security_index"
Cohesion: 0.09
Nodes (16): R11 — Security gate (`security_index.py`, `security_eval.py`), Implementation, Implementation, Review, T5 — round 1, security_gate_chunkers(), build_security_index(), delete_security_index() (+8 more)

### Community 84 - "pytest"
Cohesion: 0.05
Nodes (38): Alternatives / deferred decisions, AccessContext, Role, test_blank_tenant_refused(), test_empty_tenant_refused(), test_no_language_or_scope_fields(), test_tenant_is_stripped(), test_unknown_role_refused() (+30 more)

### Community 85 - "LexicalIndexBindingError"
Cohesion: 0.08
Nodes (28): R4/R5 — Lexical store (`lexical/store.py`, `lexical/build.py`), Components / boundaries, R10 — Security gate (`security_eval.py`), R3 — Standalone lexical open (`identity.py`, `lexical/store.py`), R4 — Freshness from the repository (`lexical/freshness.py`), R9 — `eval-compare` (`results.py`, `compare.py`), As-built notes, Interfaces / models (+20 more)

### Community 86 - "test_lexical_standalone.py"
Cohesion: 0.06
Nodes (52): build_production(), identity(), ingest_dense(), open_lexical(), payload(), rewrite_settings(), synthetic_entries(), test_bind_does_not_write_to_qdrant() (+44 more)

### Community 87 - "Backend stack"
Cohesion: 0.10
Nodes (22): Source documents are truth; chunks, embeddings, sparse entries, Qdrant points and preview indexes are derived artifacts, Backend stack, Derived retrieval index in Qdrant, FastAPI, httpx, jsonschema, Relational metadata/workflow/audit database, Multiple vector databases (avoided) (+14 more)

### Community 88 - "embedder"
Cohesion: 0.14
Nodes (13): chunker, max_chunk_chars, name, version, embedder, batch_size, fake_vector_size, model_id (+5 more)

### Community 89 - "D023 Task-gated agent workflow"
Cohesion: 0.12
Nodes (16): allowed_scopes, current_release, default_role, implemented_roles, allowed_scopes, allowed_scopes, roles, admin (+8 more)

### Community 90 - "D055 Default strategy is hybrid (Spec 007)"
Cohesion: 0.10
Nodes (23): make retrieval-baseline legacy frozen, RetrievalUnavailableError and availability classification, Known issue: git_dirty true in Spec 007 BM25/hybrid result files (user-accepted), Latency hybrid p50 80.3 ms p95 103.6 ms; bm25 p50 0.19 ms, BM25 metrics: 64/69 goldens, MRR 0.7082, Hybrid metrics: 68/69 goldens, MRR 0.9094, Retrieval misses g004 g026 g061, Next step 2: real BGE-M3 baseline committed (+15 more)

### Community 91 - "test_schemas.py"
Cohesion: 0.11
Nodes (12): EvaluationConfigurationError, build_chunk_stats(), require_retrieval_depth(), _require_settings_if_dense_served(), required_distinct_depth(), load_schemas(), test_depth_check_boundary(), test_existing_schema_is_referenced_not_copied() (+4 more)

### Community 92 - "Roadmap 13 - Graceful degradation"
Cohesion: 0.60
Nodes (5): Deferred serving concerns (circuit breaker, startup policy, Qdrant 5xx D062), Dense to BM25 degradation, Roadmap 13 - Graceful degradation, Qdrant failure to SQLite FTS5, Spec 008 early delivery (D056)

### Community 93 - "pathlib"
Cohesion: 0.25
Nodes (9): apps/api, apps/web, CloudWatch, Future multimodal mock-test evaluation, Langfuse tracing, packages/core, packages/observability, packages/rag (+1 more)

### Community 94 - "Spec status table"
Cohesion: 0.10
Nodes (21): Completion: retrospective, Spec-Review commit, merge, verified status, Spec orchestrator loop (route, role subagents, user approval, merge), GET /health endpoint, make setup, packages core/rag/observability skeletons, task-gated spec skills and skills-sync, task State lifecycle and spec/NNN branches, uv workspace and uv.lock (+13 more)

### Community 95 - "test_eligibility.py"
Cohesion: 0.23
Nodes (15): eligible_ids(), make_document(), test_active_approved_public_document_is_eligible(), test_language_filter_narrows_eligible_documents_only(), test_language_metadata_does_not_broaden_access(), test_local_repository_applies_the_policy_query(), test_non_active_lifecycle_is_excluded(), test_non_approved_status_is_excluded() (+7 more)

### Community 96 - "check_target_allowed"
Cohesion: 0.15
Nodes (16): Implementation, Review, T3 — round 3, User decision, check_target_allowed(), _inside_git_work_tree(), _is_git_ignored(), LexicalTargetRefusedError (+8 more)

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
Nodes (17): Implementation, T5 — round 1, User decision, NotComparableError, _build_run(), _mixed(), _num(), read_result() (+9 more)

### Community 102 - "AWS target"
Cohesion: 0.08
Nodes (30): Roadmap 11 - Observability, Langfuse traces, Stage latency, model/tokens/cost, release/config IDs, Full agent orchestration (avoided), Intentionally avoided choices, AWS target, Bedrock Agents / AgentCore for Phase 1 (avoided), Bedrock Knowledge Bases as core RAG (avoided) (+22 more)

### Community 103 - "make ingest"
Cohesion: 0.08
Nodes (28): D060 Standalone lexical freshness, Standalone freshness proves lexical file matches repository, not live Qdrant (D060), lexical/cli.py (make index-lexical writes only git-ignored file), Lexical file is a derived artifact, one per collection, bound by identity and chunk digest, freshness.py (verify_fresh, chunk digest recomputed from repository), lexical/ package (Spec 007), store.py (SQLite FTS5: chunks table, chunk_terms FTS5 table, settings row; LexicalIndex.open, bind_to, search), tokenizer.py (lexical-v1) (+20 more)

### Community 104 - "Retrieval package (Spec 005 and 007)"
Cohesion: 0.14
Nodes (12): graphify skill pointer, spec/NNN branch and Spec-Task trailers, spec-implementer skill (one task per run), spec-orchestrator skill, spec-planner skill, spec-reviewer retrospective skill, Task-gated agent workflow loop, task-reviewer skill (read-only) (+4 more)

### Community 105 - "retrieval_eval.py"
Cohesion: 0.06
Nodes (37): default_output_path(), write_document(), dedupe_sections(), section_key(), section_report(), Embedder, _aggregate(), BaselineResult (+29 more)

### Community 106 - "Qdrant (vector database)"
Cohesion: 0.14
Nodes (13): Authorization metadata (access_scope, owner_user_id, tenant_id), Engineering Conventions, IDs and versions conventions, Knowledge files with provenance, Language metadata (content_language, lote_languages), Logging and tracing hygiene, Domain naming terms, Prompts as versioned assets (+5 more)

### Community 107 - "Chunk"
Cohesion: 0.27
Nodes (8): Chunk, check_chunks(), ChunkTooLongError, _effective_limit(), test_above_limit_raises_with_fields(), test_at_limit_passes(), test_cap_below_model_maximum(), test_cap_none_uses_model_maximum()

### Community 108 - "Development Workflow"
Cohesion: 0.21
Nodes (12): Branching and commits (spec/NNN, Spec-Task trailer), Development Workflow, Multi-agent handoff, Implementation rule: BLOCKED spec issue, Phase discipline, Protected source-of-truth data, Required spec-reviewer retrospective, Agent skills (orchestrator, planner, implementer, task-reviewer, spec-reviewer) (+4 more)

### Community 109 - "FakeEmbedder"
Cohesion: 0.13
Nodes (15): EmbedderInfo, FakeEmbedder, _cosine_to_query(), test_run_retrieval_evaluation_on_multi_chunk_recursive_index(), _text_with_score_below(), __init__(), test_conforms_to_protocol(), test_declared_vector_size() (+7 more)

### Community 110 - "evaluation/cli.py"
Cohesion: 0.07
Nodes (29): R2 — Qdrant timeouts (`qdrant_client.py`, `config/retrieval.yaml`), _authority_map(), _compare(), default_security_output_path(), format_security_summary(), format_summary(), main(), _retrieval() (+21 more)

### Community 111 - "test_content_hash.py"
Cohesion: 0.15
Nodes (12): Approved packages, pricing and validity, Six approved packages and prices, 60-day package validity, 24-hour cancellation notice, Personal coaching package, 60-minute coaching session on Google Meet, Individual coaching and live appointments, Mock assessments, scoring, feedback and review windows (+4 more)

### Community 112 - "Spec 005 dense retrieval baseline"
Cohesion: 0.12
Nodes (25): AccessContext, Role, W2A_TENANT_ID, DenseIndex, build_access_filter, check_hit, DenseRetriever, make retrieve guest/public CLI, BGE-M3 device mps not pinned (D038), Spec 005 retrospective findings F3-F5, Spec 005 dense retrieval baseline, Spec 005 status: verified 2026-10-23 merged b33462e, AccessContext and Role (+17 more)

### Community 113 - "test_violation_names_the_document_from_the_error_attribute"
Cohesion: 0.18
Nodes (12): AGENTS.md Project Rules, DocumentRepository Abstraction, Evaluation Governance Rules, Language Separation Rules, Phase 1 Scope, Task-gated Spec Loop, CLAUDE.md Project Instructions, graphify Knowledge Graph Rules (+4 more)

### Community 114 - "Spec 009 — Task reviews"
Cohesion: 0.13
Nodes (13): Implementation, Implementation, Implementation, Review, Review, Spec 009 — Task reviews, T2 — round 1, T2 — round 3 (+5 more)

### Community 115 - "load_retrieval_config"
Cohesion: 0.25
Nodes (12): test_roles_match_policy_file(), load_retrieval_config(), test_committed_config_loads(), test_good_config_loads(), test_invalid_config_is_refused_naming_the_field(), test_schema_11_reads_default_lexical_tokenizer(), test_schema_12_loads_explicit_lexical(), test_timeout_bounds_are_inclusive() (+4 more)

### Community 116 - "fusion"
Cohesion: 0.20
Nodes (12): English, Malayalam and mixed queries, FAQ-aware retrieval/indexing, Roadmap 7 - Chunking experiments, Roadmap 8 - Multilingual retrieval, Language applicability handling, Parent-heading context and order-independent section_ids, Recursive chunking baseline, Optional semantic chunking (+4 more)

### Community 117 - "SQLite FTS5"
Cohesion: 0.12
Nodes (19): Local multilingual BGE reranker, BM25 via FTS5 bm25(), Derived local lexical file per collection, Device not pinned, recorded in results (D038), Embeddings, Deterministic fake embedder, Fusion, Lexical store (+11 more)

### Community 118 - "QdrantIndexStore"
Cohesion: 0.21
Nodes (8): QdrantIndexStore, CountingStore, test_replace_and_delete_flows(), make_points(), test_delete_documents(), test_read_state_paginates(), test_read_state_round_trip(), test_replace_shrinking_leaves_no_orphan()

### Community 119 - "slices.py"
Cohesion: 0.12
Nodes (14): absent_query_languages(), active_registry_languages(), aggregate(), _mean(), slice_by(), source_authority_key(), row(), test_absent_languages_from_a_temp_registry() (+6 more)

### Community 120 - "failing_client"
Cohesion: 0.18
Nodes (10): content-hash-v1 (sole change-detection signal), LocalDocumentRepository, Document manifest and JSON Schema validation, make validate-knowledge, persona_scope spec defect (F2), BgeM3Embedder (optional extra, pinned revision), Embedder Protocol and FakeEmbedder, HeadingChunker and slugify rule (+2 more)

### Community 121 - "test_status_handling.py"
Cohesion: 0.20
Nodes (8): Adding a New Language Guide, language_registry.json, Public Assistant Content Boundaries, access_scope, content_language, Knowledge Schema and Metadata, language_scope, lote_languages

### Community 122 - "dense_equivalence.py"
Cohesion: 0.28
Nodes (4): deterministic_clock(), equivalence_suite(), chunks_per_document_dense(), unanswerable()

### Community 123 - "test_open_retrieval_bm25_builds_no_embedder_and_no_client"
Cohesion: 0.27
Nodes (4): block_model_stack(), Raises, test_open_retrieval_bm25_builds_no_embedder_and_no_client(), test_retrieve_cli_bm25_needs_neither_qdrant_nor_the_model()

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

### Community 132 - "007 — Hybrid Retrieval Tasks"
Cohesion: 0.11
Nodes (18): Implementation, Review, T2 — round 1, User decision, 007 — Hybrid Retrieval Tasks, Out of this spec, T1 — Evaluation Suite `public-eval-v2`, T2 — v2 dense baseline (user-owned gate) (+10 more)

### Community 133 - "Vocabulary, flashcards and free access"
Cohesion: 0.29
Nodes (7): EligibilityPolicy / GUEST_PUBLIC_POLICY, Security fixtures (valid but ineligible), config/ingestion.yaml and RuntimeSettings, Ingestion pipeline (target vs current state diff), AccessContext and Role (core), resolve_access / ResolvedAccess, W2A_TENANT_ID server tenant setting

### Community 134 - ".search"
Cohesion: 0.25
Nodes (8): Phase 2 basic analytics, Assistant behavior rules, Product Context, English and Malayalam language scope, Future personas, Phase 1 guest-only scope, Way2Australia AI product, Source-of-truth priorities

### Community 135 - "Eligible failures: Qdrant connect/network, Qdrant timeout, model load/download failure with network __cause__"
Cohesion: 0.32
Nodes (8): classify_model_error, classify_qdrant_error, D057 Fallback eligibility classification, D062 5xx not eligible, Eligible failures: Qdrant connect/network, Qdrant timeout, model load/download failure with network __cause__, FallbackReason (qdrant_unavailable, qdrant_timeout, model_unavailable), RetrievalUnavailableError(reason), Non-fallback failures exit 2 (missing extra, model failure w/o network cause, HTTP error status, missing collection, mismatch, stale lexical file, authorization error)

### Community 136 - "Spec 002 document model and repository"
Cohesion: 0.16
Nodes (15): Pydantic document models and enums, EligibilityPolicy for guest/public, LocalDocumentRepository with manifest schema validation, make validate-knowledge, Spec 002 decisions made before approval (content_hash, fixtures, validate-knowledge), Seed data status: 13 public docs, evaluation datasets, security fixtures, Spec 002 retrospective findings F1-F6, Spec 002 document model and repository (+7 more)

### Community 137 - "SecurityIndex"
Cohesion: 0.16
Nodes (13): Security gate five paths, result 1.2, _UnavailableDense (harness-only fault injection), Implementation, Review, T6 security bm25 seed-subset check instead of verify_fresh, T6 — round 1, T6 — Security gate over the fallback paths, Verification (+5 more)

### Community 138 - "Evaluation Framework Goal"
Cohesion: 0.39
Nodes (8): NAATI CCL test format, scoring and results, NAATI CCL test, Deduction-based assessment, Begin interpreting within five seconds of chime, NAATI, CCL is not professional interpreter certification, Pass requirement 63/90 overall and 29/45 per dialogue, Results within 4-6 weeks

### Community 139 - "test_lexical_tokenizer.py"
Cohesion: 0.09
Nodes (6): test_chillu_pairs_tokenize_the_same_inside_and_at_end(), test_golden_file_is_the_source_of_the_pins(), test_golden_queries_pin_exact_tokens(), test_module_has_no_language_code_literal(), test_nfd_equals_nfc(), test_v2_matches_v1_without_listed_sequences()

### Community 140 - "Phase 1 - Production-oriented RAG"
Cohesion: 0.10
Nodes (22): Answerability and insufficient-evidence response, Authorization regression and staff canary, Docker, Terraform, EC2, ECR, CloudWatch, IAM, Bedrock, Bedrock Runtime (roadmap), BGE-M3 (roadmap), Citation manipulation tests and input/cost limits, Backend-owned citation validation, FastAPI skeleton (+14 more)

### Community 141 - "BGE-M3 (initial embedding model)"
Cohesion: 0.38
Nodes (6): Evaluation Candidates File, Evaluation Package (evaluation/), Evaluation Suite and Case-type Schemas, validate-evaluation, T2 Schemas and validate-evaluation, T7 Candidates

### Community 142 - "Way2Australia AI Platform Master Implementation Plan"
Cohesion: 0.29
Nodes (7): eval-retrieval, Retrieval Result Document 2.0, Section-level Metrics, Slices and small_sample, Unanswerable Reporting, T3 Retrieval Runner, T4 Unanswerable Reporting

### Community 143 - "Retrieval fallback (Spec 008, D056-D062)"
Cohesion: 0.08
Nodes (28): Answerability / insufficient-evidence decision, Amazon Bedrock generation, bm25 builds no embedder and no Qdrant client, Citation validation, Context builder (planned), D056-D062 fallback decisions, D058 Fallback policy per query, D061 Marking and evaluation of fallback (+20 more)

### Community 144 - "eval-compare"
Cohesion: 0.29
Nodes (7): AGENTS.md, Claude adapter, Initial specs, Phase 0 - Project bootstrap, Project context files, SDD workflow (Spec 003 task-gated agent workflow), Stable command interface

### Community 145 - "Payments, account access and support boundaries"
Cohesion: 0.29
Nodes (6): Vocabulary, flashcards and free access, Spaced-repetition flashcards, Free access allowance, 12 subject domains plus General vocabulary, Approved public learning samples, Sample neighbour-greeting dialogue

### Community 146 - "make retrieve"
Cohesion: 0.06
Nodes (33): results.py, compare.py (reads 1.0, 2.0, 2.1; quality gate; identity refusals), make retrieve, --allow-fake (plumbing only, never a recorded baseline), make retrieval-baseline (legacy, frozen Spec 005 producer), BASELINE_ARGS (--embedder, --allow-fake, --top-k, --suite, --release, --output, --config), Baseline metrics HitRate@5, random expectation min(1,5/N), Recall@5, MRR, p50/p95 latency, experiments/results/retrieval-baseline-<index_version>-<UTC>.json, never overwritten, D053 result 2.1 (+25 more)

### Community 147 - "make test"
Cohesion: 0.33
Nodes (6): 006 Evaluation Framework Design, Decision Brief Q1-Q10, 006 Evaluation Framework Requirements, Evaluation Framework Goal, 006 Spec Retrospective Review, Retrospective Round 1 PASS

### Community 148 - "Mission"
Cohesion: 0.33
Nodes (5): Evaluation case_id and case_version, Versioning and Releases, document_id and document_version, Phase 2 Knowledge Release Candidates, Release seed-v1

### Community 149 - "test_bm25.py"
Cohesion: 0.15
Nodes (25): LexicalRow, build(), dense_fixture(), DroppedClauseIndex, guest(), pub(), retriever(), _shape() (+17 more)

### Community 150 - "IndexSettings"
Cohesion: 0.17
Nodes (5): IndexSettings, read_index_settings(), _DenseLike, test_index_settings_1_0_upgrades_in_memory(), test_collection_with_1_0_settings_still_binds()

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

### Community 155 - "typing"
Cohesion: 0.07
Nodes (5): RuntimeSettings, default_lexical_dir(), encode_lote_column(), open_bound_lexical(), settings()

### Community 156 - "conftest.py"
Cohesion: 0.24
Nodes (8): Review, script_mix(), live_suite_rows(), test_every_v3_query_letter_matches_script_fixture(), test_g062_is_latin_only(), test_non_letters_add_no_script(), test_representative_v3_queries(), test_virama_and_vowel_sign_add_no_script()

### Community 157 - "007 — Hybrid Retrieval Design"
Cohesion: 0.14
Nodes (13): 007 — Hybrid Retrieval Design, Components / boundaries, Data flow, Error and failure behavior, Interfaces / models, Observability, R10 — `eval-compare` identity rules (`compare.py`), R12 — Docker test (+5 more)

### Community 158 - "Orchestrator State Machine"
Cohesion: 0.50
Nodes (4): Mission, Phase 1 public/guest vs Phase 2 Knowledge Operations, Mission purpose: grounded multilingual RAG assistant, Useful product, engineering learning, portfolio evidence

### Community 159 - "way2australia_api/__init__.py"
Cohesion: 0.50
Nodes (3): Coaching is optional, Way2Australia public offering and assistant scope, English-Malayalam CCL preparation offering

### Community 160 - "Project Context README"
Cohesion: 0.50
Nodes (4): 120+ practice dialogues, Materials and dialogue practice, Recordings stay in browser, No automatic score in ordinary practice

### Community 161 - "DroppedClauseLexical"
Cohesion: 0.18
Nodes (3): DroppedClauseLexical, DroppedLoteClauseLexical, __init__()

### Community 167 - "api/__init__.py"
Cohesion: 0.67
Nodes (3): Frontend stack, Next.js, TypeScript

### Community 168 - "LexicalIndex"
Cohesion: 0.14
Nodes (16): collect(), load_ingestion_config(), LexicalIndex, _read_only_connection(), _structure_config(), test_chunker_identity_matches_for_structure(), test_clis_load_recursive_config(), test_lexical_1_0_fixture_refused() (+8 more)

### Community 169 - "DocumentRepository Protocol (async)"
Cohesion: 0.33
Nodes (6): DocumentRepository Protocol (async), KnowledgeDocument model, Spec 002 retrospective round 1, Spec 002 task review log (T3-T9), Spec 002 Document model and repository (verified), Acceptance dry run on Spec 002 T3

### Community 170 - "tests/evaluation/__init__.py"
Cohesion: 0.67
Nodes (3): Canonical document metadata, Chunk metadata, Source authority precedence

### Community 191 - "continuity.py"
Cohesion: 0.14
Nodes (20): _case_keys(), compare_continuity(), _embedder_pair_from_doc(), _fmt_key(), _identity_refusals(), _info_lines(), _load_raw(), _lote_label() (+12 more)

### Community 192 - "sync_agent_skills.py"
Cohesion: 0.31
Nodes (9): discover_skills(), expected_tree(), find_problems(), inject_frontmatter(), main(), managed_skills(), read_tree(), remove() (+1 more)

### Community 193 - "DocumentRepository"
Cohesion: 0.29
Nodes (7): Roadmap 2 - Document model + repository, KnowledgeDocument, Manifest/schema validation, S3DocumentRepository and external storage, Document manifest, DocumentRepository, LocalDocumentRepository

### Community 194 - "Authorization enforced before generation"
Cohesion: 0.29
Nodes (6): Authorization model (guest/public), Graceful degradation, Poisoned public document fixture, Security plan (threats and controls), SQLite FTS5 fallback, Staff-only canary fixture

### Community 195 - "open_retrieval / OpenedRetrieval"
Cohesion: 0.18
Nodes (11): open_retrieval / OpenedRetrieval, Open-time fallback lasts for the run, Qdrant connect/query timeouts (config 1.1), retrieval_client_factory, R5 — `bm25` without Qdrant or the `bge-m3` extra, Review F1: open-time outage serves whole run, Review F4: duplicated standalone open wiring, Review F5: bind_to scroll fallback untested end to end (+3 more)

### Community 196 - "R8 — Evaluation results for degraded runs"
Cohesion: 0.40
Nodes (6): Acceptance criteria, Acceptance criteria, R8 — Evaluation results for degraded runs, R9 — `eval-compare` by served strategy, index_settings=None refusal rule (T3 F2), T5 Result 2.2 and eval-compare by served strategy

### Community 199 - "Spec 010 — task reviews"
Cohesion: 0.18
Nodes (10): Implementation, Implementation, Implementation, Review, Spec 010 — task reviews, T3 — round 1, T3 — round 2, T6 — round 1 (+2 more)

### Community 201 - "test_store_integration.py"
Cohesion: 0.36
Nodes (7): _keyword_indexed(), live_client(), store(), test_collection_has_keyword_indexes_and_cosine_dense_vector(), test_empty_without_settings_recreates_dropped_indexes(), test_repeated_create_payload_index_is_harmless(), test_settings_storage_and_refusal()

### Community 202 - "Evaluation tooling"
Cohesion: 0.36
Nodes (8): Custom retrieval metrics (plain Python), DeepEval (not yet a dependency), Evaluation tooling, Generation/e2e metrics (correctness, faithfulness, citations, refusal), GitHub Actions, LLM-as-judge not sole source of truth, Primary retrieval metrics (Recall@5, MRR, HitRate@5), pytest

### Community 203 - "Review"
Cohesion: 0.29
Nodes (5): Implementation, Review, T3 — round 2, _group_installed(), test_default_embedder_identity_equals_the_bge_m3_adapter_identity()

### Community 204 - "Evaluation result format 2.2"
Cohesion: 0.33
Nodes (6): eval-compare by served strategy (mixed refused), Latency grouped by served path, Evaluation result format 2.2, RetrievalResult marking (requested_strategy, fallback_reason), Review F2: result 2.2 does not record fallback stage, T4 deviations (header only on fallback, requested_strategy by wrapper)

### Community 205 - "R12 — Real runs (user-owned gate)"
Cohesion: 0.33
Nodes (6): Acceptance criteria, R12 — Real runs (user-owned gate), Spec 007 BM25 and hybrid reference results, T7 real runs: fallback-only and Qdrant-up results, T7 — Real runs (user-owned gate), Verification

### Community 206 - "Way2Australia AI Platform Master Implementation Plan"
Cohesion: 0.33
Nodes (6): Way2Australia AI Platform Master Implementation Plan, Phase 1 Definition of Done, Phase 1 Scope (public/guest RAG), Recruiter / portfolio story, Project Mission, Seven-day Phase 1 execution plan

### Community 207 - "Review"
Cohesion: 0.50
Nodes (4): Implementation, Review, T9 — round 1, User decision

### Community 208 - "Spec 008 Retrieval Fallback Requirements"
Cohesion: 0.50
Nodes (4): Change log, Spec 008 Retrieval Fallback Requirements, Spec 008 Retrospective Review round 1, Review F3: missing change-log lines (resolved)

## Ambiguous Edges - Review These
- `Task-gated agent workflow loop` → `graphify skill pointer`  [AMBIGUOUS]
  .claude/CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **380 isolated node(s):** `way2australia-api`, `way2australia-core`, `way2australia-observability`, `way2australia-rag`, `way2australia` (+375 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1408 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **40 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Retrieval (dense baseline Spec 005, hybrid Spec 007, fallback Spec 008)` connect `008 — Retrieval Fallback Requirements` to `make ingest`, `Eligible failures: Qdrant connect/network, Qdrant timeout, model load/download failure with network __cause__`, `Target repository shape (apps, packages, knowledge, sources, evaluation, tests, config, experiments, analytics, prompts, docs, infra)`, `Retrieval fallback (Spec 008, D056-D062)`, `Ingestion (Phase 1 baseline, Spec 004)`, `typing`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **Are the 85 inferred relationships involving `DenseIndex` (e.g. with `Design summary` and `Decisions resolved before drafting`) actually correct?**
  _`DenseIndex` has 85 INFERRED edges - model-reasoned connections that need verification._
- **What connects `way2australia-api`, `way2australia-core`, `way2australia-observability` to the rest of the system?**
  _380 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_compare.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13533834586466165 - nodes in this community are weakly interconnected._
- **Why does `D055 Default strategy is hybrid (Spec 007)` connect `D055 Default strategy is hybrid (Spec 007)` to `Development Workflow`, `typing`, `Ingestion pipeline (Spec 004)`, `Spec 007 hybrid retrieval`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Are the 36 inferred relationships involving `LocalDocumentRepository` (e.g. with `Dependencies` and `Design summary`) actually correct?**
  _`LocalDocumentRepository` has 36 INFERRED edges - model-reasoned connections that need verification._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Task-gated agent workflow loop` and `graphify skill pointer`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._