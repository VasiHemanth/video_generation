from __future__ import annotations

from pathlib import Path

from video_gen_agents.config import Settings
from video_gen_agents.models import GenerateVideoRequest
from video_gen_agents.pipeline import VideoGenerationService


def build_test_settings(tmp_path: Path) -> Settings:
    repo_root = Path(__file__).resolve().parents[2]
    agents_root = repo_root / "agents"
    return Settings(
        repo_root=repo_root,
        agents_root=agents_root,
        data_dir=tmp_path / "data",
        theme_dir=repo_root / "shared" / "themes",
        remotion_project_path=tmp_path / "remotion",
        render_output_path=tmp_path / "renders",
    )


def test_pipeline_generates_valid_ir(tmp_path: Path) -> None:
    service = VideoGenerationService(build_test_settings(tmp_path))
    response = service.generate(
        GenerateVideoRequest(
            brief=(
                "Create a motion graphics explainer about how AI agents turn a plain-language "
                "brief into a validated video plan with deterministic rendering."
            ),
            title="AI Agent Video Pipeline",
            theme_name="dark-tech",
            duration=35,
            scene_count=5,
            render_video=False,
        )
    )

    assert response.project_id.startswith("proj_")
    assert Path(response.ir_path).exists()
    assert response.ir.meta.title == "AI Agent Video Pipeline"
    assert len(response.ir.timeline.scenes) == 5

    # Audio validation
    assert response.ir.audio.music is not None
    assert response.ir.audio.music.track_id == "bg_music_default"
    assert len(response.ir.audio.sfx) >= 4  # (5 scenes - 1 transition) + some demo/payoff sfx
    
    # Asset validation
    audio_assets = {a.id for a in response.ir.assets.audio}
    assert "bg_music_default" in audio_assets
    assert "sfx_whoosh" in audio_assets
    assert "sfx_click" in audio_assets

    # Visual & Motion validation
    first_scene = response.ir.timeline.scenes[0]
    element_types = {e.type for e in first_scene.elements}
    assert "device" in element_types
    
    # Parallax validation
    particle_elements = [e for e in first_scene.elements if e.type == "particle-field"]
    assert len(particle_elements) > 0
    assert particle_elements[0].parallax_factor is not None
    assert particle_elements[0].parallax_factor > 0

    assert response.verification.status == "passed_with_warnings"
    assert response.summary.render_status == "ir_only"
    assert any(log.agent == "renderer" for log in response.logs)
