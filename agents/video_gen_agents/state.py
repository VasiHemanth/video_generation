from __future__ import annotations

from typing import Callable, TypedDict

from .models import (
    AgentLogEntry,
    AudioPlan,
    GenerateVideoRequest,
    GenerationConstraints,
    MotionScenePlan,
    Plan,
    ProjectProgressEvent,
    ProjectIR,
    SceneLayout,
    Script,
    StoryboardScene,
    ThemeTokens,
    VerificationResult,
)


class VideoAgentState(TypedDict, total=False):
    project_id: str
    request: GenerateVideoRequest
    progress_callback: Callable[[ProjectProgressEvent], None]
    plan: Plan
    constraints: GenerationConstraints
    script: Script
    storyboard: list[StoryboardScene]
    theme: ThemeTokens
    layouts: list[SceneLayout]
    motion_plan: list[MotionScenePlan]
    audio_plan: AudioPlan
    ir: ProjectIR
    ir_path: str
    render_path: str | None
    verification: VerificationResult
    agent_logs: list[AgentLogEntry]
