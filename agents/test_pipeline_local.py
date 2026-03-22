import asyncio
import os
from dotenv import load_dotenv
from video_gen_agents.pipeline import VideoGenerationService
from video_gen_agents.config import Settings
from video_gen_agents.models import GenerateVideoRequest

# Load .env first
load_dotenv()

async def main():
    # Load settings from .env
    settings = Settings.from_env()
    service = VideoGenerationService(settings)
    
    request = GenerateVideoRequest(
        brief="A short 35s educational video about how AI agents work using LangGraph and Groq. Use kinetic typography and professional motion.",
        title="AI Agents Explained",
        theme_name="dark-tech",
        aspect_ratio="16:9",
        duration=35,
        scene_count=5,
        platform="youtube",
        render_video=True
    )
    
    import time
    project_id = f"test_run_{int(time.time())}"
    print(f"Starting generation for {project_id}...")
    
    def progress_callback(event):
        print(f"[{event.stage.upper()}] {event.status}: {event.message} ({event.progress*100:.1f}%)")

    try:
        response = await asyncio.to_thread(service.generate, request, project_id, progress_callback)
        print("\nGeneration Completed!")
        print(f"Project ID: {response.project_id}")
        print(f"Status: {response.verification.status}")
        print(f"Render Path: {response.render_path}")
        print(f"IR Path: {response.ir_path}")
    except Exception as e:
        print(f"\nGeneration failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
