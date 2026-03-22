import asyncio
from dotenv import load_dotenv
from video_gen_agents.config import Settings
from video_gen_agents.pipeline import VideoGenerationService
from video_gen_agents.models import GenerateVideoRequest

async def main():
    load_dotenv("agents/.env")
    print("Generating video for: Claude Code")
    settings = Settings.from_env()
    service = VideoGenerationService(settings)
    
    request = GenerateVideoRequest(
        brief="Explain what Claude Code is, how it works, and why it's a game-changer for developers. Highlight that it sits in your terminal, understands your codebase, and writes code autonomously.",
        title="Claude Code",
        theme_name="dark-tech",
        duration=35.0,
        scene_count=5
    )
    
    response = service.generate(request)
    print("\nGeneration Complete!")
    print(f"Project ID: {response.project_id}")
    print(f"IR Path: {response.ir_path}")
    print(f"Render Status: {response.summary.render_status}")
    if response.render_path:
        print(f"Final MP4: {response.render_path}")

if __name__ == "__main__":
    asyncio.run(main())
