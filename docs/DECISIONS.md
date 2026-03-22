# Architecture Decision Records (ADR)

## Format

Each decision follows this template:
- **Status**: Proposed | Accepted | Deprecated | Superseded
- **Date**: When the decision was made
- **Context**: What prompted this decision
- **Decision**: What we chose
- **Alternatives**: What else we considered
- **Consequences**: What this means going forward

---

## ADR-001: IR as Single Source of Truth

**Status**: Accepted
**Date**: 2026-03-20

**Context**: Need a way to represent video projects that all agents can read/write and that compiles deterministically to rendered video.

**Decision**: A single JSON document (ProjectIR) is the authoritative representation of every video. Remotion components are generated from this IR — never hand-edited. Agents write to their owned sections of the IR.

**Alternatives**:
- Direct Remotion code generation (agents write JSX) — rejected because LLM code generation is unreliable and non-reversible
- Multiple linked files (timeline.json, theme.json, etc.) — rejected for simplicity; single file is easier to validate and checkpoint

**Consequences**:
- All visual/motion changes must be expressible in the IR schema
- IR schema must be rich enough to cover all scene types and animations
- Schema evolution must be managed carefully (versioned, backward-compatible)
- Enables deterministic rendering: same IR → same video, every time

---

## ADR-002: LangGraph for Agent Orchestration

**Status**: Accepted
**Date**: 2026-03-20

**Context**: Need a framework to wire 7 agents into a sequential pipeline with conditional retry routing.

**Decision**: Use LangGraph StateGraph with a TypedDict state object. Each agent is a node in the graph. Verifier has a conditional edge for retry routing.

**Alternatives**:
- CrewAI — simpler but less control over state management and routing
- AutoGen — more complex, Microsoft-specific patterns
- Custom orchestration — full control but significant engineering overhead
- LangChain Agents (tool-calling) — not designed for multi-step multi-agent workflows

**Consequences**:
- Locked into LangChain ecosystem (langchain-core, langchain-groq)
- Agent prompts must return structured JSON compatible with state schema
- LangSmith available for free observability/tracing
- Migration to LangGraph Cloud possible for scaling

---

## ADR-003: Groq as Primary LLM Provider

**Status**: Accepted
**Date**: 2026-03-20

**Context**: Need fast, cost-effective LLM inference for development and iteration. Will potentially switch providers in production.

**Decision**: Use Groq API with `llama-3.3-70b-versatile` as the primary model. Abstract via LangChain's ChatModel interface so swapping providers requires changing one line.

**Alternatives**:
- OpenAI GPT-4o — higher quality for some tasks but slower and more expensive
- Anthropic Claude — excellent for structured output but more expensive
- Local models (Ollama) — free but slower and lower quality

**Consequences**:
- Development iteration is fast (Groq's inference speed is 10-100x faster)
- Llama 3.3 70B may produce lower-quality creative output than GPT-4o/Claude for some prompts
- Must design prompts that work well with Llama 3.3's strengths (instruction following, JSON)
- Easy migration path: change `ChatGroq` → `ChatOpenAI` or `ChatAnthropic`

---

## ADR-004: Hybrid Monorepo (Python + TypeScript)

**Status**: Accepted
**Date**: 2026-03-20

**Context**: Agent logic is best in Python (LangGraph, LLM ecosystems). Rendering must be in TypeScript (Remotion is React). Dashboard can be either.

**Decision**: Single monorepo with three main packages:
- `agents/` — Python (FastAPI, LangGraph, SQLite)
- `remotion/` — TypeScript (Remotion project)
- `dashboard/` — TypeScript (Vite + React)

Communication between Python ↔ TypeScript is via:
- File system (write IR JSON → Remotion reads it)
- Subprocess (Python calls `npx remotion render`)

**Alternatives**:
- Full TypeScript (use Mastra or custom agent framework) — LLM tooling ecosystem worse in TS
- Full Python (use MoviePy instead of Remotion) — MoviePy lacks spring physics and component model
- Microservices with API communication — overkill for single-user local setup

**Consequences**:
- Two language environments to maintain
- IR schema must be kept in sync between Python dataclasses and TS types
- No direct function calls between Python and TS — only file I/O and subprocess
- Clear separation of concerns: agents think → Remotion renders

---

## ADR-005: Sequential Agent Pipeline (Not Parallel)

**Status**: Accepted
**Date**: 2026-03-20

**Context**: Agents have data dependencies (Script → Design → Motion → Render). The Replit architecture doc warns about parallel agent regressions.

**Decision**: Phase 1 uses a strictly sequential pipeline. Each agent completes fully before the next starts. Only the Verifier has a conditional edge (retry loop).

**Alternatives**:
- Parallel script + design exploration — possible but adds merge complexity
- Fan-out/fan-in for independent work — deferred to Phase 4

**Consequences**:
- Pipeline is slower but more predictable
- No merge conflicts or concurrent IR mutations
- Easy to debug (linear trace of agent outputs)
- Can selectively parallelize later with clear ownership boundaries

---

## ADR-006: Vite + React for Dashboard

**Status**: Accepted
**Date**: 2026-03-20

**Context**: Need a simple web dashboard for project management, agent progress viewing, and video preview.

**Decision**: Vite + React with vanilla CSS. No heavy framework (Next.js unnecessary for a local single-page app). WebSocket for real-time agent updates.

**Alternatives**:
- Next.js — SSR unnecessary for local dashboard, adds complexity
- Svelte — smaller ecosystem, less React synergy with Remotion
- Terminal UI — faster to build but can't embed video player or agent DAG visualization

**Consequences**:
- Fast development (Vite HMR, simple React setup)
- Must implement WebSocket client for real-time updates
- Video preview may need custom player (HTML5 `<video>`)
- Styling with CSS custom properties for easy theming

---

## ADR-007: SQLite for Persistence

**Status**: Accepted
**Date**: 2026-03-20

**Context**: Need to persist projects, agent logs, and checkpoints. Single-user local setup.

**Decision**: SQLite via SQLAlchemy async. Database file stored in `agents/data/app.db`.

**Alternatives**:
- JSON files on disk — simpler but no query capability, no ACID
- Postgres — overkill for single-user, requires running a server
- Redis — good for state/cache but not for structured persistence

**Consequences**:
- Zero operational overhead
- Concurrent access limited (single writer) — fine for single-user
- Migration to Postgres later is straightforward with SQLAlchemy
- Must be careful with large IR JSON blobs in SQLite (fine up to ~10MB per row)

---

## ADR-008: Deterministic IR → Remotion Compilation

**Status**: Accepted
**Date**: 2026-03-20

**Context**: Rendering must be reliable and reproducible. LLMs should not be involved in the rendering step.

**Decision**: The Rendering Orchestrator Agent assembles the IR but does NOT write Remotion code. Instead, the Remotion project has a fixed set of components that read the IR JSON at runtime and render accordingly. The IR is a runtime prop, not a code-generation target.

**Alternatives**:
- Code generation (agent writes .tsx files) — unreliable, hard to debug, fragile
- Template-based code gen (fill in blanks in templates) — more reliable but still requires code validation

**Consequences**:
- Remotion components must be generic enough to handle all IR variations
- Adding new scene types requires writing new Remotion components (developer work), not agent work
- 100% deterministic: same IR → same rendered video
- Easier to test: unit test IR validation, separately test Remotion components with fixture IRs
