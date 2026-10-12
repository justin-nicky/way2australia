# Product Context

## Product

Way2Australia AI is an AI support and learning assistant for Way2Australia's NAATI CCL preparation platform.

The current product supports English–Malayalam preparation through:
- practice dialogues;
- vocabulary;
- preparation materials;
- coaching;
- mock assessments;
- public support / FAQ information.

The assistant should answer from approved sources, cite those sources, refuse unsupported questions, and behave safely when evidence is insufficient.

## Phase 1 scope

Phase 1 implements a **public/guest assistant only**.

The assistant may answer from:
- approved Way2Australia public business knowledge;
- approved public learning samples;
- current official NAATI knowledge;
- current Home Affairs information where relevant.

Current runtime authorization:
- role: `guest`;
- allowed scope: `public`.

No staff/subscriber/private-user login or data retrieval is implemented in Phase 1.

## Language scope

Initial active languages:
- English;
- Malayalam.

The platform must support future CCL languages without redesigning the core RAG pipeline.

Language support should be driven by:
- configuration;
- knowledge metadata;
- evaluation coverage.

Do not build a separate RAG system per language.

## Product behavior

The assistant should:
- answer using approved evidence;
- distinguish Way2Australia policy from official NAATI rules;
- return citations to approved sources;
- answer naturally in the visitor's language where practical;
- ask for clarification when materially ambiguous;
- refuse or redirect when evidence is insufficient;
- avoid guarantees about pass results, migration outcomes, scores, or preparation timeframes;
- avoid exposing paid/private material;
- avoid claiming account actions were performed.

## Source-of-truth priorities

Business information:
1. owner-approved Way2Australia knowledge;
2. current Way2Australia public website;
3. older snapshots only for supplementary/reference use.

Official CCL information:
1. current NAATI sources.

Migration / visa eligibility:
1. Australian Department of Home Affairs.

## Future personas

The architecture should support later:
- guest/public;
- staff;
- subscriber;
- registered user/private content;
- admin.

These are future capabilities, not Phase 1 features.

## Phase 2 direction

### Knowledge Operations
- admin document management;
- versioned documents;
- S3-backed source storage;
- metadata database;
- Knowledge Release Candidates;
- document diffing and impact analysis;
- evaluation governance;
- LLM-generated evaluation suggestions for admin review;
- preview indexing;
- human approval;
- atomic publish/rollback;
- audit trail.

### Basic analytics
Potential future analytics:
- most common question categories;
- unsupported-question rate;
- language demand;
- knowledge gaps;
- retrieval failure / empty retrieval rate;
- refusal rate;
- fallback usage;
- latency/cost trends;
- release-level comparison.

No analytics pipeline or dashboard is required in Phase 1.
