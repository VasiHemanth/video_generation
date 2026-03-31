from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .config import Settings
from .ffmpeg import postprocess_video
from .models import ProjectIR


def remotion_is_available(settings: Settings) -> bool:
    return (settings.remotion_project_path / "src" / "index.ts").exists()


def render_project_ir(
    *,
    settings: Settings,
    ir: ProjectIR,
) -> str:
    if not remotion_is_available(settings):
        raise FileNotFoundError(
            f"Remotion entrypoint not found at {settings.remotion_project_path / 'src' / 'index.ts'}"
        )

    project_id = ir.meta.id
    props_dir = settings.data_dir / "render-props"
    raw_dir = settings.render_output_path / "raw"
    props_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)
    settings.render_output_path.mkdir(parents=True, exist_ok=True)

    props_path = props_dir / f"{project_id}.json"
    raw_output_path = raw_dir / f"{project_id}.mp4"
    final_output_path = settings.render_output_path / f"{project_id}.mp4"

    props_path.write_text(
        json.dumps({"ir": ir.model_dump(mode="json", by_alias=True)}, indent=2),
        encoding="utf-8",
    )

    import os
    concurrency = os.cpu_count() or 4

    command = [
        "pnpm",
        "exec",
        "remotion",
        "render",
        "src/index.ts",
        "VideoFromIR",
        str(raw_output_path),
        f"--props={props_path}",
        f"--concurrency={concurrency}",
    ]
    result = subprocess.run(
        command,
        cwd=settings.remotion_project_path,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        output = "\n".join(
            chunk for chunk in [result.stdout.strip(), result.stderr.strip()] if chunk
        )
        raise RuntimeError(f"Remotion render failed:\n{output}")

    final_path = postprocess_video(
        settings=settings,
        input_path=raw_output_path,
        output_path=final_output_path,
    )

    # ── Vision Verifier: extract frames ───────────────────────────────────
    try:
        extract_verification_frames(
            video_path=Path(final_path),
            ir=ir,
            settings=settings,
        )
    except Exception:
        pass  # Non-fatal: frame extraction failure should not break the render

    return final_path


def extract_verification_frames(
    *,
    video_path: Path,
    ir: ProjectIR,
    settings: Settings,
) -> list[Path]:
    """Extract one representative frame per scene for visual QA.

    Stores frames under agents/data/renders/frames/<project_id>/.
    Returns list of extracted frame paths.
    """
    project_id = ir.meta.id
    frames_dir = settings.data_dir / "renders" / "frames" / project_id
    frames_dir.mkdir(parents=True, exist_ok=True)

    scenes = ir.timeline.scenes
    extracted: list[Path] = []

    for i, scene in enumerate(scenes):
        # Sample at 25% into each scene for a representative frame
        timestamp = scene.start_time + scene.duration * 0.25
        out_path = frames_dir / f"scene_{i + 1:02d}_{scene.id}.jpg"

        cmd = [
            "ffmpeg",
            "-y",
            "-ss", str(timestamp),
            "-i", str(video_path),
            "-frames:v", "1",
            "-q:v", "3",
            str(out_path),
        ]
        result = subprocess.run(cmd, capture_output=True, check=False)
        if result.returncode == 0 and out_path.exists():
            extracted.append(out_path)

    return extracted
