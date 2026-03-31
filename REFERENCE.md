# 🧠 Gemini Reference: Video Generation System (Phase 3)

This document is the high-level technical reference for the **Phase 3: Motion Intelligence** iteration of the Video Generation System.

## 🏗️ Architecture Overview
The system uses a **LangGraph-orchestrated multi-agent pipeline** that transforms natural-language briefs into high-fidelity 30–60s motion graphics.

### Core Pipeline
`Brief` → `Manager` → `Script/Storyboard` → `Visual Design` → `Motion Intelligence` → `Voice Gen` → `Renderer` → `Verifier` → `MP4`

### The 8 Specialized Agents (Evolved)
1.  **Manager**: Director. Parses brief, sets constraints, builds the task DAG.
2.  **Script & Storyboard**: Narrative architect. Creates beats and scene breakdowns.
3.  **Visual Design**: Aesthetic lead. Selects themes and maps scenes to **Advanced Layout Templates**.
4.  **Motion Intelligence**: Senior Animator. Defines **ambient motion**, **stagger groups**, **spring physics**, and **SVG path animations**.
5.  **Audio & SFX**: Sound designer. Plans music and SFX triggers (Voice is now integrated).
6.  **Router**: Resilience layer. Manages fallback between **Cerebras (Qwen 3)** and **Groq (Llama 3.3)**.
7.  **Renderer**: Assembler. Compiles IR, triggers Remotion CLI (with concurrency), and runs FFmpeg.
8.  **Verifier**: Quality control. Validates IR schema and rendered output; handles retries.

---

## 🛠️ Tech Stack (Updated)
| Layer | Technology |
| :--- | :--- |
| **Agent logic** | LangGraph, Python 3.11+, Pydantic |
| **LLM Stack** | Cerebras (Qwen 2.5 72B/235B) + Groq (Llama 3.3 70B) Fallback |
| **Backend** | FastAPI, SQLAlchemy, SQLite |
| **Video Engine** | Remotion 4.x (React, TypeScript), `@remotion/paths` |
| **Frontend** | React 18, Vite 6, Vanilla CSS |
| **Observability** | Langfuse (Distributed Tracing & Evals) |
| **Voice** | ElevenLabs / OpenAI TTS (integrated via `generate_voice.py`) |

---

## 📄 Video IR v1.1 (Motion Intelligence Additions)
The `ProjectIR` schema has been extended for Phase 3:
- **`ambient`**: Continuous micro-motion (float, pulse, rotate).
- **`stagger`**: Automated sequential entry delays for group elements.
- **`svg-path`**: New element type for animated "draw-on" lines/arcs.
- **`svg-icon`**: Built-in library of 12 vector icons.
- **`easing`**: Expanded library (ease-out-back, ease-out-expo, etc.).
- **`depth_3d`**: Boolean flag for CSS perspective transforms.

---

## 📁 Project Structure (New Items)
- `agents/scripts/generate_voice.py`: Dedicated voice generation utility.
- `remotion/public/voice/`: Storage for generated voiceovers and manifests.
- `docs/PLAN_V3.md`: Detailed roadmap for Motion Intelligence features.
- `docs/motion_design_audit.md`: Technical breakdown of reference-quality motion.
- `docs/video_analysis.md`: Frame-by-frame audit of professional motion graphics.

---

## 🚀 Key Commands
### Backend & Voice
- Start API: `cd agents && uv run python -m uvicorn video_gen_agents.api.main:app --reload`
- Voice Gen: `python agents/scripts/generate_voice.py --project <id>`

### Renderer (Remotion)
- Preview: `cd remotion && pnpm start`
- Render Sample: `cd remotion && pnpm run render:sample`

---

## 📝 Current Progress (Phase 3)
- [x] **SVG Component System**: Path draw-on and icon library implemented.
- [x] **Motion Upgrades**: Ambient float, stagger, and extended easing active.
- [x] **LLM Resilience**: Cerebras/Groq router with 429 fallback.
- [x] **Observability**: Langfuse tracing integrated into pipeline.
- [x] **Voice Integration**: Voiceover segments generated and synced in IR.
- [ ] **Canvas Editor**: Drag-and-drop timeline and layout (Phase 4).
