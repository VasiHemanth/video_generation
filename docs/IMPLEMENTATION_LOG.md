# Implementation Log

This document is the dated ledger of what has actually landed in the repository.

Use it alongside:
- `docs/STATUS.md` for the current checklist
- `docs/CHANGELOG.md` for milestone-level summaries

## Update Rules

1. Add a new dated entry whenever code, scaffolding, or shared assets land in the repo.
2. Keep entries factual: what was added, what changed, and what is still missing.
3. Reference concrete files or directories when possible.
4. Do not log planned work here unless it has already been committed or created locally.

### 2026-03-30

**Phase 3 SVG Components, Groq Migration, and Flexbox Engine**

Added/Modified:
- Replaced Cerebras LangGraph fallback setup with exclusively Groq LLM model endpoints.
- Implemented Phase 3 animation features (spring, staggering, extended easing metrics).
- Added `group` elements with recursive Flexbox rendering support in `ElementRenderer.tsx`.
- Updated `random.html` to mimic a recursive layout parser.

**Phase 4: Canvas, Deterministic Edits & Scale — Initial Sprint**

Added:
- `agents/video_gen_agents/ir_mutations.py` — Deterministic IR patch engine with 6 op types (`set_theme_color`, `set_scene_duration`, `reorder_scenes`, `set_element_prop`, `set_aspect_ratio`, `swap_theme`). All ops are immutable — they return a new IR without mutating the original.
- `agents/video_gen_agents/export_presets.py` — Platform export preset system. Defines 6 platform configurations (YouTube Shorts, YouTube Long, Instagram Reels, TikTok, LinkedIn, Twitter) and generates the IR patch ops needed to conform a project to that platform's aspect ratio and duration cap.
- `agents/video_gen_agents/api/main.py` — 4 new REST endpoints: `PATCH /api/projects/{id}/ir`, `POST /api/projects/{id}/re-render`, `GET /api/export/presets`, `POST /api/projects/{id}/export/{platform}`.
- `agents/video_gen_agents/rendering.py` — `extract_verification_frames()` extracts one representative frame per scene (at 25% into each scene) using FFmpeg `-ss`. Called non-fatally after every render.
- `dashboard/src/components/TimelinePanel.tsx` — Horizontal filmstrip scene editor with native HTML5 drag-and-drop reordering, inline duration editing (calls `PATCH /ir`), and a Re-render button (calls `POST /re-render`). Wired into `App.tsx`.
- `dashboard/src/styles.css` — Timeline Panel styles (filmstrip, draggable cards, role color pills, duration badge, drag-over highlight).

Modified:
- `agents/video_gen_agents/pipeline.py` (_verify_node) — Added Vision Verifier: uses `ffprobe` to check rendered output dimensions against `meta.width × meta.height`. Non-fatal — verification warnings don't block the pipeline.
- `docs/ROADMAP.md` — Phase 3 marked ✅, Phase 4 marked 🚧 with the implemented items listed.
- `dashboard/src/types.ts` — Exported `Scene` as a standalone type (previously inlined in `ProjectIR`).

Tests:
- `agents/tests/test_ir_mutations.py` — 12 tests covering all 6 ops and chained multi-op patterns. All 12 pass.


### 2026-03-23

**Galileo Integration for Agentic Flow Tracing**

Added:
- `galileo` package to `agents/pyproject.toml`
- `galileo_api_key` to `Settings` in `agents/video_gen_agents/config.py`
- Galileo initialization and callback provider in `agents/video_gen_agents/llm.py`
- `GalileoCallback` integration in `agents/video_gen_agents/pipeline.py`

### 2026-03-20

**Live progress streaming and dashboard stage graph implemented**

Added:
- `agents/video_gen_agents/progress.py` with an in-memory progress broker and replayable per-project event history
- Async project launch path:
  - `POST /api/projects`
  - `/ws/projects/{project_id}`
- Per-stage progress events emitted from the deterministic LangGraph pipeline
- Dashboard live pipeline view:
  - WebSocket client
  - stage cards / DAG-style flow
  - live activity feed for project events

Behavior now available:
- Projects can be launched in the background without blocking the dashboard form
- The dashboard can connect to a project WebSocket immediately and receive backlog + live stage updates
- Backend tests now cover the async launch/WebSocket flow in addition to the existing sync API path

Still missing:
- Real LLM-backed agent execution
- Update/delete project flows
- Shared cross-package IR schema source of truth
- Automated end-to-end pipeline/browser smoke test

### 2026-03-20

**Baseline verified**

Implemented in repo:
- Root workspace metadata: `package.json`, `pnpm-workspace.yaml`
- Python package scaffold: `agents/pyproject.toml`
- Environment template: `agents/.env.example`
- Repository ignore rules: `.gitignore`
- Shared theme presets: `shared/themes/default.json`, `shared/themes/dark-tech.json`, `shared/themes/vibrant.json`
- Full documentation suite under `docs/`

Not implemented yet:
- `remotion/` project scaffold
- `dashboard/` project scaffold
- FastAPI application source
- LangGraph state, agents, and orchestration graph
- IR models and validation layer
- SQLite models and services
- Rendering and FFmpeg integration
- Automated tests

Next expected log entries:
- IR schema implementation in Python and TypeScript
- First runnable FastAPI/LangGraph backend scaffold
- Remotion package bootstrap
- Dashboard package bootstrap

### 2026-03-20

**Backend foundation implemented**

Added:
- Python package source under `agents/video_gen_agents/`
- Typed Pydantic models for the IR, planning artifacts, verification artifacts, and API payloads
- Theme loader that reads shared presets from `shared/themes/`
- Sequential LangGraph pipeline for manager, script, design, motion, audio stub, renderer, and verifier stages
- FastAPI app with `/health`, `/api/themes`, and `/api/generate`
- Backend tests under `agents/tests/`

Behavior now available:
- A brief can be transformed into a validated `ProjectIR`
- The renderer stage writes IR JSON to `agents/data/ir/<project_id>.json`
- The verifier reports the current limitation that rendering stops at IR assembly until Remotion and FFmpeg are scaffolded

Still missing:
- TypeScript IR types
- Real LLM-backed prompt execution in agent nodes
- SQLite persistence and project CRUD
- WebSocket progress streaming
- Remotion renderer and FFmpeg post-processing
- Dashboard

### 2026-03-20

**Remotion renderer and MP4 output implemented**

Added:
- `remotion/` package with Remotion CLI dependencies, TypeScript config, typed IR schema, sample composition, and generic scene/element rendering
- `agents/video_gen_agents/rendering.py` to invoke Remotion from the Python pipeline using inline IR props
- Sample render output path support under `remotion/renders/`

Behavior now available:
- `pnpm exec remotion compositions src/index.ts` succeeds and lists `VideoFromIR`
- `pnpm run render:sample` produces `remotion/out/sample.mp4`
- `VideoGenerationService.generate()` can render an MP4 when `render_video=True`
- Verified local run:
  - project id: `proj_68a5b942`
  - IR path: `agents/data/ir/proj_68a5b942.json`
  - MP4 path: `remotion/renders/proj_68a5b942.mp4`
  - verification status: `passed`

Still missing:
- Shared cross-package IR schema source of truth
- Real LLM-backed agent execution
- SQLite persistence and project CRUD
- WebSocket progress streaming
- FFmpeg post-processing
- Dashboard

### 2026-03-20

**SQLite persistence and FFmpeg post-processing implemented**

Added:
- `agents/video_gen_agents/database.py` with SQLAlchemy async models for projects and agent logs
- SQLite-backed project persistence for generated runs, including status, verification, IR path, render path, and logs
- API endpoints:
  - `/api/projects`
  - `/api/projects/{project_id}`
- `agents/video_gen_agents/ffmpeg.py` to post-process rendered MP4s

Behavior now available:
- API generation creates and persists project records in SQLite
- Agent logs are persisted and retrievable per project
- Rendered Remotion MP4s are re-encoded with FFmpeg and fast-start flags before being returned as final output
- Verified API smoke run:
  - project id: `proj_60f4320a`
  - render path: `remotion/renders/proj_60f4320a.mp4`
  - persisted project detail status: `rendered`
  - persisted verification status: `passed`
  - persisted logs count: `7`

Still missing:
- Shared cross-package IR schema source of truth
- Real LLM-backed agent execution
- Dashboard
- Automated end-to-end pipeline test

### 2026-03-20

**Dashboard MVP scaffold implemented**

Added:
- `dashboard/` package with Vite + React + TypeScript setup, env example, and production build config
- Dashboard UI for:
  - project list polling
  - new project generation form
  - project detail inspection
  - rendered MP4 playback
  - verifier output, persisted logs, and inline IR viewing
- Backend support for dashboard consumption:
  - CORS middleware
  - mounted media paths for `/media/renders` and `/media/ir`
  - stored `ProjectIR` included in project detail responses

Behavior now available:
- `pnpm build` succeeds in `dashboard/`
- The dashboard can use the existing API to create runs and inspect persisted project artifacts
- Rendered videos are now browser-loadable through mounted FastAPI static paths
- Verified backend tests now cover:
  - stored IR in detail responses
  - mounted IR artifact serving
  - CORS preflight for `/api/generate`

Still missing:
- Agent DAG visualization
- Update/delete project flows
- Shared cross-package IR schema source of truth
- Real LLM-backed agent execution
- Automated end-to-end pipeline/browser smoke test
