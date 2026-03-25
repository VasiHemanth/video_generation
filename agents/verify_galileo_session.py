import asyncio
import os
from dotenv import load_dotenv
from video_gen_agents.pipeline import VideoGenerationService
from video_gen_agents.config import Settings
from video_gen_agents.models import GenerateVideoRequest

load_dotenv()

async def verify_session():
    settings = Settings.from_env()
    
    # Ensure Galileo is enabled
    os.environ["GALILEO_API_KEY"] = os.getenv("GALILEO_API_KEY", "test_key")
    settings.galileo_api_key = os.environ["GALILEO_API_KEY"]
    
    service = VideoGenerationService(settings)
    
    request = GenerateVideoRequest(
        brief="Short test for Galileo session grouping.",
        title="Galileo Session Test",
        render_video=False # Just test the agent flow
    )
    
    print("\n--- Running Pipeline ---")
    try:
        response = await asyncio.to_thread(service.generate, request, "galileo_session_test")
        print("\n✅ Pipeline completed successfully.")
        print(f"Logs: {len(response.logs)} entries.")
        print("Traces should now be grouped under the session 'Video Generation - galileo_session_test' in Galileo.")
        
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_session())
