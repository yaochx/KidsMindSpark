from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

DATA_DIR = Path(os.environ.get("MINDSPARK_DATA_DIR", Path(__file__).resolve().parents[2] / "data"))
STORIES_DIR = DATA_DIR / "stories"


def save_story(story_id: str, story: dict[str, Any]) -> None:
    STORIES_DIR.mkdir(parents=True, exist_ok=True)
    story_path = STORIES_DIR / f"{story_id}.json"
    story_path.write_text(
        json.dumps(story, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_story(story_id: str) -> dict[str, Any] | None:
    story_path = STORIES_DIR / f"{story_id}.json"
    if not story_path.exists():
        return None
    return json.loads(story_path.read_text(encoding="utf-8"))
