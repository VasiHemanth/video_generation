# Agent Specifications

## Overview

Seven specialized agents operate in a sequential LangGraph StateGraph pipeline. Each agent receives the full shared state, reads upstream outputs, and writes only to its owned keys.

**LLM Backend**: Groq API → `llama-3.3-70b-versatile` (pluggable to any LangChain-compatible model)

---

## Agent Pipeline Flow

```
START
  │
  ▼
┌─────────────────────┐
│  1. Manager Agent    │  Parses brief → plan DAG → constraints
│     (Video Director) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  2. Script &        │  Script beats → scene breakdown → timing budget
│     Storyboard      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  3. Visual Design   │  Theme tokens → layout templates → element placement
│     & Layout        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  4. Motion &        │  Animations → keyframes → easing → transitions
│     Physics         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  5. Audio & SFX     │  Music → SFX events → levels (stub in Phase 1)
│     (Phase 2)       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  6. Rendering       │  Assemble IR → write JSON → trigger Remotion → FFmpeg
│     Orchestrator    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  7. Verifier        │  Validate IR → check render → pass/fail
└──────────┬──────────┘
           │
      ┌────┴────┐
      │  Pass?  │
      └────┬────┘
       yes │ no
       END │ → route back to failing agent (max 2 retries)
```

---

## 1. Manager Agent (Video Director)

### Role
Owns the brief, sets constraints, creates a task plan, and provides global context to downstream agents.

### Reads
- `brief` (user input)

### Writes
- `plan`: DAG of tasks with stable IDs
- `constraints`: duration, aspect ratio, scene limits, mood, style direction
- `agent_logs`: progress entries

### Prompt Strategy
System prompt establishes the agent as a senior creative director. User prompt contains the brief. Output is structured JSON:

```json
{
  "plan": {
    "tasks": [
      { "id": "task_script", "name": "Generate Script", "agent": "scriptwriter", "deps": [] },
      { "id": "task_design", "name": "Design Visuals", "agent": "designer", "deps": ["task_script"] },
      { "id": "task_motion", "name": "Motion Design", "agent": "motion", "deps": ["task_design"] },
      { "id": "task_render", "name": "Render Video", "agent": "renderer", "deps": ["task_motion"] }
    ]
  },
  "constraints": {
    "duration": 35,
    "scenes": 5,
    "aspect_ratio": "16:9",
    "mood": "professional, energetic",
    "style_direction": "dark tech with accent glows",
    "key_points": ["what AI agents are", "how they work", "why they matter"]
  }
}
```

### Quality Guardrails
- Duration must be 30–40s
- Scene count must be 3–8
- Must extract at least 2 key points from the brief

---

## 2. Script & Storyboard Agent

### Role
Generates narrative structure: beats, script lines, scene breakdown with timing budgets.

### Reads
- `plan`, `constraints` (from Manager)

### Writes
- `script`: structured beats with text and durations
- `storyboard`: scene list with roles, intentions, and layout hints

### Output Schema

```json
{
  "script": {
    "beats": [
      {
        "id": "beat_001",
        "type": "hook",
        "text": "What if software could think for itself?",
        "duration": 4.0,
        "visual_note": "Big question mark morphing into an AI brain icon"
      },
      {
        "id": "beat_002",
        "type": "setup",
        "text": "AI agents are autonomous programs that can reason, plan, and act.",
        "duration": 6.0,
        "visual_note": "Three pillars appearing: Reason, Plan, Act"
      }
    ]
  },
  "storyboard": [
    {
      "scene_id": "scene_001",
      "role": "intro",
      "beat_ids": ["beat_001"],
      "duration": 5.0,
      "layout_hint": "centered_hero",
      "description": "Hook question with dramatic text reveal"
    },
    {
      "scene_id": "scene_002",
      "role": "setup",
      "beat_ids": ["beat_002"],
      "duration": 7.0,
      "layout_hint": "three_columns",
      "description": "Three pillars of AI agents explained"
    }
  ]
}
```

### Quality Guardrails
- Sum of beat durations must ≤ `constraints.duration`
- Each beat must have a `visual_note` (for downstream agents)
- Scene roles must include at least "intro" and one of "payoff"/"cta"

---

## 3. Visual Design & Layout Agent

### Role
Creates the visual identity (theme) and maps each scene to concrete layouts with elements.

### Reads
- `constraints`, `storyboard` (from upstream)

### Writes
- `theme`: full ThemeTokens object
- `layouts`: per-scene element lists with types, positions, sizes, and styling

### Prompt Strategy
Receives the storyboard and mood/style direction. Selects or generates a theme, then for each scene, produces concrete element placement.

### Output Schema

```json
{
  "theme": {
    "name": "dark_tech",
    "colors": { "bg_primary": "#0A0A0F", "accent_1": "#6C5CE7", "..." : "..." },
    "typography": { "display_lg": { "family": "Inter", "weight": 800, "size": 72 }, "..." : "..." },
    "motion": { "duration_normal": 0.4, "easing_spring": { "mass": 1, "damping": 12, "stiffness": 200 } },
    "layout": { "padding": 60, "gap": 24, "card_radius": 16 }
  },
  "layouts": [
    {
      "scene_id": "scene_001",
      "background": { "type": "animated-gradient", "colors": ["#0A0A0F", "#1A1A2E"], "angle": 135 },
      "elements": [
        {
          "id": "el_001",
          "type": "text",
          "props": { "content": "What if software could think?", "style_token": "display_lg", "color": "fg_primary", "align": "center" },
          "position": { "x": "50%", "y": "40%" },
          "anchor": "center",
          "layer": 2
        },
        {
          "id": "el_002",
          "type": "particle-field",
          "props": { "count": 40, "color": "accent_1", "opacity": 0.3 },
          "position": { "x": "0%", "y": "0%" },
          "size": { "width": "100%", "height": "100%" },
          "layer": 0
        }
      ]
    }
  ]
}
```

### Quality Guardrails
- Must use at least 2 accent colors
- Every scene must have a background
- Text elements must use typography tokens (not raw sizes)
- Layout must not place elements outside safe areas

---

## 4. Motion & Physics Agent

### Role
Adds animation, timing, and motion to every element. This is where the video comes alive.

### Reads
- `constraints`, `storyboard`, `theme`, `layouts`

### Writes
- `motion_plan`: per-element animation configs (enter, exit, emphasis, keyframes)

### Core Responsibilities
1. **Entry animations**: How each element appears (fade, slide, spring, scale)
2. **Exit animations**: How elements leave before scene transitions
3. **Emphasis**: Mid-scene movements (subtle float, pulse, glow)
4. **Scene transitions**: How scenes flow into each other
5. **Stagger timing**: Sequential reveals within groups
6. **Pacing**: Ensure motion feels coherent — fast for energy, slow for drama

### Motion Vocabulary

| Pattern | Use Case | Implementation |
|---------|----------|----------------|
| `spring` | Playful reveals, UI elements | Remotion `spring()` with damping/stiffness |
| `slide-up` | Text entries, list items | `interpolate()` on Y position |
| `scale-in` | Icons, numbers, emphasis | `interpolate()` on scale |
| `fade-in` | Subtle backgrounds, overlays | `interpolate()` on opacity |
| `bounce` | Counters, achievements | Spring with low damping |
| `typewriter` | Code blocks, typing | Character-by-character reveal |
| `parallax` | Depth effect, backgrounds | Differential scroll speeds |
| `orbit` | Decorative elements | Circular path keyframes |
| `elastic` | Overshoot and settle | Elastic easing curve |
| `stagger` | Lists, grids, multiple items | Incremental delay per child |

### Output Schema

```json
{
  "motion_plan": [
    {
      "scene_id": "scene_001",
      "transition_in": { "type": "fade", "duration": 0.5 },
      "transition_out": { "type": "slide-left", "duration": 0.4 },
      "elements": [
        {
          "element_id": "el_001",
          "enter": { "type": "spring", "duration": 0.8, "spring_config": { "mass": 1, "damping": 12, "stiffness": 200 }, "delay": 0.2 },
          "exit": { "type": "fade-out", "duration": 0.3 },
          "emphasis": { "type": "float", "amplitude": 5, "period": 3.0 },
          "keyframes": []
        }
      ]
    }
  ]
}
```

### Quality Guardrails
- Every visible element must have an `enter` animation
- No two elements in the same scene should enter at exactly the same time (use stagger)
- Scene transitions must not exceed 1s
- Total animation time per scene must leave at least 1s of "resting" for readability

---

## 5. Audio & SFX Agent (Phase 2 — stub in Phase 1)

### Role
Selects music, places SFX events, and manages audio levels.

### Phase 1 Behavior
Returns a minimal default audio plan:
```json
{
  "audio_plan": {
    "music": null,
    "sfx": [],
    "voiceover": { "enabled": false }
  }
}
```

### Phase 2 Full Behavior
- Select music bed from bundled library matching mood
- Place SFX events (whoosh on transitions, click on UI elements, rise on counters)
- Set volume envelopes and ducking curves
- Generate TTS segments if voiceover enabled

---

## 6. Rendering Orchestrator Agent

### Role
Assembles all agent outputs into the final ProjectIR, writes it as JSON, triggers Remotion rendering, and runs FFmpeg post-processing.

### Reads
- Everything: `script`, `storyboard`, `theme`, `layouts`, `motion_plan`, `audio_plan`, `constraints`

### Writes
- `ir`: the fully assembled ProjectIR as a dict
- `render_path`: path to the rendered video file

### Process
1. Merge `storyboard` + `layouts` + `motion_plan` into complete `timeline.scenes`
2. Validate IR against schema
3. Write IR JSON to `remotion/public/ir/{project_id}.json`
4. Execute: `npx remotion render src/index.ts VideoComposition --output renders/{project_id}.mp4 --props '{"irPath":"ir/{project_id}.json"}'`
5. Run FFmpeg post-processing if needed
6. Return render path

### Quality Guardrails
- Must validate IR before rendering (catch missing fields, invalid references)
- Remotion render timeout: 120 seconds
- Output file must be > 100KB

---

## 7. Verifier Agent

### Role
Final quality gate. Validates the IR and rendered output, routing failures back to the responsible agent.

### Checks

| Check | Target | Severity |
|-------|--------|----------|
| Duration in range | 30–40s | ERROR |
| Scene count in range | 3–8 | ERROR |
| No empty scenes | elements.length > 0 | ERROR |
| Scene durations valid | 2–15s each | WARNING |
| Sum of scene durations = total | ± 0.5s | ERROR |
| All theme refs valid | colors, typography exist | ERROR |
| Video file exists | render_path is valid | ERROR |
| Video file size | > 100KB | ERROR |
| Element has enter animation | every element | WARNING |
| No overlapping scenes | start times sequential | ERROR |

### Failure Routing
On failure, the verifier creates a "healer" request:
```json
{
  "status": "failed",
  "errors": [
    { "check": "duration_range", "message": "Total duration is 42s, max is 40s", "route_to": "scriptwriter" },
    { "check": "empty_scene", "message": "Scene scene_003 has no elements", "route_to": "designer" }
  ]
}
```

The LangGraph conditional edge routes back to the first failing agent (up to 2 retries per run).

---

## Prompt Engineering Guidelines

### All Agents
- System prompt establishes role and expertise
- Output format is strictly JSON (use Groq's JSON mode)
- Include the IR schema in the system prompt as a reference
- Include examples of good output
- Set temperature to 0.7 for creative agents (script, design), 0.3 for structural agents (motion, renderer, verifier)

### Context Window Management
- Manager sees: brief only (~200 tokens)
- Script agent sees: brief + plan + constraints (~500 tokens)
- Design agent sees: constraints + storyboard (~1000 tokens)
- Motion agent sees: constraints + storyboard + layouts (~2000 tokens)
- Renderer sees: everything assembled (~3000 tokens)
- Verifier sees: IR + render metadata (~1000 tokens)

Keep prompts under 4000 tokens total (input + output) to stay within Groq's fast inference window.
