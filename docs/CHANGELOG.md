# Changelog

All notable changes to the Video Generation System will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/).

---

## [Unreleased]

### Phase 1 — Foundation & MVP

#### Added
- Galileo observability integration with `GalileoCallback` for agentic flow tracing and evaluation metrics
- Render concurrency support in the Remotion service (using all available CPU cores)
- Premium spring animation presets across `default`, `vibrant`, and `dark-tech` themes
- Root workspace metadata: `package.json`, `pnpm-workspace.yaml`
- Python package scaffold: `agents/pyproject.toml`
- Environment template: `agents/.env.example`
- Repository ignore rules: `.gitignore`
- Shared theme presets in `shared/themes/`
- Backend source package in `agents/video_gen_agents/`
- FastAPI app with `/health`, `/api/themes`, and `/api/generate`
- LangGraph pipeline for brief → plan → script → design → motion → audio stub → IR → verification
- Pydantic IR validation and shared theme loading
- Backend tests in `agents/tests/`
- Remotion renderer package in `remotion/`
- TypeScript Zod IR schema and renderer-side types in `remotion/src/types.ts`
- Generic Remotion scene and element rendering for the current backend output
- Backend Remotion render integration in `agents/video_gen_agents/rendering.py`
- Sample MP4 render in `remotion/out/sample.mp4`
- SQLite persistence layer in `agents/video_gen_agents/database.py`
- FFmpeg post-processing service in `agents/video_gen_agents/ffmpeg.py`
- Project listing/detail API endpoints backed by SQLite
- Dashboard package in `dashboard/` with a Vite + React project inspection UI
- Backend media mounts for render and IR artifacts
- CORS support for local dashboard development
- Async project launch endpoint and project WebSocket stream
- Replayable in-memory progress broker for live project updates
- Dashboard stage graph and live activity feed driven by WebSocket events
- Project documentation suite:
  - `ARCHITECTURE.md` — System topology, data flow, component boundaries
  - `IR_SPEC.md` — Complete Video IR schema specification
  - `AGENTS.md` — All 7 agent specifications with I/O schemas
  - `ROADMAP.md` — Phased product roadmap
  - `TECH_STACK.md` — Technology choices and rationale
  - `DECISIONS.md` — Architecture Decision Records (ADRs)
  - `CONSIDERATIONS.md` — Risks, limitations, and technical debt tracking
  - `STATUS.md` — Current implementation status dashboard
  - `CHANGELOG.md` — This file
  - `IMPLEMENTATION_LOG.md` — Dated record of what has actually landed in the repo

#### Changed
- `README.md` now distinguishes present packages from planned packages and points to the tracking docs
- `README.md` now includes the dashboard bootstrap alongside the renderer and API startup flow
- `ROADMAP.md` now marks WebSocket progress and the dashboard stage graph as implemented in the current Phase 1 baseline
- `STATUS.md` now tracks the async launch path, project WebSocket endpoint, and the implemented DAG/live activity UI
- `IMPLEMENTATION_LOG.md` now records the live progress milestone alongside the persistence, post-processing, and dashboard milestones

#### Not Yet Implemented
- [ ] Real LLM-backed agent execution
- [ ] Project update/delete flows
- [ ] Shared cross-package IR schema source of truth
- [ ] Automated end-to-end pipeline/browser test

---

### Phase 2 — Parallelization & Self-Correction ✅

#### Added
- Resilient LLM Router with Cerebras (primary) + Groq (fallback) and 429 retry logic
- Provider-specific semaphores: 3 concurrent for Cerebras, 1 for Groq
- Native async LangGraph pipeline using `asyncio.gather` for scene parallelization
- Healer Agent for automatic JSON schema error correction
- Langfuse integration for distributed tracing and session tracking
- 5 narrative archetypes with copy templates in `archetypes.py`
- 8 layout templates in `layouts.py` (centered_hero, split_layout, feature_showcase, stat_showcase, icon_grid, cta_card, quote, timeline_steps)
- Per-scene Design and Motion agent calls with LLM healing loop

#### Changed
- `pipeline.py` refactored to process Designer and Motion nodes concurrently
- `llm.py` extended with `build_resilient_model()` and semaphore management

---

### Phase 3 — Motion Intelligence, SVG Components & Scene Templates 🚧

> Plan: [PLAN_V3.md](./PLAN_V3.md)

#### Added (Planned)
- WS1: Extended easing library (ease-out-back, expo, cubic) in `animations.ts`
- WS1: Ambient float motion in `ElementRenderer.tsx`
- WS1: Stagger group auto-delay for cascading element entries
- WS2: 4 new scene templates (card_stack, terminal_demo, list_reveal, connection_graph) in `layouts.py`
- WS3: `svg-path` element type with stroke draw-on via `@remotion/paths` `evolvePath()`
- WS3: `svg-icon` element type with 12 built-in icons in `SvgRenderer.tsx`
- WS4: Enriched Designer and Motion agent prompts with full animation vocabulary
- WS5: `warm-clay.json` theme matching reference video aesthetic

#### Analysis & Research (Completed)
- Frame-by-frame reference video breakdown of @GregIsenberg's YouTube Short
- Identified 6 animation primitives and 7 scene patterns used in professional educational shorts
- Motion design audit comparing current engine capabilities vs reference quality
- Confirmed `@remotion/paths` `evolvePath()` for SVG draw-on animation

## Changelog Convention

### Categories
- **Added** — New features or files
- **Changed** — Changes to existing functionality
- **Deprecated** — Features that will be removed in future
- **Removed** — Features that have been removed
- **Fixed** — Bug fixes
- **Security** — Vulnerability patches
- **Performance** — Speed or resource improvements

### Version Scheme
- Pre-release versions follow `0.x.y` where:
  - `0.1.0` = Phase 1 MVP complete
  - `0.2.0` = Phase 2 (audio) complete
  - `0.3.0` = Phase 3 (canvas) complete
  - `1.0.0` = Production-ready release
