"""Quick test video generation using the new Layer 5 archetype + layout engine."""

import asyncio
import time
from pathlib import Path

# Load env first
from dotenv import load_dotenv
load_dotenv()

from video_gen_agents.pipeline import VideoGenerationService
from video_gen_agents.config import Settings
from video_gen_agents.models import GenerateVideoRequest


async def main():
    settings = Settings.from_env()
    service = VideoGenerationService(settings)

    # Test brief that should trigger "feature_tour" archetype
    request = GenerateVideoRequest(
        brief=(
            "Create a 30-second promo video for Nexus — a SaaS tool that helps "
            "engineering teams track bugs, manage sprints, and ship faster. "
            "It features smart automation, real-time dashboards, and integrates "
            "with GitHub, Slack, and Jira."
        ),
        title="Nexus",
        theme_name="saas-b2b",
        aspect_ratio="9:16",
        duration=30,
        scene_count=5,
        platform="instagram",
        render_video=True,
    )

    project_id = f"nexus_test_{int(time.time())}"
    print(f"\n🎬 Starting generation: {project_id}")
    print(f"   Brief: {request.brief[:80]}...")
    print(f"   Theme: {request.theme_name}")
    print()

    def progress(event):
        bar = "█" * int(event.progress * 20) + "░" * (20 - int(event.progress * 20))
        print(f"  [{bar}] {event.stage.upper():10s} — {event.message}")

    start = time.time()
    try:
        response = service.generate(request, project_id, progress)
        elapsed = time.time() - start

        print(f"\n✅ Done in {elapsed:.1f}s")
        print(f"   Project ID : {response.project_id}")
        print(f"   Status     : {response.verification.status}")
        print(f"   IR path    : {response.ir_path}")
        print(f"   Video path : {response.render_path or 'Not rendered'}")
        print(f"   Scenes     : {len(response.ir.timeline.scenes)}")

        # Print scene summary
        print("\n📋 Scene Summary:")
        for i, scene in enumerate(response.ir.timeline.scenes):
            print(f"   {i+1}. [{scene.id}] {scene.duration:.1f}s — {len(scene.elements)} elements — trans_in={scene.transition_in.type if scene.transition_in else 'none'}")

    except Exception as e:
        import traceback
        print(f"\n❌ Failed: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
