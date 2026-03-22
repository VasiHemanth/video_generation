from __future__ import annotations

import asyncio
import json
from pathlib import Path
from video_gen_agents.config import Settings
from video_gen_agents.models import ProjectIR
from video_gen_agents.rendering import render_project_ir

async def main():
    settings = Settings.from_env()
    project_id = "proj_66fbfbbe"
    ir_path = settings.data_dir / "ir" / f"{project_id}.json"
    
    if not ir_path.exists():
        print(f"Error: IR file not found at {ir_path}")
        return
        
    print(f"Loading IR from {ir_path}...")
    ir_data = json.loads(ir_path.read_text())
    ir = ProjectIR(**ir_data)
    
    print(f"Rendering video for {project_id}...")
    try:
        render_path = render_project_ir(settings=settings, ir=ir)
        print(f"\nRender Complete!")
        print(f"Final MP4 Path: {render_path}")
    except Exception as e:
        print(f"\nRender Failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
