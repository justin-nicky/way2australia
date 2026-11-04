# Graph Report - way2australia  (2026-11-04)

## Corpus Check
- 304 files · ~344,346 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 36 file(s) not represented in the graph (top: (none) 20, .jsonl 13, .mdc 1)

## Summary
- 4723 nodes · 14382 edges · 200 communities (167 shown, 33 thin omitted)
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 3089 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `423ba511`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_compare.py
- retrieval_client_factory
- open_retrieval
- LexicalIndexBindingError
- test_validate.py
- ResolvedAccess
- test_applicability.py
- DenseIndex
- Round 1 — 2026-11-03
- evaluation/validate.py
- lexical/cli.py
- ChunkerIdentity
- HeadingChunker
- compare.py
- test_lexical_cli.py
- json
- CURRENT_STATE.md current state document
- QdrantIndexStore
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
- bge_tokenizer_fixture
- KnowledgeDocument
- evaluation/cli.py
- evaluation/test_cli.py
- 010 — Multilingual Retrieval Requirements
- BgeM3Tokenizer
- 009 — Chunking Experiments Requirements
- 008 — Retrieval Fallback Requirements
- asyncio
- test_service.py
- open_retrieval
- typing
- tokenizer.py
- Workflow Reviewer
- LocalDocumentRepository
- run_retrieval_evaluation
- test_cli_config.py
- test_repository_contract.py
- Ingestion (Phase 1 baseline, Spec 004)
- 007 — Hybrid Retrieval Requirements
- LocalRepositoryConfig
- HeadingChunker
- rrf_fuse
- FallbackRetriever
- test_content_hash.py
- BgeM3Embedder
- Development Workflow
- retrieval_eval.py
- dense
- json
- Evaluation Phase 1 framework (Spec 006)
- security_eval.py
- RuntimeSettings
- manifest.py
- test_legacy_baseline_snapshot.py
- test_structure.py
- make eval-retrieval
- Spec 007 hybrid retrieval
- BM25Retriever
- ResolvedLote
- embedder
- Phase 1 RAG query pipeline
- load_retrieval_config
- Target repository shape (apps, packages, knowledge, sources, evaluation, tests, config, experiments, analytics, prompts, docs, infra)
- test_manifest_validation.py
- Section: Next step
- doc22
- test_baseline.py
- embedder
- repositories/__init__.py
- RetrievalConfigurationError
- FallbackReason
- Ingestion pipeline (Spec 004)
- open_hybrid
- retrieval/test_access.py
- LexicalIndex
- test_lexical_standalone.py
- Backend stack
- embedder
- D023 Task-gated agent workflow
- test_status_handling.py
- test_schemas.py
- Roadmap 13 - Graceful degradation
- pathlib
- Spec status table
- test_eligibility.py
- ingest_dense
- SpyIndex
- transcript_metrics.py
- CURRENT_STATE.md
- QdrantIndexStore
- read_result
- AWS target
- make ingest
- Retrieval package (Spec 005 and 007)
- dedupe_documents
- Qdrant (vector database)
- test_seed_corpus.py
- D055 Default strategy is hybrid (Spec 007)
- FakeEmbedder
- RetrievalConfigurationError
- test_content_hash.py
- Spec 005 dense retrieval baseline
- test_violation_names_the_document_from_the_error_attribute
- test_lexical_build.py
- AccessContext
- fusion
- SQLite FTS5
- Target RAG query flow (User -> FastAPI -> validation -> AccessContext -> LanguageContext -> retrieval -> RRF -> reranker -> context builder -> answerability -> prompt -> Bedrock -> citation validation)
- EvaluationConfigurationError
- failing_client
- test_status_handling.py
- repositories/__init__.py
- dense
- QdrantIndexStore
- Baseline runner and result JSON
- test_failed_write_removes_partial_file
- Development Workflow
- test_status_handling.py
- absent_query_languages
- Phase 1 - Production-oriented RAG
- RuntimeSettings
- load_suite
- Vocabulary, flashcards and free access
- .search
- git_state
- Spec 002 document model and repository
- lexical/ package (Spec 007)
- Evaluation Framework Goal
- test_lexical_tokenizer.py
- Roadmap 12 - Security
- BGE-M3 (initial embedding model)
- Way2Australia AI Platform Master Implementation Plan
- Retrieval fallback (Spec 008, D056-D062)
- eval-compare
- Payments, account access and support boundaries
- make retrieve
- make test
- Mission
- IndexIdentity
- Scripted
- Spec 004 retrospective round 1 (PASS)
- policy
- policy
- policy
- typing
- conftest.py
- LexicalIndexError
- Orchestrator State Machine
- way2australia_api/__init__.py
- Project Context README
- Roadmap 3 - Ingestion baseline
- way2australia_rag/__init__.py
- Scripted
- way2australia-core
- Phase 1 analytics event contract
- Spec-driven development workflow
- api/__init__.py
- score_distribution
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
- test_slices.py
- policy
- test_failed_write_removes_partial_file
- Spec 010 — task reviews
- Way2Australia AI Platform Master Implementation Plan

## God Nodes (most connected - your core abstractions)
1. `DenseIndex` - 113 edges
2. `LocalDocumentRepository` - 106 edges
3. `ResolvedAccess` - 79 edges
4. `Strategy` - 79 edges
5. `DenseRetriever` - 79 edges
6. `FakeTokenizer` - 78 edges
7. `run_retrieval_evaluation()` - 74 edges
8. `FakeEmbedder` - 73 edges
9. `HeadingChunker` - 69 edges
10. `LexicalIndex` - 68 edges

## Surprising Connections (you probably didn't know these)
- `Alternatives / deferred decisions` --references--> `AccessContext`  [INFERRED]
  .kiro/specs/010-multilingual-retrieval/design.md → packages/core/src/way2australia_core/access.py
- `R10 — `eval-compare` identity rules (`compare.py`)` --references--> `_refusals()`  [INFERRED]
  .kiro/specs/007-hybrid-retrieval/design.md → packages/rag/src/way2australia_rag/evaluation/compare.py
- `Change log` --references--> `run_retrieval_evaluation()`  [INFERRED]
  .kiro/specs/009-chunking-experiments/requirements.md → packages/rag/src/way2australia_rag/evaluation/retrieval_eval.py
- `T4 review follow-ups (planner amendment 2026-11-02)` --references--> `run_retrieval_evaluation()`  [INFERRED]
  .kiro/specs/009-chunking-experiments/tasks.md → packages/rag/src/way2australia_rag/evaluation/retrieval_eval.py
- `Acceptance criteria` --references--> `script_mix()`  [INFERRED]
  .kiro/specs/010-multilingual-retrieval/requirements.md → packages/rag/src/way2australia_rag/evaluation/script_mix.py

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

## Communities (200 total, 33 thin omitted)

### Community 0 - "test_compare.py"
Cohesion: 0.13
Nodes (52): Review, case(), doc(), doc21(), doc22(), ranked(), refusal(), run() (+44 more)

### Community 1 - "retrieval_client_factory"
Cohesion: 0.11
Nodes (10): R2 — Qdrant timeouts (`qdrant_client.py`, `config/retrieval.yaml`), R3 — Standalone lexical open (`identity.py`, `lexical/store.py`), Implementation, T1 — round 1, User decision, T3 — `bm25` without Qdrant or the `bge-m3` extra; one open path, Verification, default_client_factory() (+2 more)

### Community 2 - "open_retrieval"
Cohesion: 0.10
Nodes (33): 008 — Retrieval Fallback Design, Alternatives / deferred decisions, Data flow, Design summary, Error and failure behavior, Interfaces / models, Observability, Package / file placement (+25 more)

### Community 3 - "LexicalIndexBindingError"
Cohesion: 0.10
Nodes (22): R4/R5 — Lexical store (`lexical/store.py`, `lexical/build.py`), Implementation, Review, T3 — round 1, User decision, T3 — `lexical-v1` tokenizer, lexical store and `make index-lexical`, Verification, R4 — Freshness from the repository (`lexical/freshness.py`) (+14 more)

### Community 4 - "test_validate.py"
Cohesion: 0.14
Nodes (31): edit_rows(), edit_suite(), root(), run(), test_active_golden_without_relevant_documents(), test_candidate_ineligible_document_is_not_unknown(), test_candidate_not_suggested(), test_candidate_referenced_by_suite() (+23 more)

### Community 5 - "ResolvedAccess"
Cohesion: 0.12
Nodes (27): Alternatives / deferred decisions, Error and failure behavior, Phase 2 compatibility / migration, Security / authorization, Acceptance criteria, Acceptance criteria, Dependencies, Review (+19 more)

### Community 6 - "test_applicability.py"
Cohesion: 0.16
Nodes (29): active_lote_codes(), _active_list(), resolve_lote(), build_lexical(), _doc_sets(), _dropped_lote_setup(), DroppedFilterIndex, DroppedLoteClauseLexical (+21 more)

### Community 7 - "DenseIndex"
Cohesion: 0.05
Nodes (75): LexicalRow, IndexBindingError, DenseIndex, OddIdStore, build(), dense_fixture(), DroppedClauseIndex, guest() (+67 more)

### Community 8 - "Round 1 — 2026-11-03"
Cohesion: 0.06
Nodes (30): As-built notes, Carry-over clean-ups (R11), Cross-index comparison (R8), Security gate (R9), 009 — Chunking Experiments: Retrospective Review, Documentation reconciled, Extra checks (user-requested), Final handoff (+22 more)

### Community 9 - "evaluation/validate.py"
Cohesion: 0.10
Nodes (21): Implementation, Review, T1 — round 1, User decision, EvaluationSchemas, _candidate_rules(), problem(), _describe() (+13 more)

### Community 10 - "lexical/cli.py"
Cohesion: 0.05
Nodes (59): Cross-task consistency, Deviations from the approved plan, Findings, Implementation, Implementation, Review, Review, T1 — round 2 (+51 more)

### Community 11 - "ChunkerIdentity"
Cohesion: 0.07
Nodes (28): 009 — Chunking Experiments Design, Alternatives / deferred decisions, Chunker identity, settings and configuration (R5), Components / boundaries, Data flow, Design summary, Distinct-document metrics (R7), Error and failure behavior (+20 more)

### Community 12 - "HeadingChunker"
Cohesion: 0.13
Nodes (38): equivalence_suite(), basic_suite(), build(), default_eval_extras(), fusion_config(), golden(), _LexicalStub, run() (+30 more)

### Community 13 - "compare.py"
Cohesion: 0.12
Nodes (33): Implementation, Review, T7 — round 1, User decision, _changed(), compare(), Comparison, _cross_index_lines() (+25 more)

### Community 14 - "test_lexical_cli.py"
Cohesion: 0.06
Nodes (57): Branching and commits (spec/NNN, Spec-Task trailer), Development Workflow, Multi-agent handoff, Implementation rule: BLOCKED spec issue, Phase discipline, Protected source-of-truth data, Required spec-reviewer retrospective, Agent skills (orchestrator, planner, implementer, task-reviewer, spec-reviewer) (+49 more)

### Community 15 - "json"
Cohesion: 0.15
Nodes (25): committed(), edit_jsonl(), lines(), manifest(), problems(), read_lines(), root(), test_candidates_differ_only_in_promoted_as() (+17 more)

### Community 16 - "CURRENT_STATE.md current state document"
Cohesion: 0.10
Nodes (36): standalone bm25 without Qdrant or extra (IndexIdentity, freshness), CURRENT_STATE.md current state document, Current goal: Specs 001-008 complete; Spec 008 verified and merged into main (1107b67), plan next spec, Phase 2 Knowledge Release workflow designed not implemented, Public/guest retrieval only in Phase 1; English + Malayalam, Known issue: Qdrant and Hugging Face 5xx not fallback-eligible, Known issue: verify_fresh asyncio.run in event loop, Known issue: Qdrant client lifecycle leak on failed open (+28 more)

### Community 18 - "QdrantIndexStore"
Cohesion: 0.06
Nodes (48): chunker_for_result(), IndexSettingsMismatchError, build_index_settings(), compare(), IndexSettings, mismatch_message(), IndexedDocument, QdrantIndexStore (+40 more)

### Community 19 - "DenseRetriever"
Cohesion: 0.09
Nodes (34): IndexPoint, DenseRetriever, test_run_retrieval_evaluation_on_multi_chunk_recursive_index(), client_with_forbidden(), FilterDroppingIndex, test_forbidden_points_are_never_returned(), test_store_dropping_the_filter_fails_closed(), test_formula_shows_the_cap_when_k_reaches_document_count() (+26 more)

### Community 20 - "007 — Hybrid Retrieval Requirements"
Cohesion: 0.04
Nodes (46): BM25Retriever with SQL access clause, eval-compare identity rules (R10), HybridRetriever (dense leg then BM25 leg, no single-leg fallback), lexical-v1 tokenizer (NFC, ZWJ/ZWNJ dropped, L/N/Mn/Mc token chars, 64-term cap), Result format 2.1 and security result 1.1, config/retrieval.yaml and build_retriever strategy factory, Security gate over dense, bm25 and hybrid, SQLite FTS5 lexical store (derived, git-ignored, bound to dense index) (+38 more)

### Community 21 - "test_validate_knowledge.py"
Cohesion: 0.22
Nodes (26): load(), test_bad_date_fails_loading_naming_document_and_field(), test_seed_corpus_still_loads(), test_valid_date_loads(), build_repo(), metadata(), problems_for(), run_cli() (+18 more)

### Community 22 - "test_availability.py"
Cohesion: 0.08
Nodes (31): As-built notes, R1 — Failure classification (`errors.py`, `availability.py`), T1: Hugging Face error shapes (confirmed 2026-10-29), Testing / evaluation strategy, Review, classify_model_error(), classify_qdrant_error(), _optional_types() (+23 more)

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
Cohesion: 0.04
Nodes (76): Package / file placement, Requirements traceability, Implementation, Implementation, Implementation, Implementation, Review, Review (+68 more)

### Community 27 - "test_suite_v3.py"
Cohesion: 0.12
Nodes (29): Implementation, Review, T1 — round 1, User decision, candidate_row(), candidates(), edit_jsonl(), errors() (+21 more)

### Community 28 - "test_strategy_eval.py"
Cohesion: 0.10
Nodes (37): Review, User decision, Review, Strategy, build_lexical(), configured_lexical(), eval_world(), leg_order() (+29 more)

### Community 29 - "Evaluation CLI Tests"
Cohesion: 0.12
Nodes (31): assert_invalid(), document_fields(), make_document(), test_blank_required_text_is_rejected(), test_document_is_immutable(), test_duplicate_lote_languages_are_rejected(), test_effective_window_must_be_ordered(), test_empty_lote_languages_is_rejected() (+23 more)

### Community 31 - "KnowledgeDocument"
Cohesion: 0.08
Nodes (7): _check_language_code(), KnowledgeDocument, _document_ids(), collect(), DocumentQuery, ListRepository, IgnoresQueryRepository

### Community 32 - "evaluation/cli.py"
Cohesion: 0.08
Nodes (26): Implementation, Review, T4 — round 1, User decision, _authority_map(), _compare(), default_security_output_path(), format_security_summary() (+18 more)

### Community 33 - "evaluation/test_cli.py"
Cohesion: 0.16
Nodes (19): load_production_ingestion_config(), clean_env(), index_factory(), real_factory(), run(), test_bad_top_k_exits_2(), test_cli_has_no_embedder_or_allow_fake_flag(), test_existing_output_exits_2_before_qdrant() (+11 more)

### Community 34 - "010 — Multilingual Retrieval Requirements"
Cohesion: 0.07
Nodes (29): 010 — Multilingual Retrieval Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+21 more)

### Community 35 - "BgeM3Tokenizer"
Cohesion: 0.12
Nodes (10): BgeM3Tokenizer, hub(), test_bge_m3_cache_hit_counts(), test_bge_m3_miss_offline_refused(), test_bge_m3_miss_online_download(), test_bge_m3_refuses_floating_revision(), test_bge_m3_smoke_matches_sentence_transformer_tokenizer(), test_bge_m3_wrong_revision_refused() (+2 more)

### Community 36 - "009 — Chunking Experiments Requirements"
Cohesion: 0.07
Nodes (28): 009 — Chunking Experiments Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+20 more)

### Community 37 - "008 — Retrieval Fallback Requirements"
Cohesion: 0.09
Nodes (36): Baseline runner (refuses fake index without --allow-fake; HitRate@k, Recall@k, MRR, p50/p95, min(1,k/N) random expectation), Binding: embedder model ID, revision, vector size, normalization, fake flag and index_version must equal recorded IndexSettings, BM25Retriever(identity, lexical), BM25 statistics (IDF, avg length) computed over every row of a lexical file, build_access_filter (the only filter builder), build_retriever (only place a strategy name becomes a retriever), retrieval_client_factory (Qdrant client with configured timeouts), config/retrieval.yaml (default_strategy hybrid, RRF k 60, depth 50) (+28 more)

### Community 38 - "asyncio"
Cohesion: 0.26
Nodes (15): test_repository_content_hash_is_content_hash_v1(), _copy_seed(), seed_repository(), test_documents_outside_approved_roots_are_never_loaded(), test_get_document_by_id_and_version(), test_get_document_missing_raises_not_found(), test_invalid_document_fails_load_without_leaking_paths(), test_invalid_schema_raises_repository_error() (+7 more)

### Community 39 - "test_service.py"
Cohesion: 0.14
Nodes (26): BoomChunker, doc(), Harness, ShortResultEmbedder, test_bumped_document_version_updates(), test_changed_body_updates(), test_changed_metadata_field_updates(), test_chunk_shrink_leaves_no_orphan() (+18 more)

### Community 40 - "open_retrieval"
Cohesion: 0.12
Nodes (13): get_health(), HealthResponse, get_request_settings(), get_settings(), Settings, create_app(), isolate_settings_environment(), test_create_app_wires_settings() (+5 more)

### Community 41 - "typing"
Cohesion: 0.10
Nodes (31): 006-candidates.jsonl with 7 suggested rows, make eval-compare, make eval-security hard gate, result 2.2 and served-strategy eval-compare, eval-security five paths, governed suite loader and schemas, make validate-evaluation, Spec 006 retrospective findings (F1 byte-identity, eval-security not in verify) (+23 more)

### Community 42 - "tokenizer.py"
Cohesion: 0.19
Nodes (10): _is_token_char(), query_terms(), _query_terms_from(), QueryTerms, replace_sequences(), _tokenize_after_nfc(), _tokenize_v1(), _tokenize_v2() (+2 more)

### Community 43 - "Workflow Reviewer"
Cohesion: 0.07
Nodes (25): Considered and rejected, Evidence, F1 — <title> [waste | quality risk | process slip] (confidence: high/medium/low), Findings, New features and tools (official sources, since <date>), Not measurable here, P1 — <title> (addresses F#; expected saving: ...), Proposals (+17 more)

### Community 44 - "LocalDocumentRepository"
Cohesion: 0.06
Nodes (69): LocalDocumentRepository, build(), clean_env(), copy_fixtures(), DroppedClauseLexical, DroppedLoteClauseLexical, guest_access(), _lexical_work_dir() (+61 more)

### Community 45 - "run_retrieval_evaluation"
Cohesion: 0.11
Nodes (17): Implementation, T5 — round 1, User decision, DatasetType, LoadedSuite, active_golden_cases(), _fusion_report(), _lexical_report() (+9 more)

### Community 46 - "test_cli_config.py"
Cohesion: 0.09
Nodes (25): manifest_document_count(), clean_env(), _factory(), _run(), test_agrees_with_day1_baseline(), test_builds_exactly_one_embedder_per_run(), test_collection_base_comes_from_environment(), test_config_refuses_missing_or_floating_revision() (+17 more)

### Community 47 - "test_repository_contract.py"
Cohesion: 0.19
Nodes (11): InMemoryDocumentRepository, make_document(), test_document_query_has_no_filesystem_concepts(), test_document_query_is_immutable(), test_get_document_missing_raises_not_found(), test_get_document_returns_latest_or_requested_version(), test_in_memory_repository_satisfies_protocol(), test_list_documents_applies_query_filters() (+3 more)

### Community 48 - "Ingestion (Phase 1 baseline, Spec 004)"
Cohesion: 0.09
Nodes (27): BgeM3Embedder (optional bge-m3 extra, dense only), D025-D030, D032 ingestion decisions, DocumentRepository Protocol (get_document, list_documents), Embedder Protocol, Evaluation architecture (Evaluation Suite case types), Evaluation cases have stable IDs and versions; not coupled to chunk IDs, FakeEmbedder (deterministic), HeadingChunker (heading v1, character cap, stable section_id slugs) (+19 more)

### Community 49 - "007 — Hybrid Retrieval Requirements"
Cohesion: 0.09
Nodes (27): optional bge-m3 extra (sentence-transformers, PyTorch), D048 graphify tooling, make experiment CONFIG=... (target; records git commit, release, suite, chunker, embedder, strategy, metrics, latency), make format, Knowledge graph graphify (D048), /graphify . --update (user, once per spec after merge), graphify query / path / explain, graphify update . (+19 more)

### Community 50 - "LocalRepositoryConfig"
Cohesion: 0.11
Nodes (19): collect(), EligibilityPolicy, list_eligible_documents(), LocalRepositoryConfig, _corpus_problems(), assert_recursive_chunks_whitespace_fidelity(), recursive_chunker(), test_deterministic() (+11 more)

### Community 51 - "HeadingChunker"
Cohesion: 0.10
Nodes (31): R3 — Tokenizer `lexical-v1` (`lexical/tokenizer.py`), HeadingChunker, _is_word_char(), _parse_sections(), _Section, slugify(), _split_body(), _split_words() (+23 more)

### Community 52 - "rrf_fuse"
Cohesion: 0.18
Nodes (15): Implementation, T5 — round 2, User decision, rrf_fuse(), chunk(), test_both_legs_empty(), test_duplicate_in_a_leg_counts_best_rank_only(), test_empty_leg_keeps_the_other_order() (+7 more)

### Community 53 - "FallbackRetriever"
Cohesion: 0.08
Nodes (29): Fallback authorization invariant (same ResolvedAccess), BM25Retriever (identity, lexical), classify_model_error, classify_qdrant_error, Qdrant client lifecycle gap, eval-compare by served strategy (mixed refused), FallbackRetriever, Hugging Face error shapes (T1 As-built) (+21 more)

### Community 54 - "test_content_hash.py"
Cohesion: 0.15
Nodes (18): canonical_json(), _canonical_value(), _canonical_value_mapping(), compute_content_hash(), _copy_seed(), h(), _load(), test_absent_optional_fields_hash_as_null() (+10 more)

### Community 55 - "BgeM3Embedder"
Cohesion: 0.10
Nodes (14): BgeM3Embedder, OptionalDependencyError, missing(), group_installed(), test_constructing_does_not_load_the_model(), test_device_none_before_load_and_recorded_after(), test_missing_group_at_load_raises_optional_dependency_error(), test_missing_group_refused_at_construction() (+6 more)

### Community 56 - "Development Workflow"
Cohesion: 0.09
Nodes (33): Evaluation Suite includes goldens, refusal, multilingual, security, regression, Finalized stack: Python/FastAPI, Next.js, Qdrant, SQLite FTS5, BGE-M3, Bedrock, Langfuse, CloudWatch, Terraform ap-south-1, GitHub Actions, Ingestion operating notes (QDRANT_COLLECTION_BASE for fake runs, make setup-bge-m3), agent-skills sync, D001 Python-first backend, D002 RAG as reusable internal package, D003 Knowledge outside RAG package, D005 Documents are truth; chunks are derived (+25 more)

### Community 57 - "retrieval_eval.py"
Cohesion: 0.05
Nodes (32): R6 — `BM25Retriever` (`retrieval/bm25.py`), Review, T2 — v2 dense baseline (user-owned gate), Verification, Continuity command (R10), Role, _latency_by_path(), _leg_latency() (+24 more)

### Community 58 - "dense"
Cohesion: 0.05
Nodes (47): 008 — Retrieval Fallback Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+39 more)

### Community 59 - "json"
Cohesion: 0.10
Nodes (20): chunker, context_prefix, name, overlap_tokens, target_tokens, version, embedder, batch_size (+12 more)

### Community 60 - "Evaluation Phase 1 framework (Spec 006)"
Cohesion: 0.06
Nodes (37): D042-D047, D053, D054 evaluation decisions, Evaluation assets never written by evaluation code (C6); candidates suggested and human-activated, Ingestion eligibility is the only guard against synthetic/unapproved documents; poisoned_public_document is not an authorization case, Evaluation isolation and gates, models.py, suite.py (tolerant typed cases, read-only load_suite), retrieval_eval.py, slices.py, sections.py, schemas.py, validate.py (referencing registry, validate-evaluation checks), Section-level keys <document_id>#<section_id> (+29 more)

### Community 61 - "security_eval.py"
Cohesion: 0.07
Nodes (38): Implementation, Review, T8 — round 1, User decision, Review, Review, _security(), EvaluationHarnessError (+30 more)

### Community 62 - "RuntimeSettings"
Cohesion: 0.13
Nodes (5): RuntimeSettings, QdrantTimeouts, settings(), test_factory_sets_the_connect_timeout_and_disables_the_version_check(), live_client()

### Community 63 - "manifest.py"
Cohesion: 0.13
Nodes (11): build_security_repository(), _fixture_files(), split_frontmatter(), _StringDateLoader, compute_body_sha256(), sha256_hex(), check_integrity_hashes(), rewrite_document() (+3 more)

### Community 64 - "test_legacy_baseline_snapshot.py"
Cohesion: 0.12
Nodes (16): deterministic_clock(), clean_env(), _Factory, _FixedDatetime, _record_opens(), note(), wrap_func(), inner() (+8 more)

### Community 65 - "test_structure.py"
Cohesion: 0.13
Nodes (25): assert_matches_snapshot(), assert_structure_chunks_whitespace_fidelity(), chunks_to_records(), collapse_whitespace(), load_snapshot(), snapshot_for_document(), structure_chunker(), test_duplicate_sibling_headings_raise() (+17 more)

### Community 66 - "make eval-retrieval"
Cohesion: 0.13
Nodes (22): bm25 strategy, bm25 needs neither Qdrant nor the bge-m3 extra (Spec 008), config/retrieval.yaml schema 1.1 (default_strategy hybrid, qdrant.connect_timeout_s 2, query_timeout_s 3; 1.0 refused), D036 binding rules, dense strategy, --strategy dense needs no lexical file, Embedder pair from index_settings or dense_identity; fallback-only 2.2 file compares against Spec 007 bm25 file, eval-retrieval exit 0 or 2 (+14 more)

### Community 67 - "Spec 007 hybrid retrieval"
Cohesion: 0.10
Nodes (28): build_retriever, make eval-retrieval, make index-lexical, lexical package: lexical-v1 tokenizer, FTS5 store, builder, Known issue: BM25 statistics corpus-wide per file; needs per-scope files for roles, Known issue: legacy chillu sequence does not match atomic chillu in BM25, Known issue: evaluation-data gaps (ml goldens, relevant_section_ids empty), Known issue: g004 overlaps u001, keep_both (+20 more)

### Community 68 - "BM25Retriever"
Cohesion: 0.07
Nodes (38): 007 — Hybrid Retrieval Design, As-built notes, Data flow, Design summary, Interfaces / models, Observability, Package / file placement, R7 — Fusion and `HybridRetriever` (`retrieval/fusion.py`, `hybrid.py`) (+30 more)

### Community 69 - "ResolvedLote"
Cohesion: 0.08
Nodes (42): 010 — Multilingual Retrieval Design, Alternatives / deferred decisions, Applicability builders (R3), Components / boundaries, Data flow, Design summary, Error and failure behavior, Observability (+34 more)

### Community 70 - "embedder"
Cohesion: 0.11
Nodes (17): chunker, context_prefix, name, overlap_tokens, target_tokens, version, embedder, batch_size (+9 more)

### Community 71 - "Phase 1 RAG query pipeline"
Cohesion: 0.12
Nodes (16): Authorization model (guest/public), Small documents and chunking strategy, Citation strategy (backend-owned validation), FAQ-aware retrieval experiment, Graceful degradation, Hybrid retrieval (dense + BM25 + RRF), Production knowledge corpus, Poisoned public document fixture (+8 more)

### Community 72 - "load_retrieval_config"
Cohesion: 0.24
Nodes (14): load_retrieval_config(), test_build_retriever_converts_a_string_value_and_refuses_unknown(), test_build_retriever_maps_each_strategy(), test_committed_config_loads(), test_good_config_loads(), test_invalid_config_is_refused_naming_the_field(), test_lexical_strategies_need_the_lexical_index(), test_schema_11_reads_default_lexical_tokenizer() (+6 more)

### Community 73 - "Target repository shape (apps, packages, knowledge, sources, evaluation, tests, config, experiments, analytics, prompts, docs, infra)"
Cohesion: 0.17
Nodes (12): AccessContext(role, tenant_id) with blank tenant refused, Future agent folders intentionally not created, apps/api (FastAPI application layer), apps/web (Next.js/TypeScript frontend: recruiter assistant, RAG Lab, engineering views), core/access.py (Role, frozen AccessContext), guest_access, Knowledge model metadata (document_id, document_version, tenant_id, access_scope, lote_languages, content_language, source_authority...), No language filter, score threshold or reranking yet (+4 more)

### Community 74 - "test_manifest_validation.py"
Cohesion: 0.32
Nodes (18): load_schema(), metadata(), record(), run(), test_duplicate_document_id_rejected(), test_duplicate_document_version_rejected(), test_frontmatter_missing_required_field(), test_frontmatter_schema_violation_names_document_and_field() (+10 more)

### Community 75 - "Section: Next step"
Cohesion: 0.11
Nodes (17): Atomic publish and rollback, Phase 2 audit trail, AWS deployment architecture (ap-south-1), Controlled document-change workflow (Release Candidate), CI/CD pipeline, Evaluation governance states, Evaluation slices, Evaluation Suite (public-eval-v1) (+9 more)

### Community 76 - "doc22"
Cohesion: 0.27
Nodes (9): doc23(), run_cross(), test_2_3_against_2_2_one_chunk_passes_without_cross_index(), test_cli_exit_codes(), test_committed_baseline_compared_with_itself_passes(), test_cross_index_allows_index_fields(), test_cross_index_allows_lexical_digest_and_chunk_count(), test_cross_index_with_2_2_side_is_refused() (+1 more)

### Community 77 - "test_baseline.py"
Cohesion: 0.06
Nodes (46): case(), clean_env(), cli_run(), DeviceStub, _git(), run(), seeded(), setup() (+38 more)

### Community 78 - "embedder"
Cohesion: 0.14
Nodes (13): chunker, max_chunk_chars, name, version, embedder, batch_size, fake_vector_size, model_id (+5 more)

### Community 79 - "repositories/__init__.py"
Cohesion: 0.09
Nodes (20): normalize_body(), document_fields(), under_root(), check_manifest_documents(), compare_manifest_to_metadata(), date_problems(), describe_error(), load_manifest() (+12 more)

### Community 80 - "RetrievalConfigurationError"
Cohesion: 0.19
Nodes (11): ingestion_config_report(), declared_release_id(), load_suite(), test_declared_release(), test_filtering_in_temporary_suite(), test_invalid_line_names_file_and_line_only(), test_path_escaping_repo_root_refused(), test_real_suite_loads_every_golden_case_and_leaves_evaluation_unchanged() (+3 more)

### Community 81 - "FallbackReason"
Cohesion: 0.15
Nodes (16): FallbackReason, access(), Fallback, Primary, test_a_fallback_error_is_raised(), test_dense_leg_failure_on_one_query_leaves_the_others_hybrid(), test_every_reason_falls_back_with_the_same_access_and_top_k(), test_latency_includes_the_failed_attempt() (+8 more)

### Community 82 - "Ingestion pipeline (Spec 004)"
Cohesion: 0.09
Nodes (26): default_strategy, fusion, candidate_depth, k, method, weights, lexical, tokenizer (+18 more)

### Community 83 - "open_hybrid"
Cohesion: 0.17
Nodes (12): client_at(), closed_port(), open_hybrid(), run_cli(), stalled_port(), test_a_missing_extra_at_open_is_raised_not_a_fallback(), no_extra(), test_cli_explicit_dense_with_qdrant_down_exits_2() (+4 more)

### Community 84 - "retrieval/test_access.py"
Cohesion: 0.16
Nodes (15): clean_env(), guest(), payload(), _policy(), test_a_different_policy_changes_both_builders(), test_both_builders_cover_the_same_three_conditions(), test_check_hit_accepts_valid_payload(), test_check_hit_rejects_malformed_payload() (+7 more)

### Community 85 - "LexicalIndex"
Cohesion: 0.13
Nodes (13): Tokenizers (R5, R6), Implementation (user-owned runs + agent wrap-up), Review, Review, T5 — round 1, User decision, T3 — `lexical-v2`, tokenizer selection, script mix, `--cross-tokenizer`, continuity command, Verification (+5 more)

### Community 86 - "test_lexical_standalone.py"
Cohesion: 0.19
Nodes (18): build_from(), built(), copy_repository(), expected(), first_document_id(), open_it(), remove_document(), repo_at() (+10 more)

### Community 87 - "Backend stack"
Cohesion: 0.12
Nodes (20): Backend stack, Custom retrieval metrics (plain Python), DeepEval (not yet a dependency), Evaluation tooling, FastAPI, Generation/e2e metrics (correctness, faithfulness, citations, refusal), GitHub Actions, httpx (+12 more)

### Community 88 - "embedder"
Cohesion: 0.14
Nodes (13): chunker, max_chunk_chars, name, version, embedder, batch_size, fake_vector_size, model_id (+5 more)

### Community 89 - "D023 Task-gated agent workflow"
Cohesion: 0.12
Nodes (16): allowed_scopes, current_release, default_role, implemented_roles, allowed_scopes, allowed_scopes, roles, admin (+8 more)

### Community 90 - "test_status_handling.py"
Cohesion: 0.57
Nodes (4): golden_count(), suite_with_statuses(), test_exclusions_counted_by_status(), test_suggested_never_returned()

### Community 91 - "test_schemas.py"
Cohesion: 0.17
Nodes (6): load_schemas(), test_existing_schema_is_referenced_not_copied(), test_missing_schema_is_configuration_error(), test_per_type_required_field_enforced(), test_schema_files_are_valid_draft_2020_12(), test_valid_rows_pass()

### Community 92 - "Roadmap 13 - Graceful degradation"
Cohesion: 0.32
Nodes (8): Deferred serving concerns (circuit breaker, startup policy, Qdrant 5xx D062), Deduplication, context budgeting, evidence ordering, Dense to BM25 degradation, Roadmap 9 - Reranking + context building, Roadmap 13 - Graceful degradation, Qdrant failure to SQLite FTS5, Reranker failure to hybrid results, Spec 008 early delivery (D056)

### Community 93 - "pathlib"
Cohesion: 0.25
Nodes (9): apps/api, apps/web, CloudWatch, Future multimodal mock-test evaluation, Langfuse tracing, packages/core, packages/observability, packages/rag (+1 more)

### Community 94 - "Spec status table"
Cohesion: 0.10
Nodes (21): Completion: retrospective, Spec-Review commit, merge, verified status, Spec orchestrator loop (route, role subagents, user approval, merge), GET /health endpoint, make setup, packages core/rag/observability skeletons, task-gated spec skills and skills-sync, task State lifecycle and spec/NNN branches, uv workspace and uv.lock (+13 more)

### Community 95 - "test_eligibility.py"
Cohesion: 0.23
Nodes (15): eligible_ids(), make_document(), test_active_approved_public_document_is_eligible(), test_language_filter_narrows_eligible_documents_only(), test_language_metadata_does_not_broaden_access(), test_local_repository_applies_the_policy_query(), test_non_active_lifecycle_is_excluded(), test_non_approved_status_is_excluded() (+7 more)

### Community 96 - "ingest_dense"
Cohesion: 0.16
Nodes (13): build_production(), ingest_dense(), repository(), rewrite_settings(), test_bind_does_not_write_to_qdrant(), test_bind_refuses_chunk_set_mismatch_with_counts(), test_bind_refuses_identity_and_chunker_mismatch(), test_bind_refuses_when_qdrant_content_changed() (+5 more)

### Community 97 - "SpyIndex"
Cohesion: 0.21
Nodes (13): Admin content management, Agent capabilities only where they solve a real product problem, Audit trail, Basic analytics, Candidate evaluation, Change impact analysis, Evaluation Governance (keep/modify/deprecate/replace), Versioned Evaluation Suite (+5 more)

### Community 98 - "transcript_metrics.py"
Cohesion: 0.17
Nodes (12): analyse(), category(), command_kinds(), executed_text(), expand(), main(), parse_time(), render() (+4 more)

### Community 99 - "CURRENT_STATE.md"
Cohesion: 0.13
Nodes (14): interval, retries, start_period, test, timeout, container_name, healthcheck, image (+6 more)

### Community 101 - "read_result"
Cohesion: 0.13
Nodes (14): Implementation, T5 — round 1, User decision, NotComparableError, _build_run(), _mixed(), _num(), read_result() (+6 more)

### Community 102 - "AWS target"
Cohesion: 0.06
Nodes (39): Roadmap 11 - Observability, Langfuse traces, Stage latency, model/tokens/cost, release/config IDs, Full agent orchestration (avoided), Intentionally avoided choices, AWS target, Bedrock Agents / AgentCore for Phase 1 (avoided), Bedrock Knowledge Bases as core RAG (avoided) (+31 more)

### Community 103 - "make ingest"
Cohesion: 0.12
Nodes (18): docker compose up -d / down (local Qdrant), Environment: QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION_BASE, W2A_TENANT_ID, Fake embedder needs throwaway QDRANT_COLLECTION_BASE, make index-lexical, make ingest, INGEST_ARGS (--embedder {bge_m3,fake}, --config), ingest exit codes 0 success, 1 document failed, 2 refusal, Ingest summary lines (index:, added/updated/unchanged/deleted, ERROR lines) (+10 more)

### Community 104 - "Retrieval package (Spec 005 and 007)"
Cohesion: 0.14
Nodes (12): graphify skill pointer, spec/NNN branch and Spec-Task trailers, spec-implementer skill (one task per run), spec-orchestrator skill, spec-planner skill, spec-reviewer retrospective skill, Task-gated agent workflow loop, task-reviewer skill (read-only) (+4 more)

### Community 105 - "dedupe_documents"
Cohesion: 0.12
Nodes (21): Implementation, Implementation, Review, T6 — round 1, T6 — round 2, User decision, document_leg_ranks(), _leg_ranks_for() (+13 more)

### Community 106 - "Qdrant (vector database)"
Cohesion: 0.14
Nodes (13): Authorization metadata (access_scope, owner_user_id, tenant_id), Engineering Conventions, IDs and versions conventions, Knowledge files with provenance, Language metadata (content_language, lote_languages), Logging and tracing hygiene, Domain naming terms, Prompts as versioned assets (+5 more)

### Community 107 - "test_seed_corpus.py"
Cohesion: 0.48
Nodes (4): manifest_records(), seed_documents(), test_security_fixtures_are_not_in_the_production_corpus(), test_seed_ids_and_versions_are_unique()

### Community 108 - "D055 Default strategy is hybrid (Spec 007)"
Cohesion: 0.10
Nodes (23): make retrieval-baseline legacy frozen, RetrievalUnavailableError and availability classification, Known issue: git_dirty true in Spec 007 BM25/hybrid result files (user-accepted), Latency hybrid p50 80.3 ms p95 103.6 ms; bm25 p50 0.19 ms, BM25 metrics: 64/69 goldens, MRR 0.7082, Hybrid metrics: 68/69 goldens, MRR 0.9094, Retrieval misses g004 g026 g061, Next step 2: real BGE-M3 baseline committed (+15 more)

### Community 109 - "FakeEmbedder"
Cohesion: 0.13
Nodes (15): FakeEmbedder, _cosine_to_query(), _text_with_score_below(), __init__(), test_conforms_to_protocol(), test_declared_vector_size(), test_default_size_is_64(), test_fake_device_is_none() (+7 more)

### Community 110 - "RetrievalConfigurationError"
Cohesion: 0.11
Nodes (18): guest_access(), resolve_access(), _aggregate(), BaselineResult, check_output_free(), format_summary(), main(), _parser() (+10 more)

### Community 111 - "test_content_hash.py"
Cohesion: 0.15
Nodes (12): Approved packages, pricing and validity, Six approved packages and prices, 60-day package validity, 24-hour cancellation notice, Personal coaching package, 60-minute coaching session on Google Meet, Individual coaching and live appointments, Mock assessments, scoring, feedback and review windows (+4 more)

### Community 112 - "Spec 005 dense retrieval baseline"
Cohesion: 0.12
Nodes (25): AccessContext, Role, W2A_TENANT_ID, DenseIndex, build_access_filter, check_hit, DenseRetriever, make retrieve guest/public CLI, BGE-M3 device mps not pinned (D038), Spec 005 retrospective findings F3-F5, Spec 005 dense retrieval baseline, Spec 005 status: verified 2026-10-23 merged b33462e, AccessContext and Role (+17 more)

### Community 113 - "test_violation_names_the_document_from_the_error_attribute"
Cohesion: 0.18
Nodes (12): AGENTS.md Project Rules, DocumentRepository Abstraction, Evaluation Governance Rules, Language Separation Rules, Phase 1 Scope, Task-gated Spec Loop, CLAUDE.md Project Instructions, graphify Knowledge Graph Rules (+4 more)

### Community 114 - "test_lexical_build.py"
Cohesion: 0.21
Nodes (20): identity(), open_lexical(), payload(), synthetic_entries(), build(), test_atomic_replace_keeps_old_file_after_failure(), test_build_production_helper_runs(), test_build_records_settings() (+12 more)

### Community 115 - "AccessContext"
Cohesion: 0.13
Nodes (16): AccessContext, test_blank_tenant_refused(), test_empty_tenant_refused(), test_no_language_or_scope_fields(), test_roles_match_policy_file(), test_tenant_is_stripped(), test_unknown_role_refused(), test_valid_context_is_frozen() (+8 more)

### Community 116 - "fusion"
Cohesion: 0.20
Nodes (12): English, Malayalam and mixed queries, FAQ-aware retrieval/indexing, Roadmap 7 - Chunking experiments, Roadmap 8 - Multilingual retrieval, Language applicability handling, Parent-heading context and order-independent section_ids, Recursive chunking baseline, Optional semantic chunking (+4 more)

### Community 117 - "SQLite FTS5"
Cohesion: 0.11
Nodes (20): store.py (SQLite FTS5: chunks table, chunk_terms FTS5 table, settings row; LexicalIndex.open, bind_to, search), Local multilingual BGE reranker, BM25 via FTS5 bm25(), Derived local lexical file per collection, Device not pinned, recorded in results (D038), Embeddings, Deterministic fake embedder, Fusion (+12 more)

### Community 118 - "Target RAG query flow (User -> FastAPI -> validation -> AccessContext -> LanguageContext -> retrieval -> RRF -> reranker -> context builder -> answerability -> prompt -> Bedrock -> citation validation)"
Cohesion: 0.11
Nodes (24): Answerability / insufficient-evidence decision, Authorization applied inside each retriever before fusion, never after RRF, reranking or generation, Authorization filter is part of the Qdrant query so unauthorized points never leave the store, Amazon Bedrock generation, check_hit (fail-closed re-check, second line of defense), Citation validation, Context builder (planned), D035 Future fallbacks must take the same ResolvedAccess and call check_hit (+16 more)

### Community 119 - "EvaluationConfigurationError"
Cohesion: 0.09
Nodes (22): Implementation, EvaluationConfigurationError, CaseBase, CaseStatus, DatasetRef, GoldenCase, SecurityCase, SuiteManifest (+14 more)

### Community 120 - "failing_client"
Cohesion: 0.18
Nodes (10): content-hash-v1 (sole change-detection signal), LocalDocumentRepository, Document manifest and JSON Schema validation, make validate-knowledge, persona_scope spec defect (F2), BgeM3Embedder (optional extra, pinned revision), Embedder Protocol and FakeEmbedder, HeadingChunker and slugify rule (+2 more)

### Community 121 - "test_status_handling.py"
Cohesion: 0.20
Nodes (8): Adding a New Language Guide, language_registry.json, Public Assistant Content Boundaries, access_scope, content_language, Knowledge Schema and Metadata, language_scope, lote_languages

### Community 122 - "repositories/__init__.py"
Cohesion: 0.16
Nodes (7): DocumentNotFoundError, DocumentRepositoryError, DocumentValidationError, DuplicateDocumentError, ManifestValidationError, test_error_messages_name_document_and_field(), test_errors_share_base_class()

### Community 123 - "dense"
Cohesion: 0.12
Nodes (19): Components / boundaries, R10 — `eval-compare` identity rules (`compare.py`), R11 — Security gate (`security_index.py`, `security_eval.py`), R12 — Docker test, R1 — Suite v2, R4 — `make index-lexical` (`lexical/cli.py`), R8 — Strategy and config (`retrieval/strategy.py`, `config/retrieval.yaml`), R9 — Result format 2.1 (+11 more)

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

### Community 132 - "load_suite"
Cohesion: 0.31
Nodes (10): load_suite(), copy_suite(), test_access_context_is_loaded_but_ignored(), test_dataset_types_loaded_by_type(), test_escaping_path_refused(), test_extra_fields_tolerated(), test_malformed_line_names_file_and_line_only(), test_real_suite_loads_every_declared_case_and_is_read_only() (+2 more)

### Community 133 - "Vocabulary, flashcards and free access"
Cohesion: 0.29
Nodes (7): EligibilityPolicy / GUEST_PUBLIC_POLICY, Security fixtures (valid but ineligible), config/ingestion.yaml and RuntimeSettings, Ingestion pipeline (target vs current state diff), AccessContext and Role (core), resolve_access / ResolvedAccess, W2A_TENANT_ID server tenant setting

### Community 134 - ".search"
Cohesion: 0.25
Nodes (8): Phase 2 basic analytics, Assistant behavior rules, Product Context, English and Malayalam language scope, Future personas, Phase 1 guest-only scope, Way2Australia AI product, Source-of-truth priorities

### Community 135 - "git_state"
Cohesion: 0.29
Nodes (6): Implementation, Review, T9 — round 1, User decision, git_state(), _is_untracked_result()

### Community 136 - "Spec 002 document model and repository"
Cohesion: 0.16
Nodes (15): Pydantic document models and enums, EligibilityPolicy for guest/public, LocalDocumentRepository with manifest schema validation, make validate-knowledge, Spec 002 decisions made before approval (content_hash, fixtures, validate-knowledge), Seed data status: 13 public docs, evaluation datasets, security fixtures, Spec 002 retrospective findings F1-F6, Spec 002 document model and repository (+7 more)

### Community 137 - "lexical/ package (Spec 007)"
Cohesion: 0.20
Nodes (10): D060 Standalone lexical freshness, Standalone freshness proves lexical file matches repository, not live Qdrant (D060), lexical/cli.py (make index-lexical writes only git-ignored file), Lexical file is a derived artifact, one per collection, bound by identity and chunk digest, freshness.py (verify_fresh, chunk digest recomputed from repository), lexical/ package (Spec 007), tokenizer.py (lexical-v1), make index-lexical (+2 more)

### Community 138 - "Evaluation Framework Goal"
Cohesion: 0.39
Nodes (8): NAATI CCL test format, scoring and results, NAATI CCL test, Deduction-based assessment, Begin interpreting within five seconds of chime, NAATI, CCL is not professional interpreter certification, Pass requirement 63/90 overall and 29/45 per dialogue, Results within 4-6 weeks

### Community 139 - "test_lexical_tokenizer.py"
Cohesion: 0.09
Nodes (6): test_no_malayalam_specific_lote_languages_in_ingestion_code(), test_chillu_pairs_tokenize_the_same_inside_and_at_end(), test_golden_file_is_the_source_of_the_pins(), test_golden_queries_pin_exact_tokens(), test_module_has_no_language_code_literal(), test_unknown_tokenizer_is_refused()

### Community 140 - "Roadmap 12 - Security"
Cohesion: 0.13
Nodes (15): Answerability and insufficient-evidence response, Authorization regression and staff canary, Docker, Terraform, EC2, ECR, CloudWatch, IAM, Bedrock, Bedrock Runtime (roadmap), BGE-M3 (roadmap), Citation manipulation tests and input/cost limits, Backend-owned citation validation, Roadmap 4 - Dense retrieval baseline (+7 more)

### Community 141 - "BGE-M3 (initial embedding model)"
Cohesion: 0.38
Nodes (6): Evaluation Candidates File, Evaluation Package (evaluation/), Evaluation Suite and Case-type Schemas, validate-evaluation, T2 Schemas and validate-evaluation, T7 Candidates

### Community 142 - "Way2Australia AI Platform Master Implementation Plan"
Cohesion: 0.29
Nodes (7): eval-retrieval, Retrieval Result Document 2.0, Section-level Metrics, Slices and small_sample, Unanswerable Reporting, T3 Retrieval Runner, T4 Unanswerable Reporting

### Community 143 - "Retrieval fallback (Spec 008, D056-D062)"
Cohesion: 0.12
Nodes (19): bm25 builds no embedder and no Qdrant client, classify_model_error, classify_qdrant_error, D056-D062 fallback decisions, D057 Fallback eligibility classification, D058 Fallback policy per query, D061 Marking and evaluation of fallback, D062 5xx not eligible (+11 more)

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

### Community 149 - "IndexIdentity"
Cohesion: 0.07
Nodes (39): Decisions D056-D062, Spec 008 Retrieval Fallback Design, R8 — Result format 2.2 (`retrieval_eval.py`), Security gate five paths, result 1.2, T2: where the shared pieces live (2026-10-31), _UnavailableDense (harness-only fault injection), Repeated finding: graphify update ownership, Spec 008 Task Reviews (+31 more)

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
Cohesion: 0.05
Nodes (23): Acceptance criteria, AccessScope, ApprovalStatus, LanguageScope, LifecycleStatus, SourceAuthority, _canary_points(), Chunker (+15 more)

### Community 156 - "conftest.py"
Cohesion: 0.14
Nodes (15): Implementation, Implementation, Review, T3 — round 1, T3 — round 2, User decision, script_mix(), live_suite_rows() (+7 more)

### Community 157 - "LexicalIndexError"
Cohesion: 0.28
Nodes (5): Implementation, Interfaces / models, chunk_identity(), _insert(), LexicalIndexError

### Community 158 - "Orchestrator State Machine"
Cohesion: 0.50
Nodes (4): Mission, Phase 1 public/guest vs Phase 2 Knowledge Operations, Mission purpose: grounded multilingual RAG assistant, Useful product, engineering learning, portfolio evidence

### Community 159 - "way2australia_api/__init__.py"
Cohesion: 0.50
Nodes (3): Coaching is optional, Way2Australia public offering and assistant scope, English-Malayalam CCL preparation offering

### Community 160 - "Project Context README"
Cohesion: 0.50
Nodes (4): 120+ practice dialogues, Materials and dialogue practice, Recordings stay in browser, No automatic score in ordinary practice

### Community 161 - "Roadmap 3 - Ingestion baseline"
Cohesion: 0.67
Nodes (4): Content hashing, Idempotent ingestion, Roadmap 3 - Ingestion baseline, Preview indexing

### Community 167 - "api/__init__.py"
Cohesion: 0.67
Nodes (3): Frontend stack, Next.js, TypeScript

### Community 169 - "DocumentRepository Protocol (async)"
Cohesion: 0.33
Nodes (6): DocumentRepository Protocol (async), KnowledgeDocument model, Spec 002 retrospective round 1, Spec 002 task review log (T3-T9), Spec 002 Document model and repository (verified), Acceptance dry run on Spec 002 T3

### Community 170 - "tests/evaluation/__init__.py"
Cohesion: 0.67
Nodes (3): Canonical document metadata, Chunk metadata, Source authority precedence

### Community 191 - "continuity.py"
Cohesion: 0.17
Nodes (19): _chunker_text(), _case_keys(), compare_continuity(), _embedder_pair_from_doc(), _fmt_key(), _identity_refusals(), _info_lines(), _load_raw() (+11 more)

### Community 192 - "sync_agent_skills.py"
Cohesion: 0.31
Nodes (9): discover_skills(), expected_tree(), find_problems(), inject_frontmatter(), main(), managed_skills(), read_tree(), remove() (+1 more)

### Community 193 - "DocumentRepository"
Cohesion: 0.29
Nodes (7): Roadmap 2 - Document model + repository, KnowledgeDocument, Manifest/schema validation, S3DocumentRepository and external storage, Document manifest, DocumentRepository, LocalDocumentRepository

### Community 195 - "test_slices.py"
Cohesion: 0.17
Nodes (10): aggregate(), _mean(), slice_by(), source_authority_key(), row(), test_no_language_literal_in_evaluation_code(), test_real_registry_lists_en_and_the_active_product_language(), test_slice_keys_come_from_data_and_carry_n() (+2 more)

### Community 205 - "Spec 010 — task reviews"
Cohesion: 0.33
Nodes (5): Implementation, Spec 010 — task reviews, T2 — round 1, T4 — round 1, User decision

### Community 207 - "Way2Australia AI Platform Master Implementation Plan"
Cohesion: 0.33
Nodes (6): Way2Australia AI Platform Master Implementation Plan, Phase 1 Definition of Done, Phase 1 Scope (public/guest RAG), Recruiter / portfolio story, Project Mission, Seven-day Phase 1 execution plan

## Ambiguous Edges - Review These
- `Task-gated agent workflow loop` → `graphify skill pointer`  [AMBIGUOUS]
  .claude/CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **380 isolated node(s):** `way2australia-api`, `way2australia-core`, `way2australia-observability`, `way2australia-rag`, `way2australia` (+375 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1406 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **33 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Retrieval (dense baseline Spec 005, hybrid Spec 007, fallback Spec 008)` connect `008 — Retrieval Fallback Requirements` to `Target repository shape (apps, packages, knowledge, sources, evaluation, tests, config, experiments, analytics, prompts, docs, infra)`, `lexical/ package (Spec 007)`, `Retrieval fallback (Spec 008, D056-D062)`, `Ingestion (Phase 1 baseline, Spec 004)`, `Target RAG query flow (User -> FastAPI -> validation -> AccessContext -> LanguageContext -> retrieval -> RRF -> reranker -> context builder -> answerability -> prompt -> Bedrock -> citation validation)`, `retrieval_eval.py`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Are the 85 inferred relationships involving `DenseIndex` (e.g. with `Design summary` and `Decisions resolved before drafting`) actually correct?**
  _`DenseIndex` has 85 INFERRED edges - model-reasoned connections that need verification._
- **What connects `way2australia-api`, `way2australia-core`, `way2australia-observability` to the rest of the system?**
  _380 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_compare.py` be split into smaller, more focused modules?**
  _Cohesion score 0.132486388384755 - nodes in this community are weakly interconnected._
- **Why does `Change log` connect `BM25Retriever` to `ResolvedAccess`, `git_state`, `D055 Default strategy is hybrid (Spec 007)`, `compare.py`, `test_lexical_cli.py`, `LocalDocumentRepository`, `DenseRetriever`, `007 — Hybrid Retrieval Requirements`, `LexicalIndex`, `security_eval.py`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **Are the 36 inferred relationships involving `LocalDocumentRepository` (e.g. with `Dependencies` and `Design summary`) actually correct?**
  _`LocalDocumentRepository` has 36 INFERRED edges - model-reasoned connections that need verification._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Task-gated agent workflow loop` and `graphify skill pointer`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._