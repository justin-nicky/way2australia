@AGENTS.md
@docs/project/CURRENT_STATE.md

Other canonical project context is read on demand, not auto-loaded: `docs/project/MISSION.md`, `CONSTITUTION.md`, `TECH_STACK.md`, `ROADMAP.md`, `DECISIONS.md`, `PRODUCT.md`, `ARCHITECTURE.md`, `WORKFLOW.md`, `CONVENTIONS.md`, `COMMANDS.md`, and the active spec under `.kiro/specs/`. Each spec skill lists what its role must read.

Cursor does not process the `@` imports above; it uses `.cursor/rules/project.mdc` (D063).

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- When graphify-out/graph.json exists and you need to find code you have not been pointed to, start with `graphify query "<question>"` before grepping or reading source files. When a task, brief or earlier read already names the files, read them directly. Subagent prompts may include this advice; it is not required (D080). Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- In the spec workflow, `spec-orchestrator` runs `graphify update .` once per spec, before the retrospective (D080); implementers do not run it per task. Outside the spec workflow, run `graphify update .` after modifying code (AST-only, no API cost).
- A committed graphify-out/graph.json is rewritten whole on every build, so a large diff to it in a pull request is expected. Do not flag it as churn or suggest skipping the graph rebuild or its hooks.
