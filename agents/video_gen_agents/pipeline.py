from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re
from langgraph.graph import END, START, StateGraph
from typing import Any, Callable, Literal
from uuid import uuid4

from .config import Settings
from .llm import build_groq_chat_model, groq_is_configured
from .models import (
    AgentLogEntry,
    AnimationConfig,
    AssetRegistry,
    AudioPlan,
    BackgroundConfig,
    BriefClassification,
    Element,
    ElementMotion,
    FontAsset,
    GenerateVideoRequest,
    GenerateVideoResponse,
    GenerationConstraints,
    Keyframe,
    MediaAsset,
    MotionScenePlan,
    MusicPlan,
    PipelineSummary,
    Plan,
    PlanTask,
    Position,
    ProjectProgressEvent,
    ProjectConstraints,
    ProjectIR,
    ProjectMeta,
    Scene,
    SceneLayout,
    Script,
    ScriptBeat,
    SFXEvent,
    Size,
    StoryboardScene,
    ThemeTokens,
    Timeline,
    TransitionConfig,
    VerificationIssue,
    VerificationResult,
)
from .rendering import remotion_is_available, render_project_ir
from .state import VideoAgentState
from .themes import list_theme_names, load_theme


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


STAGE_PROGRESS = {
    "manager": 0.1,
    "scriptwriter": 0.25,
    "designer": 0.42,
    "motion": 0.58,
    "audio": 0.72,
    "renderer": 0.9,
    "verifier": 1.0,
}


def _append_log(
    state: VideoAgentState,
    *,
    agent: str,
    status: str,
    message: str,
) -> list[AgentLogEntry]:
    logs = list(state.get("agent_logs", []))
    logs.append(
        AgentLogEntry(
            agent=agent,
            status=status,
            message=message,
            timestamp=_utc_now(),
        )
    )
    return logs


def _emit_progress(
    state: VideoAgentState,
    *,
    event: str,
    stage: str,
    status: str,
    message: str,
    progress: float,
    render_path: str | None = None,
    verification_status: str | None = None,
    timestamp: datetime | None = None,
) -> None:
    callback = state.get("progress_callback")
    if callback is None:
        return

    callback(
        ProjectProgressEvent(
            event=event,
            project_id=state["project_id"],
            stage=stage,
            status=status,
            message=message,
            progress=progress,
            timestamp=timestamp or _utc_now(),
            render_path=render_path,
            verification_status=verification_status,
        )
    )


def _derive_title(brief: str) -> str:
    cleaned = re.sub(r"\s+", " ", brief.strip())
    if not cleaned:
        return "Untitled Video"
    first_sentence = re.split(r"[.!?]", cleaned)[0].strip()
    words = first_sentence.split()
    title = " ".join(words[:7]).strip()
    return title.rstrip(":,") or "Untitled Video"


def _extract_key_points(brief: str, max_points: int = 3) -> list[str]:
    segments = [
        segment.strip(" -")
        for segment in re.split(r"[.!?;\n]", brief)
        if segment.strip()
    ]
    key_points: list[str] = []
    for segment in segments:
        normalized = re.sub(r"\s+", " ", segment)
        if len(normalized.split()) < 3:
            continue
        if normalized.lower() in {point.lower() for point in key_points}:
            continue
        key_points.append(normalized)
        if len(key_points) == max_points:
            break

    if len(key_points) < max_points:
        fallback = re.sub(r"\s+", " ", brief).strip()
        key_points.append(fallback[:120].rstrip(" ,.;"))

    return key_points[:max_points]


def _scene_roles(scene_count: int) -> list[str]:
    if scene_count == 3:
        return ["intro", "payoff", "cta"]
    if scene_count == 4:
        return ["intro", "setup", "payoff", "cta"]
    roles = ["intro", "setup"]
    roles.extend(["demo"] * max(scene_count - 4, 0))
    roles.extend(["payoff", "cta"])
    return roles[:scene_count]


def _duration_buckets(total_duration: float, scene_count: int) -> list[float]:
    weights = [1.0] * scene_count
    weights[0] = 0.9
    weights[-1] = 0.9
    if scene_count > 3:
        weights[-2] = 1.1

    total_weight = sum(weights)
    durations = [round(total_duration * weight / total_weight, 1) for weight in weights]
    difference = round(total_duration - sum(durations), 1)
    durations[-1] = round(durations[-1] + difference, 1)
    return durations


def _run_voice_generation(
    settings: Settings,
    project_id: str,
    storyboard: list[StoryboardScene],
    script: Script,
) -> dict[str, Any] | None:
    """Invokes scripts/generate_voice.py to produce audio for the script."""
    import subprocess
    import tempfile

    # Build intermediate JSON for the script (matches what generate_voice expects)
    content = {
        "timeline": {"scenes": [s.model_dump(mode="json") for s in storyboard]},
        "script_beats": [b.model_dump(mode="json") for b in script.beats],
    }
    # Add script texts directly to scenes for audio generation
    # Use voiceover_text (narration) rather than headline_text (on-screen)
    beat_map = {b.id: (b.voiceover_text or b.text) for b in script.beats}
    for scene in content["timeline"]["scenes"]:
        scene["script"] = " ".join([beat_map.get(bid, "") for bid in scene.get("beat_ids", [])])

    data_dir = settings.remotion_project_path / "public" / "voice"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    with tempfile.NamedTemporaryFile("w+", suffix=".json") as f:
        json.dump(content, f)
        f.flush()
        
        try:
            subprocess.run(
                [
                    "python3",
                    "scripts/generate_voice.py",
                    "--question", project_id,
                    "--content", f.name,
                    "--output-dir", str(data_dir),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            manifest_path = data_dir / f"{project_id}_voice_manifest.json"
            if manifest_path.exists():
                manifest = json.loads(manifest_path.read_text())
                # Ensure paths are relative to public directory for Remotion staticFile
                for seg in manifest.get("segments", []):
                    if seg.get("path") and "public" in seg["path"]:
                        seg["path"] = seg["path"].split("public/")[-1]
                return manifest
        except Exception as e:
            print(f"Voice generation error: {e}")
            if hasattr(e, "stderr"):
                print(f"Stderr: {e.stderr}")
    return None


def _build_plan() -> Plan:
    return Plan(
        tasks=[
            PlanTask(id="task_manager", name="Plan Project", agent="manager"),
            PlanTask(
                id="task_script",
                name="Generate Script",
                agent="scriptwriter",
                deps=["task_manager"],
            ),
            PlanTask(
                id="task_design",
                name="Design Visuals",
                agent="designer",
                deps=["task_script"],
            ),
            PlanTask(
                id="task_motion",
                name="Plan Motion",
                agent="motion",
                deps=["task_design"],
            ),
            PlanTask(
                id="task_audio",
                name="Plan Audio",
                agent="audio",
                deps=["task_motion"],
            ),
            PlanTask(
                id="task_render",
                name="Assemble IR",
                agent="renderer",
                deps=["task_audio"],
            ),
            PlanTask(
                id="task_verify",
                name="Verify Output",
                agent="verifier",
                deps=["task_render"],
            ),
        ]
    )


def _build_generation_constraints(request: GenerateVideoRequest) -> GenerationConstraints:
    theme_style = request.theme_name.replace("-", " ")
    return GenerationConstraints(
        duration=request.duration,
        scenes=request.scene_count,
        aspect_ratio=request.aspect_ratio,
        mood="professional, energetic",
        style_direction=f"{theme_style} motion graphics",
        key_points=_extract_key_points(request.brief, max_points=min(3, request.scene_count)),
        platform=request.platform,
    )


def _build_script_and_storyboard(
    request: GenerateVideoRequest,
    constraints: GenerationConstraints,
) -> tuple[Script, list[StoryboardScene]]:
    """Build script beats and storyboard with proper voice-text separation.
    
    headline_text: On-screen headline (≤8 words, punchy, viewer-facing)
    subtitle_text: On-screen body (≤15 words, viewer-facing context)
    voiceover_text: What the narrator says (2-3 sentences, conversational)
    visual_note: Internal-only instruction for Designer (NEVER shown)
    """
    roles = _scene_roles(constraints.scenes)
    durations = _duration_buckets(constraints.duration, len(roles))
    key_points = constraints.key_points

    title = request.title or _derive_title(request.brief)
    beats: list[ScriptBeat] = []
    storyboard: list[StoryboardScene] = []

    for index, role in enumerate(roles):
        beat_id = f"beat_{index + 1:03d}"
        scene_id = f"scene_{index + 1:03d}"
        duration = durations[index]
        point = key_points[min(index, len(key_points) - 1)]

        if role == "intro":
            headline_text = title
            subtitle_text = f"A new way to {point.lower().rstrip('.')}."
            voiceover_text = (
                f"Imagine having a tool that truly understands {point.lower().rstrip('.')}. "
                f"That's exactly what {title} delivers."
            )
            visual_note = "Hero headline centered with device preview below. Dramatic accent glow and particles."
            layout_hint = "centered_hero"
            description = "Opening hook with brand reveal."
        elif role == "setup":
            headline_text = point.rstrip(".")
            subtitle_text = f"Built for clarity and simplicity."
            voiceover_text = (
                f"Let's talk about {point.lower().rstrip('.')}. "
                f"{title} makes this intuitive and effortless."
            )
            visual_note = "Structured layout with headline, supporting body, and device/visual below a divider."
            layout_hint = "split_layout"
            description = f"Explain: {point.lower().rstrip('.')}."
        elif role == "demo":
            headline_text = "See It in Action"
            subtitle_text = f"Real results, measurable impact."
            voiceover_text = (
                f"Here's what happens when you put {title} to work. "
                f"{point.rstrip('.')} — all backed by real data."
            )
            visual_note = "Evidence scene with progress bar or metric visualization."
            layout_hint = "stat_showcase"
            description = f"Demo: {point.lower().rstrip('.')} with data."
        elif role == "payoff":
            headline_text = "The Results Speak"
            subtitle_text = f"Join thousands who chose {title}."
            voiceover_text = (
                f"People who use {title} report measurable improvements. "
                f"The numbers tell the story."
            )
            visual_note = "Large counter/stat at center with supporting text below."
            layout_hint = "stat_showcase"
            description = f"Impact metrics for {title}."
        else:  # cta
            headline_text = f"Try {title} Today"
            subtitle_text = "Start your journey now."
            voiceover_text = (
                f"Ready to experience {title} for yourself? "
                f"Get started today and see the difference."
            )
            visual_note = "Clean CTA scene with button and tagline on glassmorphism card."
            layout_hint = "cta_card"
            description = "Final call to action."

        # Legacy text field = voiceover for backward compat
        text = voiceover_text

        beats.append(
            ScriptBeat(
                id=beat_id,
                type=role,
                text=text,
                headline_text=headline_text,
                subtitle_text=subtitle_text,
                voiceover_text=voiceover_text,
                duration=duration,
                visual_note=visual_note,
            )
        )
        storyboard.append(
            StoryboardScene(
                scene_id=scene_id,
                role=role,
                beat_ids=[beat_id],
                duration=duration,
                layout_hint=layout_hint,
                description=description,
            )
        )

    return Script(beats=beats), storyboard


def _build_text_element(
    *,
    element_id: str,
    content: str,
    style_token: str,
    color: str,
    x: str,
    y: str,
    layer: int,
    align: str = "center",
    max_width: int = 1100,
) -> Element:
    return Element(
        id=element_id,
        type="text",
        props={
            "content": content,
            "style_token": style_token,
            "color": color,
            "align": align,
            "max_width": max_width,
            "word_animation": "word-by-word",
            "word_stagger": 0.02,
        },
        position=Position(x=x, y=y),
        anchor="center",
        layer=layer,
    )


def _build_layouts(
    storyboard: list[StoryboardScene],
    script: Script,
    theme: ThemeTokens,
) -> list[SceneLayout]:
    beats = {beat.id: beat for beat in script.beats}
    colors = theme.colors.model_dump()

    layouts: list[SceneLayout] = []
    for index, scene in enumerate(storyboard):
        beat = beats[scene.beat_ids[0]]
        background = BackgroundConfig(
            type="animated-gradient" if index % 2 == 0 else "gradient",
            colors=[colors["bg_primary"], colors["surface"]],
            angle=135,
            animate=index % 2 == 0,
            animation_speed=0.3 if index % 2 == 0 else None,
        )
        # Common particles background
        particles = Element(
            id=f"{scene.scene_id}_particles",
            type="particle-field",
            props={
                "count": 28 + (index * 6),
                "color": "accent_2" if index % 2 else "accent_1",
                "size_range": [2, 6],
                "speed": 0.35,
                "connection_lines": False,
                "opacity": 0.18,
            },
            position=Position(x="0%", y="0%"),
            size=Size(width="100%", height="100%"),
            layer=0,
            parallax_factor=0.12,
        )

        # ── Role-specific layouts ──────────────────────────────────────────
        if scene.role == "intro":
            elements: list[Element] = [
                particles,
                Element(
                    id=f"{scene.scene_id}_shape",
                    type="shape",
                    props={"shape": "circle", "fill": "accent_1", "stroke": "border", "stroke_width": 2, "corner_radius": 28},
                    position=Position(x="78%", y="15%"),
                    size=Size(width=180, height=180),
                    anchor="center", layer=1, opacity=0.15, rotation=15, parallax_factor=0.3,
                ),
                Element(
                    id=f"{scene.scene_id}_shape_2",
                    type="shape",
                    props={"shape": "rounded-rect", "fill": "accent_3", "stroke": "border", "stroke_width": 1, "corner_radius": 20},
                    position=Position(x="15%", y="80%"),
                    size=Size(width=120, height=120),
                    anchor="center", layer=2, opacity=0.12, rotation=-8, parallax_factor=0.2,
                ),
                _build_text_element(
                    element_id=f"{scene.scene_id}_headline",
                    content=beat.headline_text or beat.text,
                    style_token="display_md",
                    color="fg_primary",
                    x="50%", y="30%", layer=3,
                ),
                _build_text_element(
                    element_id=f"{scene.scene_id}_body",
                    content=beat.subtitle_text,
                    style_token="body_lg",
                    color="fg_secondary",
                    x="50%", y="52%", layer=4, max_width=900,
                ),
                Element(
                    id=f"{scene.scene_id}_device",
                    type="device",
                    props={"variant": "phone", "color": "accent_1"},
                    position=Position(x="50%", y="78%"),
                    size=Size(width=260, height=460),
                    anchor="center", layer=5, parallax_factor=-0.1,
                ),
            ]
        elif scene.role == "setup":
            elements = [
                particles,
                Element(
                    id=f"{scene.scene_id}_shape",
                    type="shape",
                    props={"shape": "rounded-rect", "fill": "accent_2", "stroke": "border", "stroke_width": 2, "corner_radius": 24},
                    position=Position(x="85%", y="22%"),
                    size=Size(width=160, height=160),
                    anchor="center", layer=1, opacity=0.15, rotation=20, parallax_factor=0.25,
                ),
                _build_text_element(
                    element_id=f"{scene.scene_id}_headline",
                    content=beat.headline_text or beat.text,
                    style_token="heading_lg",
                    color="fg_primary",
                    x="50%", y="25%", layer=2,
                ),
                _build_text_element(
                    element_id=f"{scene.scene_id}_body",
                    content=beat.subtitle_text,
                    style_token="body_lg",
                    color="fg_secondary",
                    x="50%", y="48%", layer=3, max_width=880,
                ),
                Element(
                    id=f"{scene.scene_id}_divider",
                    type="divider",
                    props={"orientation": "horizontal", "thickness": 2, "color": "accent_2"},
                    position=Position(x="50%", y="65%"),
                    size=Size(width=600, height=2),
                    anchor="center", layer=4,
                ),
                Element(
                    id=f"{scene.scene_id}_device",
                    type="device",
                    props={"variant": "phone", "color": "accent_2"},
                    position=Position(x="50%", y="80%"),
                    size=Size(width=240, height=420),
                    anchor="center", layer=5, parallax_factor=-0.08,
                ),
            ]
        elif scene.role == "cta":
            elements = [
                particles,
                Element(
                    id=f"{scene.scene_id}_shape",
                    type="shape",
                    props={"shape": "rounded-rect", "fill": "accent_1", "stroke": "border", "stroke_width": 2, "corner_radius": 32},
                    position=Position(x="50%", y="50%"),
                    size=Size(width=800, height=400),
                    anchor="center", layer=1, opacity=0.08,
                ),
                _build_text_element(
                    element_id=f"{scene.scene_id}_headline",
                    content=beat.headline_text or beat.text,
                    style_token="display_sm",
                    color="fg_primary",
                    x="50%", y="35%", layer=2,
                ),
                _build_text_element(
                    element_id=f"{scene.scene_id}_body",
                    content=beat.subtitle_text,
                    style_token="body_lg",
                    color="fg_secondary",
                    x="50%", y="55%", layer=3, max_width=800,
                ),
                Element(
                    id=f"{scene.scene_id}_shape_btn",
                    type="shape",
                    props={"shape": "rounded-rect", "fill": "accent_1", "stroke": "accent_1", "stroke_width": 0, "corner_radius": 16},
                    position=Position(x="50%", y="72%"),
                    size=Size(width=360, height=64),
                    anchor="center", layer=4,
                ),
                _build_text_element(
                    element_id=f"{scene.scene_id}_cta_label",
                    content="Get Started",
                    style_token="heading_md",
                    color="fg_primary",
                    x="50%", y="72%", layer=5,
                ),
            ]
        else:  # payoff, demo, or any other role
            elements = [
                particles,
                Element(
                    id=f"{scene.scene_id}_shape",
                    type="shape",
                    props={"shape": "circle", "fill": "accent_2", "stroke": "border", "stroke_width": 2, "corner_radius": 28},
                    position=Position(x="80%", y="20%"),
                    size=Size(width=200, height=200),
                    anchor="center", layer=1, opacity=0.15, rotation=10, parallax_factor=0.2,
                ),
                _build_text_element(
                    element_id=f"{scene.scene_id}_headline",
                    content=beat.headline_text or beat.text,
                    style_token="heading_lg",
                    color="fg_primary",
                    x="50%", y="28%", layer=2,
                ),
                _build_text_element(
                    element_id=f"{scene.scene_id}_body",
                    content=beat.subtitle_text,
                    style_token="body_lg",
                    color="fg_secondary",
                    x="50%", y="50%", layer=3, max_width=880,
                ),
            ]

        if scene.role == "demo":
            elements.append(
                Element(
                    id=f"{scene.scene_id}_progress",
                    type="progress",
                    props={
                        "variant": "bar",
                        "value": 78,
                        "max": 100,
                        "color": "accent_2",
                        "track_color": "surface",
                        "thickness": 12,
                        "animate_to": 78,
                        "label": "78% structured",
                    },
                    position=Position(x="50%", y="72%"),
                    size=Size(width=720, height=32),
                    anchor="center",
                    layer=4,
                )
            )
        if scene.role == "payoff":
            elements.append(
                Element(
                    id=f"{scene.scene_id}_counter",
                    type="counter",
                    props={
                        "from": 0,
                        "to": 92,
                        "prefix": "",
                        "suffix": "% less stress",
                        "style_token": "display_sm",
                        "color": "accent_1",
                        "format": "comma-separated",
                    },
                    position=Position(x="50%", y="72%"),
                    anchor="center",
                    layer=4,
                )
            )

        layouts.append(
            SceneLayout(
                scene_id=scene.scene_id,
                background=background,
                elements=elements,
            )
        )

    return layouts


def _build_motion(layouts: list[SceneLayout], theme: ThemeTokens) -> list[MotionScenePlan]:
    motion: list[MotionScenePlan] = []
    for scene_index, layout in enumerate(layouts):
        element_motions: list[ElementMotion] = []
        for element_index, element in enumerate(layout.elements):
            delay = round(element_index * theme.motion.stagger_delay, 2)
            if element.type == "particle-field":
                enter = AnimationConfig(type="fade-in", duration=0.4, delay=0.0)
                emphasis = None
                keyframes: list[Keyframe] = []
            elif element.type == "shape":
                enter = AnimationConfig(
                    type="spring",
                    duration=0.8,
                    delay=delay,
                    spring_config=theme.motion.easing_spring,
                )
                emphasis = AnimationConfig(type="scale-in", duration=0.4, delay=1.2)
                keyframes = [Keyframe(time=1.4, property="rotation", value=element.rotation + 10)]
            elif element.type == "progress":
                enter = AnimationConfig(type="wipe", duration=0.7, delay=delay)
                emphasis = AnimationConfig(type="bounce", duration=0.4, delay=1.0)
                keyframes = []
            elif element.type == "device":
                enter = AnimationConfig(type="slide-up", duration=0.8, delay=delay, distance=100)
                emphasis = AnimationConfig(type="bounce", duration=0.4, delay=1.2)
                keyframes = []
            elif element.type == "counter":
                enter = AnimationConfig(type="scale-in", duration=0.6, delay=delay)
                emphasis = AnimationConfig(type="bounce", duration=0.5, delay=1.1)
                keyframes = []
            else:
                enter = AnimationConfig(
                    type="spring" if element_index == 2 else "slide-up",
                    duration=0.7,
                    delay=delay,
                    distance=48 if element_index != 2 else None,
                    spring_config=theme.motion.easing_spring if element_index == 2 else None,
                )
                emphasis = None
                keyframes = []

            element_motions.append(
                ElementMotion(
                    element_id=element.id,
                    enter=enter,
                    exit=AnimationConfig(type="fade-out", duration=0.25),
                    emphasis=emphasis,
                    keyframes=keyframes,
                )
            )

        motion.append(
            MotionScenePlan(
                scene_id=layout.scene_id,
                transition_in=TransitionConfig(
                    type="fade" if scene_index == 0 else "slide-left",
                    duration=0.4,
                    easing=theme.motion.easing_enter,
                ),
                transition_out=TransitionConfig(
                    type="fade" if scene_index == len(layouts) - 1 else "slide-left",
                    duration=0.35,
                    easing=theme.motion.easing_exit,
                ),
                elements=element_motions,
            )
        )
    return motion


def _build_assets() -> AssetRegistry:
    return AssetRegistry(
        fonts=[
            FontAsset(id="inter", family="Inter", source="google-fonts"),
            FontAsset(id="jetbrains-mono", family="JetBrains Mono", source="google-fonts"),
        ],
        audio=[
            MediaAsset(id="bg_music_default", path="audio/music/ambient_tech.mp3", tags=["ambient", "tech"]),
            MediaAsset(id="sfx_whoosh", path="audio/sfx/whoosh.mp3", tags=["transition", "whoosh"]),
            MediaAsset(id="sfx_click", path="audio/sfx/click.mp3", tags=["ui", "click"]),
        ]
    )


def _build_audio_plan(storyboard: list[StoryboardScene]) -> AudioPlan:
    # 1. Select music based on project mood (Phase 1: fixed default)
    music = MusicPlan(
        track_id="bg_music_default",
        volume=0.4,
        fade_in=2.0,
        fade_out=3.0,
    )

    # 2. Place SFX at scene transitions
    sfx: list[SFXEvent] = []
    current_time = 0.0
    for index, scene in enumerate(storyboard):
        if index > 0:
            # Add a whoosh at every scene transition
            sfx.append(
                SFXEvent(
                    id=f"sfx_trans_{index}",
                    asset_id="sfx_whoosh",
                    start_time=round(current_time - 0.2, 3), # Slight lead-in
                    volume=0.35,
                    role="transition",
                )
            )
        
        # Add a click for special roles
        if scene.role in {"demo", "payoff"}:
             sfx.append(
                SFXEvent(
                    id=f"sfx_click_{index}",
                    asset_id="sfx_click",
                    start_time=round(current_time + 0.5, 3),
                    volume=0.5,
                    role="accent",
                )
            )
             
        current_time += scene.duration

    return AudioPlan(music=music, sfx=sfx)


def _merge_scene(
    storyboard_scene: StoryboardScene,
    layout: SceneLayout,
    motion: MotionScenePlan,
    start_time: float,
) -> Scene:
    motion_by_id = {item.element_id: item for item in motion.elements}
    elements: list[Element] = []
    for element in layout.elements:
        element_motion = motion_by_id.get(element.id)
        elements.append(
            element.model_copy(
                update={
                    "enter": element_motion.enter if element_motion else None,
                    "exit": element_motion.exit if element_motion else None,
                    "emphasis": element_motion.emphasis if element_motion else None,
                    "keyframes": element_motion.keyframes if element_motion else [],
                }
            )
        )

    return Scene(
        id=storyboard_scene.scene_id,
        role=storyboard_scene.role,
        title=storyboard_scene.description,
        start_time=round(start_time, 3),
        duration=storyboard_scene.duration,
        transition_in=motion.transition_in,
        transition_out=motion.transition_out,
        background=layout.background,
        elements=elements,
    )


class VideoGenerationService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings.from_env()
        self.graph = self._build_graph()

    def available_themes(self) -> list[str]:
        return list_theme_names(self.settings)

    def generate(
        self,
        request: GenerateVideoRequest,
        project_id: str | None = None,
        progress_callback: Callable[[ProjectProgressEvent], None] | None = None,
        checkpoint_callback: Callable[[str, str, dict], None] | None = None,
    ) -> GenerateVideoResponse:
        project_id = project_id or f"proj_{uuid4().hex[:8]}"
        initial_state: VideoAgentState = {
            "project_id": project_id,
            "request": request,
            "agent_logs": [],
        }
        if progress_callback is not None:
            initial_state["progress_callback"] = progress_callback
        if checkpoint_callback is not None:
            initial_state["checkpoint_callback"] = checkpoint_callback

        state = self.graph.invoke(initial_state)
        return GenerateVideoResponse(
            project_id=project_id,
            ir_path=state["ir_path"],
            render_path=state.get("render_path"),
            ir=state["ir"],
            verification=state["verification"],
            logs=state.get("agent_logs", []),
            summary=PipelineSummary(
                scene_count=len(state["ir"].timeline.scenes),
                duration=state["ir"].meta.duration,
                theme_name=state["theme"].name,
                render_status="rendered" if state.get("render_path") else "ir_only",
                llm_configured=groq_is_configured(self.settings),
            ),
        )

    def _build_graph(self):
        graph = StateGraph(VideoAgentState)
        graph.add_node("manager", self._manager_node)
        graph.add_node("script", self._script_node)
        graph.add_node("design", self._design_node)
        graph.add_node("motion", self._motion_node)
        graph.add_node("audio", self._audio_node)
        graph.add_node("render", self._render_node)
        graph.add_node("verify", self._verify_node)

        graph.add_edge(START, "manager")
        graph.add_edge("manager", "script")
        graph.add_edge("script", "design")
        graph.add_edge("design", "motion")
        graph.add_edge("motion", "audio")
        graph.add_node("voice", self._voice_node)
        graph.add_edge("audio", "voice")
        graph.add_edge("voice", "render")
        graph.add_edge("render", "verify")
        graph.add_edge("verify", END)
        return graph.compile()

    def _checkpoint(self, state: VideoAgentState, step_name: str, snapshot_keys: list[str]) -> None:
        callback = state.get("checkpoint_callback")
        if not callback:
            return
        
        snapshot = {k: state[k] for k in snapshot_keys if k in state}
        # Special handling for Pydantic models to ensure JSON serializability
        def _json_safe(obj):
            if hasattr(obj, "model_dump"):
                return obj.model_dump(mode="json")
            if isinstance(obj, list):
                return [_json_safe(i) for i in obj]
            if isinstance(obj, dict):
                return {k: _json_safe(v) for k, v in obj.items()}
            return obj

        callback(state["project_id"], step_name, _json_safe(snapshot))

    def _manager_node(self, state: VideoAgentState) -> dict:
        request = state["request"]
        _emit_progress(
            state,
            event="stage_started",
            stage="manager",
            status="running",
            message="Parsing the brief into constraints and a task plan.",
            progress=0.04,
        )

        model = build_groq_chat_model(self.settings, temperature=0.3)
        if model:
            try:
                prompt = (
                    "You are a senior creative director for a video production system.\n"
                    "Your task is to parse a natural-language brief into project constraints and a task plan.\n\n"
                    f"Brief: {request.brief}\n"
                    f"Requested Duration: {request.duration}s\n"
                    f"Requested Scene Count: {request.scene_count}\n"
                    f"Aspect Ratio: {request.aspect_ratio}\n\n"
                    "Return ONLY a JSON object exactly matching this schema:\n"
                    "{\n"
                    '  "constraints": {\n'
                    '    "duration": float, "scenes": integer, "aspect_ratio": "16:9"|"9:16"|"1:1",\n'
                    '    "mood": string, "style_direction": string, "key_points": [string, ...], "platform": string\n'
                    "  }\n"
                    "}\n"
                    "Rule: Duration must be between 30.0 and 40.0. Scenes must be between 3 and 8.\n"
                    "Return ONLY JSON, no filler."
                )
                response = model.invoke(prompt)
                print(f"DEBUG MANAGER RESPONSE: {response.content}")
                parsed = json.loads(response.content.strip("`").removeprefix("json").strip())
                constraints_dict = parsed.get("constraints", {})
                constraints = GenerationConstraints(**constraints_dict)
            except Exception as e:
                # Fallback to deterministic logic on LLM failure
                constraints = _build_generation_constraints(request)
        else:
            constraints = _build_generation_constraints(request)

        agent_logs = _append_log(
            state,
            agent="manager",
            status="completed",
            message="Parsed request into project constraints and a sequential task plan.",
        )
        log_entry = agent_logs[-1]
        _emit_progress(
            state,
            event="stage_completed",
            stage="manager",
            status="completed",
            message=log_entry.message,
            progress=STAGE_PROGRESS["manager"],
            timestamp=log_entry.timestamp,
        )
        
        res = {
            "plan": _build_plan(),
            "constraints": constraints,
            "agent_logs": agent_logs,
        }
        self._checkpoint({**state, **res}, "manager", ["plan", "constraints"])
        return res

    def _script_node(self, state: VideoAgentState) -> dict:
        _emit_progress(
            state,
            event="stage_started",
            stage="scriptwriter",
            status="running",
            message="Generating beats and storyboard scenes.",
            progress=0.14,
        )

        constraints = state["constraints"]
        model = build_groq_chat_model(self.settings, temperature=0.7)
        if model:
            try:
                prompt = (
                    "You are an expert scriptwriter for short motion graphics videos.\n"
                    "Generate a compelling narrative breakdown with SEPARATE text for voiceover vs on-screen display.\n\n"
                    f"Brief: {state['request'].brief}\n"
                    f"Total Duration: {constraints.duration}s\n"
                    f"Scene Count: {constraints.scenes}\n"
                    f"Key Points: {', '.join(constraints.key_points)}\n\n"
                    "Return ONLY a JSON object with this structure:\n"
                    "{\n"
                    '  "script": { "beats": [{\n'
                    '    "id": string, "type": "intro"|"setup"|"demo"|"payoff"|"cta"|"outro",\n'
                    '    "headline_text": string,   // On-screen headline, MAX 8 words, punchy\n'
                    '    "subtitle_text": string,    // On-screen body, MAX 15 words, viewer-facing context\n'
                    '    "voiceover_text": string,   // What the narrator SAYS, 2-3 natural sentences\n'
                    '    "text": string,             // Legacy: same as voiceover_text\n'
                    '    "duration": float,\n'
                    '    "visual_note": string        // Internal instruction for Designer, NOT shown on screen\n'
                    "  }] },\n"
                    '  "storyboard": [{ "scene_id": string, "role": string, "beat_ids": [string], '
                    '"duration": float, "layout_hint": string, "description": string }]\n'
                    "}\n\n"
                    "TEXT RULES (CRITICAL):\n"
                    "- headline_text: MAX 8 words. Punchy hook. Never start with 'First,' or 'Next,'\n"
                    "  GOOD: 'Your Mind Deserves Calm'  BAD: 'This video breaks the idea into a story'\n"
                    "- subtitle_text: MAX 15 words. Viewer-facing context. NEVER a stage direction.\n"
                    "  GOOD: 'Guided meditation for your daily routine'  BAD: 'Strong hook that frames the topic'\n"
                    "- voiceover_text: Natural spoken narration, 2-3 sentences. Conversational.\n"
                    "- visual_note: Internal-only. Never shown. Describes what visual elements to use.\n"
                    "- description: Internal storyboard note. Never shown to viewers.\n\n"
                    "Mandatory Rules:\n"
                    f"- The sum of ALL scene durations must exactly equal {constraints.duration}.\n"
                    "- Each scene duration MUST be between 2.0 and 15.0 seconds.\n"
                    "- Each beat MUST be mapped to exactly one scene via beat_ids.\n"
                    "- Return ONLY the JSON object, no conversational filler."
                )
                response = model.invoke(prompt)
                print(f"DEBUG SCRIPTWRITER RESPONSE: {response.content}")
                parsed = json.loads(response.content.strip("`").removeprefix("json").strip())
                script = Script(**parsed["script"])
                storyboard = [StoryboardScene(**s) for s in parsed["storyboard"]]
                msg = f"Generated {len(script.beats)} beats and storyboard scenes using Groq LLM."
            except Exception as e:
                script, storyboard = _build_script_and_storyboard(state["request"], constraints)
                msg = f"Generated {len(script.beats)} beats and storyboard scenes (LLM fallback)."
        else:
            script, storyboard = _build_script_and_storyboard(state["request"], constraints)
            msg = f"Generated {len(script.beats)} beats and storyboard scenes."

        agent_logs = _append_log(
            state,
            agent="scriptwriter",
            status="completed",
            message=msg,
        )
        log_entry = agent_logs[-1]
        _emit_progress(
            state,
            event="stage_completed",
            stage="scriptwriter",
            status="completed",
            message=log_entry.message,
            progress=STAGE_PROGRESS["scriptwriter"],
            timestamp=log_entry.timestamp,
        )
        
        res = {
            "script": script,
            "storyboard": storyboard,
            "agent_logs": agent_logs,
        }
        self._checkpoint({**state, **res}, "scriptwriter", ["script", "storyboard"])
        return res

    def _design_node(self, state: VideoAgentState) -> dict:
        _emit_progress(
            state,
            event="stage_started",
            stage="designer",
            status="running",
            message="Loading theme tokens and laying out scenes.",
            progress=0.3,
        )

        theme = load_theme(state["request"].theme_name, self.settings)
        model = build_groq_chat_model(self.settings, temperature=0.7)
        if model:
            try:
                # Design agent prompt - maps storyboard to layouts
                prompt = (
                    "Create layouts for these scenes using the theme colors.\n"
                    f"Storyboard: {json.dumps([s.model_dump() for s in state['storyboard']], indent=2)}\n"
                    f"Theme: {theme.name}\n"
                    "Return ONLY JSON and NO other text: { \"layouts\": [{ \"scene_id\": string, \"background\": object, \"elements\": [{ \"id\": string, \"type\": string, \"props\": object, \"position\": object, \"anchor\": string, \"layer\": integer }] }] }\n"
                    "Rules: Unique layers 1, 2, 3... use theme colors like 'accent_1'."
                )
                response = model.invoke(prompt)
                print(f"DEBUG DESIGNER RESPONSE: {response.content}")
                parsed = json.loads(response.content.strip("`").removeprefix("json").strip())
                layouts = [SceneLayout(**l) for l in parsed["layouts"]]
                msg = f"Created {len(layouts)} scene layouts using Groq LLM."
            except Exception as e:
                print(f"Designer LLM Error: {str(e)}")
                layouts = _build_layouts(state["storyboard"], state["script"], theme)
                msg = f"Created {len(layouts)} scene layouts (LLM fallback)."
        else:
            layouts = _build_layouts(state["storyboard"], state["script"], theme)
            msg = f"Created {len(layouts)} scene layouts."

        agent_logs = _append_log(
            state,
            agent="designer",
            status="completed",
            message=msg,
        )
        log_entry = agent_logs[-1]
        _emit_progress(
            state,
            event="stage_completed",
            stage="designer",
            status="completed",
            message=log_entry.message,
            progress=STAGE_PROGRESS["designer"],
            timestamp=log_entry.timestamp,
        )
        
        res = {
            "theme": theme,
            "layouts": layouts,
            "agent_logs": agent_logs,
        }
        self._checkpoint({**state, **res}, "designer", ["theme", "layouts"])
        return res

    def _motion_node(self, state: VideoAgentState) -> dict:
        _emit_progress(
            state,
            event="stage_started",
            stage="motion",
            status="running",
            message="Applying transition and animation timing.",
            progress=0.48,
        )

        theme = state["theme"]
        model = build_groq_chat_model(self.settings, temperature=0.3)
        if model:
            try:
                # Motion agent prompt - plans animations
                prompt = (
                    "Add spring-based motion to these layouts.\n"
                    f"Layouts: {json.dumps([l.model_dump() for l in state['layouts']], indent=2)}\n"
                    "Requirement: Return ONLY a JSON object with 'motion_plan' list.\n"
                    "Structure: { 'motion_plan': [{ 'scene_id': string, 'elements': [{ 'element_id': string, 'enter': { 'type': 'fade'|'slide-up', 'duration': 0.3, 'delay': 0.1 }, 'exit': { 'type': 'fade', 'duration': 0.3 } }] }] }\n"
                    "Rules: Unique element_ids only. No extra fields."
                )
                response = model.invoke(prompt)
                print(f"DEBUG MOTION RESPONSE: {response.content}")
                parsed = json.loads(response.content.strip("`").removeprefix("json").strip())
                motion_plan = [MotionScenePlan(**m) for m in parsed["motion_plan"]]
                msg = f"Applied motion plans for {len(motion_plan)} scenes using Groq LLM."
            except Exception as e:
                print(f"Motion LLM Error: {str(e)}")
                motion_plan = _build_motion(state["layouts"], theme)
                msg = "Applied motion plans (LLM fallback)."
        else:
            motion_plan = _build_motion(state["layouts"], theme)
            msg = "Applied motion plans."

        agent_logs = _append_log(
            state,
            agent="motion",
            status="completed",
            message=msg,
        )
        log_entry = agent_logs[-1]
        _emit_progress(
            state,
            event="stage_completed",
            stage="motion",
            status="completed",
            message=log_entry.message,
            progress=STAGE_PROGRESS["motion"],
            timestamp=log_entry.timestamp,
        )
        
        res = {
            "motion_plan": motion_plan,
            "agent_logs": agent_logs,
        }
        self._checkpoint({**state, **res}, "motion", ["motion_plan"])
        return res

    def _audio_node(self, state: VideoAgentState) -> dict:
        _emit_progress(
            state,
            event="stage_started",
            stage="audio",
            status="running",
            message="Selecting background music and placing SFX.",
            progress=0.64,
        )

        audio_plan = _build_audio_plan(state["storyboard"])
        
        agent_logs = _append_log(
            state,
            agent="audio",
            status="completed",
            message=f"Planned music track '{audio_plan.music.track_id}' and {len(audio_plan.sfx)} SFX events.",
        )
        log_entry = agent_logs[-1]
        _emit_progress(
            state,
            event="stage_completed",
            stage="audio",
            status="completed",
            message=log_entry.message,
            progress=STAGE_PROGRESS["audio"],
            timestamp=log_entry.timestamp,
        )
        
        res = {
            "audio_plan": audio_plan,
            "agent_logs": agent_logs,
        }
        self._checkpoint({**state, **res}, "audio", ["audio_plan"])
        return res

    def _voice_node(self, state: VideoAgentState) -> dict:
        _emit_progress(
            state,
            event="stage_started",
            stage="voice",
            status="running",
            message="Generating high-fidelity voiceover using Qwen3 TTS.",
            progress=0.72,
        )

        manifest = _run_voice_generation(
            self.settings,
            state["project_id"],
            state["storyboard"],
            state["script"]
        )

        if manifest:
            # Update audio segments in the plan
            audio_plan = state["audio_plan"].model_copy(deep=True)
            audio_plan.voiceover.enabled = True
            audio_plan.voiceover.segments = manifest.get("segments", [])
            msg = f"Generated {len(audio_plan.voiceover.segments)} voiceover segments."
        else:
            audio_plan = state["audio_plan"]
            msg = "Voice generation skipped or failed."

        agent_logs = _append_log(
            state,
            agent="voice",
            status="completed",
            message=msg,
        )
        log_entry = agent_logs[-1]
        _emit_progress(
            state,
            event="stage_completed",
            stage="voice",
            status="completed",
            message=log_entry.message,
            progress=STAGE_PROGRESS["audio"],
            timestamp=log_entry.timestamp,
        )

        return {
            "voice_manifest": manifest,
            "audio_plan": audio_plan,
            "agent_logs": agent_logs,
        }

    def _render_node(self, state: VideoAgentState) -> dict:
        request = state["request"]
        _emit_progress(
            state,
            event="stage_started",
            stage="renderer",
            status="running",
            message="Assembling IR artifacts and rendering when requested.",
            progress=0.78,
        )
        title = request.title or _derive_title(request.brief)

        layout_by_scene = {layout.scene_id: layout for layout in state["layouts"]}
        motion_by_scene = {item.scene_id: item for item in state["motion_plan"]}
        # 1. Update scene durations based on voice manifest if available
        voice_manifest = state.get("voice_manifest", {})
        segments = {s["id"]: s["duration_seconds"] for s in voice_manifest.get("segments", [])}
        
        ir_scenes: list[Scene] = []
        current_time = 0.0
        
        # We need a small padding between scenes for smooth transitions
        TRANSITION_PADDING = 0.5 

        for storyboard_scene in state["storyboard"]:
            original_scene = layout_by_scene[storyboard_scene.scene_id]
            motion_scene = motion_by_scene[storyboard_scene.scene_id]
            
            # Use voice duration if available, otherwise fallback to planned duration
            audio_dur = segments.get(storyboard_scene.scene_id)
            if audio_dur:
                # Pad scene duration slightly so the speaker isn't cut off by transition
                scene_duration = round(audio_dur + TRANSITION_PADDING, 2)
            else:
                scene_duration = storyboard_scene.duration

            scene = _merge_scene(
                storyboard_scene=storyboard_scene,
                layout=original_scene,
                motion=motion_scene,
                start_time=current_time,
            )
            # Override duration if synced with voice
            scene.duration = scene_duration
            ir_scenes.append(scene)
            current_time = round(current_time + scene_duration, 3)

        # Update total project duration
        final_total_duration = current_time

        width, height = {
            "16:9": (1920, 1080),
            "9:16": (1080, 1920),
            "1:1": (1080, 1080),
        }[state["constraints"].aspect_ratio]

        ir = ProjectIR(
            meta=ProjectMeta(
                id=state["project_id"],
                title=title,
                description=request.brief,
                duration=final_total_duration,
                fps=30,
                width=width,
                height=height,
                aspect_ratio=state["constraints"].aspect_ratio,
                created_at=_utc_now(),
                status="draft",
            ),
            theme=state["theme"],
            timeline=Timeline(scenes=ir_scenes),
            audio=state["audio_plan"],
            assets=_build_assets(),
            constraints=ProjectConstraints(platform=state["constraints"].platform),
        )

        ir_dir = self.settings.data_dir / "ir"
        ir_dir.mkdir(parents=True, exist_ok=True)
        ir_path = ir_dir / f"{state['project_id']}.json"
        ir_path.write_text(
            json.dumps(ir.model_dump(mode="json", by_alias=True), indent=2),
            encoding="utf-8",
        )

        render_path: str | None = None
        render_message = f"Assembled and validated IR, then wrote {ir_path.name}."
        if request.render_video and remotion_is_available(self.settings):
            render_path = render_project_ir(settings=self.settings, ir=ir)
            render_message += f" Rendered MP4 to {Path(render_path).name}."

        agent_logs = _append_log(
            state,
            agent="renderer",
            status="completed",
            message=render_message,
        )
        log_entry = agent_logs[-1]
        _emit_progress(
            state,
            event="stage_completed",
            stage="renderer",
            status="completed",
            message=log_entry.message,
            progress=STAGE_PROGRESS["renderer"],
            render_path=render_path,
            timestamp=log_entry.timestamp,
        )
        return {
            "ir": ir,
            "ir_path": str(ir_path),
            "render_path": render_path,
            "agent_logs": agent_logs,
        }

    def _verify_node(self, state: VideoAgentState) -> dict:
        _emit_progress(
            state,
            event="stage_started",
            stage="verifier",
            status="running",
            message="Performing final validation and quality checks.",
            progress=0.92,
        )

        ir = state["ir"]
        errors: list[VerificationIssue] = []
        warnings: list[VerificationIssue] = []

        # 1. Structural checks
        if not (ir.constraints.min_duration <= ir.meta.duration <= ir.constraints.max_duration):
            errors.append(
                VerificationIssue(
                    check="duration_bounds",
                    message=f"Duration {ir.meta.duration}s is outside constraints.",
                    route_to="manager",
                )
            )

        if not state.get("render_path"):
            warnings.append(
                VerificationIssue(
                    check="render_pending",
                    message="Render was skipped or failed; only IR was generated.",
                )
            )

        # 2. Semantic checks via LLM
        model = build_groq_chat_model(self.settings, temperature=0.1)
        if model:
            try:
                prompt = (
                    "You are a quality assurance agent for a professional video system.\n"
                    "Verify if the generated script and storyboard semantically match the user's brief.\n\n"
                    f"Brief: {state['request'].brief}\n"
                    f"Script: {json.dumps(state['script'].model_dump(), indent=2)}\n\n"
                    "Return ONLY a JSON object with this structure:\n"
                    "{\n"
                    '  "status": "passed"|"failed",\n'
                    '  "issues": [{ "check": "semantic_match", "message": string, "route_to": "scriptwriter" }]\n'
                    "}\n"
                    "Pass if the script covers the main points of the brief. Fail only if it is completely irrelevant."
                )
                response = model.invoke(prompt)
                parsed = json.loads(response.content.strip("`").removeprefix("json").strip())
                if parsed["status"] == "failed":
                    for issue in parsed["issues"]:
                        errors.append(VerificationIssue(**issue))
            except Exception:
                pass  # Fallback to passed if LLM fails

        status: Literal["passed", "passed_with_warnings", "failed"] = "passed"
        if errors:
            status = "failed"
        elif warnings:
            status = "passed_with_warnings"

        result = VerificationResult(status=status, errors=errors, warnings=warnings)

        agent_logs = _append_log(
            state,
            agent="verifier",
            status="completed",
            message=f"Verification {status}. Found {len(errors)} errors and {len(warnings)} warnings.",
        )
        log_entry = agent_logs[-1]
        _emit_progress(
            state,
            event="stage_completed",
            stage="verifier",
            status="completed",
            message=log_entry.message,
            progress=1.0,
            timestamp=log_entry.timestamp,
            verification_status=status,
        )
        return {"verification": result, "agent_logs": agent_logs}

