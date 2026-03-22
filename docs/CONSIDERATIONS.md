# Considerations, Risks & Known Challenges

## Critical Design Considerations

### 1. LLM Output Reliability for Structured JSON

**Challenge**: Agents must produce valid, schema-conformant JSON. LLMs can hallucinate fields, miss required properties, or produce malformed JSON.

**Mitigations**:
- Use Groq's JSON mode (`response_format: {"type": "json_object"}`)
- Pydantic validation on every agent output before writing to state
- Include the exact schema in agent system prompts with examples
- Retry with error feedback if validation fails (up to 2 retries)
- Keep output schemas as flat and simple as possible

**Risk Level**: 🟡 Medium — Llama 3.3 70B is generally good at JSON but can struggle with deeply nested structures

---

### 2. IR Schema Evolution

**Challenge**: As we add features (Phase 2 audio, Phase 3 new scene types), the IR schema will evolve. Old projects must remain loadable.

**Mitigations**:
- Version field in IR (`"version": "1.0.0"`)
- Backwards-compatible additions only (new optional fields, never removing required fields)
- Migration scripts when breaking changes are unavoidable
- Default values for all optional fields

**Risk Level**: 🟢 Low — manageable with discipline

---

### 3. Remotion Rendering Performance

**Challenge**: Remotion renders each frame by taking a screenshot of a React component. Complex scenes with many elements can be slow (30fps × 35s = 1050 frames).

**Mitigations**:
- Keep element count per scene reasonable (<20 elements)
- Use simple CSS transforms (GPU-accelerated) over complex SVG manipulations
- Remotion's `--concurrency` flag for parallel frame rendering
- Output at 720p for previews, 1080p for final only
- Profile and optimize hot paths in Remotion components

**Risk Level**: 🟡 Medium — renders should complete in 60-120s for Phase 1 complexity

---

### 4. Motion Quality & Coherence

**Challenge**: LLM-generated motion plans may not feel "professional." Timing, easing, and stagger decisions require genuine motion design expertise.

**Mitigations**:
- Strong motion token system with curated presets (not arbitrary numbers)
- Motion Agent prompt includes motion design principles and anti-patterns
- Constrain choices to a vocabulary of proven patterns rather than arbitrary keyframes
- Verifier checks for basic motion sanity (no overlapping animations, minimum resting time)
- Iterate on prompts with real output feedback

**Risk Level**: 🟡 Medium — this is where the most creative iteration will be needed

---

### 5. Token / Context Window Limits

**Challenge**: Agent prompts include system prompt + IR schema reference + upstream outputs + task instructions. Must stay within model context limits.

**Mitigations**:
- Groq's Llama 3.3 70B has 128K context — generous
- But keep prompts lean for speed (larger prompts = slower and costlier)
- Each agent sees only relevant upstream data, not the full state
- Summarize verbose upstream outputs before passing downstream
- Target <4000 tokens total (prompt + response) per agent call for fast Groq inference

**Risk Level**: 🟢 Low — 128K context is ample for our use case

---

### 6. SVG / Visual Asset Generation

**Challenge**: Phase 1 relies on parameterized shapes and text — limited visual richness. Phase 2+ needs richer assets.

**Mitigations (Phase 1)**:
- Focus on what looks good with shapes: geometric patterns, gradients, particles, kinetic text
- Use glow effects, layering, and motion to compensate for simple shapes
- Curate a library of motion patterns that make simple elements feel premium

**Mitigations (Phase 2+)**:
- LLM-generated SVG for custom illustrations (test quality before relying on it)
- Bundled SVG icon/illustration library for common elements
- External asset API integration (Unsplash, Storyset) for richer visuals

**Risk Level**: 🟡 Medium — Phase 1 will look "motion-graphics-y" not "illustrated," which is acceptable for Tier 1

---

### 7. Audio Synchronization

**Challenge (Phase 2)**: Audio events (SFX, VO, music beats) must precisely align with visual events. Misalignment is immediately noticeable.

**Mitigations**:
- Audio timing is defined in the IR with frame-accurate precision
- FFmpeg muxing uses exact timestamps
- TTS generates duration estimates before IR assembly so scenes can accommodate VO
- Build a sync verification check in the Verifier

**Risk Level**: 🟡 Medium — deferred to Phase 2

---

### 8. Error Recovery & Debugging

**Challenge**: When the pipeline fails (LLM returns bad JSON, Remotion render crashes, FFmpeg errors), diagnosing the failure can be hard.

**Mitigations**:
- Structured logging at every agent step (agent name, input hash, output hash, duration)
- Full agent trace stored in SQLite (agent_logs table)
- WebSocket error events pushed to dashboard in real-time
- Each agent's raw LLM response stored for debugging
- Verifier provides actionable error messages with routing hints

**Risk Level**: 🟢 Low — good logging solved this in the Replit architecture

---

## Performance Considerations

| Operation | Expected Time | Bottleneck |
|-----------|--------------|------------|
| Manager Agent | 2-3s | LLM inference |
| Script Agent | 3-5s | LLM inference (creative generation) |
| Visual Design Agent | 3-5s | LLM inference |
| Motion Agent | 3-5s | LLM inference |
| Audio Agent (Phase 1 stub) | <1s | No LLM call needed |
| Rendering Orchestrator | 2-3s | IR assembly + validation |
| Remotion Render (1080p, 35s) | 60-120s | CPU-bound frame rendering |
| FFmpeg Post-processing | 5-10s | Encoding |
| Verifier | 1-2s | Validation checks |
| **Total Pipeline** | **~2-3 minutes** | Remotion rendering dominates |

---

## Security Considerations

- **API Keys**: Stored in `.env`, never committed to git. Add `.env` to `.gitignore`.
- **LLM Injection**: Agents produce structured data, not executable code. IR is validated before use.
- **Subprocess Execution**: Remotion and FFmpeg invoked with argument arrays, not shell strings. No shell injection risk.
- **File System**: Agents write only to designated directories (IR, renders). No arbitrary file access.
- **WebSocket**: Local-only (localhost binding). No authentication needed for Phase 1.

---

## Known Limitations (Phase 1)

1. **No audio** — videos are silent. SFX and music deferred to Phase 2.
2. **No voiceover** — TTS integration deferred to Phase 2.
3. **Manual theme selection only** — no AI-driven theme exploration yet.
4. **No undo/redo** — checkpoint and rollback deferred to Phase 2.
5. **No concurrent agents** — strictly sequential pipeline.
6. **No custom assets** — only parameterized shapes, text, and particles.
7. **No platform-specific exports** — single output format (1080p MP4).
8. **Single user only** — no auth, no multi-user support.
9. **No editing after generation** — regenerate from scratch to make changes.
10. **English only** — prompts and generated content assume English.

---

## Future Technical Debt to Watch

- [ ] IR schema Python ↔ TypeScript sync (manual currently, should auto-generate)
- [ ] Agent prompt management (currently inline strings, should be template files)
- [ ] Test coverage for Remotion components (currently untested)
- [ ] Database migrations (currently using create_all, should use Alembic)
- [ ] WebSocket reconnection handling in dashboard
- [ ] Render queue (currently one-at-a-time, should queue multiple projects)
