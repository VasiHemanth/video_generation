from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
import math
import re

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


HEX_COLOR_RE = re.compile(r"^#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})$")
ELEMENT_TYPES = {
    "text",
    "shape",
    "group",
    "progress",
    "counter",
    "code-block",
    "icon",
    "particle-field",
    "divider",
    "image",
    "device",
}


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TypographyToken(StrictModel):
    family: str
    weight: int
    size: int
    line_height: float = Field(alias="lineHeight")

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class SpringConfig(StrictModel):
    mass: float = 1.0
    damping: float = 12.0
    stiffness: float = 200.0


class MotionTokens(StrictModel):
    duration_fast: float
    duration_normal: float
    duration_slow: float
    duration_very_slow: float
    easing_default: str
    easing_enter: str
    easing_exit: str
    easing_bounce: str
    easing_spring: SpringConfig
    stagger_delay: float


class LayoutTokens(StrictModel):
    padding: int
    gap: int
    card_radius: int
    safe_area_x: int
    safe_area_y: int


class ThemeColors(StrictModel):
    bg_primary: str
    bg_secondary: str
    fg_primary: str
    fg_secondary: str
    accent_1: str
    accent_2: str
    accent_3: str
    gradient_start: str
    gradient_end: str
    surface: str
    border: str

    @field_validator("*")
    @classmethod
    def validate_color(cls, value: str) -> str:
        if not HEX_COLOR_RE.match(value):
            raise ValueError(f"Invalid hex color: {value}")
        return value


class ThemeTokens(StrictModel):
    name: str = "default"
    colors: ThemeColors
    typography: dict[str, TypographyToken]
    motion: MotionTokens
    layout: LayoutTokens


class Position(StrictModel):
    x: float | str
    y: float | str


class Size(StrictModel):
    width: float | str
    height: float | str


class TransitionConfig(StrictModel):
    type: str
    duration: float
    easing: str | None = None


class BackgroundConfig(StrictModel):
    type: str
    colors: list[str]
    angle: float | None = None
    animate: bool | None = None
    animation_speed: float | None = None


class AnimationConfig(StrictModel):
    type: str
    duration: float
    easing: str | None = None
    delay: float | None = None
    spring_config: SpringConfig | None = None
    distance: float | None = None


class Keyframe(StrictModel):
    time: float
    property: str
    value: float
    easing: str | None = None


class Element(StrictModel):
    id: str
    type: str
    props: dict[str, Any]
    position: Position
    size: Size | None = None
    anchor: str | None = None
    layer: int
    opacity: float = 1.0
    rotation: float = 0.0
    scale: float = 1.0
    enter: AnimationConfig | None = None
    exit: AnimationConfig | None = None
    emphasis: AnimationConfig | None = None
    keyframes: list[Keyframe] = Field(default_factory=list)
    delay: float | None = None
    parallax_factor: float | None = Field(default=None, alias="parallax_factor")

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str) -> str:
        if value not in ELEMENT_TYPES:
            raise ValueError(f"Unsupported element type: {value}")
        return value

    @model_validator(mode="after")
    def validate_props(self) -> "Element":
        required_props = {
            "text": {"content", "style_token", "color"},
            "shape": {"shape", "fill"},
            "progress": {"variant", "value", "max", "color", "track_color"},
            "counter": {"from", "to", "style_token", "color"},
            "code-block": {"code", "language"},
            "particle-field": {"count", "color"},
            "group": {"layout", "children"},
            "divider": {"orientation", "color"},
        }
        required = required_props.get(self.type, set())
        missing = sorted(required.difference(self.props))
        if missing:
            raise ValueError(f"{self.type} missing props: {', '.join(missing)}")
        return self


class Scene(StrictModel):
    id: str
    role: str
    title: str | None = None
    start_time: float
    duration: float
    transition_in: TransitionConfig | None = None
    transition_out: TransitionConfig | None = None
    background: BackgroundConfig
    elements: list[Element]

    @model_validator(mode="after")
    def validate_elements(self) -> "Scene":
        if not self.elements:
            raise ValueError("Scene must contain at least one element")
        return self


class Timeline(StrictModel):
    scenes: list[Scene]


class MusicPlan(StrictModel):
    track_id: str
    volume: float
    fade_in: float
    fade_out: float
    start_offset: float = 0.0


class VoiceoverPlan(StrictModel):
    enabled: bool = False
    segments: list[dict[str, Any]] = Field(default_factory=list)


class SFXEvent(StrictModel):
    id: str
    asset_id: str
    start_time: float
    volume: float
    role: str


class AudioPlan(StrictModel):
    music: MusicPlan | None = None
    voiceover: VoiceoverPlan = Field(default_factory=VoiceoverPlan)
    sfx: list[SFXEvent] = Field(default_factory=list)


class FontAsset(StrictModel):
    id: str
    family: str
    source: str


class MediaAsset(StrictModel):
    id: str
    path: str
    duration: float | None = None
    tags: list[str] = Field(default_factory=list)


class AssetRegistry(StrictModel):
    fonts: list[FontAsset]
    audio: list[MediaAsset] = Field(default_factory=list)
    svg: list[MediaAsset] = Field(default_factory=list)
    images: list[MediaAsset] = Field(default_factory=list)


class ProjectConstraints(StrictModel):
    min_duration: float = 30.0
    max_duration: float = 40.0
    min_scenes: int = 3
    max_scenes: int = 8
    min_scene_duration: float = 2.0
    max_scene_duration: float = 15.0
    platform: str = "youtube"
    brand: str | None = None
    content_safety: str = "standard"


class ProjectMeta(StrictModel):
    id: str
    title: str
    description: str = ""
    duration: float
    fps: int = 30
    width: int = 1920
    height: int = 1080
    aspect_ratio: Literal["16:9", "9:16", "1:1"] = "16:9"
    created_at: datetime
    status: Literal["draft", "generating", "rendered", "failed"] = "draft"


class ProjectIR(StrictModel):
    version: str = "1.0.0"
    meta: ProjectMeta
    theme: ThemeTokens
    timeline: Timeline
    audio: AudioPlan
    assets: AssetRegistry
    constraints: ProjectConstraints

    @model_validator(mode="after")
    def validate_consistency(self) -> "ProjectIR":
        scenes = self.timeline.scenes
        constraints = self.constraints
        total_duration = sum(scene.duration for scene in scenes)
        if not (constraints.min_duration <= self.meta.duration <= constraints.max_duration):
            raise ValueError("Project duration is outside configured limits")
        if not (constraints.min_scenes <= len(scenes) <= constraints.max_scenes):
            raise ValueError("Scene count is outside configured limits")
        if math.fabs(total_duration - self.meta.duration) > 0.5:
            raise ValueError("Scene durations must sum to the project duration")

        expected_start = 0.0
        theme_colors = set(self.theme.colors.model_dump().keys())
        typography_tokens = set(self.theme.typography.keys())
        for scene in scenes:
            if not (constraints.min_scene_duration <= scene.duration <= constraints.max_scene_duration):
                raise ValueError(f"Scene {scene.id} has invalid duration")
            if math.fabs(scene.start_time - expected_start) > 0.01:
                raise ValueError(f"Scene {scene.id} has a non-sequential start_time")
            expected_start = round(expected_start + scene.duration, 3)

            seen_layers: set[int] = set()
            for color in scene.background.colors:
                self._validate_color_ref(color, theme_colors)

            for element in scene.elements:
                if element.layer in seen_layers:
                    raise ValueError(f"Duplicate layer {element.layer} in scene {scene.id}")
                seen_layers.add(element.layer)
                self._validate_element_refs(element, theme_colors, typography_tokens)

        return self

    @staticmethod
    def _validate_color_ref(value: Any, theme_colors: set[str]) -> None:
        if not isinstance(value, str):
            return
        if value in theme_colors:
            return
        if HEX_COLOR_RE.match(value):
            return
        raise ValueError(f"Unknown color reference: {value}")

    def _validate_element_refs(
        self,
        element: Element,
        theme_colors: set[str],
        typography_tokens: set[str],
    ) -> None:
        if element.type == "text":
            style_token = element.props.get("style_token")
            if style_token not in typography_tokens:
                raise ValueError(f"Unknown typography token: {style_token}")
            self._validate_color_ref(element.props.get("color"), theme_colors)
        elif element.type == "shape":
            self._validate_color_ref(element.props.get("fill"), theme_colors)
            stroke = element.props.get("stroke")
            if stroke is not None:
                self._validate_color_ref(stroke, theme_colors)
        elif element.type == "progress":
            self._validate_color_ref(element.props.get("color"), theme_colors)
            self._validate_color_ref(element.props.get("track_color"), theme_colors)
        elif element.type == "counter":
            if element.props.get("style_token") not in typography_tokens:
                raise ValueError(f"Unknown typography token: {element.props.get('style_token')}")
            self._validate_color_ref(element.props.get("color"), theme_colors)
        elif element.type in {"particle-field", "divider"}:
            self._validate_color_ref(element.props.get("color"), theme_colors)


class PlanTask(StrictModel):
    id: str
    name: str
    agent: str
    deps: list[str] = Field(default_factory=list)


class Plan(StrictModel):
    tasks: list[PlanTask]


class GenerationConstraints(StrictModel):
    duration: float
    scenes: int
    aspect_ratio: Literal["16:9", "9:16", "1:1"] = "16:9"
    mood: str
    style_direction: str
    key_points: list[str]
    platform: str = "youtube"


class BriefClassification(StrictModel):
    archetype: str = "product_launch"
    scene_vocabulary: list[str] = Field(default_factory=list)
    mood: str = "professional"
    visual_style: str = "dark-tech"
    voice_tone: str = "confident"
    target_audience: str = "general"
    key_entities: list[str] = Field(default_factory=list)


class ScriptBeat(StrictModel):
    id: str
    type: str
    text: str = ""  # Legacy field, kept for backward compat
    headline_text: str = ""  # On-screen headline (≤8 words)
    subtitle_text: str = ""  # On-screen body (≤15 words)
    voiceover_text: str = ""  # What the narrator says
    duration: float
    visual_note: str


class Script(StrictModel):
    beats: list[ScriptBeat]


class StoryboardScene(StrictModel):
    scene_id: str
    role: str
    beat_ids: list[str]
    duration: float
    layout_hint: str
    description: str  # Internal-only stage direction (NOT shown to viewers)
    visual_style: str = ""  # For designer context


class SceneLayout(StrictModel):
    scene_id: str
    background: BackgroundConfig
    elements: list[Element]


class ElementMotion(StrictModel):
    element_id: str
    enter: AnimationConfig | None = None
    exit: AnimationConfig | None = None
    emphasis: AnimationConfig | None = None
    keyframes: list[Keyframe] = Field(default_factory=list)


class MotionScenePlan(StrictModel):
    scene_id: str
    transition_in: TransitionConfig | None = None
    transition_out: TransitionConfig | None = None
    elements: list[ElementMotion]


class VerificationIssue(StrictModel):
    check: str
    message: str
    route_to: str | None = None


class VerificationResult(StrictModel):
    status: Literal["passed", "passed_with_warnings", "failed"]
    errors: list[VerificationIssue] = Field(default_factory=list)
    warnings: list[VerificationIssue] = Field(default_factory=list)


class AgentLogEntry(StrictModel):
    agent: str
    status: str
    message: str
    timestamp: datetime


class PipelineSummary(StrictModel):
    scene_count: int
    duration: float
    theme_name: str
    render_status: str
    llm_configured: bool


class GenerateVideoRequest(StrictModel):
    brief: str
    title: str | None = None
    theme_name: str = "default"
    aspect_ratio: Literal["16:9", "9:16", "1:1"] = "16:9"
    duration: float = 35.0
    scene_count: int = 5
    platform: str = "youtube"
    render_video: bool = True

    @field_validator("brief")
    @classmethod
    def validate_brief(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 20:
            raise ValueError("Brief must contain at least 20 characters")
        return value

    @field_validator("duration")
    @classmethod
    def validate_duration(cls, value: float) -> float:
        if not (30 <= value <= 40):
            raise ValueError("Duration must be between 30 and 40 seconds")
        return value

    @field_validator("scene_count")
    @classmethod
    def validate_scene_count(cls, value: int) -> int:
        if not (3 <= value <= 8):
            raise ValueError("Scene count must be between 3 and 8")
        return value


class GenerateVideoResponse(StrictModel):
    project_id: str
    ir_path: str
    render_path: str | None = None
    ir: ProjectIR
    verification: VerificationResult
    logs: list[AgentLogEntry]
    summary: PipelineSummary


class ProjectLaunchResponse(StrictModel):
    project_id: str
    status: Literal["generating"] = "generating"
    detail_path: str
    websocket_path: str


class ProjectProgressEvent(StrictModel):
    event: Literal[
        "project_created",
        "stage_started",
        "stage_completed",
        "project_completed",
        "project_failed",
    ]
    project_id: str
    stage: str
    status: str
    message: str
    progress: float
    timestamp: datetime
    render_path: str | None = None
    verification_status: str | None = None


class StoredProjectSummary(StrictModel):
    project_id: str
    title: str
    status: str
    verification_status: str | None = None
    theme_name: str
    duration: float
    scene_count: int
    render_requested: bool
    render_path: str | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime


class StoredProjectDetail(StoredProjectSummary):
    brief: str
    aspect_ratio: str
    platform: str
    ir_path: str | None = None
    ir: ProjectIR | None = None
    summary: PipelineSummary | None = None
    verification: VerificationResult | None = None
    logs: list[AgentLogEntry] = Field(default_factory=list)
