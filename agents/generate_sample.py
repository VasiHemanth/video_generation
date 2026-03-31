import asyncio
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from video_gen_agents.pipeline import VideoGenerationService
from video_gen_agents.config import Settings
from video_gen_agents.models import GenerateVideoRequest

async def main():
    settings = Settings.from_env()
    service = VideoGenerationService(settings)

    request = GenerateVideoRequest(
        brief=(
            "How a RAG System Works in detail. "
            "1. Ingestion: Processing raw documents into clean text. "
            "2. Chunking: Breaking the text into manageable semantic pieces. "
            "3. Vectorization: Using an embedding model to convert chunks into dense vectors. "
            "4. Hybrid Search: Combining keyword and semantic vector search to feed context to the LLM."
        ),
        title="RAG Systems Explained",
        theme_name="warm-clay",
        aspect_ratio="9:16",
        duration=30,
        scene_count=4,
        platform="youtube",
        render_video=True,
    )

    project_id = f"sample_{int(time.time())}"
    print(f"🚀 Starting Sample Generation: {project_id}")

    def progress_callback(event):
        print(f"  [{event.stage.upper():12s}] {event.status:8s} | {event.message} ({event.progress*100:.0f}%)")

    try:
        response = await service.generate(request, project_id, progress_callback)
        print(f"\n✅ Sample Generation completed for {project_id}!")
    except Exception as e:
        print(f"\n❌ Sample Generation failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
