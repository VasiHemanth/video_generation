# [Goal Description]
Phase 2: Transition the video generation pipeline from a sequential MVP into a high-performance, self-correcting, and visually rich production system.

## User Review Required

> [!IMPORTANT]
> **Scene Parallelization** significantly increases peak token throughput (TPM). We must verify that your Cerebras and Groq tiers can handle 5-10 concurrent requests without hitting rate limits before deploying this to production.

## Proposed Changes

### Core Pipeline Optimization (Performance)

#### [MODIFY] [pipeline.py](file:///Users/hemanthvasi/Documents/Developer/video_generation/agents/video_gen_agents/pipeline.py)
- Refactor the LangGraph to process `Designer` and `Motion` nodes in parallel using a `foreach` construct or `asyncio.gather`.
- Decouple scene generation from the main sequential chain.

### Intelligence & Error Recovery (Robustness)

#### [NEW] [corrector.py](file:///Users/hemanthvasi/Documents/Developer/video_generation/agents/video_gen_agents/corrector.py)
- Implement a **"Healer" Agent** that catches Pydantic validation errors (like the `heading` vs `text` issue seen during testing).
- Automatically retries the LLM with the error trace as context to produce valid JSON.

### Visual Architecture (Aesthetics)

#### [NEW] [assets.py](file:///Users/hemanthvasi/Documents/Developer/video_generation/agents/video_gen_agents/assets.py)
- Add a service to search and resolve real-time background images (Unsplash/Pexels) based on scene keywords.
- Update `Visual Design` agent prompts to suggest specific image queries.

## Verification Plan

### Automated Tests
- `pytest agents/tests/test_parallel_execution.py`: Verify that multiple scenes are generated concurrently and correctly assembled into the final IR.
- `verify_self_correction.py`: Provide intentionally malformed inputs and verify that the "Healer" agent corrects them on the second pass.

### Manual Verification
- **Langfuse Dashboard**: Confirm that parallel requests show up as simultaneous spans in the traces.
- **Render Check**: Verify that scenes with dynamic assets render correctly in Remotion.
