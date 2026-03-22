from __future__ import annotations

import json

from .config import Settings
from .models import ThemeTokens


def list_theme_names(settings: Settings) -> list[str]:
    return sorted(path.stem for path in settings.theme_dir.glob("*.json"))


def load_theme(theme_name: str, settings: Settings) -> ThemeTokens:
    available = list_theme_names(settings)
    if theme_name not in available:
        raise ValueError(
            f"Unknown theme '{theme_name}'. Available themes: {', '.join(available)}"
        )

    theme_path = settings.theme_dir / f"{theme_name}.json"
    with theme_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    data["name"] = theme_name
    return ThemeTokens.model_validate(data)
