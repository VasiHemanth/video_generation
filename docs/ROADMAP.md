# Product Roadmap

## Current Phase: Phase 1 — Foundation & MVP 🚧

**Goal**: End-to-end pipeline from brief → agents → IR → Remotion → MP4

**Timeline**: Active development

> Repo baseline verified on 2026-03-20: documentation, shared themes, workspace metadata, Python agent/backend source, tests, a runnable `remotion/` package, a runnable `dashboard/` package, `.gitignore`, and env examples for `agents/` and `dashboard/` exist.

### Milestones

| # | Milestone | Status | Description |
|---|-----------|--------|-------------|
| 1.1 | Project Scaffolding | 🚧 In Progress | Root manifests, Python package metadata, agent/backend source, tests, ignore rules, env examples, theme presets, and runnable `remotion/` and `dashboard/` packages exist; shared schema packaging and some root-level dev ergonomics are still missing |
| 1.2 | IR Schema & Types | 🚧 In Progress | Python Pydantic IR models exist in `agents/video_gen_agents/models.py`; TypeScript Zod schema and types now exist in `remotion/src/types.ts`, but the schema is not shared across packages yet |
| 1.3 | LangGraph Agents | 🚧 In Progress | Sequential LangGraph pipeline, state schema, and deterministic agent nodes are implemented; Groq-backed generation is not wired into node execution yet |
| 1.4 | Remotion Pipeline | 🚧 In Progress | The `remotion/` package can load typed IR, resolve composition metadata, list compositions, and render a sample MP4; scene coverage and backend integration are still expanding |
| 1.5 | FastAPI Backend | 🚧 In Progress | FastAPI app, health/theme/generate/project endpoints, async project launch, SQLite-backed project persistence, static media mounts for MP4/IR artifacts, WebSocket progress streaming, backend tests, and Remotion-backed MP4 rendering are implemented; update/delete flows are still missing |
| 1.6 | Dashboard MVP | 🚧 In Progress | Vite + React dashboard can launch runs in the background, subscribe to project WebSockets, display a stage graph, inspect logs/verification/IR, and play rendered MP4s; update/delete flows and broader project management controls are still missing |
| 1.7 | E2E Integration | ✅ Complete | Manual brief → IR → Remotion → FFmpeg → MP4 smoke runs work locally. |
| 1.8 | LLM Resiliency | ✅ Complete | Cerebras + Groq fallback router with 429 retries. |
| 1.9 | Observability | ✅ Complete | Langfuse integration for distributed tracing and session tracking. |

### Tier 1 Visual Capabilities (Phase 1)
- Kinetic typography (word-by-word, char-by-char reveals)
- Geometric shapes with parametric animation
- Animated gradients and mesh backgrounds
- Counters and progress indicators
- Particle/dot field effects
- Code block typing animations
- Scene transitions (fade, slide, wipe)

---

## Phase 2 — Parallelization & Self-Correction ✅

**Goal**: High-performance, resilient, and parallel processing.

### Completed Milestones
- [x] **Provider-Specific Semaphores**: 3 concurrent for Cerebras, 1 for Groq.
- [x] **LangGraph Async Overhaul**: Entire pipeline is now native async.
- [x] **Scene Parallelization**: Designer and Motion nodes process scenes concurrently.
- [x] **Healer Agent**: Automatically corrects LLM JSON schema errors on-the-fly.

---

## Phase 3 — Motion Intelligence, SVG Components & Scene Templates ✅

**Goal**: Professional motion design quality through animation upgrades, dynamic SVG system, and prompt enrichment.

**Plan**: See [PLAN_V3.md](./PLAN_V3.md) for detailed technical plan.

### Workstreams
| WS | Feature | Priority | Description |
|----|---------|----------|-------------|
| WS1 | Animation Engine Upgrades | P0 | Ambient float, 4 new easing curves, stagger groups, 3D depth |
| WS2 | Scene Templates | P0 | card-stack, terminal-demo, list-reveal, connection-graph layouts |
| WS3 | Dynamic SVG Components | P0 | `svg-path` draw-on via `@remotion/paths`, `svg-icon` with 12 built-in icons |
| WS4 | Prompt Enrichment | P0 | Rewrite Designer + Motion agent prompts with full animation vocabulary |
| WS5 | Theme Upgrade | P1 | Warm claymorphic theme matching reference video aesthetic |

### Tier 2 Visual Capabilities
- SVG path draw-on animations (connecting lines, flow arcs)
- Built-in SVG icon library (12 icons: checkmark, document, calendar, code, etc.)
- Spring-physics card stacking with stagger cascades
- Terminal/browser frame mockups with typewriter text
- Ambient float motion on decorative elements
- Glassmorphism card surfaces with 3D perspective depth
- Extended easing curves (ease-out-back, expo, cubic)

---

## Phase 4 — Canvas, Deterministic Edits & Scale 🚧

**Goal**: Visual editing UI, non-LLM edits, production readiness

### Implemented So Far (Phase 4)
- [x] **IR Mutation API** (`ir_mutations.py`): deterministic ops for color, duration, reorder, aspect ratio, theme swap
- [x] **Re-render endpoint** (`POST /api/projects/{id}/re-render`): queue Remotion render from stored IR
- [x] **Export Presets** (`export_presets.py` + `POST /api/projects/{id}/export/{platform}`): YouTube, Instagram, TikTok, LinkedIn, Twitter
- [x] **Dashboard Timeline Panel** (`TimelinePanel.tsx`): drag-and-drop scene reordering + inline duration editor
- [x] **Vision Verifier** (`rendering.py`): per-scene frame extraction + aspect ratio guard in verifier node

### Features

| Feature | Priority | Description |
|---------|----------|-------------|
| Timeline Canvas | P0 | Drag-and-drop scene reordering, duration adjustment |
| Layout Canvas | P0 | On-canvas element positioning, scaling, anchoring |
| Deterministic IR Mutations | P0 | Color/font/timing changes without LLM calls |
| Motion Token Editor | P1 | Visual easing curve editor, spring physics playground |
| Theme Switcher | P0 | One-click theme swap across entire video |
| Platform Presets | P1 | One-click export for YouTube, Instagram, TikTok, LinkedIn |
| Limited Concurrency | P2 | Safe parallel agent execution for independent tasks |
| Orchestration DSL | P2 | Typed DSL replacing raw JSON tool calls |
| Asset Manager | P1 | Upload/manage custom SVGs, fonts, audio |
| Version History | P1 | Full project versioning with diff view |

### Tier 3 Visual Capabilities
- Complex multi-layer compositions
- Camera movement simulation (zoom, pan, track)
- 3D perspective transforms
- Advanced particle systems
- Procedural generative backgrounds
- Character animation rigging (basic)

---

## Phase 4 — Intelligence & Ecosystem 📋

**Goal**: Smarter agents, better quality, ecosystem integrations

### Features

| Feature | Priority | Description |
|---------|----------|-------------|
| Vision Verifier | P1 | Screenshot-based visual quality checks |
| A/B Variant Generation | P2 | Generate multiple versions for testing |
| Brand Kit Support | P1 | Upload brand guidelines, auto-apply across videos |
| External Asset Sources | P2 | Integration with Unsplash, Storyset, icon APIs |
| AI Music Generation | P2 | Suno/Udio integration for custom music beds |
| Multi-user Support | P3 | Postgres, auth, team workspaces |
| Cloud Rendering | P2 | Remotion Lambda for parallel remote renders |
| API Access | P2 | Headless API for programmatic video generation |
| Plugin System | P3 | Custom scene types, effects, and agent extensions |

---

## Backlog / Ideas

These are ideas captured from the original blueprint that may be explored in future phases:

- [ ] Design Canvas with Figma-like element manipulation
- [ ] Explain-and-refine loop (system explains creative choices, user refines)
- [ ] Brief templates for common video types (explainer, promo, CTA, tutorial)
- [ ] Batch generation (produce 10 variants of a brief)
- [ ] Analytics integration (which video styles perform best)
- [ ] Real-time collaboration (multiple users editing same project)
- [ ] Mobile-responsive dashboard
- [ ] Webhook notifications when render completes
- [ ] S3/GCS for render storage
- [ ] CI/CD for automated testing of IR → Remotion pipeline
