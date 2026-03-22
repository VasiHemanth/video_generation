# Video IR (Intermediate Representation) Specification

## Overview

The Video IR is the **single source of truth** for every video project. It is a typed JSON document that fully describes a video's content, visuals, motion, audio, and constraints. All agents write to it, and the Remotion rendering pipeline reads from it deterministically.

**Key principle**: IR → Remotion is a pure, deterministic compilation. No LLM is involved in rendering — only in producing the IR.

---

## Top-Level Schema

```json
{
  "version": "1.0.0",
  "meta": { /* ProjectMeta */ },
  "theme": { /* ThemeTokens */ },
  "timeline": { /* Timeline */ },
  "audio": { /* AudioPlan */ },
  "assets": { /* AssetRegistry */ },
  "constraints": { /* ProjectConstraints */ }
}
```

---

## `meta` — Project Metadata

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `id` | string | yes | uuid | Unique project identifier |
| `title` | string | yes | — | Video title |
| `description` | string | no | "" | Brief description of the video |
| `duration` | number | yes | 35.0 | Total duration in seconds (30–40) |
| `fps` | number | yes | 30 | Frames per second |
| `width` | number | yes | 1920 | Canvas width in pixels |
| `height` | number | yes | 1080 | Canvas height in pixels |
| `aspect_ratio` | string | yes | "16:9" | "16:9", "9:16", or "1:1" |
| `created_at` | string | yes | — | ISO 8601 timestamp |
| `status` | string | yes | "draft" | "draft", "generating", "rendered", "failed" |

---

## `theme` — Design Tokens

### `theme.colors`

| Token | Type | Example | Usage |
|-------|------|---------|-------|
| `bg_primary` | hex | "#0A0A0F" | Main background |
| `bg_secondary` | hex | "#12121A" | Card / panel backgrounds |
| `fg_primary` | hex | "#FFFFFF" | Primary text |
| `fg_secondary` | hex | "#A0A0B0" | Secondary / muted text |
| `accent_1` | hex | "#6C5CE7" | Primary accent (headings, highlights) |
| `accent_2` | hex | "#00CEC9" | Secondary accent (charts, links) |
| `accent_3` | hex | "#FD79A8" | Tertiary accent (alerts, emphasis) |
| `gradient_start` | hex | "#6C5CE7" | Gradient start color |
| `gradient_end` | hex | "#00CEC9" | Gradient end color |
| `surface` | hex | "#1A1A2E" | Elevated surface color |
| `border` | hex | "#2D2D44" | Border / separator color |

### `theme.typography`

| Token | Font Family | Weight | Size (px) | Line Height | Usage |
|-------|-------------|--------|-----------|-------------|-------|
| `display_lg` | Inter | 800 | 72 | 1.1 | Hero headlines |
| `display_md` | Inter | 700 | 56 | 1.15 | Section titles |
| `display_sm` | Inter | 700 | 40 | 1.2 | Subtitles |
| `heading_lg` | Inter | 600 | 32 | 1.3 | Card headings |
| `heading_md` | Inter | 600 | 24 | 1.35 | Labels |
| `body_lg` | Inter | 400 | 20 | 1.5 | Large body text |
| `body_md` | Inter | 400 | 16 | 1.5 | Standard body |
| `caption` | Inter | 400 | 14 | 1.4 | Captions |
| `code` | JetBrains Mono | 400 | 16 | 1.5 | Code snippets |

### `theme.motion`

| Token | Value | Description |
|-------|-------|-------------|
| `duration_fast` | 0.2 | Quick micro-interactions (s) |
| `duration_normal` | 0.4 | Standard transitions (s) |
| `duration_slow` | 0.8 | Dramatic reveals (s) |
| `duration_very_slow` | 1.2 | Cinematic movements (s) |
| `easing_default` | "ease-out" | Standard easing |
| `easing_enter` | "ease-out" | Elements entering |
| `easing_exit` | "ease-in" | Elements leaving |
| `easing_bounce` | "cubic-bezier(0.68, -0.55, 0.27, 1.55)" | Playful overshoot |
| `easing_spring` | { mass: 1, damping: 12, stiffness: 200 } | Spring physics |
| `stagger_delay` | 0.08 | Delay between staggered items (s) |

### `theme.layout`

| Token | Value | Description |
|-------|-------|-------------|
| `padding` | 60 | Safe area padding (px) |
| `gap` | 24 | Standard gap between elements (px) |
| `card_radius` | 16 | Border radius for cards (px) |
| `safe_area_x` | 120 | Horizontal safe zone (px) |
| `safe_area_y` | 80 | Vertical safe zone (px) |

---

## `timeline` — Scene Timeline

### Scene

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Unique scene ID (e.g., "scene_001") |
| `role` | string | yes | "intro", "setup", "demo", "payoff", "cta", "outro" |
| `title` | string | no | Internal label for the scene |
| `start_time` | number | yes | Start time in seconds |
| `duration` | number | yes | Duration in seconds (min 2s, max 15s) |
| `transition_in` | TransitionConfig | no | How this scene enters |
| `transition_out` | TransitionConfig | no | How this scene exits |
| `background` | BackgroundConfig | yes | Scene background |
| `elements` | Element[] | yes | All visual elements in this scene |

### TransitionConfig

| Field | Type | Options |
|-------|------|---------|
| `type` | string | "cut", "fade", "slide-left", "slide-right", "slide-up", "wipe", "morph" |
| `duration` | number | Transition duration in seconds |
| `easing` | string | Easing function name or cubic-bezier |

### BackgroundConfig

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | "solid", "gradient", "radial-gradient", "animated-gradient", "mesh" |
| `colors` | string[] | Color values (references to theme tokens or hex) |
| `angle` | number | Gradient angle in degrees (for linear gradients) |
| `animate` | boolean | Whether background animates |
| `animation_speed` | number | If animated, speed multiplier |

### Element

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Unique element ID |
| `type` | string | yes | "text", "shape", "group", "progress", "counter", "code-block", "icon", "particle-field", "divider", "image" |
| `props` | object | yes | Type-specific properties (see below) |
| `position` | { x, y } | yes | Position (absolute px or percentage string) |
| `size` | { width, height } | no | Element size |
| `anchor` | string | no | "top-left", "center", "bottom-right", etc. |
| `layer` | number | yes | Z-index for layering (0 = bottom) |
| `opacity` | number | no | Static opacity (0-1), default 1 |
| `rotation` | number | no | Static rotation in degrees, default 0 |
| `scale` | number | no | Static scale, default 1 |
| `enter` | AnimationConfig | no | Entry animation |
| `exit` | AnimationConfig | no | Exit animation |
| `emphasis` | AnimationConfig | no | Mid-scene emphasis (pulse, shake, etc.) |
| `keyframes` | Keyframe[] | no | Custom keyframe animations |
| `delay` | number | no | Delay before element appears (seconds from scene start) |

### Element Props by Type

**`text`**
```json
{
  "content": "Hello World",
  "style_token": "display_lg",
  "color": "fg_primary",
  "align": "center",
  "max_width": 800,
  "word_animation": "none" | "word-by-word" | "char-by-char" | "line-by-line",
  "word_stagger": 0.05,
  "highlight_words": [{ "word": "AI", "color": "accent_1" }]
}
```

**`shape`**
```json
{
  "shape": "circle" | "rectangle" | "rounded-rect" | "triangle" | "polygon" | "star" | "line" | "arc",
  "fill": "accent_1",
  "stroke": "border",
  "stroke_width": 2,
  "sides": 6,
  "corner_radius": 16,
  "glow": { "color": "accent_1", "blur": 20, "opacity": 0.3 }
}
```

**`progress`**
```json
{
  "variant": "bar" | "circle" | "semicircle",
  "value": 75,
  "max": 100,
  "color": "accent_2",
  "track_color": "surface",
  "thickness": 8,
  "animate_to": 75,
  "label": "75%"
}
```

**`counter`**
```json
{
  "from": 0,
  "to": 10000,
  "prefix": "$",
  "suffix": "+",
  "style_token": "display_md",
  "color": "accent_1",
  "format": "comma-separated"
}
```

**`code-block`**
```json
{
  "code": "const agent = new Agent();",
  "language": "typescript",
  "theme": "dark",
  "highlight_lines": [1, 3],
  "typing_effect": true,
  "typing_speed": 0.03
}
```

**`particle-field`**
```json
{
  "count": 30,
  "color": "accent_1",
  "size_range": [2, 6],
  "speed": 0.5,
  "connection_lines": true,
  "connection_distance": 100,
  "opacity": 0.4
}
```

**`group`**
```json
{
  "layout": "horizontal" | "vertical" | "grid",
  "gap": 24,
  "children": [ /* nested Element[] */ ]
}
```

**`divider`**
```json
{
  "orientation": "horizontal" | "vertical",
  "color": "border",
  "thickness": 2,
  "style": "solid" | "dashed" | "gradient"
}
```

### AnimationConfig

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | "fade-in", "fade-out", "slide-up", "slide-down", "slide-left", "slide-right", "scale-in", "scale-out", "spring", "bounce", "rotate-in", "blur-in", "typewriter", "wipe", "flip" |
| `duration` | number | Duration in seconds |
| `easing` | string | Easing function |
| `delay` | number | Delay before animation starts |
| `spring_config` | object | { mass, damping, stiffness } for spring animations |
| `distance` | number | Pixels to travel for slide animations |

### Keyframe

| Field | Type | Description |
|-------|------|-------------|
| `time` | number | Time within the scene (seconds from scene start) |
| `property` | string | "x", "y", "scale", "opacity", "rotation", "width", "height" |
| `value` | number | Target value at this keyframe |
| `easing` | string | Easing to use from previous keyframe to this one |

---

## `audio` — Audio Plan (Phase 2, stubbed in Phase 1)

```json
{
  "music": {
    "track_id": "ambient_tech_01",
    "volume": 0.3,
    "fade_in": 1.0,
    "fade_out": 2.0,
    "start_offset": 0
  },
  "voiceover": {
    "enabled": false,
    "segments": []
  },
  "sfx": [
    {
      "id": "sfx_001",
      "asset_id": "whoosh_01",
      "start_time": 2.5,
      "volume": 0.6,
      "role": "transition"
    }
  ]
}
```

---

## `assets` — Asset Registry

```json
{
  "fonts": [
    { "id": "inter", "family": "Inter", "source": "google-fonts" },
    { "id": "jetbrains", "family": "JetBrains Mono", "source": "google-fonts" }
  ],
  "audio": [
    { "id": "whoosh_01", "path": "sfx/whoosh_01.mp3", "duration": 0.5, "tags": ["transition"] }
  ],
  "svg": [],
  "images": []
}
```

---

## `constraints` — Project Constraints

```json
{
  "min_duration": 30,
  "max_duration": 40,
  "min_scenes": 3,
  "max_scenes": 8,
  "min_scene_duration": 2.0,
  "max_scene_duration": 15.0,
  "platform": "youtube",
  "brand": null,
  "content_safety": "standard"
}
```

---

## Validation Rules

1. `meta.duration` must be between `constraints.min_duration` and `constraints.max_duration`
2. Sum of all `scene.duration` must equal `meta.duration` (± 0.5s tolerance)
3. Number of scenes must be between `constraints.min_scenes` and `constraints.max_scenes`
4. Each `scene.duration` must be between `constraints.min_scene_duration` and `constraints.max_scene_duration`
5. Every element must have a valid `type` with matching `props`
6. All color references (e.g., `"accent_1"`) must exist in `theme.colors` or be valid hex
7. All typography references must exist in `theme.typography`
8. Scene `start_time` values must be sequential and non-overlapping
9. Element `layer` values within a scene must be unique

---

## Example: Minimal Valid IR

```json
{
  "version": "1.0.0",
  "meta": {
    "id": "proj_001",
    "title": "What is AI?",
    "duration": 35.0,
    "fps": 30,
    "width": 1920,
    "height": 1080,
    "aspect_ratio": "16:9",
    "created_at": "2026-03-20T17:00:00Z",
    "status": "draft"
  },
  "theme": {
    "colors": {
      "bg_primary": "#0A0A0F",
      "fg_primary": "#FFFFFF",
      "accent_1": "#6C5CE7",
      "accent_2": "#00CEC9"
    },
    "typography": {
      "display_lg": { "family": "Inter", "weight": 800, "size": 72 },
      "body_md": { "family": "Inter", "weight": 400, "size": 16 }
    },
    "motion": {
      "duration_normal": 0.4,
      "easing_default": "ease-out",
      "easing_spring": { "mass": 1, "damping": 12, "stiffness": 200 }
    },
    "layout": { "padding": 60, "gap": 24 }
  },
  "timeline": {
    "scenes": [
      {
        "id": "scene_001",
        "role": "intro",
        "title": "Title Reveal",
        "start_time": 0,
        "duration": 7,
        "background": { "type": "gradient", "colors": ["#0A0A0F", "#1A1A2E"], "angle": 135 },
        "elements": [
          {
            "id": "el_001",
            "type": "text",
            "props": { "content": "What is AI?", "style_token": "display_lg", "color": "fg_primary", "align": "center" },
            "position": { "x": "50%", "y": "45%" },
            "anchor": "center",
            "layer": 1,
            "enter": { "type": "spring", "duration": 0.8 }
          }
        ]
      }
    ]
  },
  "audio": { "music": null, "voiceover": { "enabled": false }, "sfx": [] },
  "assets": { "fonts": [{ "id": "inter", "family": "Inter", "source": "google-fonts" }], "audio": [], "svg": [], "images": [] },
  "constraints": { "min_duration": 30, "max_duration": 40, "min_scenes": 3, "max_scenes": 8 }
}
```
