# 🧠 Gemini Reference: Video Generation System

This document serves as a high-level technical reference for the Video Generation System.

## 🏗️ Architecture Overview
The system follows a **Research -> Strategy -> Execution** pattern across two main environments: **Python (Agents/Backend)** and **TypeScript (Rendering/Dashboard)**.

### Core Pipeline
`Brief` → `LangGraph Agents (Python)` → `Video IR (JSON)` → `Remotion (React/TS)` → `FFmpeg` → `MP4`

### The 7 Specialized Agents
1.  **Manager**: Director. Parses brief, sets constraints (duration, aspect), builds task plan.
2.  **Script & Storyboard**: Narrative architect. Creates beats and scene breakdowns.
3.  **Visual Design**: Aesthetic lead. Selects theme tokens and per-scene layouts.
4.  **Motion & Physics**: Animator. Defines keyframes, spring physics, and transitions.
5.  **Audio & SFX**: Sound designer (Phase 2). Plans music and SFX triggers.
6.  **Renderer**: Assembler. Compiles IR, triggers Remotion CLI, and runs FFmpeg.
7.  **Verifier**: Quality control. Validates IR schema and rendered output; handles retries.

---

## 🛠️ Tech Stack
| Layer | Technology |
| :--- | :--- |
| **Agent Logic** | LangGraph, Python 3.11+, Pydantic |
| **LLM** | Groq (Llama 3.3 70B) |
| **Backend** | FastAPI, SQLAlchemy, SQLite |
| **Video Engine** | Remotion (React, TypeScript) |
| **Frontend** | React 18, Vite, Vanilla CSS |
| **Post-processing** | FFmpeg |

---

## 📁 Project Structure
- `agents/`: Python source. FastAPI app, LangGraph nodes, IR models, SQLite DB.
- `remotion/`: React source. Composition logic, element renderers, IR-to-React mapping.
- `dashboard/`: React source. Project management, live progress (WS), video preview.
- `shared/themes/`: JSON presets for colors, typography, and motion.
- `docs/`: Deep technical specs (IR Schema, Agent Prompts, ADRs).

---

## 📄 Video IR (The Single Source of Truth)
Every video is defined by a `ProjectIR` JSON object:
- `meta`: ID, duration, FPS, resolution.
- `theme`: Colors, typography tokens, motion presets.
- `timeline`: List of `scenes`, each containing `elements` (text, shape, progress, etc.).
- `audio`: Music and SFX plan.
- `constraints`: Boundaries for duration and scene counts.

---

## 🚀 Key Commands
### Backend (Python)
- Start API: `cd agents && uvicorn video_gen_agents.api.main:app --reload`
- Run Tests: `cd agents && pytest`

### Renderer (Remotion)
- Preview: `cd remotion && pnpm start`
- Render Sample: `cd remotion && pnpm run render:sample`

### Dashboard (Vite)
- Dev Mode: `cd dashboard && pnpm dev`
- Build: `cd dashboard && pnpm build`

---

## 📝 Ongoing Development (Phase 1)
- [x] End-to-end pipeline (Brief to MP4)
- [x] Dashboard with live WebSocket progress
- [x] SQLite persistence for projects and logs
- [ ] Real LLM prompt integration (currently deterministic/placeholder)
- [ ] Shared IR schema package (syncing Python/TS types)
- [ ] Audio integration (Music/SFX/TTS)
