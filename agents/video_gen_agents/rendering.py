from __future__ import annotations

import json
import subprocess

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

    command = [
        "pnpm",
        "exec",
        "remotion",
        "render",
        "src/index.ts",
        "VideoFromIR",
        str(raw_output_path),
        f"--props={props_path}",
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

    return postprocess_video(
        settings=settings,
        input_path=raw_output_path,
        output_path=final_output_path,
    )
