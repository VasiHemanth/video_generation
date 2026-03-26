# Phase 3: Motion Intelligence, SVG Components & Scene Templates

> **Status**: Planning Complete · Awaiting Execution  
> **Branch**: TBD (will branch from `main`)  
> **Date**: 2026-03-26  
> **Predecessor**: [PLAN_V2.md](./PLAN_V2.md) (Phase 2: Parallelization — ✅ Complete)

---

## Goal

Transform the pipeline from generating flat "slide-deck" videos with basic `fade`/`slide-up` animations to producing **reference-quality motion design** by:

1. Building a **dynamic SVG illustration system** (path draw-on, icon library)
2. Upgrading the **animation engine** (ambient float, extended easing, stagger groups)
3. Adding **4 new scene templates** that match professional educational shorts
4. **Enriching LLM prompts** so the Designer and Motion agents actually use the advanced features

## Background & Motivation

### Reference Analysis

A frame-by-frame analysis of [@GregIsenberg's "Claude Code + Obsidian"](https://www.youtube.com/shorts/yJK5GueSHmU) YouTube Short revealed that the entire 60s video uses only **6 animation primitives** and **~7 scene patterns**:

| Primitive | Parameters | Status in Our Engine |
|:---|:---|:---|
| Spring pop | mass:1, damping:14, stiffness:180 | ✅ Supported, never generated |
| Stagger delay | 100-200ms per item | ❌ Missing |
| Typewriter text | 80ms/char, cursor blink | ⚠️ word-by-word exists, char-by-char missing |
| Spatial reposition | spring + translateY | ❌ Missing (hard, deferred) |
| SVG path draw-on | stroke-dashoffset animation | ❌ Missing |
| Ambient float | Math.sin() drift | ❌ Missing |

### The Root Problem

The renderer (`animations.ts`, `ElementRenderer.tsx`) already supports spring physics, parallax, word-by-word, glassmorphism, bounce, and device mockups. But:

- `_design_scene` prompt (pipeline.py L1200) is **17 lines** with no animation vocabulary
- `_motion_scene` prompt (pipeline.py L1239) only mentions `fade`, `zoom`, `slide-left`, `spring`, `slide-up`
- The LLM defaults to the simplest options every time

---

## Workstreams

### WS1: Animation Engine Upgrades

**Files**: `animations.ts`, `ElementRenderer.tsx`, `types.ts`

#### Extended Easing Library

Add to `resolveEasing()` in `animations.ts`:

| Easing | Function | Use Case |
|:---|:---|:---|
| `ease-out-back` | `Easing.out(Easing.back(1.5))` | Overshoot on card entries |
| `ease-out-expo` | `Easing.out(Easing.exp)` | Dramatic reveals |
| `ease-in-out-expo` | `Easing.inOut(Easing.exp)` | Smooth transitions |
| `ease-out-cubic` | `Easing.out(Easing.cubic)` | Natural deceleration |

#### Ambient Float Motion

In `ElementRenderer.tsx`, read `props.ambient`:

```typescript
// Element with ambient: { type: "float", amplitude: 4, frequency: 0.3 }
const ambientY = Math.sin(frame * frequency * 0.1 + phase) * amplitude;
const ambientX = Math.cos(frame * frequency * 0.07 + phase) * amplitude * 0.5;
```

#### Stagger Group Support

Elements with `stagger_index` get auto-calculated entry delay:

```typescript
const staggerDelay = stagger_index * (stagger_delay ?? 0.1);
const effectiveEnter = { ...element.enter, delay: (enter.delay ?? 0) + staggerDelay };
```

#### 3D Depth

Elements with `props.depth_3d: true` get `perspective` + subtle `rotateY`:

```typescript
style.perspective = "1000px";
style.transform += " rotateY(2deg)";
```

---

### WS2: New Scene Templates

**File**: `layouts.py`

| Template | Visual Pattern | Reference Scene |
|:---|:---|:---|
| `layout_card_stack` | Hero card + 2-3 stagger cards below | Scene 4: Calendar → Tasks → Notes |
| `layout_terminal_demo` | Browser frame + typewriter code text | Scene 2-3: Claude Code terminal |
| `layout_list_reveal` | Container + 4-8 staggered rows | Scene 6: .MD FILE list |
| `layout_connection_graph` | 2 cards + SVG connector path | Scene 7: Graph connections |

Each template encodes the motion design knowledge (spring configs, stagger timings, ambient props) so the LLM doesn't need to guess.

---

### WS3: Dynamic SVG Components

**Files**: `models.py`, `types.ts`, `SvgRenderer.tsx` (new), `ElementRenderer.tsx`

#### New Element Types

| Type | Props | Description |
|:---|:---|:---|
| `svg-path` | `path_data`, `stroke_color`, `stroke_width`, `stroke_dash`, `draw_duration`, `draw_delay`, `fill` | Animated connecting lines/arcs using `@remotion/paths` `evolvePath()` |
| `svg-icon` | `icon_name`, `color`, `size`, `stroke_width` | Icons from built-in library |

#### Built-in Icon Library (12 icons)

| Icon | Path Description | Use Case |
|:---|:---|:---|
| `checkmark` | ✓ check path | Task completion, feature checkmarks |
| `arrow_right` | → arrow | Flow direction, navigation |
| `arrow_down` | ↓ arrow | Sequential steps |
| `document` | 📄 page outline | File references, notes |
| `calendar` | 📅 grid with marks | Date/scheduling features |
| `folder` | 📁 folder outline | Organization, vaults |
| `link` | 🔗 chain links | Connections, linking |
| `code` | `</>` brackets | Code, terminal, dev tools |
| `star` | ⭐ five-point star | Highlights, ratings |
| `gear` | ⚙ cog wheel | Settings, configuration |
| `lightning` | ⚡ bolt | Speed, performance |
| `chart_bar` | 📊 bar chart | Data, metrics |

#### SVG Path Draw-On (via `@remotion/paths`)

```typescript
import { evolvePath } from "@remotion/paths";

// progress: 0 → invisible, 1 → fully drawn
const evolved = evolvePath(progress, pathData);
// Apply strokeDasharray + strokeDashoffset to <path> element
```

**New dependency**: `npm install @remotion/paths`

---

### WS4: Prompt Enrichment

**Files**: `pipeline.py`, `archetypes.py`

#### `_design_scene` Prompt Rewrite (pipeline.py L1200-1215)

**Current** (17 lines): Generic "create a professional layout" with minimal examples.

**New** (~40 lines): Explicit menu of:
- All element types with props (text, shape, device, counter, progress, svg-path, svg-icon, particle-field, divider)
- Animation props (word_animation, glassmorphism, ambient, stagger_index, parallax_factor)
- Layout pattern suggestions per scene role
- Rules enforcing spring > fade, word-by-word for text, ambient on decorative shapes, max 5 elements

#### `_motion_scene` Prompt Rewrite (pipeline.py L1239-1248)

**Current** (9 lines): Only mentions fade/zoom/slide-left/spring/slide-up.

**New** (~30 lines): Explicit listing of:
- All 7 animation types (spring, slide-up, slide-left, fade, scale, bounce, wipe)
- All 7 easing options (ease-out, ease-in, ease-in-out, ease-out-back, ease-out-expo, ease-in-out-expo, ease-out-cubic)
- Spring config values for cards vs text vs shapes
- SVG timing rules (draw_delay after connected card enters)
- Rules enforcing spring/bounce for cards, stagger delays, zoom/cross-dissolve for scene transitions

#### Archetype Updates (archetypes.py)

- Update `layout_hint` values to use new templates (`card_stack`, `terminal_demo`, etc.)
- Enrich `visual_note` fields with specific motion instructions:
  - Reference SVG icons by name
  - Specify stagger patterns
  - Request ambient float on decorative shapes

---

### WS5: Theme Upgrade

**File**: `shared/themes/warm-clay.json` (new)

Warm beige/teal aesthetic matching the reference video:
- Light warm background (`#E8E0D4`)
- Dark surface cards (`#2D2D3A`)
- Teal accent (`#5BA8A0`)
- Purple secondary (`#7B6BA4`)
- Orange tertiary (`#E8913A`)
- Easing defaults: `ease-out-back` for entries, `ease-out-cubic` for default
- Spring config: `mass:1, damping:14, stiffness:180`

---

## File Change Matrix

| # | File | WS | Type | ~Lines |
|:---|:---|:---|:---|:---|
| 1 | `remotion/src/lib/animations.ts` | WS1 | MODIFY | +20 |
| 2 | `remotion/src/components/ElementRenderer.tsx` | WS1+WS3 | MODIFY | +50 |
| 3 | `remotion/src/types.ts` | WS1+WS3 | MODIFY | +5 |
| 4 | `agents/.../layouts.py` | WS2 | MODIFY | +200 |
| 5 | `agents/.../models.py` | WS3 | MODIFY | +15 |
| 6 | `remotion/src/components/SvgRenderer.tsx` | WS3 | **NEW** | +150 |
| 7 | `agents/.../pipeline.py` | WS4 | MODIFY | +80 |
| 8 | `agents/.../archetypes.py` | WS4 | MODIFY | +40 |
| 9 | `shared/themes/warm-clay.json` | WS5 | **NEW** | +46 |
| 10 | `remotion/package.json` | WS3 | MODIFY | +1 |

**Total**: ~600 lines across 10 files, 1 new npm dependency

---

## Execution Order

1. **WS1 + WS3 + WS5** (parallel) — Independent renderer and theme work
2. **WS2** — Templates depend on WS1 (stagger) and WS3 (svg-path)
3. **WS4** — Prompts need all templates and element types to exist
4. **Verification** — Build, generate, visual compare

---

## Verification Plan

### Automated
- `npm install && npm run build` — TypeScript + `@remotion/paths` compilation
- `pytest agents/tests/` — Pydantic accepts `svg-path` and `svg-icon` element types
- Generate test IR with each new layout template

### Visual
- Render `connection_graph` template → verify path draw-on animation
- Render `card_stack` → verify stagger cascade timing
- Render with `warm-clay` theme → verify beige/teal aesthetic
- Generate full video with brief *"How RAG works in 3 steps"* → frame comparison

---

## Deferred (Phase 4+)

- **Spatial repositioning** — Elements moving to accommodate new entries (requires layout engine rewrite)
- **Audio/TTS integration** — Real narration with word-level sync
- **SVG shape morphing** — Transitioning between SVG paths
- **Lottie animation import** — Complex illustrations from After Effects
