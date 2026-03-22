from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from video_gen_agents.api.main import create_app
from video_gen_agents.config import Settings


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


def test_generate_endpoint_returns_ir(tmp_path: Path) -> None:
    app = create_app(build_test_settings(tmp_path))
    with TestClient(app) as client:
        response = client.post(
            "/api/generate",
            json={
                "brief": "Build a short explainer showing how a brief becomes storyboard, design, motion, and a validated IR.",
                "theme_name": "default",
                "duration": 35,
                "scene_count": 4,
                "render_video": False,
            },
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["verification"]["status"] == "passed_with_warnings"
        assert len(payload["ir"]["timeline"]["scenes"]) == 4
        assert payload["summary"]["theme_name"] == "default"


def test_theme_endpoint_lists_available_themes(tmp_path: Path) -> None:
    app = create_app(build_test_settings(tmp_path))
    with TestClient(app) as client:
        response = client.get("/api/themes")
        assert response.status_code == 200
        assert set(response.json()["themes"]) >= {"default", "dark-tech", "vibrant"}


def test_generate_persists_project_and_logs(tmp_path: Path) -> None:
    app = create_app(build_test_settings(tmp_path))
    with TestClient(app) as client:
        response = client.post(
            "/api/generate",
            json={
                "brief": "Create a short backend smoke run that should be persisted into SQLite along with the generated agent logs.",
                "theme_name": "dark-tech",
                "duration": 35,
                "scene_count": 5,
                "render_video": False,
            },
        )

        assert response.status_code == 200
        project_id = response.json()["project_id"]

        projects_response = client.get("/api/projects")
        assert projects_response.status_code == 200
        projects = projects_response.json()
        assert len(projects) == 1
        assert projects[0]["project_id"] == project_id
        assert projects[0]["status"] == "generated_with_warnings"

        detail_response = client.get(f"/api/projects/{project_id}")
        assert detail_response.status_code == 200
        detail = detail_response.json()
        assert detail["project_id"] == project_id
        assert detail["verification"]["status"] == "passed_with_warnings"
        assert detail["ir"]["meta"]["id"] == project_id
        assert len(detail["logs"]) >= 6


def test_media_ir_mount_serves_generated_ir(tmp_path: Path) -> None:
    app = create_app(build_test_settings(tmp_path))
    with TestClient(app) as client:
        response = client.post(
            "/api/generate",
            json={
                "brief": "Persist an IR document so the dashboard can read it through the API and mounted media path during local development.",
                "theme_name": "vibrant",
                "duration": 35,
                "scene_count": 4,
                "render_video": False,
            },
        )

        assert response.status_code == 200
        payload = response.json()
        ir_filename = Path(payload["ir_path"]).name

        ir_response = client.get(f"/media/ir/{ir_filename}")
        assert ir_response.status_code == 200
        assert ir_response.json()["meta"]["id"] == payload["project_id"]


def test_generate_endpoint_supports_cors_preflight(tmp_path: Path) -> None:
    app = create_app(build_test_settings(tmp_path))
    with TestClient(app) as client:
        response = client.options(
            "/api/generate",
            headers={
                "Origin": "http://127.0.0.1:5173",
                "Access-Control-Request-Method": "POST",
            },
        )

        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == "*"


def test_project_launch_streams_progress_over_websocket(tmp_path: Path) -> None:
    app = create_app(build_test_settings(tmp_path))
    with TestClient(app) as client:
        response = client.post(
            "/api/projects",
            json={
                "brief": "Launch a background project and stream stage progress so the dashboard can show a live DAG while the deterministic pipeline runs.",
                "theme_name": "default",
                "duration": 35,
                "scene_count": 4,
                "render_video": False,
            },
        )

        assert response.status_code == 202
        payload = response.json()
        project_id = payload["project_id"]

        events: list[dict] = []
        with client.websocket_connect(payload["websocket_path"]) as websocket:
            for _ in range(16):
                event = websocket.receive_json()
                events.append(event)
                if event["event"] in {"project_completed", "project_failed"}:
                    break

        assert events[0]["event"] == "project_created"
        assert any(
            event["event"] == "stage_completed" and event["stage"] == "manager"
            for event in events
        )
        assert events[-1]["event"] == "project_completed"
        assert events[-1]["verification_status"] == "passed_with_warnings"

        detail_response = client.get(f"/api/projects/{project_id}")
        assert detail_response.status_code == 200
        detail = detail_response.json()
        assert detail["project_id"] == project_id
        assert detail["status"] == "generated_with_warnings"
