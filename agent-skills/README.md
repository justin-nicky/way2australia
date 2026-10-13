# Agent Skills (canonical source)

This folder is the single editable source for the project's spec-driven development skills:

| Skill | Role | Intended tier | Invocation |
|---|---|---|---|
| `spec-planner` | Create or revise one spec with staged, recorded approvals | BEST | may auto-trigger |
| `spec-implementer` | Implement one approved spec, leave it pending review | BEST_MINUS_ONE | explicit only |
| `spec-reviewer` | Independent review, writes `review.md`, PASS/FAIL | BEST | explicit only, isolated context |

The lifecycle they follow (`Status:` lines, `review.md`, remediation rounds) is defined in `docs/project/WORKFLOW.md` → "Spec status".

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

- **Claude Code:** `scripts/sync_agent_skills.py` injects them into `.claude/skills` only.
  - `spec-implementer`: `disable-model-invocation: true`, `argument-hint`.
  - `spec-reviewer`: `disable-model-invocation: true`, `argument-hint`, `context: fork`, `background: false` (fresh context, no implementer history).
- **Codex:** `agents/openai.yaml` in a skill folder sets `allow_implicit_invocation: false` (implementer, reviewer).

## Using the skills per tool

- **Claude Code:** `/spec-planner <topic>`, `/spec-implementer <NNN-spec>`, `/spec-reviewer <NNN-spec>`. Choose the model with `/model` before invoking the planner or implementer. The reviewer runs as a forked subagent.
- **Codex:** `$spec-planner`, `$spec-implementer <NNN-spec>`, `$spec-reviewer <NNN-spec>` (or `/skills`). Run the reviewer in a new session.
- **Kiro:** `/spec-planner`, `/spec-implementer`, `/spec-reviewer`. Start planning from a Vibe session. **Do not use Quick Spec** or auto-generated specs: they skip the approval gates. Prefer `/spec-implementer` over "Run all tasks". Do not edit `tasks.meta.json`. Custom Kiro agents need `skill://.kiro/skills/*/SKILL.md` in `resources`.

## Model tiers

See [MODEL_PREFERENCES.md](MODEL_PREFERENCES.md).
