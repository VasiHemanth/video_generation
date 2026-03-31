from __future__ import annotations

import re
from typing import Any

from .models import (
    AnimationConfig,
    BackgroundConfig,
    Element,
    FlexLayout,
    Position,
    SceneLayout,
    ScriptBeat,
    Size,
    StoryboardScene,
    ThemeTokens,
)

def _particles(scene_id: str, index: int) -> Element:
    return Element(
        id=f"{scene_id}_particles",
        type="particle-field",
        positioning="absolute",
        position=Position(x="50%", y="50%"),
        size=Size(width="100%", height="100%"),
        anchor="center",
        layer=0,
        parallax_factor=0.1,
        props={
            "count": 24 + (index * 5),
            "color": "accent_2" if index % 2 else "accent_1",
            "size_range": [2, 5],
            "speed": 0.3,
            "connection_lines": False,
            "opacity": 0.15,
        },
    )

def _bg_gradient(index: int) -> BackgroundConfig:
    return BackgroundConfig(type="gradient", colors=["bg_primary", "surface"], angle=135 + (index * 15))

def _bg_animated(index: int) -> BackgroundConfig:
    return BackgroundConfig(type="animated-gradient", colors=["bg_primary", "surface"], angle=120 + (index * 20), animate=True, animation_speed=0.35)

def _bg_radial(index: int) -> BackgroundConfig:
    return BackgroundConfig(type="radial-gradient", colors=["surface", "bg_primary"])

def _bg_mesh() -> BackgroundConfig:
    return BackgroundConfig(type="mesh", colors=["bg_primary", "surface", "bg_secondary"], angle=150)

def _pick_bg(index: int, total: int) -> BackgroundConfig:
    if index == 0: return _bg_animated(index)
    if index == total - 1: return _bg_radial(index)
    if index % 3 == 0: return _bg_mesh()
    if index % 2 == 0: return _bg_animated(index)
    return _bg_gradient(index)


def layout_concept_hero(scene_id: str, beat: ScriptBeat, index: int, total: int) -> SceneLayout:
    root = Element(
        id=f"{scene_id}_root",
        type="group",
        positioning="absolute",
        position=Position(x="50%", y="50%"),
        size=Size(width=1000, height=800),
        anchor="center",
        layout=FlexLayout(display="flex", flex_direction="column", align_items="center", justify_content="center", gap=24),
        children=[
            Element(
                id=f"{scene_id}_headline",
                type="text",
                positioning="flow",
                props={
                    "content": beat.headline_text or beat.text,
                    "style_token": "display_md",
                    "color": "fg_primary",
                    "align": "center",
                    "max_width": 900,
                },
            ),
            Element(
                id=f"{scene_id}_subtitle",
                type="text",
                positioning="flow",
                props={
                    "content": beat.subtitle_text,
                    "style_token": "body_lg",
                    "color": "fg_secondary",
                    "align": "center",
                    "max_width": 800,
                },
            ),
        ]
    )
    return SceneLayout(scene_id=scene_id, background=_pick_bg(index, total), elements=[_particles(scene_id, index), root])


def layout_comparison_split(scene_id: str, beat: ScriptBeat, index: int, total: int) -> SceneLayout:
    root = Element(
        id=f"{scene_id}_root",
        type="group",
        positioning="absolute",
        position=Position(x="50%", y="50%"),
        size=Size(width="90%", height="80%"),
        anchor="center",
        layout=FlexLayout(display="flex", flex_direction="row", gap=40, align_items="center", justify_content="center"),
        children=[
            Element(
                id=f"{scene_id}_left",
                type="group",
                positioning="flow",
                layout=FlexLayout(flex_direction="column", gap=16, align_items="flex-start", justify_content="center"),
                children=[
                    Element(
                        id=f"{scene_id}_headline",
                        type="text",
                        positioning="flow",
                        props={
                            "content": beat.headline_text or beat.text,
                            "style_token": "heading_lg",
                            "color": "fg_primary",
                            "align": "left",
                            "max_width": 520,
                        },
                    ),
                    Element(
                        id=f"{scene_id}_subtitle",
                        type="text",
                        positioning="flow",
                        props={
                            "content": beat.subtitle_text,
                            "style_token": "body_lg",
                            "color": "fg_secondary",
                            "align": "left",
                            "max_width": 520,
                        },
                    ),
                ]
            ),
            Element(
                id=f"{scene_id}_right_device",
                type="device",
                positioning="flow",
                props={"variant": "phone", "color": "accent_1"},
            )
        ]
    )
    return SceneLayout(scene_id=scene_id, background=_pick_bg(index, total), elements=[_particles(scene_id, index), root])


def layout_stat_callout(scene_id: str, beat: ScriptBeat, index: int, total: int) -> SceneLayout:
    numbers = re.findall(r"(\d+)", beat.headline_text or "87")
    counter_val = int(numbers[0]) if numbers else 87
    
    root = Element(
        id=f"{scene_id}_root",
        type="group",
        positioning="absolute",
        position=Position(x="50%", y="50%"),
        size=Size(width="80%", height="80%"),
        anchor="center",
        layout=FlexLayout(display="flex", flex_direction="column", gap=24, align_items="center", justify_content="center"),
        children=[
            Element(
                id=f"{scene_id}_counter",
                type="counter",
                positioning="flow",
                props={
                    "from": 0, "to": counter_val, "suffix": "%",
                    "style_token": "display_md", "color": "accent_1", "format": "comma-separated",
                },
            ),
            Element(
                id=f"{scene_id}_headline",
                type="text",
                positioning="flow",
                props={
                    "content": beat.headline_text or beat.text,
                    "style_token": "heading_lg",
                    "color": "fg_primary",
                    "align": "center",
                },
            ),
            Element(
                id=f"{scene_id}_subtitle",
                type="text",
                positioning="flow",
                props={
                    "content": beat.subtitle_text,
                    "style_token": "body_lg",
                    "color": "fg_secondary",
                    "align": "center",
                    "max_width": 800,
                },
            ),
            Element(
                id=f"{scene_id}_progress",
                type="progress",
                positioning="flow",
                props={
                    "variant": "bar", "value": counter_val, "max": 100,
                    "color": "accent_2", "track_color": "surface", "thickness": 12,
                    "animate_to": counter_val, "label": f"{counter_val}% improvement",
                },
                size=Size(width=680, height=32),
            )
        ]
    )
    return SceneLayout(scene_id=scene_id, background=_pick_bg(index, total), elements=[_particles(scene_id, index), root])


def layout_feature_list(scene_id: str, beat: ScriptBeat, index: int, total: int) -> SceneLayout:
    items = [s.strip() for s in re.split(r"[.,;]", beat.subtitle_text) if s.strip()]
    if len(items) < 2:
        items = ["Feature One", "Feature Two", "Feature Three"]
    items = items[:3]

    rows = []
    icons = ["document", "calendar", "checkmark"]
    colors = ["accent_1", "accent_2", "accent_3"]
    for i, item in enumerate(items):
        rows.append(
            Element(
                id=f"{scene_id}_row_{i}",
                type="group",
                positioning="flow",
                layout=FlexLayout(flex_direction="row", gap=16, align_items="center"),
                children=[
                    Element(
                        id=f"{scene_id}_icon_{i}",
                        type="svg-icon",
                        positioning="flow",
                        props={"icon_name": icons[i % len(icons)], "color": colors[i % len(colors)], "size": 28},
                    ),
                    Element(
                        id=f"{scene_id}_text_{i}",
                        type="text",
                        positioning="flow",
                        props={"content": item, "style_token": "body_lg", "color": "fg_primary", "align": "left", "max_width": 500},
                    )
                ]
            )
        )

    root = Element(
        id=f"{scene_id}_root",
        type="group",
        positioning="absolute",
        position=Position(x="50%", y="50%"),
        anchor="center",
        layout=FlexLayout(display="flex", flex_direction="column", gap=40, align_items="center", justify_content="center"),
        children=[
            Element(
                id=f"{scene_id}_header",
                type="group",
                positioning="flow",
                layout=FlexLayout(flex_direction="column", gap=12, align_items="center"),
                children=[
                    Element(
                        id=f"{scene_id}_headline",
                        type="text",
                        positioning="flow",
                        props={
                            "content": beat.headline_text or beat.text,
                            "style_token": "heading_lg",
                            "color": "fg_primary",
                            "align": "center",
                        },
                    )
                ]
            ),
            Element(
                id=f"{scene_id}_list",
                type="group",
                positioning="flow",
                layout=FlexLayout(flex_direction="column", gap=24, align_items="flex-start"),
                children=rows
            )
        ]
    )
    return SceneLayout(scene_id=scene_id, background=_pick_bg(index, total), elements=[_particles(scene_id, index), root])


def layout_cta_card(scene_id: str, beat: ScriptBeat, index: int, total: int) -> SceneLayout:
    root = Element(
        id=f"{scene_id}_root",
        type="group",
        positioning="absolute",
        position=Position(x="50%", y="50%"),
        size=Size(width=780, height=480),
        anchor="center",
        layout=FlexLayout(display="flex", flex_direction="column", gap=24, align_items="center", justify_content="center", padding=40),
        props={"fill": "surface", "corner_radius": 24},  # Treated as a background fill for the group
        children=[
            Element(
                id=f"{scene_id}_headline",
                type="text",
                positioning="flow",
                props={
                    "content": beat.headline_text or beat.text,
                    "style_token": "display_sm",
                    "color": "fg_primary",
                    "align": "center",
                },
            ),
            Element(
                id=f"{scene_id}_subtitle",
                type="text",
                positioning="flow",
                props={
                    "content": beat.subtitle_text,
                    "style_token": "body_lg",
                    "color": "fg_secondary",
                    "align": "center",
                    "max_width": 650,
                },
            ),
            Element(
                id=f"{scene_id}_btn_group",
                type="group",
                positioning="flow",
                layout=FlexLayout(justify_content="center", align_items="center", padding=20),
                props={"fill": "accent_1", "corner_radius": 16},
                children=[
                    Element(
                        id=f"{scene_id}_btn_label",
                        type="text",
                        positioning="flow",
                        props={"content": "Get Started", "style_token": "heading_md", "color": "fg_primary", "align": "center"},
                    ),
                ]
            )
        ]
    )
    return SceneLayout(scene_id=scene_id, background=_bg_radial(index), elements=[_particles(scene_id, index), root])


def layout_flow_diagram(scene_id: str, beat: ScriptBeat, index: int, total: int) -> SceneLayout:
    root = Element(
        id=f"{scene_id}_root",
        type="group",
        positioning="absolute",
        position=Position(x="50%", y="50%"),
        anchor="center",
        layout=FlexLayout(display="flex", flex_direction="row", gap=80, align_items="center", justify_content="center"),
        children=[
            Element(
                id=f"{scene_id}_node_A",
                type="group",
                positioning="flow",
                layout=FlexLayout(flex_direction="column", gap=16, align_items="center", padding=20),
                props={"fill": "surface", "corner_radius": 16},
                children=[
                    Element(id=f"{scene_id}_icon_A", type="svg-icon", positioning="flow", props={"icon_name": "document", "color": "accent_1", "size": 32}),
                    Element(id=f"{scene_id}_label_A", type="text", positioning="flow", props={"content": "Source", "style_token": "heading_md", "color": "fg_primary"}),
                ]
            ),
            Element(
                id=f"{scene_id}_node_B",
                type="group",
                positioning="flow",
                layout=FlexLayout(flex_direction="column", gap=16, align_items="center", padding=20),
                props={"fill": "surface", "corner_radius": 16},
                children=[
                    Element(id=f"{scene_id}_icon_B", type="svg-icon", positioning="flow", props={"icon_name": "database", "color": "accent_2", "size": 32}),
                    Element(id=f"{scene_id}_label_B", type="text", positioning="flow", props={"content": "Destination", "style_token": "heading_md", "color": "fg_primary"}),
                ]
            )
        ]
    )
    # The connector is absolute behind the root to avoid flex bounds
    connector = Element(
        id=f"{scene_id}_connector",
        type="svg-path",
        positioning="absolute",
        position=Position(x="50%", y="50%"),
        size=Size(width="80%", height="20%"),
        anchor="center",
        layer=0,
        props={
            "path_data": "M 10 50 Q 50 0 90 50",  # Simple placeholder path, scaled in Remotion
            "stroke_color": "accent_1",
            "stroke_width": 3,
            "stroke_dash": "12 8",
            "draw_duration": 0.8,
            "draw_delay": 0.5,
        },
    )
    return SceneLayout(scene_id=scene_id, background=_pick_bg(index, total), elements=[_particles(scene_id, index), connector, root])


def layout_analogy_bridge(scene_id: str, beat: ScriptBeat, index: int, total: int) -> SceneLayout:
    root = Element(
        id=f"{scene_id}_root",
        type="group",
        positioning="absolute",
        position=Position(x="50%", y="50%"),
        anchor="center",
        layout=FlexLayout(display="flex", flex_direction="row", gap=40, align_items="center", justify_content="center"),
        children=[
            Element(
                id=f"{scene_id}_quote_mark",
                type="text",
                positioning="flow",
                props={
                    "content": "“",
                    "style_token": "display_lg",
                    "color": "accent_1",
                    "align": "left",
                },
            ),
            Element(
                id=f"{scene_id}_text_grp",
                type="group",
                positioning="flow",
                layout=FlexLayout(flex_direction="column", gap=16, align_items="flex-start"),
                children=[
                    Element(
                        id=f"{scene_id}_headline",
                        type="text",
                        positioning="flow",
                        props={
                            "content": beat.headline_text or beat.text,
                            "style_token": "heading_lg",
                            "color": "fg_primary",
                            "align": "left",
                            "max_width": 700,
                        },
                    ),
                    Element(
                        id=f"{scene_id}_subtitle",
                        type="text",
                        positioning="flow",
                        props={
                            "content": beat.subtitle_text,
                            "style_token": "body_lg",
                            "color": "fg_secondary",
                            "align": "left",
                            "max_width": 600,
                        },
                    ),
                ]
            )
        ]
    )
    return SceneLayout(scene_id=scene_id, background=_pick_bg(index, total), elements=[_particles(scene_id, index), root])


LAYOUT_MAP = {
    "centered_hero": layout_concept_hero,
    "concept_hero": layout_concept_hero,
    "split_layout": layout_comparison_split,
    "comparison_split": layout_comparison_split,
    "stat_showcase": layout_stat_callout,
    "stat_callout": layout_stat_callout,
    "feature_showcase": layout_feature_list,
    "feature_list": layout_feature_list,
    "icon_grid": layout_feature_list,
    "cta_card": layout_cta_card,
    "quote": layout_analogy_bridge,
    "analogy_bridge": layout_analogy_bridge,
    "timeline_steps": layout_feature_list,
    "card_stack": layout_feature_list,
    "terminal_demo": layout_comparison_split,
    "list_reveal": layout_feature_list,
    "connection_graph": layout_flow_diagram,
    "flow_diagram": layout_flow_diagram,
}


def build_layouts_v2(
    storyboard: list[StoryboardScene],
    script_beats: list[ScriptBeat],
    theme: ThemeTokens,
) -> list[SceneLayout]:
    beats_by_id = {b.id: b for b in script_beats}
    total = len(storyboard)
    layouts: list[SceneLayout] = []

    for index, scene in enumerate(storyboard):
        beat = beats_by_id[scene.beat_ids[0]]
        hint = scene.layout_hint or "concept_hero"

        if beat.type.startswith("step_"):
            hint = "feature_list"

        layout_fn = LAYOUT_MAP.get(hint, layout_concept_hero)
        layout = layout_fn(scene.scene_id, beat, index, total)
        layouts.append(layout)

    return layouts
