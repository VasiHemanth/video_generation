# How This Video Was Crafted: Frame-by-Frame Breakdown

**Video**: [Claude Code + Obsidian in under 1 minute](https://www.youtube.com/shorts/yJK5GueSHmU) by @GregIsenberg
**Format**: YouTube Short (9:16 vertical), ~60s
**Engagement**: 3.5k likes, 39 comments
**Top comment**: *"Most people here are more interested in how it was done than..."* — confirms audiences care about the craft.

---

## Scene Map (7 Scenes, ~60 seconds)

### Scene 1: The Obsidian Introduction (0-8s)
![Obsidian logo on dark card, centered on warm beige gradient background](/Users/hemanthvasi/.gemini/antigravity/brain/3f9025af-a724-474e-92b2-d12d0528ab35/frame_60pct_1774544301134.png)

**What's on screen**:
- Warm beige/cream gradient background with subtle depth (darker edges, lighter center)
- A single **3D claymorphic card** centered: dark background, rounded corners (~20px), soft drop shadow
- Inside the card: Obsidian's **purple crystal logo** (3D-rendered, with specular highlights)
- Text below logo: `"OBSIDIAN"` in spaced uppercase

**Motion techniques**:
- Card pops in with **spring physics** (overshoot ~5%, settle over 400ms)
- Logo has subtle **rotate-on-Y-axis** shimmer suggesting 3D presence
- Background is slightly animated — warm gradient subtly shifts position

**Key craft decision**: The logo card uses **real depth** (thick drop shadow + inner lighting) making it feel like a physical object floating in space.

---

### Scene 2: Claude Code Terminal (10-15s)
![Teal terminal window with "CLAUDE CODE" and slash command input](/Users/hemanthvasi/.gemini/antigravity/brain/3f9025af-a724-474e-92b2-d12d0528ab35/frame_10pct_1774544276575.png)

**What's on screen**:
- The Obsidian card has **exited** (zoomed out or faded)
- A **teal/green terminal window** dominates the center
- Window chrome: 3 dots (●●●) in top-left corner — browser/app frame
- Inside: `"CLAUDE CODE"` in a retro pixel/monospace font
- Bottom section: A command input field showing `/`

**Motion techniques**:
- Terminal window enters with a **scale-and-bounce** (starts at ~85%, overshoots to 102%, settles at 100%)
- The `"CLAUDE CODE"` text uses a **typewriter reveal** — characters appear left-to-right with cursor
- The `/` in the command field **blinks** (cursor animation)

**Key craft decision**: The terminal is rendered as a **3D object with perspective** — slight rotation on Y-axis gives it depth. The teal color is the video's "action" color — it signifies "this is the tool doing things."

---

### Scene 3: /today Command (15-20s)
![Terminal with /today command typed in, same teal card](/Users/hemanthvasi/.gemini/antigravity/brain/3f9025af-a724-474e-92b2-d12d0528ab35/frame_20pct_1774544277961.png)

**What's on screen**:
- Same terminal card, but the input field now shows `/today`
- The text was **typed out character by character** with a visible cursor

**Motion techniques**:
- **Typing animation**: Each character appears at ~80ms intervals
- The card itself has a subtle **continuous float** — micro-drift up/down (~2px amplitude)
- Caption overlay at top syncs: *"daily operations like a today command that"*

**Key craft decision**: This scene exists purely for **pacing** — it gives the viewer time to absorb "what Claude Code is" before the complexity ramps up. One concept per scene.

---

### Scene 4: Staggered Card Stack (20-30s)
![Terminal card repositioned to top, with Calendar, Tasks, and Notes cards stacking below](/Users/hemanthvasi/.gemini/antigravity/brain/3f9025af-a724-474e-92b2-d12d0528ab35/frame_30pct_1774544279400.png)

**What's on screen**:
- The Claude Code terminal has **physically moved up** to make room
- Below it, THREE dark cards have stacked vertically with ~12px gaps:
  1. **Calendar** card — with a ▦ grid icon on the right
  2. **Tasks** card — with a checklist icon, showing items: ✓ "Finish first draft", ✓ "Work on website"
  3. **Notes** card — appears in the next beat

**Motion techniques**:
- **Spatial repositioning**: The terminal card SLIDES UP with spring physics as new cards need space below — this is the most sophisticated technique in the video
- **Staggered entry**: Calendar enters first (0ms), Tasks enters ~150ms later, Notes ~300ms later
- Each card uses **slide-up + fade-in + slight scale** (starts at 95% scale)
- The Tasks card's checklist items **reveal one by one** after the card itself lands

**Key craft decision**: This is the "wow" moment. **Elements react to each other spatially** — the terminal moves because the new cards need room. This creates a feeling of a living, responsive layout, not static slides.

---

### Scene 5: Obsidian Feature Scroll (30-38s)
![Dark scrolling panel showing Plugins, Canvas, Graph, Links with descriptions](/Users/hemanthvasi/.gemini/antigravity/brain/3f9025af-a724-474e-92b2-d12d0528ab35/frame_50pct_1774544299749.png)

**What's on screen**:
- Full-screen dark panel (app screenshot mockup)
- Four feature blocks stacked vertically, each with:
  - **Bold title** in white: Plugins, Canvas, Graph, Links
  - **Description text** in gray, wrapping to 2-3 lines
  - Blue hyperlinks ("Learn more.")
- Below: A content preview with linked text (Wikipedia-style)

**Motion techniques**:
- The feature list **scrolls upward** — a simulated UI scroll revealing content progressively
- Each feature block has a **stagger-in from bottom** at ~100ms intervals
- The entire panel fades in from a slight blur — **blur-in transition**

**Key craft decision**: Instead of animating custom graphics, they **screencast the actual product UI** and animate the scroll. This is a production shortcut that looks professional because it's showing the real product.

---

### Scene 6: Vault File Structure (38-48s)

````carousel
![Vault file list with 8 ".MD FILE" entries and sidebar icons](/Users/hemanthvasi/.gemini/antigravity/brain/3f9025af-a724-474e-92b2-d12d0528ab35/frame_70pct_1774544302571.png)
<!-- slide -->
![Same vault expanded with file entries highlighted in blue and orange gradients, VAULT label at bottom](/Users/hemanthvasi/.gemini/antigravity/brain/3f9025af-a724-474e-92b2-d12d0528ab35/frame_80pct_1774544304221.png)
````

**What's on screen**:
- A **dark app mockup** with sidebar icons (edit, folder, search, etc.)
- 8 file entries: "New note 1" through "New note 8", each labeled `.MD FILE`
- Bottom reveals a **"VAULT"** label in teal with accent border

**Motion techniques**:
- File rows appear with **stagger-in from top**: each row slides in 80ms after the previous
- The first 2 rows get **highlighted** with blue/orange border-left accents — progressive color reveal
- The VAULT label at bottom enters LAST as the payoff
- The entire card has a **3D perspective tilt** — it's not perfectly flat, it's slightly rotated

**Key craft decision**: This uses a **list-reveal** pattern — items populating a container one by one. This is extremely effective for demonstrating "many things" without overwhelming. The stagger timing creates visual rhythm.

---

### Scene 7: Graph Connections + Finale (48-60s)

````carousel
![Dashed teal line drawing from top-right to bottom-left, connecting to "Project Notes" card](/Users/hemanthvasi/.gemini/antigravity/brain/3f9025af-a724-474e-92b2-d12d0528ab35/frame_90pct_1774544305697.png)
<!-- slide -->
![Final card: "Thinking Commands" in teal with rounded corners, centered](/Users/hemanthvasi/.gemini/antigravity/brain/3f9025af-a724-474e-92b2-d12d0528ab35/final_frame_1774544329986.png)
````

**What's on screen (90%)**:
- A **dashed teal SVG path** curving from the top-right corner down to a card
- The "Project Notes" card at the bottom — dark green, rounded, with a page icon
- The path **draws itself** from origin to destination

**What's on screen (final)**:
- A single centered card: `"Thinking Commands"` in white on teal
- Orange accent border on top edge
- Clean exit — this is the CTA

**Motion techniques**:
- **SVG path draw-on**: The dashed line uses `stroke-dashoffset` animation — it "draws" from point A to point B over ~800ms
- The path follows a **cubic bezier curve** — it arcs, not straight
- The "Project Notes" card enters with a **spring** AFTER the path reaches it (sequenced timing)
- Final "Thinking Commands" card enters with a **pop-and-settle** (scale from 0 → 1.05 → 1.0)

**Key craft decision**: The SVG path draw-on is the most technically sophisticated moment. It visualizes the **relationship between ideas** — which is exactly what Obsidian's graph view does. The animation IS the concept.

---

## The Production Architecture

### Rendering Stack
This is almost certainly **Remotion** (confirmed by comments). The key architectural elements:

| Component | Implementation |
|:---|:---|
| **Background** | Static warm gradient, NOT animated — all motion is in the foreground objects |
| **Cards** | React `<div>` elements with CSS `box-shadow`, `border-radius`, `backdrop-filter` |
| **3D depth** | CSS `perspective` + `transform: rotateY(2deg)` on card containers |
| **Typography** | Mix of system sans-serif (card labels) and pixel/monospace (terminal text) |
| **SVG paths** | Inline `<svg>` with `stroke-dasharray` + `stroke-dashoffset` animated via `interpolate()` |
| **Captions** | Separate layer, auto-generated word-level sync from TTS/narration |

### The 6 Animation Primitives Used

Every motion in this video can be decomposed into **6 base primitives**:

| # | Primitive | Parameters | Where Used |
|:---|:---|:---|:---|
| 1 | **Spring pop** | `mass:1, damping:14, stiffness:180` | Card entries, logo reveal, final CTA |
| 2 | **Stagger delay** | `100-200ms` per item | Card stack, file list, feature blocks |
| 3 | **Typewriter** | `80ms/char, cursor blink at 500ms` | Terminal text, command input |
| 4 | **Spatial reposition** | `spring + translateY` | Terminal sliding up for new cards |
| 5 | **Path draw-on** | `stroke-dashoffset: length → 0` over `800ms` | Graph connection line |
| 6 | **Continuous float** | `Math.sin(frame * 0.02) * 3` | Subtle drift on all cards |

### What Makes It Feel Expensive

1. **Objects respond to each other** — the terminal moves when cards appear below it
2. **Stagger creates rhythm** — nothing arrives simultaneously
3. **3D perspective** — slight tilt on cards makes them feel physical
4. **One concept per scene** — maximum 2-3 elements visible at once
5. **Consistent material** — every card uses the same shadow depth, corner radius, and color family
6. **The animation IS the content** — the path draw-on *demonstrates* graph linking, not just decorates it
