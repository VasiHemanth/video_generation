"""Narrative archetypes for varied script generation.

Each archetype defines a story structure with roles, copy patterns, and
visual hints.  The pipeline picks an archetype based on the brief content
or explicit request, eliminating the old hardcoded "Imagine having a tool…"
template.
"""

from __future__ import annotations

import random
import re
from typing import Any

from .models import ScriptBeat, StoryboardScene


# ── Archetype definitions ─────────────────────────────────────────────────────

ARCHETYPES: dict[str, dict[str, Any]] = {
    "problem_solution": {
        "description": "Identify a pain point then show how the product solves it.",
        "roles": ["hook", "problem", "solution", "proof", "cta"],
        "keywords": ["problem", "solve", "fix", "struggle", "challenge", "pain", "issue", "difficult"],
    },
    "feature_tour": {
        "description": "Walk through 2-3 standout features with demos.",
        "roles": ["hook", "feature_1", "feature_2", "feature_3", "cta"],
        "keywords": ["feature", "built", "includes", "offers", "provides", "capabilities", "tools"],
    },
    "how_it_works": {
        "description": "Step-by-step walkthrough of a process or workflow.",
        "roles": ["hook", "step_1", "step_2", "step_3", "cta"],
        "keywords": ["how", "steps", "process", "workflow", "guide", "tutorial", "learn"],
    },
    "data_story": {
        "description": "Lead with compelling stats and back claims with data.",
        "roles": ["hook_stat", "context", "insight", "proof", "cta"],
        "keywords": ["data", "stats", "percent", "growth", "revenue", "metrics", "numbers", "roi"],
    },
    "before_after": {
        "description": "Contrast the old way vs. the new way.",
        "roles": ["hook", "before", "after", "impact", "cta"],
        "keywords": ["before", "after", "transform", "change", "upgrade", "replace", "better", "new way"],
    },
}

# ── Copy templates per archetype × role ────────────────────────────────────────

COPY_TEMPLATES: dict[str, dict[str, dict[str, Any]]] = {
    "problem_solution": {
        "hook": {
            "headlines": [
                "Still Doing This Manually?",
                "This Costs You Every Day",
                "There's a Better Way",
                "Stop Wasting Time on {topic}",
            ],
            "subtitles": [
                "Most teams lose hours every week on {topic}.",
                "{topic} doesn't have to be this hard.",
                "What if you could automate {topic}?",
            ],
            "voiceovers": [
                "Every day, teams struggle with {topic}. It's slow, it's painful, and it costs real money.",
                "If {topic} feels like a constant uphill battle, you're not alone. Most people accept it — but you don't have to.",
            ],
            "layout_hint": "centered_hero",
            "visual_note": "Bold headline with accent glow. Dark dramatic background with subtle particles.",
        },
        "problem": {
            "headlines": [
                "The Real Cost of {topic}",
                "Here's What's Breaking",
                "Why {topic} Fails",
            ],
            "subtitles": [
                "Wasted hours. Missed deadlines. Frustrated teams.",
                "Manual {topic} creates bottlenecks at every step.",
                "The old approach simply can't keep up.",
            ],
            "voiceovers": [
                "The problem with traditional {topic} is simple: it doesn't scale. Teams spend hours on tasks that should take minutes.",
                "Think about the last time {topic} slowed your team down. Now multiply that across every week, every quarter.",
            ],
            "layout_hint": "split_layout",
            "visual_note": "Problem visualization with red/orange accents. Show pain metrics or broken workflow diagram.",
        },
        "solution": {
            "headlines": [
                "Meet {title}",
                "{title} Changes Everything",
                "Built for This Exact Problem",
            ],
            "subtitles": [
                "Automate {topic} in minutes, not hours.",
                "One platform. Zero friction.",
                "{title} handles {topic} so you don't have to.",
            ],
            "voiceovers": [
                "That's exactly why we built {title}. It takes the pain out of {topic} and replaces it with a system that works.",
                "{title} was designed from the ground up to solve {topic}. No workarounds. No compromises.",
            ],
            "layout_hint": "feature_showcase",
            "visual_note": "Product reveal moment. Clean layout with device mockup or interface preview. Accent color shift to positive.",
        },
        "proof": {
            "headlines": [
                "The Numbers Don't Lie",
                "Real Results, Real Teams",
                "Proven at Scale",
            ],
            "subtitles": [
                "Teams save an average of 12 hours per week.",
                "Join thousands who made the switch.",
                "Results that speak for themselves.",
            ],
            "voiceovers": [
                "Teams using {title} report measurable improvements within the first week. That's not a promise — it's data.",
                "The results? Faster delivery, happier teams, and a process that actually scales.",
            ],
            "layout_hint": "stat_showcase",
            "visual_note": "Data visualization: animated counter, progress bar, or metric cards. Use accent colors for emphasis.",
        },
        "cta": {
            "headlines": [
                "Start Today",
                "Ready to Fix {topic}?",
                "Your Turn",
            ],
            "subtitles": [
                "Free trial. No credit card required.",
                "See the difference in your first week.",
                "Join the teams that chose better.",
            ],
            "voiceovers": [
                "Ready to see what {title} can do for you? Start your free trial today. No credit card, no commitment.",
                "Don't let {topic} slow you down another day. Try {title} and see the difference.",
            ],
            "layout_hint": "cta_card",
            "visual_note": "Clean CTA with button element. Glassmorphism card. Confident, closing energy.",
        },
    },
    "feature_tour": {
        "hook": {
            "headlines": [
                "What {title} Can Do",
                "Three Features That Matter",
                "Built Different",
            ],
            "subtitles": [
                "A quick look at what sets {title} apart.",
                "The features your workflow is missing.",
                "Designed to make {topic} effortless.",
            ],
            "voiceovers": [
                "Let me show you what makes {title} different. Three features that change how you think about {topic}.",
                "{title} is packed with tools designed for {topic}. Here are the three you'll use every day.",
            ],
            "layout_hint": "centered_hero",
            "visual_note": "Hero title with subtle icon grid preview below. Animated gradient background.",
        },
        "feature_1": {
            "headlines": [
                "Smart {topic} Engine",
                "Intelligent Automation",
                "One-Click {topic}",
            ],
            "subtitles": [
                "Set it up once. Let it work forever.",
                "AI-powered {topic} that learns your patterns.",
                "From hours to seconds.",
            ],
            "voiceovers": [
                "Feature one: intelligent automation. {title} analyzes your {topic} patterns and automates the repetitive work.",
                "The first thing you'll notice is the automation engine. It handles {topic} in the background while you focus on what matters.",
            ],
            "layout_hint": "split_layout",
            "visual_note": "Feature card with icon on left, description right. Device mockup showing the feature.",
        },
        "feature_2": {
            "headlines": [
                "Real-Time Insights",
                "See Everything at Once",
                "Dashboard That Works",
            ],
            "subtitles": [
                "Live data, zero lag.",
                "Every metric you need, right where you need it.",
                "Clarity at a glance.",
            ],
            "voiceovers": [
                "Feature two: real-time visibility. See exactly what's happening with {topic} across your entire team.",
                "No more guessing. {title} gives you a live dashboard that shows every metric that matters.",
            ],
            "layout_hint": "stat_showcase",
            "visual_note": "Dashboard mockup or data visualization. Animated charts or metric cards.",
        },
        "feature_3": {
            "headlines": [
                "Works With Your Stack",
                "Seamless Integration",
                "Connect Everything",
            ],
            "subtitles": [
                "Plug into the tools you already use.",
                "60+ integrations, zero migration pain.",
                "Your workflow, supercharged.",
            ],
            "voiceovers": [
                "Feature three: it connects to everything. {title} integrates with the tools your team already uses.",
                "And the best part? It fits right into your existing workflow. No migration, no disruption.",
            ],
            "layout_hint": "icon_grid",
            "visual_note": "Grid of integration icons or logo cards. Clean grid layout with connection lines.",
        },
        "cta": {
            "headlines": [
                "Try {title} Free",
                "See It in Action",
                "Start Building Today",
            ],
            "subtitles": [
                "Your first project is on us.",
                "Five minutes to your first win.",
                "No setup required.",
            ],
            "voiceovers": [
                "Ready to try it? Start your free trial of {title} today. Five minutes is all you need.",
                "See these features in action. Sign up for {title} and start building something better.",
            ],
            "layout_hint": "cta_card",
            "visual_note": "Strong CTA card with button. Confident energy. Quick signup message.",
        },
    },
    "how_it_works": {
        "hook": {
            "headlines": [
                "How {title} Works",
                "{topic} in 3 Simple Steps",
                "From Zero to Done",
            ],
            "subtitles": [
                "Simple enough for anyone. Powerful enough for teams.",
                "No learning curve. Just results.",
                "Here's exactly how to get started.",
            ],
            "voiceovers": [
                "Let me walk you through how {title} works. It's simpler than you think — just three steps.",
                "Wondering how to get started with {topic}? Here's the exact process, step by step.",
            ],
            "layout_hint": "centered_hero",
            "visual_note": "Clean title with step indicators (1-2-3) subtly visible. Minimal, confident.",
        },
        "step_1": {
            "headlines": [
                "Step 1: Connect",
                "Step 1: Set Up",
                "Step 1: Upload",
            ],
            "subtitles": [
                "Link your existing tools in seconds.",
                "One-time setup, permanent results.",
                "Drop your data in and watch it work.",
            ],
            "voiceovers": [
                "Step one: connect your tools. {title} integrates with your existing stack in under a minute.",
                "Getting started is easy. Connect your data source and {title} handles the rest.",
            ],
            "layout_hint": "split_layout",
            "visual_note": "Step number '1' large on left, description and visual on right. Progress indicator.",
        },
        "step_2": {
            "headlines": [
                "Step 2: Configure",
                "Step 2: Customize",
                "Step 2: Define",
            ],
            "subtitles": [
                "Set your rules. {title} follows them.",
                "Tailor everything to your workflow.",
                "Tell it what you need. It adapts.",
            ],
            "voiceovers": [
                "Step two: customize. Set your preferences, define your rules, and {title} adapts to your specific needs.",
                "Next, configure it for your workflow. {title} is flexible enough to match how your team actually works.",
            ],
            "layout_hint": "split_layout",
            "visual_note": "Step '2' with configuration UI mockup. Settings panel or workflow builder visual.",
        },
        "step_3": {
            "headlines": [
                "Step 3: Launch",
                "Step 3: Go Live",
                "Step 3: Sit Back",
            ],
            "subtitles": [
                "Hit go and watch it run.",
                "From setup to results in minutes.",
                "Your {topic} runs on autopilot.",
            ],
            "voiceovers": [
                "Step three: launch. Hit go, and {title} takes care of {topic} automatically. You just watch the results come in.",
                "And that's it. Three steps. {title} handles {topic} from here, and you get your time back.",
            ],
            "layout_hint": "stat_showcase",
            "visual_note": "Celebration moment. Results dashboard or success state. Confetti-like particles.",
        },
        "cta": {
            "headlines": [
                "Your Turn",
                "Try the 3-Step Setup",
                "Start in 60 Seconds",
            ],
            "subtitles": [
                "It really is that simple.",
                "Free to start. Easy to scale.",
                "Join teams who already made the switch.",
            ],
            "voiceovers": [
                "It really is that simple. Try {title} today and see how easy {topic} can be.",
                "Ready? Start your free trial and go through the three steps yourself. It takes less than a minute.",
            ],
            "layout_hint": "cta_card",
            "visual_note": "Final CTA with progress bar at 100%. Confident close.",
        },
    },
    "data_story": {
        "hook_stat": {
            "headlines": [
                "87% of Teams Fail at This",
                "The {topic} Gap Is Growing",
                "$2.3M Lost Every Year",
            ],
            "subtitles": [
                "The data tells a clear story.",
                "These numbers should worry you.",
                "Here's what the research shows.",
            ],
            "voiceovers": [
                "Here's a number that should get your attention. The vast majority of teams are still struggling with {topic}.",
                "The data on {topic} is clear — and it's not good news for most organizations.",
            ],
            "layout_hint": "stat_showcase",
            "visual_note": "Large animated counter as hero element. Dramatic number reveal. Bold typography.",
        },
        "context": {
            "headlines": [
                "Why This Matters",
                "The Hidden Cost",
                "What's Really Going On",
            ],
            "subtitles": [
                "It's not just about {topic}. It's about everything it touches.",
                "The real impact goes deeper than you think.",
                "Context changes everything.",
            ],
            "voiceovers": [
                "Here's why this matters. Bad {topic} doesn't just slow you down — it compounds across your entire organization.",
                "The hidden cost of poor {topic} is staggering. It affects productivity, morale, and your bottom line.",
            ],
            "layout_hint": "split_layout",
            "visual_note": "Context visualization. Ripple effect diagram or cascading metrics. Warm accent colors.",
        },
        "insight": {
            "headlines": [
                "{title} Found the Fix",
                "Data-Driven {topic}",
                "The Breakthrough",
            ],
            "subtitles": [
                "Built on real data, not guesswork.",
                "Finally, a {topic} solution that's measurable.",
                "Evidence-based approach to {topic}.",
            ],
            "voiceovers": [
                "{title} was built on real data. Every feature is designed to address the specific problems teams actually face with {topic}.",
                "We analyzed thousands of {topic} workflows to find what actually works. {title} is the result.",
            ],
            "layout_hint": "feature_showcase",
            "visual_note": "Insight visualization. Before/after metrics. Chart showing improvement curve.",
        },
        "proof": {
            "headlines": [
                "3x Faster Delivery",
                "Results in Week One",
                "The Proof Is in the Data",
            ],
            "subtitles": [
                "Measured across 500+ teams.",
                "Average improvement in the first 30 days.",
                "These aren't projections. They're actuals.",
            ],
            "voiceovers": [
                "Teams using {title} see results in their first week. On average, delivery speed triples within 30 days.",
                "Don't take our word for it. The data shows a clear pattern: {title} users outperform on every metric we track.",
            ],
            "layout_hint": "stat_showcase",
            "visual_note": "Multiple metric cards with animated counters. Progress bars filling. Data-rich scene.",
        },
        "cta": {
            "headlines": [
                "See Your Numbers Improve",
                "Get the Full Report",
                "Start Measuring Today",
            ],
            "subtitles": [
                "Free trial with real-time analytics.",
                "Track your {topic} improvement from day one.",
                "Data-driven teams start here.",
            ],
            "voiceovers": [
                "Want to see these numbers for your own team? Start your free trial of {title} and track the improvement from day one.",
                "Ready to make {topic} measurable? Try {title} and see the data for yourself.",
            ],
            "layout_hint": "cta_card",
            "visual_note": "CTA with mini dashboard preview. Analytics-forward close.",
        },
    },
    "before_after": {
        "hook": {
            "headlines": [
                "There's a Better Way",
                "Time for an Upgrade",
                "Old Way vs. New Way",
            ],
            "subtitles": [
                "Stop settling for {topic} that doesn't work.",
                "What if {topic} was actually enjoyable?",
                "The contrast is striking.",
            ],
            "voiceovers": [
                "What if I told you there's a completely different way to handle {topic}? Let me show you the contrast.",
                "Most people accept that {topic} is just hard. But what if the problem isn't {topic} — it's the tools?",
            ],
            "layout_hint": "centered_hero",
            "visual_note": "Split screen hint. Before/after visual contrast. Dramatic lighting.",
        },
        "before": {
            "headlines": [
                "The Old Way",
                "Before {title}",
                "How It Used to Be",
            ],
            "subtitles": [
                "Slow. Manual. Frustrating.",
                "Hours wasted on tasks that shouldn't exist.",
                "Sound familiar?",
            ],
            "voiceovers": [
                "The old way: manual processes, constant context-switching, and a {topic} workflow that fights you at every step.",
                "Before {title}, {topic} meant spreadsheets, meetings, and hoping nothing fell through the cracks.",
            ],
            "layout_hint": "split_layout",
            "visual_note": "Desaturated, slightly chaotic visual. Crossed-out elements or 'X' marks. Problem state.",
        },
        "after": {
            "headlines": [
                "The New Way",
                "After {title}",
                "How It Works Now",
            ],
            "subtitles": [
                "Fast. Automated. Delightful.",
                "One click. Zero stress.",
                "This is what {topic} should feel like.",
            ],
            "voiceovers": [
                "With {title}, everything changes. {topic} becomes automated, visible, and actually enjoyable.",
                "After {title}: clean workflows, real-time visibility, and a {topic} process that runs itself.",
            ],
            "layout_hint": "feature_showcase",
            "visual_note": "Vibrant, clean visual. Checkmarks and success states. Bright accent colors. Product mockup.",
        },
        "impact": {
            "headlines": [
                "The Difference Is Clear",
                "Measurable Impact",
                "Teams Are Switching",
            ],
            "subtitles": [
                "Faster, cheaper, better — pick all three.",
                "The numbers make the case.",
                "Once you switch, you never go back.",
            ],
            "voiceovers": [
                "The impact is measurable. Teams that switch to {title} see immediate improvements across every metric that matters.",
                "The difference? It's not subtle. {title} doesn't just improve {topic} — it transforms it.",
            ],
            "layout_hint": "stat_showcase",
            "visual_note": "Before/after comparison metrics side by side. Animated improvement indicators.",
        },
        "cta": {
            "headlines": [
                "Make the Switch",
                "Upgrade Today",
                "Choose the New Way",
            ],
            "subtitles": [
                "Free trial. Instant results.",
                "Your team deserves better {topic}.",
                "Start now. Thank yourself later.",
            ],
            "voiceovers": [
                "Ready to make the switch? Try {title} free and experience {topic} the way it should be.",
                "Your team deserves better. Start your free trial of {title} today.",
            ],
            "layout_hint": "cta_card",
            "visual_note": "Confident CTA. Transformation complete. Button with glow effect.",
        },
    },
}


# ── Archetype detection ────────────────────────────────────────────────────────


def detect_archetype(brief: str) -> str:
    """Detect the best narrative archetype from the brief text."""
    brief_lower = brief.lower()
    scores: dict[str, int] = {}

    for name, meta in ARCHETYPES.items():
        score = sum(1 for kw in meta["keywords"] if kw in brief_lower)
        scores[name] = score

    best = max(scores, key=lambda k: scores[k])
    # If no strong signal, pick one at random (avoids same-every-time)
    if scores[best] == 0:
        return random.choice(list(ARCHETYPES.keys()))
    return best


# ── Extract topic from brief ───────────────────────────────────────────────────


def extract_topic(brief: str) -> str:
    """Extract a short topic phrase from the brief for template interpolation."""
    # Take the first meaningful clause (up to 5 words)
    cleaned = re.sub(r"\s+", " ", brief.strip())
    # Try to find the core subject by removing common prefixes
    prefixes = [
        r"^create\s+a\s+video\s+(?:about|for|on)\s+",
        r"^make\s+a\s+video\s+(?:about|for|on)\s+",
        r"^generate\s+a\s+video\s+(?:about|for|on)\s+",
        r"^a\s+video\s+(?:about|for|on)\s+",
        r"^(?:about|for|on)\s+",
    ]
    topic = cleaned
    for prefix in prefixes:
        topic = re.sub(prefix, "", topic, flags=re.IGNORECASE)

    words = topic.split()
    # Take up to 5 words as the topic
    return " ".join(words[:5]).rstrip(".,;:!?")


# ── Build beats and storyboard from archetype ──────────────────────────────────


def build_from_archetype(
    *,
    archetype_name: str,
    brief: str,
    title: str,
    total_duration: float,
) -> tuple[list[ScriptBeat], list[StoryboardScene]]:
    """Build script beats and storyboard scenes from a narrative archetype."""
    templates = COPY_TEMPLATES.get(archetype_name)
    arch_meta = ARCHETYPES.get(archetype_name)
    if not templates or not arch_meta:
        # Fallback to problem_solution
        archetype_name = "problem_solution"
        templates = COPY_TEMPLATES["problem_solution"]
        arch_meta = ARCHETYPES["problem_solution"]

    roles = arch_meta["roles"]
    topic = extract_topic(brief)
    scene_count = len(roles)

    # Distribute duration with weighted buckets
    weights = [1.0] * scene_count
    weights[0] = 0.9   # Hook is slightly shorter
    weights[-1] = 0.85  # CTA is shortest
    if scene_count > 3:
        weights[1] = 1.1  # Second scene slightly longer (problem/feature)
    total_weight = sum(weights)
    durations = [round(total_duration * w / total_weight, 1) for w in weights]
    # Fix rounding error
    diff = round(total_duration - sum(durations), 1)
    durations[-1] = round(durations[-1] + diff, 1)

    beats: list[ScriptBeat] = []
    storyboard: list[StoryboardScene] = []

    for idx, role in enumerate(roles):
        beat_id = f"beat_{idx + 1:03d}"
        scene_id = f"scene_{idx + 1:03d}"
        duration = durations[idx]

        role_templates = templates.get(role, templates.get("cta", {}))
        # Pick copy (deterministic per-brief via hash so same brief = same video)
        seed = hash(f"{brief}:{role}:{idx}") % 1000

        headlines = role_templates.get("headlines", [""])
        subtitles = role_templates.get("subtitles", [""])
        voiceovers = role_templates.get("voiceovers", [""])

        headline = headlines[seed % len(headlines)]
        subtitle = subtitles[seed % len(subtitles)]
        voiceover = voiceovers[seed % len(voiceovers)]

        # Interpolate {title} and {topic}
        headline = headline.format(title=title, topic=topic)
        subtitle = subtitle.format(title=title, topic=topic)
        voiceover = voiceover.format(title=title, topic=topic)

        layout_hint = role_templates.get("layout_hint", "centered_hero")
        visual_note = role_templates.get("visual_note", "")
        description = f"{archetype_name}/{role}: {visual_note[:60]}"

        beats.append(
            ScriptBeat(
                id=beat_id,
                type=role,
                text=voiceover,
                headline_text=headline,
                subtitle_text=subtitle,
                voiceover_text=voiceover,
                duration=duration,
                visual_note=visual_note,
            )
        )
        storyboard.append(
            StoryboardScene(
                scene_id=scene_id,
                role=role,
                beat_ids=[beat_id],
                duration=duration,
                layout_hint=layout_hint,
                description=description,
            )
        )

    return beats, storyboard
