import asyncio
import json
import sys
import os
from dotenv import load_dotenv

# Add current directory to path so we can import video_gen_agents
base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(base_dir, ".env"))
sys.path.append(base_dir)

from video_gen_agents.pipeline import VideoGenerationService
from video_gen_agents.models import GenerateVideoRequest
from video_gen_agents.config import Settings

async def main():
    settings = Settings.from_env()
    service = VideoGenerationService(settings)
    
    request = GenerateVideoRequest(
        brief="A 30-second video about the benefits of parallel computing for AI agents.",
        theme_name="default",
        scene_count=4,
        render_video=False
    )
    
    from video_gen_agents.models import ProjectProgressEvent
    
    def progress_callback(event: ProjectProgressEvent) -> None:
        print(f"[{event.stage.upper()}] {event.message} ({event.progress*100:.0f}%)")
    
    print("🚀 Starting Phase 2 Generation (Parallel + Healer)...")
    try:
        response = await service.generate(
            request, 
            f"p2_test_{int(asyncio.get_event_loop().time())}",
            progress_callback=progress_callback
        )
        
        print("\n✅ Generation Complete!")
        print(f"Project ID: {response.project_id}")
        print(f"Status: {response.verification.status}")
        print(f"Summary: {response.summary.scene_count} scenes, {response.summary.duration}s")
        
        print("\n📜 Agent Logs:")
        for log in response.logs:
            print(f"[{log.agent}] {log.message}")
            
    except Exception as e:
        print(f"\n❌ Generation Failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
