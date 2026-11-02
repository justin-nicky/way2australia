# Graph Report - way2australia  (2026-11-02)

## Corpus Check
- 276 files · ~302,726 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 32 file(s) not represented in the graph (top: (none) 20, .jsonl 9, .mdc 1)

## Summary
- 4168 nodes · 12313 edges · 195 communities (154 shown, 41 thin omitted)
- Extraction: 80% EXTRACTED · 20% INFERRED · 0% AMBIGUOUS · INFERRED: 2464 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e67185fc`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- DenseRetriever
- opening.py
- open_retrieval
- test_bm25.py
- test_validate.py
- test_service.py
- IngestionError
- test_index.py
- run_security_evaluation
- evaluation/validate.py
- evaluation/cli.py
- verify_fresh
- HeadingChunker
- sync_agent_skills.py
- test_lexical_cli.py
- test_strategy_eval.py
- Strategy Eval Tests
- dense
- Index Binding Errors
- Document Model Tests
- 007 — Hybrid Retrieval Requirements
- test_validate_knowledge.py
- Date and Policy Tests
- BGE-M3 Adapter
- test_lexical_standalone.py
- Spec 004 ingestion baseline
- tokenization.py
- ingest_dense
- Strategy
- Evaluation CLI Tests
- Review
- test_suite_v2.py
- test_baseline.py
- test_lexical_build.py
- test_content_hash.py
- SpyIndex
- 009 — Chunking Experiments Requirements
- 008 — Retrieval Fallback Requirements
- baseline.py
- Evaluation Slices
- open_retrieval
- typing
- test_legacy_baseline_snapshot.py
- QdrantTimeouts
- LocalDocumentRepository
- test_lexical_standalone.py
- production_entries
- test_authorization_isolation.py
- make eval-retrieval
- 007 — Hybrid Retrieval Requirements
- repositories/__init__.py
- HeadingChunker
- test_text.py
- FallbackRetriever
- HybridRetriever (dense leg then BM25 leg, no single-leg fallback)
- asyncio
- Development Workflow
- pathlib
- EvaluationSchemas
- json
- make eval-security
- SecurityIndex
- Target RAG query flow (User -> FastAPI -> validation -> AccessContext -> LanguageContext -> retrieval -> RRF -> reranker -> context builder -> answerability -> prompt -> Bedrock -> citation validation)
- way2australia_core/__init__.py
- baseline.py
- RetrievalUnavailableError
- make ingest
- Spec 007 hybrid retrieval
- IndexIdentity
- FakeEmbedder
- ARCHITECTURE.md
- AWS target
- EvaluationConfigurationError
- retrieval/test_access.py
- Constitution
- Section: Next step
- Spec 007 - hybrid retrieval (verified 2026-10-28, merged 3cf70eb; 10 tasks)
- Components / boundaries
- test_repository_contract.py
- Spec 005 dense retrieval baseline
- IngestionConfigurationError
- list_eligible_documents
- Ingestion pipeline (Spec 004)
- Retrieval fallback (Spec 008, D056-D062)
- Result format 2.1 and security result 1.1
- SecurityIndex
- test_fallback.py
- Backend stack
- R2 — v2 dense baseline (user-owned gate)
- D023 Task-gated agent workflow
- Phase 1 - Production-oriented RAG
- test_schemas.py
- Fallback (hybrid only)
- pathlib
- AGENTS.md Project Rules
- IngestionService
- SpyIndex
- HybridRetriever
- CURRENT_STATE.md
- QdrantIndexStore
- repositories/__init__.py
- 006 Evaluation Framework Tasks
- test_recursive.py
- Retrieval package (Spec 005 and 007)
- D035 One filter builder, fail-closed re-check, same path for later fallbacks (Spec 005)
- Qdrant (vector database)
- make validate-evaluation
- test_structure.py
- make eval-retrieval
- Intentionally avoided choices
- test_content_hash.py
- test_hybrid.py
- test_violation_names_the_document_from_the_error_attribute
- pytest
- test_bm25.py
- fusion
- evaluation/cli.py
- EmbedderInfo
- evaluation/errors.py
- failing_client
- test_status_handling.py
- make eval-compare
- R5 — Lexical index binding
- QdrantIndexStore
- Baseline runner and result JSON
- test_failed_write_removes_partial_file
- Development Workflow
- test_status_handling.py
- absent_query_languages
- BGE-M3 embeddings
- RuntimeSettings
- lexical/ package (Spec 007)
- Vocabulary, flashcards and free access
- .search
- Acceptance criteria
- Spec 002 document model and repository
- Acceptance criteria
- Evaluation Framework Goal
- security_index.py
- LocalRepositoryConfig
- BGE-M3 (initial embedding model)
- Way2Australia AI Platform Master Implementation Plan
- Evaluation tooling
- eval-compare
- Payments, account access and support boundaries
- DroppedClauseLexical
- make test
- Mission
- test_open_retrieval_bm25_builds_no_embedder_and_no_client
- Acceptance criteria
- Spec 004 retrospective round 1 (PASS)
- policy
- policy
- policy
- test_status_handling.py
- Acceptance criteria
- Acceptance criteria
- Orchestrator State Machine
- way2australia_api/__init__.py
- Project Context README
- R14 — Unchanged behavior, protected paths and spec-wide verification
- way2australia_rag/__init__.py
- Scripted
- way2australia-core
- Phase 1 analytics event contract
- Spec-driven development workflow
- api/__init__.py
- DocumentRepository Protocol (async)
- R15 — Documentation and decisions
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
- metrics.py, goldens.py, baseline.py, baseline_cli.py
- .search
- R3 — Tokenizer `lexical-v1`

## God Nodes (most connected - your core abstractions)
1. `DenseIndex` - 105 edges
2. `LocalDocumentRepository` - 94 edges
3. `Strategy` - 73 edges
4. `HeadingChunker` - 65 edges
5. `FakeEmbedder` - 63 edges
6. `DECISIONS.md architecture decision log` - 62 edges
7. `run_retrieval_evaluation()` - 61 edges
8. `ResolvedAccess` - 61 edges
9. `open_retrieval()` - 61 edges
10. `DenseRetriever` - 60 edges

## Surprising Connections (you probably didn't know these)
- `R10 — `eval-compare` identity rules (`compare.py`)` --references--> `_refusals()`  [INFERRED]
  .kiro/specs/007-hybrid-retrieval/design.md → packages/rag/src/way2australia_rag/evaluation/compare.py
- `Interfaces / models` --references--> `Chunk`  [INFERRED]
  .kiro/specs/009-chunking-experiments/design.md → packages/rag/src/way2australia_rag/ingestion/chunking.py
- `Acceptance criteria` --references--> `slugify()`  [INFERRED]
  .kiro/specs/009-chunking-experiments/requirements.md → packages/rag/src/way2australia_rag/ingestion/chunking.py
- ``structure` v1 (R3)` --references--> `IngestionConfigurationError`  [INFERRED]
  .kiro/specs/009-chunking-experiments/design.md → packages/rag/src/way2australia_rag/ingestion/errors.py
- `Acceptance criteria` --references--> `ChunkTokenizer`  [INFERRED]
  .kiro/specs/009-chunking-experiments/requirements.md → packages/rag/src/way2australia_rag/ingestion/tokenization.py

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

## Communities (195 total, 41 thin omitted)

### Community 0 - "DenseRetriever"
Cohesion: 0.06
Nodes (85): Implementation, Review, T7 — round 1, User decision, _changed(), compare(), Comparison, _delta_line() (+77 more)

### Community 1 - "opening.py"
Cohesion: 0.07
Nodes (42): 007 — Hybrid Retrieval Design, Alternatives / deferred decisions, As-built notes, Data flow, Design summary, Error and failure behavior, Interfaces / models, Observability (+34 more)

### Community 2 - "open_retrieval"
Cohesion: 0.07
Nodes (30): Components / boundaries, Interfaces / models, R3 — Standalone lexical open (`identity.py`, `lexical/store.py`), R5 — `bm25` without Qdrant or the extra (`bm25.py`), R6 — `FallbackRetriever` (`fallback.py`) and `open_retrieval` (`opening.py`), R7 — Marking (`models.py`, `retrieval/cli.py`), R8 — Result format 2.2 (`retrieval_eval.py`), R9 — `eval-compare` (`results.py`, `compare.py`) (+22 more)

### Community 3 - "test_bm25.py"
Cohesion: 0.17
Nodes (24): LexicalRow, DenseIndex, build(), dense_fixture(), DroppedClauseIndex, guest(), pub(), retriever() (+16 more)

### Community 4 - "test_validate.py"
Cohesion: 0.14
Nodes (31): edit_rows(), edit_suite(), root(), run(), test_active_golden_without_relevant_documents(), test_candidate_ineligible_document_is_not_unknown(), test_candidate_not_suggested(), test_candidate_referenced_by_suite() (+23 more)

### Community 5 - "test_service.py"
Cohesion: 0.18
Nodes (24): BoomChunker, doc(), Harness, test_bumped_document_version_updates(), test_changed_body_updates(), test_changed_metadata_field_updates(), test_chunk_shrink_leaves_no_orphan(), test_chunk_too_long_report_has_no_chunk_text() (+16 more)

### Community 6 - "IngestionError"
Cohesion: 0.11
Nodes (15): Implementation, Review, T1 — round 1, IndexSettingsMismatchError, IngestionError, check_chunks(), ChunkTooLongError, _effective_limit() (+7 more)

### Community 7 - "test_index.py"
Cohesion: 0.11
Nodes (42): IndexBindingError, bound_index(), client(), failing_client(), fake_info(), http_client(), make_settings(), open_index() (+34 more)

### Community 8 - "run_security_evaluation"
Cohesion: 0.14
Nodes (16): Review, T8 — round 1, User decision, EvaluationHarnessError, _gate(), _lexical_sanity_check(), _open_lexical_sanity(), _path_strategy() (+8 more)

### Community 9 - "evaluation/validate.py"
Cohesion: 0.14
Nodes (19): Implementation, Review, T1 — round 1, User decision, _candidate_rules(), problem(), _describe(), _document_problems() (+11 more)

### Community 10 - "evaluation/cli.py"
Cohesion: 0.05
Nodes (33): Dependencies, _compare(), default_security_output_path(), format_security_summary(), format_summary(), main(), _retrieval(), _security() (+25 more)

### Community 11 - "verify_fresh"
Cohesion: 0.12
Nodes (16): T2: where the shared pieces live (2026-10-31), Repeated finding: graphify update ownership, Spec 008 Task Reviews, Implementation, Implementation, Implementer Sonnet 5.5 / reviewer Opus 5.5 pattern, Review, T2 — round 1 (+8 more)

### Community 12 - "HeadingChunker"
Cohesion: 0.08
Nodes (41): write_document(), deterministic_clock(), equivalence_suite(), basic_suite(), build(), fusion_config(), golden(), run() (+33 more)

### Community 13 - "sync_agent_skills.py"
Cohesion: 0.31
Nodes (9): discover_skills(), expected_tree(), find_problems(), inject_frontmatter(), main(), managed_skills(), read_tree(), remove() (+1 more)

### Community 14 - "test_lexical_cli.py"
Cohesion: 0.09
Nodes (39): Implementation, Implementation, Review, Review, T3 — round 2, T3 — round 3, User decision, _group_installed() (+31 more)

### Community 15 - "test_strategy_eval.py"
Cohesion: 0.05
Nodes (62): User decision, clean_env(), index_factory(), real_factory(), run(), test_bad_top_k_exits_2(), test_existing_output_exits_2_before_qdrant(), test_fake_embedder_exits_2_before_qdrant() (+54 more)

### Community 16 - "Strategy Eval Tests"
Cohesion: 0.08
Nodes (45): RetrievalUnavailableError and availability classification, standalone bm25 without Qdrant or extra (IndexIdentity, freshness), CURRENT_STATE.md current state document, Current goal: Specs 001-008 complete; Spec 008 verified and merged into main (1107b67), plan next spec, Evaluation Suite includes goldens, refusal, multilingual, security, regression, Phase 2 Knowledge Release workflow designed not implemented, Public/guest retrieval only in Phase 1; English + Malayalam, Known issue: Qdrant and Hugging Face 5xx not fallback-eligible (+37 more)

### Community 17 - "dense"
Cohesion: 0.04
Nodes (65): R11 — Security gate (`security_index.py`, `security_eval.py`), T9 — Strategy comparison and default-strategy decision (user-owned gate), Verification, Decisions D056-D062, Spec 008 Retrieval Fallback Design, Security gate five paths, result 1.2, _UnavailableDense (harness-only fault injection), 008 — Retrieval Fallback Requirements (+57 more)

### Community 18 - "Index Binding Errors"
Cohesion: 0.07
Nodes (40): compare(), IndexSettings, mismatch_message(), IndexedDocument, QdrantIndexStore, _DenseLike, base_settings(), test_build_index_settings_records_embedder_and_chunker() (+32 more)

### Community 19 - "Document Model Tests"
Cohesion: 0.15
Nodes (23): IndexPoint, DenseRetriever, test_forbidden_points_are_never_returned(), build_client(), docs(), guest(), open_spy(), RaisingEmbedder (+15 more)

### Community 20 - "007 — Hybrid Retrieval Requirements"
Cohesion: 0.17
Nodes (11): 007 — Hybrid Retrieval Requirements, Acceptance criteria, Acceptance criteria, Decisions resolved before drafting, Definition of Done, Goal, Out of scope, R1 — Evaluation Suite `public-eval-v2` (+3 more)

### Community 21 - "test_validate_knowledge.py"
Cohesion: 0.22
Nodes (26): load(), test_bad_date_fails_loading_naming_document_and_field(), test_seed_corpus_still_loads(), test_valid_date_loads(), build_repo(), metadata(), problems_for(), run_cli() (+18 more)

### Community 22 - "Date and Policy Tests"
Cohesion: 0.08
Nodes (29): R1 — Failure classification (`errors.py`, `availability.py`), T1: Hugging Face error shapes (confirmed 2026-10-29), Testing / evaluation strategy, Review, classify_model_error(), classify_qdrant_error(), _optional_types(), caused_by() (+21 more)

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
Cohesion: 0.08
Nodes (19): Tokenizer (R1), Implementation, Review, T1 — round 2, User decision, EmbedderConfig, BgeM3Tokenizer, build_tokenizer() (+11 more)

### Community 27 - "ingest_dense"
Cohesion: 0.18
Nodes (12): build_production(), ingest_dense(), open_lexical(), repository(), rewrite_settings(), test_bind_does_not_write_to_qdrant(), test_bind_refuses_chunk_set_mismatch_with_counts(), test_bind_refuses_identity_and_chunker_mismatch() (+4 more)

### Community 28 - "Strategy"
Cohesion: 0.12
Nodes (31): R8 — Strategy and config (`retrieval/strategy.py`, `config/retrieval.yaml`), Implementation, Review, 008 — Retrieval Fallback Tasks, T8 — Documentation, decisions and final verification, Verification, _check_standalone_open(), _retrievers() (+23 more)

### Community 29 - "Evaluation CLI Tests"
Cohesion: 0.12
Nodes (31): assert_invalid(), document_fields(), make_document(), test_blank_required_text_is_rejected(), test_document_is_immutable(), test_duplicate_lote_languages_are_rejected(), test_effective_window_must_be_ordered(), test_empty_lote_languages_is_rejected() (+23 more)

### Community 30 - "Review"
Cohesion: 0.13
Nodes (20): Implementation, Implementation, Implementation, Review, Review, T2 — round 1, T5 — round 1, T6 — round 1 (+12 more)

### Community 31 - "test_suite_v2.py"
Cohesion: 0.14
Nodes (24): committed(), edit_jsonl(), lines(), manifest(), problems(), read_lines(), root(), test_candidates_differ_only_in_promoted_as() (+16 more)

### Community 32 - "test_baseline.py"
Cohesion: 0.09
Nodes (26): BaselineResult, write_result(), case(), clean_env(), cli_run(), DeviceStub, _git(), run() (+18 more)

### Community 33 - "test_lexical_build.py"
Cohesion: 0.20
Nodes (18): identity(), payload(), synthetic_entries(), build(), test_atomic_replace_keeps_old_file_after_failure(), test_build_production_helper_runs(), test_build_records_settings(), test_digest_is_stable_and_order_independent() (+10 more)

### Community 34 - "test_content_hash.py"
Cohesion: 0.14
Nodes (19): canonical_json(), _canonical_value(), _canonical_value_mapping(), compute_content_hash(), _copy_seed(), h(), _load(), test_absent_optional_fields_hash_as_null() (+11 more)

### Community 35 - "SpyIndex"
Cohesion: 0.20
Nodes (3): OddIdStore, SpyIndex, broken()

### Community 36 - "009 — Chunking Experiments Requirements"
Cohesion: 0.07
Nodes (28): 009 — Chunking Experiments Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+20 more)

### Community 37 - "008 — Retrieval Fallback Requirements"
Cohesion: 0.11
Nodes (32): Binding: embedder model ID, revision, vector size, normalization, fake flag and index_version must equal recorded IndexSettings, BM25Retriever(identity, lexical), BM25 statistics (IDF, avg length) computed over every row of a lexical file, build_retriever (only place a strategy name becomes a retriever), retrieval_client_factory (Qdrant client with configured timeouts), config/retrieval.yaml (default_strategy hybrid, RRF k 60, depth 50), D033-D041 retrieval decisions, D049-D055 (+24 more)

### Community 38 - "baseline.py"
Cohesion: 0.10
Nodes (20): Implementation, Review, T9 — round 1, User decision, 007 — Hybrid Retrieval Tasks, Notes for the retrospective, Out of this spec, T10 — Documentation, decisions and hand-off (+12 more)

### Community 39 - "Evaluation Slices"
Cohesion: 0.08
Nodes (28): AccessContext, test_blank_tenant_refused(), test_empty_tenant_refused(), test_no_language_or_scope_fields(), test_roles_match_policy_file(), test_tenant_is_stripped(), test_unknown_role_refused(), test_valid_context_is_frozen() (+20 more)

### Community 40 - "open_retrieval"
Cohesion: 0.12
Nodes (13): get_health(), HealthResponse, get_request_settings(), get_settings(), Settings, create_app(), isolate_settings_environment(), test_create_app_wires_settings() (+5 more)

### Community 41 - "typing"
Cohesion: 0.09
Nodes (32): 006-candidates.jsonl with 7 suggested rows, make eval-compare, make eval-security hard gate, result 2.2 and served-strategy eval-compare, eval-security five paths, governed suite loader and schemas, make validate-evaluation, Spec 006 retrospective findings (F1 byte-identity, eval-security not in verify) (+24 more)

### Community 42 - "test_legacy_baseline_snapshot.py"
Cohesion: 0.06
Nodes (27): BgeM3Embedder, group_installed(), test_constructing_does_not_load_the_model(), test_device_none_before_load_and_recorded_after(), test_missing_group_at_load_raises_optional_dependency_error(), test_missing_group_refused_at_construction(), test_model_loaded_once_with_revision_and_batches(), fake_loader() (+19 more)

### Community 43 - "QdrantTimeouts"
Cohesion: 0.18
Nodes (4): QdrantTimeouts, settings(), test_factory_sets_the_connect_timeout_and_disables_the_version_check(), live_client()

### Community 44 - "LocalDocumentRepository"
Cohesion: 0.14
Nodes (31): LocalDocumentRepository, build(), guest_access(), new_base(), real_queries(), seed_repository(), spied(), test_a_dropped_lexical_clause_names_the_four_lexical_paths() (+23 more)

### Community 45 - "test_lexical_standalone.py"
Cohesion: 0.18
Nodes (19): LexicalIndexBindingError, build_from(), built(), copy_repository(), expected(), first_document_id(), open_it(), remove_document() (+11 more)

### Community 46 - "production_entries"
Cohesion: 0.06
Nodes (38): R4 — `make index-lexical` (`lexical/cli.py`), R4/R5 — Lexical store (`lexical/store.py`, `lexical/build.py`), Implementation, Review, T3 — round 1, User decision, T3 — `lexical-v1` tokenizer, lexical store and `make index-lexical`, Verification (+30 more)

### Community 47 - "test_authorization_isolation.py"
Cohesion: 0.22
Nodes (3): client_with_forbidden(), FilterDroppingIndex, test_store_dropping_the_filter_fails_closed()

### Community 48 - "make eval-retrieval"
Cohesion: 0.12
Nodes (23): BgeM3Embedder (optional bge-m3 extra, dense only), D025-D030, D032 ingestion decisions, DocumentRepository Protocol (get_document, list_documents), Embedder Protocol, FakeEmbedder (deterministic), GUEST_PUBLIC_POLICY, HeadingChunker (heading v1, character cap, stable section_id slugs), IndexSettings and mismatch comparison (+15 more)

### Community 49 - "007 — Hybrid Retrieval Requirements"
Cohesion: 0.09
Nodes (27): optional bge-m3 extra (sentence-transformers, PyTorch), D048 graphify tooling, make experiment CONFIG=... (target; records git commit, release, suite, chunker, embedder, strategy, metrics, latency), make format, Knowledge graph graphify (D048), /graphify . --update (user, once per spec after merge), graphify query / path / explain, graphify update . (+19 more)

### Community 50 - "repositories/__init__.py"
Cohesion: 0.08
Nodes (10): AccessScope, ApprovalStatus, LanguageScope, LifecycleStatus, SourceAuthority, _check_language_code(), KnowledgeDocument, ListRepository (+2 more)

### Community 51 - "HeadingChunker"
Cohesion: 0.11
Nodes (26): HeadingChunker, _is_word_char(), slugify(), ids(), test_deterministic(), test_duplicate_headings_get_unique_ids_in_order(), test_duplicate_suffix_does_not_collide_with_literal_heading(), test_headings_inside_code_fences_ignored() (+18 more)

### Community 52 - "test_text.py"
Cohesion: 0.24
Nodes (6): make_payload(), make_point(), test_retrieve_cli_hit_line_is_single_clean_line(), test_safe_text_keeps_malayalam_joiners(), test_safe_text_strips_bidi_controls_but_keeps_zwj_zwnj(), test_safe_text_strips_controls_and_ansi()

### Community 53 - "FallbackRetriever"
Cohesion: 0.08
Nodes (29): Fallback authorization invariant (same ResolvedAccess), BM25Retriever (identity, lexical), classify_model_error, classify_qdrant_error, Qdrant client lifecycle gap, eval-compare by served strategy (mixed refused), FallbackRetriever, Hugging Face error shapes (T1 As-built) (+21 more)

### Community 54 - "HybridRetriever (dense leg then BM25 leg, no single-leg fallback)"
Cohesion: 0.22
Nodes (9): BM25Retriever with SQL access clause, HybridRetriever (dense leg then BM25 leg, no single-leg fallback), lexical-v1 tokenizer (NFC, ZWJ/ZWNJ dropped, L/N/Mn/Mc token chars, 64-term cap), RRF fusion (k 60, equal weights, depth 50, fail closed), SQLite FTS5 lexical store (derived, git-ignored, bound to dense index), R6 — BM25 retriever and authorization, R7 — RRF fusion and hybrid retriever, T3 round 2 FAIL: case-insensitive APFS bypass of protected-folder guard (+1 more)

### Community 55 - "asyncio"
Cohesion: 0.21
Nodes (18): _copy_seed(), seed_repository(), test_documents_outside_approved_roots_are_never_loaded(), test_get_document_by_id_and_version(), test_get_document_missing_raises_not_found(), test_invalid_document_fails_load_without_leaking_paths(), test_invalid_schema_raises_repository_error(), test_language_filter_is_data_driven_and_does_not_affect_access() (+10 more)

### Community 56 - "Development Workflow"
Cohesion: 0.10
Nodes (32): Finalized stack: Python/FastAPI, Next.js, Qdrant, SQLite FTS5, BGE-M3, Bedrock, Langfuse, CloudWatch, Terraform ap-south-1, GitHub Actions, Ingestion operating notes (QDRANT_COLLECTION_BASE for fake runs, make setup-bge-m3), agent-skills sync, D001 Python-first backend, D002 RAG as reusable internal package, D003 Knowledge outside RAG package, D005 Documents are truth; chunks are derived, D007 Public-only Phase 1 (+24 more)

### Community 57 - "pathlib"
Cohesion: 0.11
Nodes (17): _is_token_char(), query_terms(), QueryTerms, tokenize(), live_suite_rows(), test_zero_term_queries_skip_the_lexical_sanity_and_are_counted(), test_business_008_words_stay_whole(), test_deterministic() (+9 more)

### Community 59 - "json"
Cohesion: 0.12
Nodes (16): chunker, max_chunk_chars, name, version, embedder, batch_size, fake_vector_size, model_id (+8 more)

### Community 60 - "make eval-security"
Cohesion: 0.15
Nodes (14): Security gate on throwaway w2a-sectest-<8 hex> collection with fake embedder, security_corpus.py, security_index.py, security_eval.py, D040, Throwaway collection w2a-sectest-<8 hex>, eval-security exit 0 pass, 1 violation, 2 harness or configuration error, Security fixtures poisoned_public_document.md and staff_only_canary.md, Forbidden points: staff scope, other tenant, owned, missing owner, staff-only canary; nearest neighbour of every query, Authorization hard gate (forbidden points never returned) (+6 more)

### Community 61 - "SecurityIndex"
Cohesion: 0.16
Nodes (18): clean_env(), copy_fixtures(), _lexical_work_dir(), spy_lexical_path(), wrapper(), strip_forbidden_terms(), test_cli_clause_less_lexical_store_exits_one_naming_strategies(), test_cli_harness_error_exits_two_and_writes_nothing() (+10 more)

### Community 62 - "Target RAG query flow (User -> FastAPI -> validation -> AccessContext -> LanguageContext -> retrieval -> RRF -> reranker -> context builder -> answerability -> prompt -> Bedrock -> citation validation)"
Cohesion: 0.13
Nodes (20): Answerability / insufficient-evidence decision, Authorization applied inside each retriever before fusion, never after RRF, reranking or generation, Authorization filter is part of the Qdrant query so unauthorized points never leave the store, Amazon Bedrock generation, build_access_filter (the only filter builder), check_hit (fail-closed re-check, second line of defense), Citation validation, Context builder (planned) (+12 more)

### Community 64 - "baseline.py"
Cohesion: 0.06
Nodes (41): Review, T2 — v2 dense baseline (user-owned gate), Verification, Implementation, Review, T5 — round 1, User decision, Distinct-document metrics (R7) (+33 more)

### Community 65 - "RetrievalUnavailableError"
Cohesion: 0.11
Nodes (17): 008 — Retrieval Fallback Design, Alternatives / deferred decisions, As-built notes, Data flow, Design summary, Error and failure behavior, Observability, Package / file placement (+9 more)

### Community 66 - "make ingest"
Cohesion: 0.08
Nodes (30): D061 fallback marking, docker compose up -d / down (local Qdrant), Environment: QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION_BASE, W2A_TENANT_ID, eval-retrieval options (--top-k, --strategy, --retrieval-config, --suite default public-eval-v2, --release seed-v1, --output, --repo-root, --config); no --embedder or --allow-fake, Fake embedder needs throwaway QDRANT_COLLECTION_BASE, strategy: bm25 (requested: hybrid; fallback: <reason>) plus stderr WARNING, exit 0, Fallback reasons qdrant_unavailable, qdrant_timeout, model_unavailable (never exception text), Default hybrid needs lexical file; exits 2 without it; setup order make ingest then make index-lexical (+22 more)

### Community 67 - "Spec 007 hybrid retrieval"
Cohesion: 0.08
Nodes (35): build_retriever, make index-lexical, lexical package: lexical-v1 tokenizer, FTS5 store, builder, Known issue: BM25 statistics corpus-wide per file; needs per-scope files for roles, Known issue: legacy chillu sequence does not match atomic chillu in BM25, Known issue: evaluation-data gaps (ml goldens, relevant_section_ids empty), Known issue: g004 overlaps u001, keep_both, Known issue: git_dirty true in Spec 007 BM25/hybrid result files (user-accepted) (+27 more)

### Community 68 - "IndexIdentity"
Cohesion: 0.11
Nodes (5): T8 — Security gate for BM25 and hybrid, Docker isolation test, Verification, _differences(), LexicalIndex, _read_only_connection()

### Community 69 - "FakeEmbedder"
Cohesion: 0.11
Nodes (14): FakeEmbedder, live_client(), __init__(), test_conforms_to_protocol(), test_declared_vector_size(), test_default_size_is_64(), test_fake_device_is_none(), test_info_reports_fake_identity() (+6 more)

### Community 70 - "ARCHITECTURE.md"
Cohesion: 0.12
Nodes (19): D042-D047, D053, D054 evaluation decisions, Evaluation architecture (Evaluation Suite case types), Evaluation assets never written by evaluation code (C6); candidates suggested and human-activated, Ingestion eligibility is the only guard against synthetic/unapproved documents; poisoned_public_document is not an authorization case, Evaluation isolation and gates, models.py, suite.py (tolerant typed cases, read-only load_suite), retrieval_eval.py, slices.py, sections.py, Section-level keys <document_id>#<section_id> (+11 more)

### Community 71 - "AWS target"
Cohesion: 0.10
Nodes (22): Roadmap 11 - Observability, Langfuse traces, Stage latency, model/tokens/cost, release/config IDs, AWS target, Bedrock Knowledge Bases as core RAG (avoided), Bedrock model selection criteria, Amazon CloudWatch, Derived retrieval index in Qdrant (+14 more)

### Community 72 - "EvaluationConfigurationError"
Cohesion: 0.07
Nodes (37): EvaluationConfigurationError, CaseBase, CaseStatus, DatasetRef, DatasetType, GoldenCase, LoadedSuite, SecurityCase (+29 more)

### Community 73 - "retrieval/test_access.py"
Cohesion: 0.16
Nodes (16): clean_env(), guest(), payload(), _policy(), test_a_different_policy_changes_both_builders(), test_both_builders_cover_the_same_three_conditions(), test_check_hit_accepts_valid_payload(), test_check_hit_rejects_malformed_payload() (+8 more)

### Community 74 - "Constitution"
Cohesion: 0.19
Nodes (23): load_manifest(), load_schema(), schema_problems(), validate_manifest(), metadata(), record(), run(), test_duplicate_document_id_rejected() (+15 more)

### Community 75 - "Section: Next step"
Cohesion: 0.08
Nodes (23): Way2Australia AI Platform Master Implementation Plan, Atomic publish and rollback, Phase 2 audit trail, AWS deployment architecture (ap-south-1), Controlled document-change workflow (Release Candidate), CI/CD pipeline, Phase 1 Definition of Done, Evaluation governance states (+15 more)

### Community 76 - "Spec 007 - hybrid retrieval (verified 2026-10-28, merged 3cf70eb; 10 tasks)"
Cohesion: 0.10
Nodes (21): Completion: retrospective, Spec-Review commit, merge, verified status, Spec orchestrator loop (route, role subagents, user approval, merge), GET /health endpoint, make setup, packages core/rag/observability skeletons, task-gated spec skills and skills-sync, task State lifecycle and spec/NNN branches, uv workspace and uv.lock (+13 more)

### Community 77 - "Components / boundaries"
Cohesion: 0.33
Nodes (6): Components / boundaries, R10 — `eval-compare` identity rules (`compare.py`), R12 — Docker test, R1 — Suite v2, R3 — Tokenizer `lexical-v1` (`lexical/tokenizer.py`), R9 — Result format 2.1

### Community 78 - "test_repository_contract.py"
Cohesion: 0.19
Nodes (11): InMemoryDocumentRepository, make_document(), test_document_query_has_no_filesystem_concepts(), test_document_query_is_immutable(), test_get_document_missing_raises_not_found(), test_get_document_returns_latest_or_requested_version(), test_in_memory_repository_satisfies_protocol(), test_list_documents_applies_query_filters() (+3 more)

### Community 79 - "Spec 005 dense retrieval baseline"
Cohesion: 0.16
Nodes (16): AccessContext, Role, W2A_TENANT_ID, make retrieval-baseline legacy frozen, BGE-M3 device mps not pinned (D038), Spec 005 retrospective findings F3-F5, Next step 2: real BGE-M3 baseline committed, experiments/results/retrieval-baseline-idx-v1-20261023T063534Z.json real BGE-M3 baseline, Spec 005 dense retrieval baseline, Spec 005 status: verified 2026-10-23 merged b33462e (+8 more)

### Community 80 - "IngestionConfigurationError"
Cohesion: 0.04
Nodes (82): 009 — Chunking Experiments Design, Alternatives / deferred decisions, As-built notes, Carry-over clean-ups (R11), Chunker identity, settings and configuration (R5), Cross-index comparison (R8), Data flow, Design summary (+74 more)

### Community 81 - "list_eligible_documents"
Cohesion: 0.09
Nodes (23): _authority_map(), collect(), _document_ids(), collect(), DocumentRepository, EligibilityPolicy, list_eligible_documents(), eligible_ids() (+15 more)

### Community 82 - "Ingestion pipeline (Spec 004)"
Cohesion: 0.11
Nodes (18): default_strategy, fusion, candidate_depth, k, method, weights, qdrant, connect_timeout_s (+10 more)

### Community 83 - "Retrieval fallback (Spec 008, D056-D062)"
Cohesion: 0.12
Nodes (18): bm25 builds no embedder and no Qdrant client, classify_model_error, classify_qdrant_error, D056-D062 fallback decisions, D057 Fallback eligibility classification, D058 Fallback policy per query, D061 Marking and evaluation of fallback, D062 5xx not eligible (+10 more)

### Community 84 - "Result format 2.1 and security result 1.1"
Cohesion: 0.40
Nodes (5): eval-compare identity rules (R10), Result format 2.1 and security result 1.1, config/retrieval.yaml and build_retriever strategy factory, Security gate over dense, bm25 and hybrid, T6 round 1 FAIL: hybrid leg_ranks not document-level (leg_document_ranks fix)

### Community 85 - "SecurityIndex"
Cohesion: 0.13
Nodes (7): Implementation, delete_security_index(), lexical_probe_text(), SecurityIndex, test_a_forbidden_hit_injected_into_a_path_fails_the_gate_naming_it(), test_the_security_index_records_a_fake_embedder_and_is_removed(), test_server_filter_keeps_every_forbidden_point_out()

### Community 86 - "test_fallback.py"
Cohesion: 0.11
Nodes (28): Review, FallbackReason, FallbackRetriever, access(), client_at(), closed_port(), Fallback, open_hybrid() (+20 more)

### Community 87 - "Backend stack"
Cohesion: 0.12
Nodes (18): Lexical file is a derived artifact, one per collection, bound by identity and chunk digest, Source documents are truth; chunks, embeddings, sparse entries, Qdrant points and preview indexes are derived artifacts, Backend stack, FastAPI, httpx, jsonschema, Multiple vector databases (avoided), Pandas (+10 more)

### Community 88 - "R2 — v2 dense baseline (user-owned gate)"
Cohesion: 0.40
Nodes (5): Acceptance criteria, R13 strategy comparison and default-strategy rule, R1 Evaluation Suite public-eval-v2 (91 cases), R2 — v2 dense baseline (user-owned gate), T9 strategy comparison and default-strategy decision

### Community 89 - "D023 Task-gated agent workflow"
Cohesion: 0.12
Nodes (16): allowed_scopes, current_release, default_role, implemented_roles, allowed_scopes, allowed_scopes, roles, admin (+8 more)

### Community 90 - "Phase 1 - Production-oriented RAG"
Cohesion: 0.10
Nodes (26): Answerability and insufficient-evidence response, Docker, Terraform, EC2, ECR, CloudWatch, IAM, Bedrock, Bedrock Runtime (roadmap), Deferred serving concerns (circuit breaker, startup policy, Qdrant 5xx D062), Citation manipulation tests and input/cost limits, Backend-owned citation validation, Deduplication, context budgeting, evidence ordering, Dense to BM25 degradation (+18 more)

### Community 91 - "test_schemas.py"
Cohesion: 0.17
Nodes (6): load_schemas(), test_existing_schema_is_referenced_not_copied(), test_missing_schema_is_configuration_error(), test_per_type_required_field_enforced(), test_schema_files_are_valid_draft_2020_12(), test_valid_rows_pass()

### Community 92 - "Fallback (hybrid only)"
Cohesion: 0.21
Nodes (14): bm25 strategy, bm25 needs neither Qdrant nor the bge-m3 extra (Spec 008), config/retrieval.yaml schema 1.1 (default_strategy hybrid, qdrant.connect_timeout_s 2, query_timeout_s 3; 1.0 refused), dense strategy, --strategy dense needs no lexical file, Embedder pair from index_settings or dense_identity; fallback-only 2.2 file compares against Spec 007 bm25 file, eval-retrieval fallback: Qdrant unreachable with default hybrid is served by bm25 for every case, Fallback never applies to explicit dense or bm25 (+6 more)

### Community 93 - "pathlib"
Cohesion: 0.13
Nodes (16): Roadmap 2 - Document model + repository, KnowledgeDocument, Manifest/schema validation, S3DocumentRepository and external storage, apps/api, apps/web, CloudWatch, Document manifest (+8 more)

### Community 94 - "AGENTS.md Project Rules"
Cohesion: 0.38
Nodes (7): test_filtering_in_temporary_suite(), test_invalid_line_names_file_and_line_only(), test_path_escaping_repo_root_refused(), test_real_suite_loads_every_golden_case_and_leaves_evaluation_unchanged(), test_release_id_mismatch_refused(), tree_hashes(), write_suite()

### Community 96 - "IngestionService"
Cohesion: 0.12
Nodes (16): Authorization model (guest/public), Small documents and chunking strategy, Citation strategy (backend-owned validation), FAQ-aware retrieval experiment, Graceful degradation, Hybrid retrieval (dense + BM25 + RRF), Production knowledge corpus, Poisoned public document fixture (+8 more)

### Community 97 - "SpyIndex"
Cohesion: 0.17
Nodes (16): Admin content management, Agent capabilities only where they solve a real product problem, Audit trail, Basic analytics, Candidate evaluation, Change impact analysis, Content hashing, Evaluation Governance (keep/modify/deprecate/replace) (+8 more)

### Community 98 - "HybridRetriever"
Cohesion: 0.11
Nodes (25): R7 — Fusion and `HybridRetriever` (`retrieval/fusion.py`, `hybrid.py`), Change log, Implementation, Review, Review, T5 — round 2, User decision, T5 — RRF fusion, hybrid retriever and `config/retrieval.yaml` (+17 more)

### Community 99 - "CURRENT_STATE.md"
Cohesion: 0.13
Nodes (14): interval, retries, start_period, test, timeout, container_name, healthcheck, image (+6 more)

### Community 101 - "repositories/__init__.py"
Cohesion: 0.06
Nodes (26): DocumentQuery, split_frontmatter(), _StringDateLoader, compute_body_sha256(), normalize_body(), sha256_hex(), document_fields(), under_root() (+18 more)

### Community 102 - "006 Evaluation Framework Tasks"
Cohesion: 0.16
Nodes (15): Local multilingual BGE reranker, BM25 via FTS5 bm25(), Derived local lexical file per collection, Fusion, Generation, Lexical store, lexical-v1 tokens (D051), make index-lexical (+7 more)

### Community 103 - "test_recursive.py"
Cohesion: 0.19
Nodes (16): assert_matches_snapshot(), assert_recursive_chunks_whitespace_fidelity(), chunks_to_records(), collapse_whitespace(), load_snapshot(), snapshot_for_document(), recursive_chunker(), test_deterministic() (+8 more)

### Community 104 - "Retrieval package (Spec 005 and 007)"
Cohesion: 0.14
Nodes (12): graphify skill pointer, spec/NNN branch and Spec-Task trailers, spec-implementer skill (one task per run), spec-orchestrator skill, spec-planner skill, spec-reviewer retrospective skill, Task-gated agent workflow loop, task-reviewer skill (read-only) (+4 more)

### Community 105 - "D035 One filter builder, fail-closed re-check, same path for later fallbacks (Spec 005)"
Cohesion: 0.17
Nodes (20): DenseIndex, build_access_filter, check_hit, DenseRetriever, make eval-retrieval, FallbackRetriever and open_retrieval wiring (merged 1107b67), make retrieve guest/public CLI, Strategy Protocol, BM25Retriever, rrf_fuse, HybridRetriever, Spec 008 retro F4: duplicated standalone open wiring, Next step 1: real eval-retrieval and eval-compare PASS 2026-10-24, retrieval-evaluation-idx-v1-20261024T193140Z.json v1 2.0 closed baseline (+12 more)

### Community 106 - "Qdrant (vector database)"
Cohesion: 0.14
Nodes (13): Authorization metadata (access_scope, owner_user_id, tenant_id), Engineering Conventions, IDs and versions conventions, Knowledge files with provenance, Language metadata (content_language, lote_languages), Logging and tracing hygiene, Domain naming terms, Prompts as versioned assets (+5 more)

### Community 107 - "make validate-evaluation"
Cohesion: 0.15
Nodes (13): schemas.py, validate.py (referencing registry, validate-evaluation checks), Error format ERROR <ClassName>: <message>; eval-compare refusals start with 'not comparable:', EVAL_ARGS, python -m way2australia_rag.evaluation.cli {validate,retrieval,security,compare}, make eval-generation does not exist yet, Retrieval evaluation supports Recall@5, MRR, HitRate@5 and language/category/source-authority slices, Evaluation commands (single module evaluation.cli), Suite status draft, active, deprecated, replaced (+5 more)

### Community 108 - "test_structure.py"
Cohesion: 0.20
Nodes (20): manifest_document_count(), assert_structure_chunks_whitespace_fidelity(), make_document(), structure_chunker(), test_duplicate_sibling_headings_raise(), test_fence_blocks_are_atomic_and_headings_inside_ignored(), test_long_list_splits_only_between_items(), test_main_collision_with_heading_slug() (+12 more)

### Community 109 - "make eval-retrieval"
Cohesion: 0.12
Nodes (17): --allow-fake (plumbing only, never a recorded baseline), make retrieval-baseline (legacy, frozen Spec 005 producer), BASELINE_ARGS (--embedder, --allow-fake, --top-k, --suite, --release, --output, --config), Baseline metrics HitRate@5, random expectation min(1,5/N), Recall@5, MRR, p50/p95 latency, experiments/results/retrieval-baseline-<index_version>-<UTC>.json, never overwritten, D036 binding rules, D053 result 2.1, eval-retrieval exit 0 or 2 (+9 more)

### Community 110 - "Intentionally avoided choices"
Cohesion: 0.18
Nodes (13): Full agent orchestration (avoided), Intentionally avoided choices, Bedrock Agents / AgentCore for Phase 1 (avoided), Containers, Docker, Docker Compose, ECR, Fine-tuning (avoided) (+5 more)

### Community 111 - "test_content_hash.py"
Cohesion: 0.15
Nodes (12): Approved packages, pricing and validity, Six approved packages and prices, 60-day package validity, 24-hour cancellation notice, Personal coaching package, 60-minute coaching session on Google Meet, Individual coaching and live appointments, Mock assessments, scoring, feedback and review windows (+4 more)

### Community 112 - "test_hybrid.py"
Cohesion: 0.10
Nodes (14): dense_pair(), ForbiddenDenseIndex, production_lexical(), real_hybrid(), test_any_other_leg_error_propagates_without_fallback(), retrieve(), test_empty_bm25_leg_keeps_the_dense_order(), test_forbidden_bm25_hit_fails_the_whole_query() (+6 more)

### Community 113 - "test_violation_names_the_document_from_the_error_attribute"
Cohesion: 0.18
Nodes (12): AGENTS.md Project Rules, DocumentRepository Abstraction, Evaluation Governance Rules, Language Separation Rules, Phase 1 Scope, Task-gated Spec Loop, CLAUDE.md Project Instructions, graphify Knowledge Graph Rules (+4 more)

### Community 114 - "pytest"
Cohesion: 0.17
Nodes (12): AccessContext(role, tenant_id) with blank tenant refused, Future agent folders intentionally not created, apps/api (FastAPI application layer), apps/web (Next.js/TypeScript frontend: recruiter assistant, RAG Lab, engineering views), core/access.py (Role, frozen AccessContext), guest_access, Knowledge model metadata (document_id, document_version, tenant_id, access_scope, lote_languages, content_language, source_authority...), No language filter, score threshold or reranking yet (+4 more)

### Community 115 - "test_bm25.py"
Cohesion: 0.15
Nodes (13): BM25, Deterministic regression gates, Versioned Evaluation Suite, Golden, refusal and security cases, HitRate@5, Roadmap 5 - Evaluation framework, Roadmap 6 - Hybrid retrieval, Roadmap 15 - CI/CD + regression gates (+5 more)

### Community 116 - "fusion"
Cohesion: 0.20
Nodes (12): English, Malayalam and mixed queries, FAQ-aware retrieval/indexing, Roadmap 7 - Chunking experiments, Roadmap 8 - Multilingual retrieval, Language applicability handling, Parent-heading context and order-independent section_ids, Recursive chunking baseline, Optional semantic chunking (+4 more)

### Community 117 - "evaluation/cli.py"
Cohesion: 0.21
Nodes (12): Branching and commits (spec/NNN, Spec-Task trailer), Development Workflow, Multi-agent handoff, Implementation rule: BLOCKED spec issue, Phase discipline, Protected source-of-truth data, Required spec-reviewer retrospective, Agent skills (orchestrator, planner, implementer, task-reviewer, spec-reviewer) (+4 more)

### Community 119 - "evaluation/errors.py"
Cohesion: 0.13
Nodes (12): active_registry_languages(), aggregate(), _mean(), slice_by(), source_authority_key(), row(), test_absent_languages_from_a_temp_registry(), test_missing_registry_section_is_a_configuration_error() (+4 more)

### Community 120 - "failing_client"
Cohesion: 0.18
Nodes (10): content-hash-v1 (sole change-detection signal), LocalDocumentRepository, Document manifest and JSON Schema validation, make validate-knowledge, persona_scope spec defect (F2), BgeM3Embedder (optional extra, pinned revision), Embedder Protocol and FakeEmbedder, HeadingChunker and slugify rule (+2 more)

### Community 121 - "test_status_handling.py"
Cohesion: 0.20
Nodes (8): Adding a New Language Guide, language_registry.json, Public Assistant Content Boundaries, access_scope, content_language, Knowledge Schema and Metadata, language_scope, lote_languages

### Community 122 - "make eval-compare"
Cohesion: 0.20
Nodes (11): results.py, compare.py (reads 1.0, 2.0, 2.1; quality gate; identity refusals), eval-compare exit 0 pass, 1 gate failure, 2 refusal, WARNING flipped hit->miss / miss->hit lines (<case_id> v<case_version>), Gate: fail if more than 1 fewer hit cases or MRR drop above 1/n, Fallback path latency marked 'includes failed dense attempt' (informational), Not-comparable refusals (suite, case sets, top_k, fake, collection, index_version, embedder, lexical index, mixed served strategies), BASE and CANDIDATE variables, make eval-compare (+3 more)

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

### Community 130 - "BGE-M3 embeddings"
Cohesion: 0.22
Nodes (9): Authorization regression and staff canary, BGE-M3 (roadmap), Roadmap 4 - Dense retrieval baseline, Public access filter, Device not pinned, recorded in results (D038), Embeddings, Deterministic fake embedder, BGE-M3 embeddings (+1 more)

### Community 131 - "RuntimeSettings"
Cohesion: 0.33
Nodes (9): NAATI CCL candidate rules and test-day setup, Direct first-person speech requirement, Report technical incidents within 24 hours, NAATI, Online proctoring with separate phone or tablet, Prohibited materials and tools, Recording under 20 minutes, One repeated segment per dialogue without penalty (+1 more)

### Community 132 - "lexical/ package (Spec 007)"
Cohesion: 0.22
Nodes (9): D060 Standalone lexical freshness, Standalone freshness proves lexical file matches repository, not live Qdrant (D060), lexical/cli.py (make index-lexical writes only git-ignored file), freshness.py (verify_fresh, chunk digest recomputed from repository), lexical/ package (Spec 007), store.py (SQLite FTS5: chunks table, chunk_terms FTS5 table, settings row; LexicalIndex.open, bind_to, search), tokenizer.py (lexical-v1), make index-lexical (+1 more)

### Community 133 - "Vocabulary, flashcards and free access"
Cohesion: 0.29
Nodes (7): EligibilityPolicy / GUEST_PUBLIC_POLICY, Security fixtures (valid but ineligible), config/ingestion.yaml and RuntimeSettings, Ingestion pipeline (target vs current state diff), AccessContext and Role (core), resolve_access / ResolvedAccess, W2A_TENANT_ID server tenant setting

### Community 134 - ".search"
Cohesion: 0.25
Nodes (8): Phase 2 basic analytics, Assistant behavior rules, Product Context, English and Malayalam language scope, Future personas, Phase 1 guest-only scope, Way2Australia AI product, Source-of-truth priorities

### Community 136 - "Spec 002 document model and repository"
Cohesion: 0.16
Nodes (15): Pydantic document models and enums, EligibilityPolicy for guest/public, LocalDocumentRepository with manifest schema validation, make validate-knowledge, Spec 002 decisions made before approval (content_hash, fixtures, validate-knowledge), Seed data status: 13 public docs, evaluation datasets, security fixtures, Spec 002 retrospective findings F1-F6, Spec 002 document model and repository (+7 more)

### Community 138 - "Evaluation Framework Goal"
Cohesion: 0.39
Nodes (8): NAATI CCL test format, scoring and results, NAATI CCL test, Deduction-based assessment, Begin interpreting within five seconds of chime, NAATI, CCL is not professional interpreter certification, Pass requirement 63/90 overall and 29/45 per dialogue, Results within 4-6 weeks

### Community 139 - "security_index.py"
Cohesion: 0.06
Nodes (34): Acceptance criteria, build_security_index(), _canary_points(), _forbidden_payload(), forbidden_variant(), _lexical_forbidden_entries(), require_security_base(), Chunk (+26 more)

### Community 140 - "LocalRepositoryConfig"
Cohesion: 0.10
Nodes (10): build_security_repository(), _fixture_files(), DocumentNotFoundError, DocumentRepositoryError, DocumentValidationError, DuplicateDocumentError, ManifestValidationError, LocalRepositoryConfig (+2 more)

### Community 141 - "BGE-M3 (initial embedding model)"
Cohesion: 0.38
Nodes (6): Evaluation Candidates File, Evaluation Package (evaluation/), Evaluation Suite and Case-type Schemas, validate-evaluation, T2 Schemas and validate-evaluation, T7 Candidates

### Community 142 - "Way2Australia AI Platform Master Implementation Plan"
Cohesion: 0.29
Nodes (7): eval-retrieval, Retrieval Result Document 2.0, Section-level Metrics, Slices and small_sample, Unanswerable Reporting, T3 Retrieval Runner, T4 Unanswerable Reporting

### Community 143 - "Evaluation tooling"
Cohesion: 0.36
Nodes (8): Custom retrieval metrics (plain Python), DeepEval (not yet a dependency), Evaluation tooling, Generation/e2e metrics (correctness, faithfulness, citations, refusal), GitHub Actions, LLM-as-judge not sole source of truth, Primary retrieval metrics (Recall@5, MRR, HitRate@5), pytest

### Community 144 - "eval-compare"
Cohesion: 0.29
Nodes (7): AGENTS.md, Claude adapter, Initial specs, Phase 0 - Project bootstrap, Project context files, SDD workflow (Spec 003 task-gated agent workflow), Stable command interface

### Community 145 - "Payments, account access and support boundaries"
Cohesion: 0.29
Nodes (6): Vocabulary, flashcards and free access, Spaced-repetition flashcards, Free access allowance, 12 subject domains plus General vocabulary, Approved public learning samples, Sample neighbour-greeting dialogue

### Community 147 - "make test"
Cohesion: 0.33
Nodes (6): 006 Evaluation Framework Design, Decision Brief Q1-Q10, 006 Evaluation Framework Requirements, Evaluation Framework Goal, 006 Spec Retrospective Review, Retrospective Round 1 PASS

### Community 148 - "Mission"
Cohesion: 0.33
Nodes (5): Evaluation case_id and case_version, Versioning and Releases, document_id and document_version, Phase 2 Knowledge Release Candidates, Release seed-v1

### Community 149 - "test_open_retrieval_bm25_builds_no_embedder_and_no_client"
Cohesion: 0.29
Nodes (4): block_model_stack(), Raises, test_open_retrieval_bm25_builds_no_embedder_and_no_client(), test_retrieve_cli_bm25_needs_neither_qdrant_nor_the_model()

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

### Community 155 - "test_status_handling.py"
Cohesion: 0.26
Nodes (5): security_repository(), golden_count(), suite_with_statuses(), test_exclusions_counted_by_status(), test_suggested_never_returned()

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
Cohesion: 0.33
Nodes (3): test_every_path_is_gated_for_every_query(), counting(), counting()

### Community 192 - "metrics.py, goldens.py, baseline.py, baseline_cli.py"
Cohesion: 0.50
Nodes (4): Baseline runner (refuses fake index without --allow-fake; HitRate@k, Recall@k, MRR, p50/p95, min(1,k/N) random expectation), D037 Baseline runner decisions, make retrieval-baseline (legacy dense-only), metrics.py, goldens.py, baseline.py, baseline_cli.py

## Ambiguous Edges - Review These
- `Task-gated agent workflow loop` → `graphify skill pointer`  [AMBIGUOUS]
  .claude/CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **380 isolated node(s):** `way2australia-api`, `way2australia-core`, `way2australia-observability`, `way2australia-rag`, `way2australia` (+375 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1248 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **41 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Change log` connect `HybridRetriever` to `DenseRetriever`, `opening.py`, `Spec 007 hybrid retrieval`, `IndexIdentity`, `baseline.py`, `run_security_evaluation`, `test_lexical_cli.py`, `Document Model Tests`, `007 — Hybrid Retrieval Requirements`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Are the 78 inferred relationships involving `DenseIndex` (e.g. with `Design summary` and `Decisions resolved before drafting`) actually correct?**
  _`DenseIndex` has 78 INFERRED edges - model-reasoned connections that need verification._
- **What connects `way2australia-api`, `way2australia-core`, `way2australia-observability` to the rest of the system?**
  _380 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `DenseRetriever` be split into smaller, more focused modules?**
  _Cohesion score 0.0612668743509865 - nodes in this community are weakly interconnected._
- **Why does `D055 Default strategy is hybrid (Spec 007)` connect `Spec 007 hybrid retrieval` to `Development Workflow`, `typing`, `Ingestion pipeline (Spec 004)`, `D035 One filter builder, fail-closed re-check, same path for later fallbacks (Spec 005)`?**
  _High betweenness centrality (0.093) - this node is a cross-community bridge._
- **Are the 29 inferred relationships involving `LocalDocumentRepository` (e.g. with `Dependencies` and `Design summary`) actually correct?**
  _`LocalDocumentRepository` has 29 INFERRED edges - model-reasoned connections that need verification._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Task-gated agent workflow loop` and `graphify skill pointer`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._