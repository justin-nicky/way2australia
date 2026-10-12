# Engineering Conventions

## Python

Prefer:
- explicit type hints;
- Pydantic models at external/data boundaries;
- `Protocol` for replaceable components;
- async APIs where I/O is genuinely asynchronous;
- small modules with clear responsibility;
- dependency injection rather than global mutable state.

Avoid:
- hidden global state;
- large framework abstractions that hide retrieval/evaluation behavior;
- direct filesystem/Qdrant/Bedrock calls scattered through route handlers.

## Naming

Use consistent domain terms:

- `KnowledgeDocument`
- `DocumentRepository`
- `LocalDocumentRepository`
- `AccessContext`
- `LanguageContext`
- `RetrievedChunk`
- `EvaluationCase`
- `EvaluationSuite`
- `KnowledgeRelease`
- `KnowledgeReleaseCandidate` (Phase 2)

## IDs and versions

Stable IDs do not change when content changes:
- `document_id`;
- `case_id`.

Version fields increment when approved assets change:
- `document_version`;
- `case_version`;
- `evaluation_suite_version`.

Chunk IDs are derived and must not become stable business/evaluation identity.

## Authorization metadata

Preferred concepts:
- `access_scope`;
- `owner_user_id`;
- `tenant_id`.

Do not encode authorization through:
- filenames;
- directories only;
- language;
- prompt instructions.

## Language metadata

Keep separate:
- `content_language`;
- `language_scope`;
- `lote_languages`;
- query language.

Current active LOTE:
- Malayalam: `ml`.

Global knowledge:
- `lote_languages: ["*"]`.

## Knowledge files

Normalized knowledge should be human-reviewable and machine-readable.

Markdown + frontmatter is acceptable for Phase 1.

Knowledge should retain:
- provenance;
- authority;
- approval status;
- review date;
- version information.

Raw sources are preserved separately and are not automatically production knowledge.

## Evaluation

Evaluation cases should record:
- stable case ID;
- version;
- status;
- query;
- expected behavior/facts;
- relevant stable document/section IDs;
- language/category metadata.

LLM-generated suggestions are not active cases until human review/approval.

## Prompts

Prompts are versioned application assets under `prompts/`.

Do not store:
- secrets;
- private customer data;
- credentials;
- security boundaries that depend only on prompt secrecy.

## Logging / tracing

Do not indiscriminately log:
- secrets;
- private content;
- full raw context;
- credentials.

Prefer trace metadata:
- IDs;
- versions;
- scores;
- timings;
- decisions;
- fallback status.

## Tests

Prefer:
- deterministic unit tests for core behavior;
- integration tests for boundaries;
- explicit security regression tests;
- evaluation datasets for RAG quality.

Security fixtures must be clearly synthetic and isolated from production indexing.
