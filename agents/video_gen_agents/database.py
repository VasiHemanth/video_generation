from __future__ import annotations

from datetime import datetime, timezone
from typing import AsyncIterator

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text, select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .config import Settings
from .models import (
    AgentLogEntry,
    GenerateVideoRequest,
    GenerateVideoResponse,
    PipelineSummary,
    ProjectIR,
    StoredProjectDetail,
    StoredProjectSummary,
    VerificationResult,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class ProjectRecord(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    brief: Mapped[str] = mapped_column(Text)
    theme_name: Mapped[str] = mapped_column(String(64))
    aspect_ratio: Mapped[str] = mapped_column(String(16))
    duration: Mapped[float] = mapped_column(Float)
    scene_count: Mapped[int] = mapped_column(Integer)
    platform: Mapped[str] = mapped_column(String(64))
    render_requested: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(32), default="generating")
    verification_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    ir_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    render_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    verification_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ir_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )


class AgentLogRecord(Base):
    __tablename__ = "agent_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("projects.project_id", ondelete="CASCADE"),
        index=True,
    )
    agent: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32))
    message: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ProjectCheckpoint(Base):
    __tablename__ = "project_checkpoints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("projects.project_id", ondelete="CASCADE"),
        index=True,
    )
    step_name: Mapped[str] = mapped_column(String(64))
    state_snapshot: Mapped[dict] = mapped_column(JSON)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class Database:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.engine: AsyncEngine = create_async_engine(settings.database_url, future=True)
        self.session_factory = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    async def init(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def dispose(self) -> None:
        await self.engine.dispose()

    async def session(self) -> AsyncIterator[AsyncSession]:
        async with self.session_factory() as session:
            yield session

    async def create_project(self, project_id: str, request: GenerateVideoRequest) -> None:
        async with self.session_factory() as session:
            async with session.begin():
                session.add(
                    ProjectRecord(
                        project_id=project_id,
                        title=request.title or "Untitled Video",
                        brief=request.brief,
                        theme_name=request.theme_name,
                        aspect_ratio=request.aspect_ratio,
                        duration=request.duration,
                        scene_count=request.scene_count,
                        platform=request.platform,
                        render_requested=request.render_video,
                        status="generating",
                    )
                )

    async def save_checkpoint(
        self,
        project_id: str,
        step_name: str,
        state_snapshot: dict,
    ) -> None:
        async with self.session_factory() as session:
            async with session.begin():
                session.add(
                    ProjectCheckpoint(
                        project_id=project_id,
                        step_name=step_name,
                        state_snapshot=state_snapshot,
                    )
                )

    async def save_generation_result(
        self,
        request: GenerateVideoRequest,
        response: GenerateVideoResponse,
    ) -> None:
        async with self.session_factory() as session:
            async with session.begin():
                project = await session.scalar(
                    select(ProjectRecord).where(ProjectRecord.project_id == response.project_id)
                )
                if project is None:
                    project = ProjectRecord(
                        project_id=response.project_id,
                        title=response.ir.meta.title,
                        brief=request.brief,
                        theme_name=request.theme_name,
                        aspect_ratio=request.aspect_ratio,
                        duration=request.duration,
                        scene_count=request.scene_count,
                        platform=request.platform,
                        render_requested=request.render_video,
                    )
                    session.add(project)

                project.title = response.ir.meta.title
                project.status = (
                    "rendered"
                    if response.render_path
                    else "generated_with_warnings"
                    if response.verification.status == "passed_with_warnings"
                    else "generated"
                )
                project.verification_status = response.verification.status
                project.ir_path = response.ir_path
                project.render_path = response.render_path
                project.error_message = None
                project.summary_json = response.summary.model_dump(mode="json")
                project.verification_json = response.verification.model_dump(mode="json")
                project.ir_json = response.ir.model_dump(mode="json", by_alias=True)
                project.updated_at = utc_now()

                await session.execute(
                    AgentLogRecord.__table__.delete().where(
                        AgentLogRecord.project_id == response.project_id
                    )
                )
                session.add_all(
                    [
                        AgentLogRecord(
                            project_id=response.project_id,
                            agent=entry.agent,
                            status=entry.status,
                            message=entry.message,
                            timestamp=entry.timestamp,
                        )
                        for entry in response.logs
                    ]
                )

    async def mark_project_failed(
        self,
        *,
        project_id: str,
        request: GenerateVideoRequest,
        error_message: str,
    ) -> None:
        async with self.session_factory() as session:
            async with session.begin():
                project = await session.scalar(
                    select(ProjectRecord).where(ProjectRecord.project_id == project_id)
                )
                if project is None:
                    project = ProjectRecord(
                        project_id=project_id,
                        title=request.title or "Untitled Video",
                        brief=request.brief,
                        theme_name=request.theme_name,
                        aspect_ratio=request.aspect_ratio,
                        duration=request.duration,
                        scene_count=request.scene_count,
                        platform=request.platform,
                        render_requested=request.render_video,
                    )
                    session.add(project)

                project.status = "failed"
                project.error_message = error_message
                project.updated_at = utc_now()

    async def list_projects(self) -> list[StoredProjectSummary]:
        async with self.session_factory() as session:
            result = await session.scalars(
                select(ProjectRecord).order_by(ProjectRecord.created_at.desc())
            )
            return [self._to_summary(record) for record in result.all()]

    async def get_project(self, project_id: str) -> StoredProjectDetail | None:
        async with self.session_factory() as session:
            project = await session.scalar(
                select(ProjectRecord).where(ProjectRecord.project_id == project_id)
            )
            if project is None:
                return None

            logs = await session.scalars(
                select(AgentLogRecord)
                .where(AgentLogRecord.project_id == project_id)
                .order_by(AgentLogRecord.timestamp.asc())
            )
            return self._to_detail(project, list(logs.all()))

    def _to_summary(self, record: ProjectRecord) -> StoredProjectSummary:
        return StoredProjectSummary(
            project_id=record.project_id,
            title=record.title,
            status=record.status,
            verification_status=record.verification_status,
            theme_name=record.theme_name,
            duration=record.duration,
            scene_count=record.scene_count,
            render_requested=record.render_requested,
            render_path=record.render_path,
            error_message=record.error_message,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

    def _to_detail(
        self,
        record: ProjectRecord,
        logs: list[AgentLogRecord],
    ) -> StoredProjectDetail:
        ir = ProjectIR.model_validate(record.ir_json) if record.ir_json is not None else None
        summary = (
            PipelineSummary.model_validate(record.summary_json)
            if record.summary_json is not None
            else None
        )
        verification = (
            VerificationResult.model_validate(record.verification_json)
            if record.verification_json is not None
            else None
        )
        return StoredProjectDetail(
            **self._to_summary(record).model_dump(),
            brief=record.brief,
            aspect_ratio=record.aspect_ratio,
            platform=record.platform,
            ir_path=record.ir_path,
            ir=ir,
            summary=summary,
            verification=verification,
            logs=[
                AgentLogEntry(
                    agent=entry.agent,
                    status=entry.status,
                    message=entry.message,
                    timestamp=entry.timestamp,
                )
                for entry in logs
            ],
        )
