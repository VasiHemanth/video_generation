from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


def _resolve_path(value: str, base: Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (base / path).resolve()


@dataclass(slots=True)
class Settings:
    repo_root: Path
    agents_root: Path
    data_dir: Path
    theme_dir: Path
    remotion_project_path: Path
    render_output_path: Path
    database_url: str | None = None
    groq_api_key: str | None = None
    cerebras_api_key: str | None = None
    galileo_api_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_public_key: str | None = None
    groq_model: str = "llama-3.3-70b-versatile"
    cerebras_model: str = "gpt-oss-120b"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    def __post_init__(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "ir").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "render-props").mkdir(parents=True, exist_ok=True)
        (self.render_output_path / "raw").mkdir(parents=True, exist_ok=True)
        self.render_output_path.mkdir(parents=True, exist_ok=True)
        if not self.database_url:
            self.database_url = f"sqlite+aiosqlite:///{(self.data_dir / 'app.db').resolve()}"

    @classmethod
    def from_env(cls) -> "Settings":
        agents_root = Path(__file__).resolve().parents[1]
        repo_root = agents_root.parent

        database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/app.db")
        data_dir = agents_root / "data"
        if database_url.startswith("sqlite") and "./data/" in database_url:
            data_dir = agents_root / "data"

        remotion_project = _resolve_path(
            os.getenv("REMOTION_PROJECT_PATH", "../remotion"),
            agents_root,
        )
        render_output = _resolve_path(
            os.getenv("RENDER_OUTPUT_PATH", "../remotion/renders"),
            agents_root,
        )

        return cls(
            repo_root=repo_root,
            agents_root=agents_root,
            data_dir=data_dir.resolve(),
            theme_dir=(repo_root / "shared" / "themes").resolve(),
            remotion_project_path=remotion_project,
            render_output_path=render_output,
            database_url=database_url,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            cerebras_api_key=os.getenv("CEREBRAS_API_KEY"),
            galileo_api_key=os.getenv("GALILEO_API_KEY"),
            langfuse_secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            langfuse_public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            groq_model=os.getenv("LLM_MODEL_NAME", os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")),
            cerebras_model=os.getenv("CEREBRAS_MODEL", "gpt-oss-120b"),
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8000")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )
