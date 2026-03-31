"""ir_mutations.py — Deterministic IR patch system.

Applies typed mutation ops to a ProjectIR without any LLM call.
All ops are idempotent and return a new ProjectIR (immutable).
"""
from __future__ import annotations

from typing import Annotated, Any, Literal, Union
from pydantic import BaseModel, Field

from .models import ProjectIR
from .themes import load_theme


# ── Op models ──────────────────────────────────────────────────────────────

class SetThemeColorOp(BaseModel):
    op: Literal["set_theme_color"]
    key: str   # e.g. "accent_1"
    value: str  # e.g. "#FF5500"


class SetSceneDurationOp(BaseModel):
    op: Literal["set_scene_duration"]
    scene_id: str
    duration: float  # seconds


class ReorderScenesOp(BaseModel):
    op: Literal["reorder_scenes"]
    scene_ids: list[str]  # new order, must contain all existing scene IDs


class SetElementPropOp(BaseModel):
    op: Literal["set_element_prop"]
    scene_id: str
    element_id: str
    prop: str    # top-level prop key inside element.props
    value: Any


class SetAspectRatioOp(BaseModel):
    op: Literal["set_aspect_ratio"]
    ratio: Literal["16:9", "9:16", "1:1"]


class SwapThemeOp(BaseModel):
    op: Literal["swap_theme"]
    theme_name: str


class SetElementPositionOp(BaseModel):
    op: Literal["set_element_position"]
    scene_id: str
    element_id: str
    x: str | float
    y: str | float


class UpdateThemeMotionOp(BaseModel):
    op: Literal["update_theme_motion"]
    motion: dict[str, Any]


class AddAssetOp(BaseModel):
    op: Literal["add_asset"]
    asset_type: Literal["fonts", "audio", "svg", "images"]
    asset: dict[str, Any]


IRPatchOp = Annotated[
    Union[
        SetThemeColorOp,
        SetSceneDurationOp,
        ReorderScenesOp,
        SetElementPropOp,
        SetElementPositionOp,
        SetAspectRatioOp,
        SwapThemeOp,
        UpdateThemeMotionOp,
        AddAssetOp,
    ],
    Field(discriminator="op"),
]


class IRPatch(BaseModel):
    ops: list[IRPatchOp] = Field(...)


# ── Dispatcher ─────────────────────────────────────────────────────────────

def apply_patch(ir: ProjectIR, patch: IRPatch) -> ProjectIR:
    """Apply a list of ops and return an updated IR (deep copy via model_dump)."""
    data: dict[str, Any] = ir.model_dump(mode="json")
    for op in patch.ops:
        data = _apply_op(data, op)
    return ProjectIR.model_validate(data)


def _apply_op(data: dict[str, Any], op: IRPatchOp) -> dict[str, Any]:
    match op.op:
        case "set_theme_color":
            return _set_theme_color(data, op)
        case "set_scene_duration":
            return _set_scene_duration(data, op)
        case "reorder_scenes":
            return _reorder_scenes(data, op)
        case "set_element_prop":
            return _set_element_prop(data, op)
        case "set_element_position":
            return _set_element_position(data, op)
        case "set_aspect_ratio":
            return _set_aspect_ratio(data, op)
        case "swap_theme":
            return _swap_theme(data, op)
        case "update_theme_motion":
            return _update_theme_motion(data, op)
        case "add_asset":
            return _add_asset(data, op)
        case _:
            raise ValueError(f"Unknown op: {op.op}")


# ── Op implementations ──────────────────────────────────────────────────────

def _set_theme_color(data: dict, op: SetThemeColorOp) -> dict:
    data = _deep_copy(data)
    colors = data["theme"]["colors"]
    if op.key not in colors:
        raise ValueError(f"Unknown theme color key: {op.key!r}. Valid: {list(colors)}")
    colors[op.key] = op.value
    return data


def _set_scene_duration(data: dict, op: SetSceneDurationOp) -> dict:
    data = _deep_copy(data)
    scenes = data["timeline"]["scenes"]
    scene_map = {s["id"]: s for s in scenes}
    if op.scene_id not in scene_map:
        raise ValueError(f"Scene {op.scene_id!r} not found.")
    if op.duration < 1.0:
        raise ValueError("Scene duration must be ≥ 1 second.")

    # Update duration and recalculate start_times sequentially
    scene_map[op.scene_id]["duration"] = op.duration
    _recalc_start_times(scenes)
    # Keep meta.duration in sync
    data["meta"]["duration"] = round(sum(s["duration"] for s in scenes), 3)
    return data


def _reorder_scenes(data: dict, op: ReorderScenesOp) -> dict:
    data = _deep_copy(data)
    scenes = data["timeline"]["scenes"]
    scene_map = {s["id"]: s for s in scenes}
    if set(op.scene_ids) != set(scene_map.keys()):
        raise ValueError("reorder_scenes: scene_ids must contain exactly the same IDs as the current scenes.")
    reordered = [scene_map[sid] for sid in op.scene_ids]
    _recalc_start_times(reordered)
    data["timeline"]["scenes"] = reordered
    return data


def _set_element_prop(data: dict, op: SetElementPropOp) -> dict:
    data = _deep_copy(data)
    for scene in data["timeline"]["scenes"]:
        if scene["id"] != op.scene_id:
            continue
        for element in scene["elements"]:
            if element["id"] != op.element_id:
                continue
            element["props"][op.prop] = op.value
            return data
    raise ValueError(f"Element {op.element_id!r} in scene {op.scene_id!r} not found.")


def _set_element_position(data: dict, op: SetElementPositionOp) -> dict:
    data = _deep_copy(data)
    for scene in data["timeline"]["scenes"]:
        if scene["id"] != op.scene_id:
            continue
        for element in scene["elements"]:
            if element["id"] != op.element_id:
                continue
            element["position"]["x"] = op.x
            element["position"]["y"] = op.y
            return data
    raise ValueError(f"Element {op.element_id!r} in scene {op.scene_id!r} not found.")


def _set_aspect_ratio(data: dict, op: SetAspectRatioOp) -> dict:
    data = _deep_copy(data)
    ratio = op.ratio
    data["meta"]["aspect_ratio"] = ratio
    # Update canvas dimensions
    match ratio:
        case "9:16":
            data["meta"]["width"] = 1080
            data["meta"]["height"] = 1920
        case "16:9":
            data["meta"]["width"] = 1920
            data["meta"]["height"] = 1080
        case "1:1":
            data["meta"]["width"] = 1080
            data["meta"]["height"] = 1080
    return data


def _swap_theme(data: dict, op: SwapThemeOp) -> dict:
    data = _deep_copy(data)
    from .config import Settings
    settings = Settings.from_env()
    theme_tokens = load_theme(op.theme_name, settings)
    data["theme"] = theme_tokens.model_dump(mode="json")
    return data


def _update_theme_motion(data: dict, op: UpdateThemeMotionOp) -> dict:
    data = _deep_copy(data)
    data["theme"]["motion"] = op.motion
    return data


def _add_asset(data: dict, op: AddAssetOp) -> dict:
    data = _deep_copy(data)
    asset_list = data["assets"].setdefault(op.asset_type, [])
    # Optional: check for uniqueness
    asset_list.append(op.asset)
    return data


# ── Helpers ────────────────────────────────────────────────────────────────

def _recalc_start_times(scenes: list[dict]) -> None:
    """Recalculate start_time for each scene in place based on cumulative durations."""
    t = 0.0
    for scene in scenes:
        scene["start_time"] = round(t, 3)
        t += scene["duration"]


def _deep_copy(data: dict) -> dict:
    import json
    return json.loads(json.dumps(data))
