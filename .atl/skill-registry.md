# Skill Registry

**Delegator use only.** Any agent that launches sub-agents reads this registry to resolve compact rules, then injects them directly into sub-agent prompts. Sub-agents do NOT read this registry or individual SKILL.md files.

See `_shared/skill-resolver.md` for the full resolution protocol.

## User Skills

| Trigger | Skill | Path |
|---------|-------|------|
| When user asks to create, build, or generate a knowledge base for a project, document a project from source documents (.txt, .docx, .pdf), or asks to "armar base de conocimiento" / "crear KB" / "documentar proyecto" | kb-creator | /home/joaquin/.gemini/config/skills/kb-creator/SKILL.md |
| When user asks to create, build, regenerate, or update CHANGES.md, roadmap, change map, implementation plan; or says "armar CHANGES", "armar roadmap", "crear mapa de changes", "generar plan de implementación", "qué changes necesito", "índice de changes" | roadmap-generator | /home/joaquin/.gemini/config/skills/roadmap-generator/SKILL.md |
| When user asks "how do I do X", "find a skill for X", "is there a skill that can...", or looks for installable skills | find-skills | /home/joaquin/.gemini/config/skills/find-skill/SKILL.md |
| When user asks to create/generate/update AGENTS.md or CLAUDE.md, "armar las reglas del proyecto", "instrucciones para los agentes", "generar claude.md", or after running kb-creator + roadmap-generator | agents-md-generator | /home/joaquin/.gemini/config/skills/agent-instruction/SKILL.md |
| /active-orchestrator:init, /active-orchestrator:kb, /active-orchestrator:design, /active-orchestrator:rules, /active-orchestrator:discovery, /active-orchestrator:openspec, /active-orchestrator:devops, /active-orchestrator:find-skill — or when user wants to start a new project from scratch using SDD/OpenSpec foundation flow | active-orchestrator | /home/joaquin/.gemini/config/skills/active-orchestrator/SKILL.md |

## Compact Rules

Pre-digested rules per skill. Delegators copy matching blocks into sub-agent prompts as `## Project Standards (auto-resolved)`.

### kb-creator
- Output MUST be placed in `knowledge-base/` at project root, never inside `docs/`
- Always create the 10 canonical files (`01_vision_y_objetivos.md` to `10_preguntas_abiertas.md`) plus `README.md`
- Mode A (silent): triggers if `docs/` has source files; reads sources and generates all files without asking questions
- Mode B (interactive): triggers if `docs/` is absent/empty; asks 3-5 strategic discovery questions before generating
- Extra domains use prefix `1X_` or `2X_` and never replace the 10 canonical files
- In orchestrated runs (`.active-orchestrator-state.json` exists), update only `state.kb` (`source`, `discovery`, `files`)
- Never touch `step`, `owner`, `roadmap`, `skills`, or `agents` in state

### roadmap-generator
- Output MUST be a single file `CHANGES.md` at project root, never inside `openspec/`
- Pre-checks: verify `knowledge-base/` exists with all 10 canonical files and `openspec/` is initialized before running
- Follow strict section structure: Cómo usar, Árbol de dependencias, Paralelismo por fase (GATES), Camino crítico, Plan con 3 agentes, Fases
- Changes must be named with 2-digit sequential codes `C-01`, `C-02`, etc. in kebab-case
- Infer dependencies: infra first (C-01), core models second, auth before protected resources, referenced before referencing entities
- Each change must specify: Estado, Scope (dense operational bullets), Dependencias, Governance (BAJO/MEDIO/ALTO/CRITICO), Leer antes (3-5 KB files)
- In orchestrated runs, update only `state.roadmap` (`created_by`, `source`, `changes` list); do not mutate `step`

### find-skills
- Search open skills ecosystem using `npx skills find [query]` or inspect the skills.sh leaderboard first
- Verify quality before recommending: prefer >= 1,000 installs and reputable official authors
- In orchestrated workflows, run in RECOMMEND-ONLY mode: write `state.skills.recommended` and leave `installed: []`
- NEVER install skills autonomously with `-y` without explicit user selection and confirmation
- Global installs require `-g` flag: `npx skills add <repo> --skill <name> -g`
- Present recommendations with: skill name, install count, source repo, and rationale for matching

### agents-md-generator
- Generate identical project instructions in both `AGENTS.md` and `CLAUDE.md` at the project root
- Pre-checks: require `knowledge-base/` and `02_descripcion_general.md` to exist before generation
- Read stack from KB 02, roadmap from `CHANGES.md`, and available skills from `.atl/skill-registry.md`
- NEVER duplicate universal rules from `~/.claude/CLAUDE.md`; inherit them and reference the global file
- Hard rules must be stack-aware (derived from actual project technologies: Go, Python, React, etc.)
- Confirm candidate hard rules interactively with the user before writing
- Map detected skills to agent roles (Backend Core, Backend Aux, Frontend, Orchestration) without duplicating compact rules

### active-orchestrator
- Thin orchestrator role: manage state file `.active-orchestrator-state.json` and own ONLY `step`, `version`, and `owner`
- Dispatch foundation phases strictly in sequence: [discovery-research] -> kb-creator -> design-system -> roadmap-generator -> find-skill -> skill-registry -> agent-instruction
- Hold an inter-phase checkpoint at EVERY phase boundary; never advance `step` without user confirmation
- Interactive phases (`kb-creator`, `design-system`, `agent-instruction`) run inline (`Skill`); mechanical phases delegate to subagents (`Agent`)
- Never ask strategic discovery content questions (system_type, scale, stack) — those belong exclusively to `kb-creator`
- Never install skills autonomously; present recommendations and wait for user selection
- Check sub-skill presence before dispatch; offer install or mark skipped in state if declined

## Project Conventions

| File | Path | Notes |
|------|------|-------|
| *(none)* | — | No convention files found yet (AGENTS.md/CLAUDE.md will be created in Phase 5) |

Read the convention files listed above for project-specific patterns and rules. All referenced paths have been extracted — no need to read index files to discover more.
