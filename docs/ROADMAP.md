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

## Phase 2 — Audio, Advanced Visuals & Polish 📋

**Goal**: Full audio pipeline, richer visuals, production polish

### Features

| Feature | Priority | Description |
|---------|----------|-------------|
| Audio & SFX Agent | P0 | Full audio planning: music selection, SFX placement, level management |
| TTS Integration | P0 | Voiceover via local Qwen or Google Cloud TTS |
| Bundled SFX Library | P0 | Whoosh, click, impact, rise, drop, notification, ambient |
| Music Library | P1 | Curated royalty-free music tracks bundled in project |
| Audio Muxing | P0 | FFmpeg audio track composition, ducking, normalization |
| Checkpoint System | P1 | IR snapshots with rollback capability |
| Tier 2 Visuals | P1 | SVG illustrations, icon compositions, diagram scenes |
| Advanced Motion | P1 | Parallax, camera simulation, depth layers |
| Scene Templates | P2 | Pre-designed scene archetypes (comparison, list, timeline) |
| Scene Parallelization | P0 | Parallel execution of independent agent nodes |
| Error Recovery v2 | P1 | Self-healing loops for schema validation errors |
| Audio & SFX Agent | P0 | Full audio planning: music selection, SFX placement |

### Tier 2 Visual Capabilities
- SVG icon compositions and illustrations
- Diagram and flowchart animations
- Device mockup frames (phone, laptop, browser)
- Before/after comparison layouts
- Timeline / journey visualizations
- Data dashboard layouts

---

## Phase 3 — Canvas, Deterministic Edits & Scale 📋

**Goal**: Visual editing UI, non-LLM edits, production readiness

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
