# Agent Skills (canonical source)

This folder is the single editable source for the project's spec-driven development skills. Together they run the task-gated loop defined in `docs/project/WORKFLOW.md`:

```text
spec-planner → spec-orchestrator → spec-implementer (one task) → task-reviewer → user approval
                     ↑___________________ repeat per task ___________________|
all tasks approved → [optional] spec-reviewer → orchestrator merges spec/<NNN> into main
```

| Skill | Role | Intended tier | Invocation |
|---|---|---|---|
| `spec-orchestrator` | Reads repository state, starts the next role, records user decisions, pushes and merges | BEST_MINUS_ONE | explicit only |
| `spec-planner` | Create or revise one spec with staged, recorded approvals | BEST | may auto-trigger |
| `spec-implementer` | Implement one task on `spec/<NNN>`, then stop | BEST_MINUS_ONE | explicit only |
| `task-reviewer` | Verify one task, PASS/FAIL, user summary (read-only for code and specs) | BEST | explicit only |
| `spec-reviewer` | Optional end-of-spec retrospective, writes `review.md` | BEST | explicit only |

Each role runs in a fresh session and hands off through repository files (`tasks.md` states, `task-reviews.md`, `Spec-Task` commit trailers), not chat. Lifecycle, states, branching and file formats are in `docs/project/WORKFLOW.md`.

## Editing and syncing

Edit only this folder, then run:

```bash
make skills-sync    # regenerate the tool-specific mirrors
make skills-check   # fail if any mirror differs (part of make verify)
```

Mirrors (generated, committed, never edited by hand):

| Tool | Location | Notes |
|---|---|---|
| Claude Code | `.claude/skills/` | Sync adds Claude-only frontmatter (see below). |
| OpenAI Codex | `.agents/skills/` | Documented repo-scope location. Do not also keep `.codex/skills/`: Codex would list each skill twice. |
| Kiro | `.kiro/skills/` | Workspace skills; shown as slash commands. |

Canonical `SKILL.md` frontmatter contains only portable Agent Skills fields (`name`, `description`). Host-specific additions:

- **Claude Code:** `scripts/sync_agent_skills.py` injects `disable-model-invocation: true` and an `argument-hint` into `.claude/skills` for the orchestrator, implementer, task reviewer and spec reviewer. No skill is forked and none pins a model; independence comes from starting the reviewer in a fresh session.
- **Codex:** `agents/openai.yaml` in a skill folder sets `allow_implicit_invocation: false` (orchestrator, implementer, task reviewer, spec reviewer).

## Using the skills per tool

- **Claude Code:** `/spec-orchestrator [NNN-spec]` is the usual entry point. Directly: `/spec-planner <topic>`, `/spec-implementer <NNN-spec> [task-id]`, `/task-reviewer <NNN-spec> <task-id>`, `/spec-reviewer <NNN-spec>`. In the desktop app the orchestrator starts each role in a fresh session on its tier's model; elsewhere pick the model with `/model` when starting the session.
- **Codex:** `$spec-orchestrator`, `$spec-planner`, `$spec-implementer <NNN-spec> [task-id]`, `$task-reviewer <NNN-spec> <task-id>`, `$spec-reviewer <NNN-spec>` (or `/skills`). Run each role in a new session.
- **Kiro:** `/spec-orchestrator`, `/spec-planner`, `/spec-implementer`, `/task-reviewer`, `/spec-reviewer`. Start planning from a Vibe session. **Do not use Quick Spec** or auto-generated specs: they skip the approval gates. Prefer `/spec-implementer` over "Run all tasks". Do not edit `tasks.meta.json`. Custom Kiro agents need `skill://.kiro/skills/*/SKILL.md` in `resources`.

Hosts that cannot start sessions: the orchestrator prints the exact command and intended model (e.g. `New session on Sonnet: /spec-implementer 002 T3`); run it by hand.

## Model tiers

See [MODEL_PREFERENCES.md](MODEL_PREFERENCES.md). Tiers are advisory and applied when a session starts.
