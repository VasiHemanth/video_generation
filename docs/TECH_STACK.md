# Technology Stack

## Overview

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| **Agent Orchestration** | LangGraph | latest | DAG-based agent pipelines, built-in state management, conditional routing |
| **LLM Providers** | Cerebras (Primary) + Groq (Fallback) | — | Multi-provider fallback for high reliability |
| **Reasoning Model**| Qwen 3 235B / Llama 3.3 70B | — | Top-tier reasoning for complex Video IR |
| **Observability** | Langfuse | v4 | Distributed tracing, session tracking, cost monitoring |
| **Backend API** | FastAPI | 0.115+ | Async, WebSocket support, automatic OpenAPI docs |
| **Database** | SQLite | 3.x | Zero-config, local-first, sufficient for single-user |
| **ORM** | SQLAlchemy | 2.0+ | Async support, model definitions, migrations |
| **Video Composition** | Remotion | 4.x | React-based video, programmatic rendering, spring physics |
| **Video Encoding** | FFmpeg | 7.x | Industry standard, all codecs, audio muxing |
| **Frontend Framework** | React | 18+ | Dashboard UI, same ecosystem as Remotion |
| **Frontend Build** | Vite | 6.x | Fast HMR, TypeScript support |
| **Styling** | Vanilla CSS | — | Maximum control, no framework dependency |
| **Package Manager (Python)** | uv / pip | — | Fast dependency resolution |
| **Package Manager (JS)** | pnpm | 9.x | Fast, disk-efficient, monorepo support |
| **TTS (Phase 2)** | Qwen local / Google Cloud TTS | — | Pluggable: free local or high-quality cloud |
| **Audio Processing** | FFmpeg | — | Audio muxing, normalization, format conversion |

---

## Python Dependencies (agents/)

### Core
```
fastapi>=0.115.0          # HTTP API framework
uvicorn[standard]>=0.32.0 # ASGI server
websockets>=13.0          # WebSocket support
sqlalchemy>=2.0.0         # Database ORM
aiosqlite>=0.20.0         # Async SQLite driver
pydantic>=2.0.0           # Data validation and schemas
python-dotenv>=1.0.0      # Environment variable loading
```

### LangGraph & LLM
```
langgraph>=0.2.0          # Agent orchestration framework
langchain-core>=0.3.0     # LangChain base abstractions
langchain-groq>=0.2.0     # Groq LLM integration
langchain-cerebras>=0.1.0 # Cerebras LLM integration
langfuse>=2.0.0           # Distributed tracing
langsmith>=0.1.0          # Tracing (optional/legacy)
```

### Utilities
```
httpx>=0.27.0             # Async HTTP client
structlog>=24.0.0         # Structured logging
```

### Testing
```
pytest>=8.0.0
pytest-asyncio>=0.24.0
pytest-cov>=5.0.0
```

---

## TypeScript Dependencies (remotion/)

### Core
```json
{
  "@remotion/cli": "^4.0.0",
  "@remotion/renderer": "^4.0.0",
  "remotion": "^4.0.0",
  "react": "^18.0.0",
  "react-dom": "^18.0.0",
  "typescript": "^5.0.0"
}
```

### Utilities
```json
{
  "zod": "^3.23.0"        // Runtime IR validation
}
```

---

## TypeScript Dependencies (dashboard/)

### Core
```json
{
  "react": "^18.0.0",
  "react-dom": "^18.0.0",
  "react-router-dom": "^7.0.0",
  "typescript": "^5.0.0",
  "vite": "^6.0.0"
}
```

### Utilities
```json
{
  "lucide-react": "^0.400.0"  // Icon library
}
```

---

## System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **OS** | macOS 13+ | macOS 14+ (Sonoma) |
| **Node.js** | 18.x | 20.x LTS |
| **Python** | 3.11+ | 3.12+ |
| **FFmpeg** | 6.x | 7.x |
| **RAM** | 8GB | 16GB+ |
| **Disk** | 5GB free | 20GB+ (for renders) |
| **CPU** | 4 cores | 8+ cores (Remotion rendering is CPU-heavy) |

---

## Environment Variables

```bash
# .env (agents/)
GROQ_API_KEY=gsk_...                # Required: Groq API key
CEREBRAS_API_KEY=csk_...            # Required: Cerebras API key
LANGFUSE_SECRET_KEY=sk-lf-...       # Required: Langfuse Secret
LANGFUSE_PUBLIC_KEY=pk-lf-...       # Required: Langfuse Public
LANGFUSE_BASE_URL=https://...       # Required: Langfuse Base URL
DATABASE_URL=sqlite:///./data/app.db # SQLite database path

# Future additions
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
# GOOGLE_TTS_KEY=...
# ELEVENLABS_API_KEY=...
```

---

## Why These Choices?

### LangGraph over CrewAI / AutoGen
- **State management**: Built-in TypedDict state with ownership semantics — perfect for IR-as-shared-state
- **Conditional routing**: Native support for Verifier → retry loops
- **Observability**: LangSmith integration for tracing agent decisions
- **Control**: More explicit than CrewAI, less boilerplate than AutoGen
- **Production-ready**: Used by LangChain team in production systems

### Groq over direct OpenAI / Anthropic
- **Speed**: 10-100x faster inference than OpenAI/Anthropic for same-quality models
- **Cost**: Free tier generous enough for development
- **Llama 3.3 70B**: Competitive with GPT-4o on structured tasks, especially JSON output
- **Pluggable**: LangChain abstraction makes swapping trivial

### Remotion over raw FFmpeg / After Effects scripting
- **React-based**: Leverages React ecosystem, familiar component model
- **Programmatic**: Perfect for IR → component tree compilation
- **Spring physics**: Built-in `spring()` function for natural motion
- **Preview**: In-browser preview during development
- **Deterministic**: Same IR always produces same output

### SQLite over Postgres / Redis
- **Zero config**: No server to run, works immediately
- **Local-first**: Perfect for single-user, single-machine setup
- **Sufficient**: Project count will be low (100s, not millions)
- **Portable**: Single file, easy to backup/move
- **Upgradeable**: Can migrate to Postgres later if needed

### Vanilla CSS over Tailwind
- **Control**: Full control over design tokens and animations
- **No build step**: No PostCSS/JIT complexity
- **CSS Variables**: Native theme token system using custom properties
- **Animations**: Native @keyframes and transitions, no utility class bloat
