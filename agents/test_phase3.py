"""Phase 3 verification: test new templates, SVG components, and enriched prompts."""
import asyncio
import json
import os
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

    # Use "how_it_works" archetype keywords to trigger step_1→terminal_demo, step_2→list_reveal
    request = GenerateVideoRequest(
        brief=(
            "How RAG (Retrieval Augmented Generation) works in 3 simple steps. "
            "Step 1: Connect your documents to the vector database. "
            "Step 2: Query processing, embedding, similarity search, context retrieval. "
            "Step 3: The LLM generates accurate answers using retrieved context."
        ),
        title="RAG Explained",
        theme_name="dark-tech",
        aspect_ratio="9:16",
        duration=35,
        scene_count=5,
        platform="youtube",
        render_video=False,  # IR only for fast verification
    )

    project_id = f"phase3_test_{int(time.time())}"
    print(f"🚀 Starting Phase 3 verification: {project_id}")
    print(f"   Brief: {request.brief[:80]}...")
    print()

    def progress_callback(event):
        print(f"  [{event.stage.upper():12s}] {event.status:8s} | {event.message} ({event.progress*100:.0f}%)")

    try:
        response = await service.generate(request, project_id, progress_callback)
        print(f"\n✅ Generation completed!")
        print(f"   IR Path: {response.ir_path}")
        print(f"   Status: {response.verification.status}")

        # Load and inspect the generated IR
        if response.ir_path and Path(response.ir_path).exists():
            ir_data = json.loads(Path(response.ir_path).read_text())
            timeline = ir_data.get("timeline", {})
            scenes = timeline.get("scenes", [])
            
            print(f"\n📊 IR Analysis ({len(scenes)} scenes):")
            print(f"   {'─' * 60}")
            
            # Track Phase 3 feature usage
            animation_types = set()
            easing_types = set()
            element_types = set()
            has_stagger = False
            has_ambient = False
            has_svg = False
            has_word_animation = False
            has_glassmorphism = False

            for scene in scenes:
                print(f"\n   Scene: {scene.get('id', '?')} | Role: {scene.get('role', '?')}")
                elements = scene.get("elements", [])
                for el in elements:
                    etype = el.get("type", "?")
                    element_types.add(etype)
                    
                    props = el.get("props", {})
                    # Check both top-level (new schema) and props (fallback)
                    if el.get("stagger_index") is not None or props.get("stagger_index") is not None:
                        has_stagger = True
                    if el.get("ambient") or props.get("ambient"):
                        has_ambient = True
                    if el.get("word_animation") == "word-by-word" or props.get("word_animation") == "word-by-word":
                        has_word_animation = True
                    if el.get("glassmorphism") or props.get("glassmorphism"):
                        has_glassmorphism = True
                    if etype.startswith("svg"):
                        has_svg = True
                    
                    enter = el.get("enter", {})
                    if enter:
                        animation_types.add(enter.get("type", "?"))
                        if enter.get("easing"):
                            easing_types.add(enter.get("easing"))
                    
                    exit_anim = el.get("exit", {})
                    if exit_anim:
                        animation_types.add(exit_anim.get("type", "?"))
                    
                    print(f"     [{etype:16s}] layer={el.get('layer', '?')} "
                          f"enter={enter.get('type', 'none') if enter else 'none'}")

            print(f"\n{'═' * 62}")
            print(f"   Phase 3 Feature Usage Report")
            print(f"{'═' * 62}")
            print(f"   Element Types:    {sorted(element_types)}")
            print(f"   Animation Types:  {sorted(animation_types)}")
            print(f"   Easing Types:     {sorted(easing_types)}")
            print(f"   Stagger Groups:   {'✅' if has_stagger else '❌'}")
            print(f"   Ambient Float:    {'✅' if has_ambient else '❌'}")
            print(f"   SVG Elements:     {'✅' if has_svg else '❌'}")
            print(f"   Word Animation:   {'✅' if has_word_animation else '❌'}")
            print(f"   Glassmorphism:    {'✅' if has_glassmorphism else '❌'}")
            
            # Score
            features_used = sum([
                "spring" in animation_types or "bounce" in animation_types,
                has_stagger,
                has_ambient,
                has_svg,
                has_word_animation,
                has_glassmorphism,
                len(animation_types) > 2,
                len(element_types) > 3,
            ])
            print(f"\n   Phase 3 Score: {features_used}/8 features active")
            if features_used >= 6:
                print("   🎉 EXCELLENT — prompts are driving rich output!")
            elif features_used >= 4:
                print("   ✅ GOOD — most features active")
            elif features_used >= 2:
                print("   ⚠️  PARTIAL — some features missing")
            else:
                print("   ❌ LOW — prompts may not be reaching the LLM correctly")
        
    except Exception as e:
        print(f"\n❌ Generation failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
