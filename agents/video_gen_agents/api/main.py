from __future__ import annotations

from contextlib import asynccontextmanager, suppress
from datetime import datetime, timezone
from functools import lru_cache
import asyncio
from uuid import uuid4

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool
import uvicorn

from ..config import Settings
from ..database import Database
from ..export_presets import build_export_patch, list_presets
from ..ir_mutations import IRPatch, apply_patch
from ..models import (
    GenerateVideoRequest,
    GenerateVideoResponse,
    ProjectIR,
    ProjectLaunchResponse,
    ProjectProgressEvent,
    StoredProjectDetail,
    StoredProjectSummary,
)
from ..pipeline import VideoGenerationService
from ..progress import ProgressBroker
from ..rendering import render_project_ir


@lru_cache(maxsize=1)
def get_service() -> VideoGenerationService:
    return VideoGenerationService(Settings.from_env())


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or Settings.from_env()
    service = VideoGenerationService(resolved_settings)
    database = Database(resolved_settings)
    broker = ProgressBroker()
    background_tasks: set[asyncio.Task[None]] = set()

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        await database.init()
        try:
            yield
        finally:
            for task in list(background_tasks):
                task.cancel()
            if background_tasks:
                with suppress(Exception):
                    await asyncio.gather(*background_tasks, return_exceptions=True)
            await database.dispose()

    app = FastAPI(
        title="Video Generation Agents API",
        version="0.1.0",
        description="Phase 1 backend foundation for brief-to-IR video generation.",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.mount(
        "/media/renders",
        StaticFiles(directory=resolved_settings.render_output_path),
        name="media-renders",
    )
    app.mount(
        "/media/ir",
        StaticFiles(directory=resolved_settings.data_dir / "ir"),
        name="media-ir",
    )

    def utc_now() -> datetime:
        return datetime.now(timezone.utc)

    async def run_generation_job(project_id: str, payload: GenerateVideoRequest) -> None:
        loop = asyncio.get_running_loop()

        def progress_callback(event: ProjectProgressEvent) -> None:
            broker.publish_threadsafe(loop, event)

        try:
            response = await service.generate(
                payload,
                project_id,
                progress_callback,
            )
        except ValueError as exc:
            await database.mark_project_failed(
                project_id=project_id,
                request=payload,
                error_message=str(exc),
            )
            broker.publish(
                ProjectProgressEvent(
                    event="project_failed",
                    project_id=project_id,
                    stage="pipeline",
                    status="failed",
                    message=str(exc),
                    progress=1.0,
                    timestamp=utc_now(),
                )
            )
            return
        except Exception as exc:
            await database.mark_project_failed(
                project_id=project_id,
                request=payload,
                error_message=str(exc),
            )
            broker.publish(
                ProjectProgressEvent(
                    event="project_failed",
                    project_id=project_id,
                    stage="pipeline",
                    status="failed",
                    message=str(exc),
                    progress=1.0,
                    timestamp=utc_now(),
                )
            )
            return

        await database.save_generation_result(payload, response)
        broker.publish(
            ProjectProgressEvent(
                event="project_completed",
                project_id=project_id,
                stage="pipeline",
                status=response.verification.status,
                message="Project generation completed and persisted.",
                progress=1.0,
                timestamp=utc_now(),
                render_path=response.render_path,
                verification_status=response.verification.status,
            )
        )

    def launch_generation_job(project_id: str, payload: GenerateVideoRequest) -> None:
        task = asyncio.create_task(run_generation_job(project_id, payload))
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)

    @app.get("/health")
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/themes")
    def list_themes() -> dict[str, list[str]]:
        return {"themes": service.available_themes()}

    @app.get("/api/projects", response_model=list[StoredProjectSummary])
    async def list_projects() -> list[StoredProjectSummary]:
        return await database.list_projects()

    @app.get("/api/projects/{project_id}", response_model=StoredProjectDetail)
    async def get_project(project_id: str) -> StoredProjectDetail:
        project = await database.get_project(project_id)
        if project is None:
            raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found.")
        return project

    @app.post("/api/projects", response_model=ProjectLaunchResponse, status_code=202)
    async def create_project(payload: GenerateVideoRequest) -> ProjectLaunchResponse:
        project_id = f"proj_{uuid4().hex[:8]}"
        await database.create_project(project_id, payload)
        broker.publish(
            ProjectProgressEvent(
                event="project_created",
                project_id=project_id,
                stage="pipeline",
                status="generating",
                message="Project accepted and queued for generation.",
                progress=0.0,
                timestamp=utc_now(),
            )
        )
        launch_generation_job(project_id, payload)
        return ProjectLaunchResponse(
            project_id=project_id,
            detail_path=f"/api/projects/{project_id}",
            websocket_path=f"/ws/projects/{project_id}",
        )

    @app.post("/api/generate", response_model=GenerateVideoResponse)
    async def generate_video(payload: GenerateVideoRequest) -> GenerateVideoResponse:
        project_id = f"proj_{uuid4().hex[:8]}"
        await database.create_project(project_id, payload)
        try:
            response = await service.generate(payload, project_id)
        except ValueError as exc:
            await database.mark_project_failed(
                project_id=project_id,
                request=payload,
                error_message=str(exc),
            )
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:
            await database.mark_project_failed(
                project_id=project_id,
                request=payload,
                error_message=str(exc),
            )
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        await database.save_generation_result(payload, response)
        return response

    @app.websocket("/ws/projects/{project_id}")
    async def project_progress_socket(websocket: WebSocket, project_id: str) -> None:
        await websocket.accept()
        queue = broker.register(project_id)
        try:
            while True:
                event = await queue.get()
                await websocket.send_json(event.model_dump(mode="json"))
        except WebSocketDisconnect:
            pass
        finally:
            broker.unregister(project_id, queue)

    # ── IR Mutation endpoint ───────────────────────────────────────────────
    @app.patch("/api/projects/{project_id}/ir")
    async def patch_ir(project_id: str, patch: IRPatch) -> dict:
        project = await database.get_project(project_id)
        if project is None or project.ir is None:
            raise HTTPException(status_code=404, detail=f"Project IR for '{project_id}' not found.")
        try:
            ir = ProjectIR.model_validate(project.ir)
            updated_ir = apply_patch(ir, patch)
        except (ValueError, Exception) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        # Persist the updated IR back to JSON file and save to the database history
        props_dir = resolved_settings.data_dir / "render-props"
        props_dir.mkdir(parents=True, exist_ok=True)
        (props_dir / f"{project_id}.json").write_text(
            updated_ir.model_dump_json(indent=2, by_alias=True)
        )
        
        op_summary = f"Applied {len(patch.ops)} op(s): " + ", ".join(op.op for op in patch.ops)
        await database.save_ir_mutation(project_id, updated_ir, op_summary)

        return {"status": "ok", "ir": updated_ir.model_dump(mode="json")}

    @app.get("/api/projects/{project_id}/history")
    async def get_project_history(project_id: str) -> list[dict]:
        return await database.get_history(project_id)

    @app.post("/api/projects/{project_id}/restore/{checkpoint_id}")
    async def restore_project_ir(project_id: str, checkpoint_id: int) -> dict:
        restored_ir = await database.restore_ir(project_id, checkpoint_id)
        if restored_ir is None:
            raise HTTPException(status_code=404, detail=f"Checkpoint {checkpoint_id} not found.")
        
        # Sync to disk
        props_dir = resolved_settings.data_dir / "render-props"
        props_dir.mkdir(parents=True, exist_ok=True)
        (props_dir / f"{project_id}.json").write_text(
            restored_ir.model_dump_json(indent=2, by_alias=True)
        )
        
        return {"status": "ok", "ir": restored_ir.model_dump(mode="json")}

    # ── Re-render endpoint ────────────────────────────────────────────────
    @app.post("/api/projects/{project_id}/re-render", status_code=202)
    async def re_render_project(project_id: str) -> dict:
        project = await database.get_project(project_id)
        if project is None or project.ir is None:
            raise HTTPException(status_code=404, detail=f"Project IR for '{project_id}' not found.")

        ir = ProjectIR.model_validate(project.ir)

        async def _run_render() -> None:
            try:
                render_path = await run_in_threadpool(
                    render_project_ir, settings=resolved_settings, ir=ir
                )
                broker.publish(
                    ProjectProgressEvent(
                        event="project_completed",
                        project_id=project_id,
                        stage="renderer",
                        status="rendered",
                        message="Re-render completed.",
                        progress=1.0,
                        timestamp=utc_now(),
                        render_path=render_path,
                    )
                )
            except Exception as exc:
                broker.publish(
                    ProjectProgressEvent(
                        event="project_failed",
                        project_id=project_id,
                        stage="renderer",
                        status="failed",
                        message=str(exc),
                        progress=1.0,
                        timestamp=utc_now(),
                    )
                )

        task = asyncio.create_task(_run_render())
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)
        return {"status": "accepted", "project_id": project_id}

    # ── Export presets ────────────────────────────────────────────────────
    @app.get("/api/export/presets")
    def get_export_presets() -> dict:
        return {"presets": list_presets()}

    @app.post("/api/projects/{project_id}/export/{platform}", status_code=202)
    async def export_to_platform(project_id: str, platform: str) -> dict:
        project = await database.get_project(project_id)
        if project is None or project.ir is None:
            raise HTTPException(status_code=404, detail=f"Project IR for '{project_id}' not found.")
        try:
            ir = ProjectIR.model_validate(project.ir)
            patch = build_export_patch(ir, platform)
            patched_ir = apply_patch(ir, patch)
        except (ValueError, Exception) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        # Kick off a re-render with the patched IR
        async def _run_export() -> None:
            try:
                await run_in_threadpool(
                    render_project_ir, settings=resolved_settings, ir=patched_ir
                )
            except Exception:
                pass

        task = asyncio.create_task(_run_export())
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)
        return {
            "status": "accepted",
            "project_id": project_id,
            "platform": platform,
            "patch_ops": len(patch.ops),
        }

    return app


app = create_app()


def run() -> None:
    settings = Settings.from_env()
    uvicorn.run(
        "video_gen_agents.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )


if __name__ == "__main__":
    run()
