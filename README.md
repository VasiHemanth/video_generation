# 🎬 Video Generation System

A multi-agent AI system that transforms natural-language briefs into 30–40 second motion graphics videos.

## Architecture

```
Brief → [LangGraph Agents] → Video IR → [Remotion] → [FFmpeg] → MP4
```

**7 specialized agents** collaborate through a shared Video IR (Intermediate Representation):

1. **Manager** — Parses brief, builds task plan, sets constraints
2. **Script & Storyboard** — Generates narrative beats and scene breakdown
3. **Visual Design** — Creates theme tokens and per-scene layouts
4. **Motion & Physics** — Designs animations, keyframes, and transitions
5. **Renderer** — Assembles IR, triggers Remotion + FFmpeg
6. **Verifier** — Validates output, routes failures for retry
7. **Router (New)** — Managed resilient fallback between Cerebras and Groq

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent Orchestration | LangGraph (Python) |
| LLM | Cerebras (Qwen 3 235B) + Groq Fallback |
| Backend API | FastAPI + SQLite |
| Video Rendering | Remotion (React/TS) |
| Post-Processing | FFmpeg |
| Dashboard | Vite + React |
| Observability | Langfuse (Distributed Tracing) |

## Project Structure

```
video_generation/
├── agents/        # Present — FastAPI app, LangGraph pipeline, IR models, tests
├── shared/        # Present — theme presets and shared design tokens
├── docs/          # Present — architecture, specs, roadmap, status tracking
├── remotion/      # Present — TypeScript renderer, IR schema, sample composition, render output
└── dashboard/     # Present — Vite + React dashboard for runs, renders, logs, and IR inspection
```

## Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE](docs/ARCHITECTURE.md) | System topology, data flow, component boundaries |
| [IR_SPEC](docs/IR_SPEC.md) | Complete Video IR schema specification |
| [AGENTS](docs/AGENTS.md) | Agent specifications, I/O schemas, prompt strategies |
| [ROADMAP](docs/ROADMAP.md) | Phased product roadmap |
| [TECH_STACK](docs/TECH_STACK.md) | Technology choices and rationale |
| [DECISIONS](docs/DECISIONS.md) | Architecture Decision Records (ADRs) |
| [CONSIDERATIONS](docs/CONSIDERATIONS.md) | Risks, limitations, and technical debt |
| [STATUS](docs/STATUS.md) | Implementation status dashboard |
| [IMPLEMENTATION_LOG](docs/IMPLEMENTATION_LOG.md) | Dated log of what has actually landed in the repo |
| [CHANGELOG](docs/CHANGELOG.md) | Change history |

## Quick Start

> **Prerequisites**: Node.js 18+, Python 3.11+, FFmpeg, pnpm

```bash
cd remotion
pnpm install --ignore-workspace
pnpm run render:sample

cd agents
uv run python -m uvicorn video_gen_agents.api.main:app --reload

cd dashboard
pnpm install --ignore-workspace
pnpm dev
```

## Status

🚧 **Phase 1 — Foundation & MVP**: The repo now turns a brief into a validated Video IR, renders an MP4 through Remotion, post-processes it through FFmpeg, persists project records in SQLite, supports background project launch with live WebSocket stage updates, and exposes a dashboard for project creation, DAG-style run inspection, video playback, logs, and IR viewing. Update/delete flows, shared schema packaging, and automated browser-level end-to-end checks are still pending.

## Tracking

Use [docs/STATUS.md](docs/STATUS.md) for the current checklist, [docs/IMPLEMENTATION_LOG.md](docs/IMPLEMENTATION_LOG.md) for dated implementation notes, and [docs/CHANGELOG.md](docs/CHANGELOG.md) for milestone-level changes.

## License

Private — All rights reserved.
