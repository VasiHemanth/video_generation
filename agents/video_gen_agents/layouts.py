"""Expanded layout engine with 10+ layout templates.

Maps layout_hint strings (from archetypes or LLM) to rich Scene layouts
with varied element compositions. Each layout is a function that takes
a beat and theme, returning positioned elements.
"""

from __future__ import annotations

from typing import Any

from .models import (
    BackgroundConfig,
    Element,
    Position,
    SceneLayout,
    ScriptBeat,
    Size,
    StoryboardScene,
    ThemeTokens,
)


def _text_element(
    *,
    element_id: str,
    content: str,
    style_token: str,
    color: str,
    x: str,
    y: str,
    layer: int,
    align: str = "center",
    max_width: int = 1100,
) -> Element:
    return Element(
        id=element_id,
        type="text",
        props={
            "content": content,
            "style_token": style_token,
            "color": color,
            "align": align,
            "max_width": max_width,
            "word_animation": "word-by-word",
            "word_stagger": 0.02,
        },
        position=Position(x=x, y=y),
        anchor="center",
        layer=layer,
    )


def _particles(scene_id: str, index: int) -> Element:
    return Element(
        id=f"{scene_id}_particles",
        type="particle-field",
        props={
            "count": 24 + (index * 5),
            "color": "accent_2" if index % 2 else "accent_1",
            "size_range": [2, 5],
            "speed": 0.3,
            "connection_lines": False,
            "opacity": 0.15,
        },
        position=Position(x="0%", y="0%"),
        size=Size(width="100%", height="100%"),
        layer=0,
        parallax_factor=0.1,
    )


def _accent_shape(
    scene_id: str,
    *,
    shape: str = "circle",
    fill: str = "accent_1",
    x: str = "80%",
    y: str = "18%",
    w: int = 160,
    h: int = 160,
    layer: int = 1,
    opacity: float = 0.12,
    rotation: float = 12.0,
) -> Element:
    return Element(
        id=f"{scene_id}_accent_{layer}",
        type="shape",
        props={
            "shape": shape,
            "fill": fill,
            "stroke": "border",
            "stroke_width": 1,
            "corner_radius": 28 if shape == "circle" else 20,
        },
        position=Position(x=x, y=y),
        size=Size(width=w, height=h),
        anchor="center",
        layer=layer,
        opacity=opacity,
        rotation=rotation,
        parallax_factor=0.2,
    )


def _glassmorphism_card(
    scene_id: str,
    *,
    x: str = "50%",
    y: str = "50%",
    w: int = 800,
    h: int = 420,
    layer: int = 1,
) -> Element:
    return Element(
        id=f"{scene_id}_glass_card",
        type="shape",
        props={
            "shape": "rounded-rect",
            "fill": "surface",
            "stroke": "border",
            "stroke_width": 1,
            "corner_radius": 24,
        },
        position=Position(x=x, y=y),
        size=Size(width=w, height=h),
        anchor="center",
        layer=layer,
        opacity=0.6,
    )


def _divider(
    scene_id: str,
    *,
    x: str = "50%",
    y: str = "50%",
    width: int = 600,
    color: str = "accent_1",
    layer: int,
) -> Element:
    return Element(
        id=f"{scene_id}_divider_{layer}",
        type="divider",
        props={"orientation": "horizontal", "thickness": 2, "color": color},
        position=Position(x=x, y=y),
        size=Size(width=width, height=2),
        anchor="center",
        layer=layer,
    )


def _counter_element(
    scene_id: str,
    *,
    from_val: int = 0,
    to_val: int = 87,
    prefix: str = "",
    suffix: str = "%",
    color: str = "accent_1",
    x: str = "50%",
    y: str = "40%",
    layer: int = 2,
) -> Element:
    return Element(
        id=f"{scene_id}_counter",
        type="counter",
        props={
            "from": from_val,
            "to": to_val,
            "prefix": prefix,
            "suffix": suffix,
            "style_token": "display_md",
            "color": color,
            "format": "comma-separated",
        },
        position=Position(x=x, y=y),
        anchor="center",
        layer=layer,
    )


def _progress_bar(
    scene_id: str,
    *,
    value: int = 78,
    label: str = "",
    color: str = "accent_2",
    x: str = "50%",
    y: str = "68%",
    width: int = 680,
    layer: int = 5,
) -> Element:
    return Element(
        id=f"{scene_id}_progress",
        type="progress",
        props={
            "variant": "bar",
            "value": value,
            "max": 100,
            "color": color,
            "track_color": "surface",
            "thickness": 12,
            "animate_to": value,
            "label": label,
        },
        position=Position(x=x, y=y),
        size=Size(width=width, height=32),
        anchor="center",
        layer=layer,
    )


# ── Background generators ─────────────────────────────────────────────────────


def _bg_gradient(index: int) -> BackgroundConfig:
    return BackgroundConfig(
        type="gradient",
        colors=["bg_primary", "surface"],
        angle=135 + (index * 15),  # Vary angle per scene
    )


def _bg_animated(index: int) -> BackgroundConfig:
    return BackgroundConfig(
        type="animated-gradient",
        colors=["bg_primary", "surface"],
        angle=120 + (index * 20),
        animate=True,
        animation_speed=0.35,
    )


def _bg_radial(index: int) -> BackgroundConfig:
    return BackgroundConfig(
        type="radial-gradient",
        colors=["surface", "bg_primary"],
    )


def _bg_mesh() -> BackgroundConfig:
    return BackgroundConfig(
        type="mesh",
        colors=["bg_primary", "surface", "bg_secondary"],
        angle=150,
    )


def _pick_bg(index: int, total: int) -> BackgroundConfig:
    """Pick a background style based on position in the video."""
    if index == 0:
        return _bg_animated(index)  # Opening is always animated
    if index == total - 1:
        return _bg_radial(index)    # CTA gets radial
    if index % 3 == 0:
        return _bg_mesh()
    if index % 2 == 0:
        return _bg_animated(index)
    return _bg_gradient(index)


# ── Layout templates ───────────────────────────────────────────────────────────


def layout_centered_hero(
    scene_id: str,
    beat: ScriptBeat,
    index: int,
    total: int,
) -> SceneLayout:
    """Big headline centered, subtitle below, accent shapes in corners."""
    return SceneLayout(
        scene_id=scene_id,
        background=_pick_bg(index, total),
        elements=[
            _particles(scene_id, index),
            _accent_shape(scene_id, shape="circle", fill="accent_1", x="82%", y="14%", w=180, h=180, layer=1, rotation=15),
            _accent_shape(scene_id, shape="rounded-rect", fill="accent_3", x="12%", y="82%", w=120, h=120, layer=2, rotation=-10),
            _text_element(
                element_id=f"{scene_id}_headline",
                content=beat.headline_text or beat.text,
                style_token="display_md",
                color="fg_primary",
                x="50%", y="32%", layer=3,
            ),
            _text_element(
                element_id=f"{scene_id}_subtitle",
                content=beat.subtitle_text,
                style_token="body_lg",
                color="fg_secondary",
                x="50%", y="54%", layer=4, max_width=900,
            ),
            _divider(scene_id, x="50%", y="68%", width=200, color="accent_1", layer=5),
        ],
    )


def layout_split_layout(
    scene_id: str,
    beat: ScriptBeat,
    index: int,
    total: int,
) -> SceneLayout:
    """Headline left-aligned top, body below, device mockup on right side."""
    return SceneLayout(
        scene_id=scene_id,
        background=_pick_bg(index, total),
        elements=[
            _particles(scene_id, index),
            _accent_shape(scene_id, shape="rounded-rect", fill="accent_2", x="88%", y="20%", w=140, h=140, layer=1, rotation=20),
            _text_element(
                element_id=f"{scene_id}_headline",
                content=beat.headline_text or beat.text,
                style_token="heading_lg",
                color="fg_primary",
                x="32%", y="28%", layer=2, max_width=520, align="left",
            ),
            _text_element(
                element_id=f"{scene_id}_subtitle",
                content=beat.subtitle_text,
                style_token="body_lg",
                color="fg_secondary",
                x="32%", y="50%", layer=3, max_width=520, align="left",
            ),
            _divider(scene_id, x="32%", y="65%", width=280, color="accent_2", layer=4),
            Element(
                id=f"{scene_id}_device",
                type="device",
                props={"variant": "phone", "color": "accent_1"},
                position=Position(x="76%", y="55%"),
                size=Size(width=220, height=400),
                anchor="center",
                layer=5, parallax_factor=-0.08,
            ),
        ],
    )


def layout_feature_showcase(
    scene_id: str,
    beat: ScriptBeat,
    index: int,
    total: int,
) -> SceneLayout:
    """Glassmorphism card with headline, body, and visual accent."""
    return SceneLayout(
        scene_id=scene_id,
        background=_pick_bg(index, total),
        elements=[
            _particles(scene_id, index),
            _glassmorphism_card(scene_id, x="50%", y="50%", w=860, h=440, layer=1),
            _accent_shape(scene_id, shape="circle", fill="accent_1", x="20%", y="30%", w=60, h=60, layer=2, opacity=0.3),
            _text_element(
                element_id=f"{scene_id}_headline",
                content=beat.headline_text or beat.text,
                style_token="heading_lg",
                color="fg_primary",
                x="50%", y="34%", layer=3,
            ),
            _text_element(
                element_id=f"{scene_id}_subtitle",
                content=beat.subtitle_text,
                style_token="body_lg",
                color="fg_secondary",
                x="50%", y="52%", layer=4, max_width=720,
            ),
            _divider(scene_id, x="50%", y="65%", width=300, color="accent_1", layer=5),
            Element(
                id=f"{scene_id}_device",
                type="device",
                props={"variant": "browser", "color": "accent_2"},
                position=Position(x="50%", y="80%"),
                size=Size(width=400, height=200),
                anchor="center",
                layer=6, parallax_factor=-0.06,
            ),
        ],
    )


def layout_stat_showcase(
    scene_id: str,
    beat: ScriptBeat,
    index: int,
    total: int,
) -> SceneLayout:
    """Counter + progress bar + headline for data-heavy scenes."""
    # Try to extract a number from the headline for the counter
    import re
    numbers = re.findall(r"(\d+)", beat.headline_text or "87")
    counter_val = int(numbers[0]) if numbers else 87

    return SceneLayout(
        scene_id=scene_id,
        background=_pick_bg(index, total),
        elements=[
            _particles(scene_id, index),
            _accent_shape(scene_id, shape="circle", fill="accent_2", x="82%", y="18%", w=200, h=200, layer=1, opacity=0.1),
            _counter_element(scene_id, to_val=counter_val, suffix="%", color="accent_1", x="50%", y="30%", layer=2),
            _text_element(
                element_id=f"{scene_id}_headline",
                content=beat.headline_text or beat.text,
                style_token="heading_lg",
                color="fg_primary",
                x="50%", y="48%", layer=3,
            ),
            _text_element(
                element_id=f"{scene_id}_subtitle",
                content=beat.subtitle_text,
                style_token="body_lg",
                color="fg_secondary",
                x="50%", y="62%", layer=4, max_width=800,
            ),
            _progress_bar(scene_id, value=counter_val, label=f"{counter_val}% improvement", color="accent_2", y="78%", layer=5),
        ],
    )


def layout_icon_grid(
    scene_id: str,
    beat: ScriptBeat,
    index: int,
    total: int,
) -> SceneLayout:
    """Grid of small cards suggesting integrations/features."""
    # Create a grid of small shapes to represent icons/cards
    grid_elements: list[Element] = [
        _particles(scene_id, index),
        _text_element(
            element_id=f"{scene_id}_headline",
            content=beat.headline_text or beat.text,
            style_token="heading_lg",
            color="fg_primary",
            x="50%", y="18%", layer=1,
        ),
        _text_element(
            element_id=f"{scene_id}_subtitle",
            content=beat.subtitle_text,
            style_token="body_lg",
            color="fg_secondary",
            x="50%", y="32%", layer=2, max_width=800,
        ),
    ]

    # Create a 3x2 grid of cards
    colors = ["accent_1", "accent_2", "accent_3", "accent_1", "accent_2", "accent_3"]
    positions = [
        ("25%", "52%"), ("50%", "52%"), ("75%", "52%"),
        ("25%", "74%"), ("50%", "74%"), ("75%", "74%"),
    ]
    for i, (px, py) in enumerate(positions):
        grid_elements.append(Element(
            id=f"{scene_id}_card_{i}",
            type="shape",
            props={
                "shape": "rounded-rect",
                "fill": colors[i],
                "stroke": "border",
                "stroke_width": 1,
                "corner_radius": 16,
            },
            position=Position(x=px, y=py),
            size=Size(width=180, height=120),
            anchor="center",
            layer=3 + i,
            opacity=0.2,
        ))

    return SceneLayout(
        scene_id=scene_id,
        background=_pick_bg(index, total),
        elements=grid_elements,
    )


def layout_cta_card(
    scene_id: str,
    beat: ScriptBeat,
    index: int,
    total: int,
) -> SceneLayout:
    """Call-to-action with glassmorphism card, headline, and button."""
    return SceneLayout(
        scene_id=scene_id,
        background=_bg_radial(index),
        elements=[
            _particles(scene_id, index),
            _glassmorphism_card(scene_id, x="50%", y="48%", w=780, h=380, layer=1),
            _text_element(
                element_id=f"{scene_id}_headline",
                content=beat.headline_text or beat.text,
                style_token="display_sm",
                color="fg_primary",
                x="50%", y="34%", layer=2,
            ),
            _text_element(
                element_id=f"{scene_id}_subtitle",
                content=beat.subtitle_text,
                style_token="body_lg",
                color="fg_secondary",
                x="50%", y="50%", layer=3, max_width=650,
            ),
            # Button shape
            Element(
                id=f"{scene_id}_btn",
                type="shape",
                props={
                    "shape": "rounded-rect",
                    "fill": "accent_1",
                    "stroke": "accent_1",
                    "stroke_width": 0,
                    "corner_radius": 16,
                },
                position=Position(x="50%", y="66%"),
                size=Size(width=340, height=60),
                anchor="center",
                layer=4,
            ),
            _text_element(
                element_id=f"{scene_id}_btn_label",
                content="Get Started",
                style_token="heading_md",
                color="fg_primary",
                x="50%", y="66%", layer=5,
            ),
        ],
    )


def layout_quote(
    scene_id: str,
    beat: ScriptBeat,
    index: int,
    total: int,
) -> SceneLayout:
    """Large quote with decorative accent - good for testimonials."""
    return SceneLayout(
        scene_id=scene_id,
        background=_pick_bg(index, total),
        elements=[
            _particles(scene_id, index),
            # Large decorative quote mark
            _text_element(
                element_id=f"{scene_id}_quote_mark",
                content="\u201C",
                style_token="display_lg",
                color="accent_1",
                x="18%", y="28%", layer=1,
            ),
            _glassmorphism_card(scene_id, x="50%", y="50%", w=900, h=360, layer=2),
            _text_element(
                element_id=f"{scene_id}_headline",
                content=beat.headline_text or beat.text,
                style_token="heading_lg",
                color="fg_primary",
                x="50%", y="42%", layer=3, max_width=760,
            ),
            _text_element(
                element_id=f"{scene_id}_subtitle",
                content=beat.subtitle_text,
                style_token="body_lg",
                color="fg_secondary",
                x="50%", y="60%", layer=4, max_width=700,
            ),
            _divider(scene_id, x="50%", y="72%", width=160, color="accent_1", layer=5),
        ],
    )


def layout_timeline_steps(
    scene_id: str,
    beat: ScriptBeat,
    index: int,
    total: int,
) -> SceneLayout:
    """Step indicator with numbered circle + description."""
    # Extract step number from beat type (step_1, step_2, step_3)
    import re
    step_match = re.search(r"(\d+)", beat.type)
    step_num = step_match.group(1) if step_match else str(index)

    return SceneLayout(
        scene_id=scene_id,
        background=_pick_bg(index, total),
        elements=[
            _particles(scene_id, index),
            # Step number circle
            Element(
                id=f"{scene_id}_step_circle",
                type="shape",
                props={
                    "shape": "circle",
                    "fill": "accent_1",
                    "stroke": "accent_1",
                    "stroke_width": 0,
                    "corner_radius": 999,
                },
                position=Position(x="50%", y="24%"),
                size=Size(width=100, height=100),
                anchor="center",
                layer=1,
                opacity=0.25,
            ),
            _text_element(
                element_id=f"{scene_id}_step_num",
                content=step_num,
                style_token="display_md",
                color="fg_primary",
                x="50%", y="24%", layer=2,
            ),
            _text_element(
                element_id=f"{scene_id}_headline",
                content=beat.headline_text or beat.text,
                style_token="heading_lg",
                color="fg_primary",
                x="50%", y="45%", layer=3,
            ),
            _text_element(
                element_id=f"{scene_id}_subtitle",
                content=beat.subtitle_text,
                style_token="body_lg",
                color="fg_secondary",
                x="50%", y="60%", layer=4, max_width=800,
            ),
            _progress_bar(scene_id, value=int(float(step_num) / 3 * 100), label=f"Step {step_num} of 3", color="accent_1", y="78%", width=500, layer=5),
        ],
    )


# ── Layout dispatcher ──────────────────────────────────────────────────────────

LAYOUT_MAP = {
    "centered_hero": layout_centered_hero,
    "split_layout": layout_split_layout,
    "feature_showcase": layout_feature_showcase,
    "stat_showcase": layout_stat_showcase,
    "icon_grid": layout_icon_grid,
    "cta_card": layout_cta_card,
    "quote": layout_quote,
    "timeline_steps": layout_timeline_steps,
}


def build_layouts_v2(
    storyboard: list[StoryboardScene],
    script_beats: list[ScriptBeat],
    theme: ThemeTokens,
) -> list[SceneLayout]:
    """Build rich, varied scene layouts using the new layout templates."""
    beats_by_id = {b.id: b for b in script_beats}
    total = len(storyboard)
    layouts: list[SceneLayout] = []

    for index, scene in enumerate(storyboard):
        beat = beats_by_id[scene.beat_ids[0]]
        hint = scene.layout_hint or "centered_hero"

        # Map step roles to the timeline_steps layout
        if beat.type.startswith("step_"):
            hint = "timeline_steps"

        layout_fn = LAYOUT_MAP.get(hint, layout_centered_hero)
        layout = layout_fn(scene.scene_id, beat, index, total)
        layouts.append(layout)

    return layouts
