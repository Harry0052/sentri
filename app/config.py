"""Runtime settings. Environment variables override the defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_dotenv(path: Path) -> None:
    """Load KEY=value lines into the environment without overriding existing vars."""
    if not path.is_file():
        return
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


@dataclass(frozen=True)
class Settings:
    video_path: Path
    alert_threshold: int = 2
    pace: bool = True
    loop: bool = True
    max_missed: int = 10
    confirm_hits: int = 3
    max_match_distance: float = 120.0

    @staticmethod
    def from_env() -> Settings:
        load_dotenv(ROOT / ".env")
        video = os.environ.get("VIDEO_PATH", "demo-videos/sample.avi").strip()
        if not video:
            video = "demo-videos/sample.avi"
        path = Path(video)
        if not path.is_absolute():
            path = ROOT / path

        raw_threshold = os.environ.get("ALERT_THRESHOLD", "").strip()
        if raw_threshold == "":
            threshold = 2
        else:
            try:
                threshold = int(raw_threshold)
            except ValueError as exc:
                raise RuntimeError(
                    f"ALERT_THRESHOLD must be an integer, got {raw_threshold!r}"
                ) from exc
        if threshold < 0:
            raise RuntimeError("ALERT_THRESHOLD must be zero or greater")

        return Settings(video_path=path, alert_threshold=threshold)
