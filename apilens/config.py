# ABOUTME: Configuration loading from apilens.toml.
# ABOUTME: Provides typed config with sensible defaults; all fields are optional.

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]


@dataclass
class Config:
    # Dotted import path to the FastAPI app object, e.g. "myapp.main:app"
    app: str = ""
    # Directory where snapshot JSON files are stored
    snapshots_dir: Path = field(default_factory=lambda: Path("openapi-snapshots"))
    # Host/port for `apilens serve`
    host: str = "127.0.0.1"
    port: int = 8765
    # Whether to post a comment on PRs summarizing API changes
    pr_comments: bool = True


def load(path: Path | None = None) -> Config:
    config_path = path or Path("apilens.toml")
    if not config_path.exists():
        return Config()
    with open(config_path, "rb") as f:
        data = tomllib.load(f)
    section = data.get("apilens", {})
    return Config(
        app=section.get("app", ""),
        snapshots_dir=Path(section.get("snapshots_dir", "openapi-snapshots")),
        host=section.get("host", "127.0.0.1"),
        port=int(section.get("port", 8765)),
        pr_comments=section.get("pr_comments", True),
    )
