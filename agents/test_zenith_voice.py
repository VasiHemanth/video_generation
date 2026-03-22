import asyncio
import os
from video_gen_agents.config import Settings
from video_gen_agents.models import GenerateVideoRequest
from video_gen_agents.pipeline import VideoGenerationService

async def main():
    settings = Settings.from_env()
    service = VideoGenerationService(settings)
    
    brief = (
        "Zenith: A minimalist iOS meditation app. "
        "Show a calm interface designed for deep focus and stress relief. "
        "Highlight the daily mindfulness benefits with a serene motion aesthetic."
    )
    
    request = GenerateVideoRequest(
        brief=brief,
        title="Zenith",
        theme_name="default", # Or whatever theme fits
        aspect_ratio="9:16",
        duration=35.0,
        scene_count=4,
        render_video=True # We want it to render the MP4
    )
    
    print(f"Generating video with voiceover for: {request.title}")
    
    response = service.generate(request)
    
    print("\nGeneration Complete!")
    print(f"Project ID: {response.project_id}")
    print(f"IR Path: {response.ir_path}")
    print(f"Render Status: {response.summary.render_status}")
    if response.render_path:
        print(f"Final MP4: {response.render_path}")

if __name__ == "__main__":
    asyncio.run(main())
