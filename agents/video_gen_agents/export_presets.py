"""export_presets.py — Platform export configurations.

Maps platform slugs to aspect ratio, resolution, and duration cap,
and generates the IRPatchOps needed to conform a ProjectIR to that platform.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .ir_mutations import IRPatch, IRPatchOp, SetAspectRatioOp, SetSceneDurationOp
from .models import ProjectIR


AspectRatio = Literal["16:9", "9:16", "1:1"]

PLATFORM_PRESETS: dict[str, "ExportPreset"] = {}


@dataclass(frozen=True)
class ExportPreset:
    label: str
    aspect_ratio: AspectRatio
    width: int
    height: int
    max_duration: float | None  # None = unlimited


def _register(slug: str, preset: ExportPreset) -> None:
    PLATFORM_PRESETS[slug] = preset


_register("youtube_shorts", ExportPreset("YouTube Shorts", "9:16", 1080, 1920, 60.0))
_register("youtube_long",   ExportPreset("YouTube",        "16:9", 1920, 1080, None))
_register("instagram_reels",ExportPreset("Instagram Reels","9:16", 1080, 1920, 30.0))
_register("tiktok",         ExportPreset("TikTok",         "9:16", 1080, 1920, 30.0))
_register("linkedin",       ExportPreset("LinkedIn",       "1:1",  1080, 1080, 30.0))
_register("twitter",        ExportPreset("Twitter/X",      "16:9", 1920, 1080, 30.0))


def list_presets() -> list[dict]:
    return [
        {
            "slug": slug,
            "label": preset.label,
            "aspect_ratio": preset.aspect_ratio,
            "width": preset.width,
            "height": preset.height,
            "max_duration": preset.max_duration,
        }
        for slug, preset in PLATFORM_PRESETS.items()
    ]


def build_export_patch(ir: ProjectIR, platform: str) -> IRPatch:
    """Return an IRPatch that conforms the IR to the given platform preset."""
    preset = PLATFORM_PRESETS.get(platform)
    if preset is None:
        raise ValueError(
            f"Unknown platform {platform!r}. Available: {list(PLATFORM_PRESETS)}"
        )

    ops: list[IRPatchOp] = [
        SetAspectRatioOp(op="set_aspect_ratio", ratio=preset.aspect_ratio),
    ]

    # Trim scene durations proportionally if total exceeds platform cap
    if preset.max_duration is not None:
        total = sum(s.duration for s in ir.timeline.scenes)
        if total > preset.max_duration:
            ratio = preset.max_duration / total
            for scene in ir.timeline.scenes:
                trimmed = max(1.0, round(scene.duration * ratio, 1))
                ops.append(
                    SetSceneDurationOp(
                        op="set_scene_duration",
                        scene_id=scene.id,
                        duration=trimmed,
                    )
                )

    return IRPatch(ops=ops)
