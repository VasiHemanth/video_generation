"""Tests for ir_mutations.py — deterministic IR patch system."""
from __future__ import annotations

import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Helpers to build minimal valid IR dicts for testing
# ---------------------------------------------------------------------------

def _minimal_ir(scenes: list[dict] | None = None) -> dict:
    """Return a minimal ProjectIR dict with optional scene override."""
    default_scenes = [
        {
            "id": "s1",
            "role": "intro",
            "title": "Scene 1",
            "start_time": 0.0,
            "duration": 15.0,
            "transition_in": None,
            "transition_out": None,
            "background": {"type": "gradient", "colors": ["bg_primary", "bg_secondary"], "angle": 135},
            "elements": [
                {
                    "id": "e1",
                    "type": "text",
                    "props": {"content": "Hello", "style_token": "heading_lg", "color": "fg_primary"},
                    "position": {"x": "50%", "y": "50%"},
                    "size": None,
                    "anchor": None,
                    "layer": 1,
                    "opacity": 1.0,
                    "rotation": 0.0,
                    "scale": 1.0,
                    "enter": None,
                    "exit": None,
                    "emphasis": None,
                    "keyframes": [],
                    "delay": None,
                    "parallax_factor": None,
                    "ambient": None,
                    "stagger_index": None,
                    "stagger_delay": None,
                    "word_animation": None,
                    "word_stagger": None,
                },
            ],
        },
        {
            "id": "s2",
            "role": "cta",
            "title": "Scene 2",
            "start_time": 15.0,
            "duration": 15.0,
            "transition_in": None,
            "transition_out": None,
            "background": {"type": "gradient", "colors": ["bg_primary"], "angle": 135},
            "elements": [
                {
                    "id": "e2",
                    "type": "text",
                    "props": {"content": "CTA", "style_token": "heading_md", "color": "fg_primary"},
                    "position": {"x": "50%", "y": "50%"},
                    "size": None,
                    "anchor": None,
                    "layer": 1,
                    "opacity": 1.0,
                    "rotation": 0.0,
                    "scale": 1.0,
                    "enter": None,
                    "exit": None,
                    "emphasis": None,
                    "keyframes": [],
                    "delay": None,
                    "parallax_factor": None,
                    "ambient": None,
                    "stagger_index": None,
                    "stagger_delay": None,
                    "word_animation": None,
                    "word_stagger": None,
                },
            ],
        },

    ]
    return {
        "version": "1.0.0",
        "meta": {
            "id": "test_proj",
            "title": "Test Project",
            "description": "A test IR",
            "duration": 30.0,
            "fps": 30,
            "width": 1080,
            "height": 1920,
            "aspect_ratio": "9:16",
            "created_at": "2026-03-30T00:00:00Z",
            "status": "draft",
        },
        "theme": {
            "name": "warm-clay",
            "colors": {
                "bg_primary": "#E8E0D4",
                "bg_secondary": "#D4CBC0",
                "fg_primary": "#1A1A2E",
                "fg_secondary": "#4A4A5A",
                "accent_1": "#5BA8A0",
                "accent_2": "#7B6BA4",
                "accent_3": "#E8913A",
                "gradient_start": "#E8E0D4",
                "gradient_end": "#D4CBC0",
                "surface": "#2D2D3A",
                "border": "#3D3D4A",
            },
            "typography": {
                "display_lg":  {"family": "Inter", "weight": 800, "size": 72, "lineHeight": 1.1},
                "display_md":  {"family": "Inter", "weight": 700, "size": 56, "lineHeight": 1.15},
                "display_sm":  {"family": "Inter", "weight": 700, "size": 40, "lineHeight": 1.2},
                "heading_lg":  {"family": "Inter", "weight": 600, "size": 32, "lineHeight": 1.3},
                "heading_md":  {"family": "Inter", "weight": 600, "size": 24, "lineHeight": 1.35},
                "body_lg":     {"family": "Inter", "weight": 400, "size": 20, "lineHeight": 1.5},
                "body_md":     {"family": "Inter", "weight": 400, "size": 16, "lineHeight": 1.5},
                "caption":     {"family": "Inter", "weight": 400, "size": 14, "lineHeight": 1.4},
                "code":        {"family": "JetBrains Mono", "weight": 400, "size": 16, "lineHeight": 1.5},
            },
            "motion": {
                "duration_fast": 0.15,
                "duration_normal": 0.4,
                "duration_slow": 0.7,
                "duration_very_slow": 1.0,
                "easing_default": "ease-out-cubic",
                "easing_enter": "ease-out-back",
                "easing_exit": "ease-in",
                "easing_bounce": "ease-out-back",
                "easing_spring": {"mass": 1.0, "damping": 14.0, "stiffness": 180.0},
                "stagger_delay": 0.1,
            },
            "layout": {
                "padding": 60,
                "gap": 24,
                "card_radius": 20,
                "safe_area_x": 120,
                "safe_area_y": 80,
            },
        },
        "timeline": {"scenes": scenes or default_scenes},
        "audio": {
            "music": None,
            "voiceover": {"enabled": False, "segments": []},
            "sfx": [],
        },
        "assets": {"fonts": [], "audio": [], "svg": [], "images": []},
        "constraints": {
            "min_duration": 1,
            "max_duration": 40,
            "min_scenes": 2,
            "max_scenes": 8,
            "min_scene_duration": 2,
            "max_scene_duration": 15,
            "platform": "youtube",
            "brand": None,
            "content_safety": "standard",
        },
    }


def _load_ir(d: dict):
    from video_gen_agents.models import ProjectIR
    return ProjectIR.model_validate(d)


# ---------------------------------------------------------------------------
# set_theme_color
# ---------------------------------------------------------------------------

class TestSetThemeColor:
    def test_valid_color_swap(self):
        from video_gen_agents.ir_mutations import IRPatch, apply_patch

        ir = _load_ir(_minimal_ir())
        patch = IRPatch(ops=[{"op": "set_theme_color", "key": "accent_1", "value": "#FF0000"}])
        result = apply_patch(ir, patch)
        assert result.theme.colors.accent_1 == "#FF0000"
        # Original untouched
        assert ir.theme.colors.accent_1 == "#5BA8A0"

    def test_invalid_key_raises(self):
        from video_gen_agents.ir_mutations import IRPatch, apply_patch

        ir = _load_ir(_minimal_ir())
        patch = IRPatch(ops=[{"op": "set_theme_color", "key": "nonexistent", "value": "#FF0000"}])
        with pytest.raises(ValueError, match="Unknown theme color key"):
            apply_patch(ir, patch)


# ---------------------------------------------------------------------------
# set_scene_duration
# ---------------------------------------------------------------------------

class TestSetSceneDuration:
    def test_duration_updated_and_start_times_recalculated(self):
        from video_gen_agents.ir_mutations import IRPatch, apply_patch

        ir = _load_ir(_minimal_ir())
        patch = IRPatch(ops=[{"op": "set_scene_duration", "scene_id": "s1", "duration": 8.0}])
        result = apply_patch(ir, patch)

        scenes = result.timeline.scenes
        assert scenes[0].duration == 8.0
        assert scenes[0].start_time == 0.0
        assert scenes[1].start_time == 8.0  # shifted

    def test_too_short_raises(self):
        from video_gen_agents.ir_mutations import IRPatch, apply_patch

        ir = _load_ir(_minimal_ir())
        patch = IRPatch(ops=[{"op": "set_scene_duration", "scene_id": "s1", "duration": 0.5}])
        with pytest.raises(ValueError, match="≥ 1 second"):
            apply_patch(ir, patch)

    def test_unknown_scene_raises(self):
        from video_gen_agents.ir_mutations import IRPatch, apply_patch

        ir = _load_ir(_minimal_ir())
        patch = IRPatch(ops=[{"op": "set_scene_duration", "scene_id": "doesnt_exist", "duration": 5.0}])
        with pytest.raises(ValueError, match="not found"):
            apply_patch(ir, patch)


# ---------------------------------------------------------------------------
# reorder_scenes
# ---------------------------------------------------------------------------

class TestReorderScenes:
    def test_reorder_swaps_scenes(self):
        from video_gen_agents.ir_mutations import IRPatch, apply_patch

        ir = _load_ir(_minimal_ir())
        patch = IRPatch(ops=[{"op": "reorder_scenes", "scene_ids": ["s2", "s1"]}])
        result = apply_patch(ir, patch)

        scenes = result.timeline.scenes
        assert scenes[0].id == "s2"
        assert scenes[1].id == "s1"
        # start_times recalculated
        assert scenes[0].start_time == 0.0
        assert scenes[1].start_time == scenes[0].duration

    def test_missing_ids_raises(self):
        from video_gen_agents.ir_mutations import IRPatch, apply_patch

        ir = _load_ir(_minimal_ir())
        patch = IRPatch(ops=[{"op": "reorder_scenes", "scene_ids": ["s1"]}])
        with pytest.raises(ValueError, match="same IDs"):
            apply_patch(ir, patch)


# ---------------------------------------------------------------------------
# set_element_prop
# ---------------------------------------------------------------------------

class TestSetElementProp:
    def test_prop_updated(self):
        from video_gen_agents.ir_mutations import IRPatch, apply_patch

        ir = _load_ir(_minimal_ir())
        patch = IRPatch(ops=[{
            "op": "set_element_prop",
            "scene_id": "s1",
            "element_id": "e1",
            "prop": "content",
            "value": "Updated Text",
        }])
        result = apply_patch(ir, patch)
        assert result.timeline.scenes[0].elements[0].props["content"] == "Updated Text"
        # Original unchanged
        assert ir.timeline.scenes[0].elements[0].props["content"] == "Hello"

    def test_unknown_element_raises(self):
        from video_gen_agents.ir_mutations import IRPatch, apply_patch

        ir = _load_ir(_minimal_ir())
        patch = IRPatch(ops=[{
            "op": "set_element_prop",
            "scene_id": "s1",
            "element_id": "nonexistent",
            "prop": "content",
            "value": "x",
        }])
        with pytest.raises(ValueError, match="not found"):
            apply_patch(ir, patch)


# ---------------------------------------------------------------------------
# set_aspect_ratio
# ---------------------------------------------------------------------------

class TestSetAspectRatio:
    def test_16_9_dimensions(self):
        from video_gen_agents.ir_mutations import IRPatch, apply_patch

        ir = _load_ir(_minimal_ir())
        patch = IRPatch(ops=[{"op": "set_aspect_ratio", "ratio": "16:9"}])
        result = apply_patch(ir, patch)
        assert result.meta.width == 1920
        assert result.meta.height == 1080
        assert result.meta.aspect_ratio == "16:9"

    def test_1_1_dimensions(self):
        from video_gen_agents.ir_mutations import IRPatch, apply_patch

        ir = _load_ir(_minimal_ir())
        patch = IRPatch(ops=[{"op": "set_aspect_ratio", "ratio": "1:1"}])
        result = apply_patch(ir, patch)
        assert result.meta.width == 1080
        assert result.meta.height == 1080


# ---------------------------------------------------------------------------
# Chained ops — multiple mutations in one patch
# ---------------------------------------------------------------------------

class TestChainedOps:
    def test_multiple_ops_applied_in_order(self):
        from video_gen_agents.ir_mutations import IRPatch, apply_patch

        ir = _load_ir(_minimal_ir())
        patch = IRPatch(ops=[
            {"op": "set_theme_color", "key": "accent_1", "value": "#AABBCC"},
            {"op": "set_scene_duration", "scene_id": "s1", "duration": 12.0},
            {"op": "set_aspect_ratio", "ratio": "16:9"},
        ])
        result = apply_patch(ir, patch)

        assert result.theme.colors.accent_1 == "#AABBCC"
        assert result.timeline.scenes[0].duration == 12.0
        assert result.meta.aspect_ratio == "16:9"
        assert result.meta.width == 1920
