from __future__ import annotations

import asyncio
import json
from pathlib import Path
from video_gen_agents.config import Settings
from video_gen_agents.database import Database
from video_gen_agents.models import GenerateVideoRequest
from video_gen_agents.pipeline import VideoGenerationService

async def main():
    settings = Settings.from_env()
    database = Database(settings)
    await database.init()
    
    service = VideoGenerationService(settings)
    
    brief = (
        "Zenith: A minimalist iOS meditation app designed for deep focus and stress relief. "
        "The video should show the calm UI, a session timer, and the benefits of daily mindfulness. "
        "Use a serene aesthetic with soft transitions and gentle motion."
    )
    
    request = GenerateVideoRequest(
        brief=brief,
        title="Zenith: Mindfulness Redefined",
        theme_name="vibrant",
        aspect_ratio="9:16",
        duration=35.0,
        scene_count=5,
        render_video=False # Set to False since we might not have remotion/ffmpeg in this env, but we want the IR
    )
    
    print(f"Generating video for: {request.title}")
    
    async def checkpoint_callback(project_id, step, snapshot):
        print(f"[Checkpoint] Step: {step}")
        await database.save_checkpoint(project_id, step, snapshot)

    # Note: service.generate is sync, but we use an async checkpoint callback. 
    # In a real app, we'd use run_in_threadpool or similar.
    # For this script, we'll wrap the callback.
    
    def sync_checkpoint(project_id, step, snapshot):
        # Fire and forget or run in a new loop
        asyncio.run_coroutine_threadsafe(
            database.save_checkpoint(project_id, step, snapshot), 
            asyncio.get_event_loop()
        )

    response = service.generate(
        request, 
        checkpoint_callback=lambda p, s, snap: asyncio.run(database.save_checkpoint(p, s, snap))
    )
    
    print("\nGeneration Complete!")
    print(f"Project ID: {response.project_id}")
    print(f"IR Path: {response.ir_path}")
    print(f"Summary: {response.summary.model_dump_json(indent=2)}")
    
    # Detailed look at the IR to see the new features
    ir = response.ir
    print("\n--- Phase 2 Features Verification ---")
    print(f"Music Track: {ir.audio.music.track_id if ir.audio.music else 'None'}")
    print(f"SFX Count: {len(ir.audio.sfx)}")
    
    # Check for device element and parallax
    for scene in ir.timeline.scenes:
        device_elements = [e for e in scene.elements if e.type == "device"]
        parallax_elements = [e for e in scene.elements if e.parallax_factor is not None]
        print(f"Scene {scene.id} ({scene.role}):")
        if device_elements:
            print(f"  - Device: {device_elements[0].props.get('variant')}")
        if parallax_elements:
            print(f"  - Parallax Elements: {len(parallax_elements)}")

if __name__ == "__main__":
    asyncio.run(main())
