from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .config import Settings


def ffmpeg_command(settings: Settings) -> list[str] | None:
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return [system_ffmpeg]

    if (settings.remotion_project_path / "package.json").exists():
        return ["pnpm", "exec", "remotion", "ffmpeg"]

    return None


def postprocess_video(
    *,
    settings: Settings,
    input_path: Path,
    output_path: Path,
) -> str:
    command_prefix = ffmpeg_command(settings)
    if command_prefix is None:
        raise FileNotFoundError(
            "No FFmpeg binary available. Install ffmpeg or use the Remotion package."
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        *command_prefix,
        "-y",
        "-i",
        str(input_path),
        "-map",
        "0:v:0",
        "-map",
        "0:a?",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-af",
        "loudnorm=I=-16:TP=-1.5:LRA=11",
        str(output_path),
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
        raise RuntimeError(f"FFmpeg post-processing failed:\n{output}")

    return str(output_path)
