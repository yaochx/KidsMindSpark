from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..providers.config import get_story_provider
from ..providers.errors import ProviderError
from ..storage.json_store import load_story, save_story
from .page_policy import (
    MAX_STORY_PANELS,
    MAX_STORY_PAGES,
    MIN_STORY_PAGES,
    page_count_in_range,
)


class ScriptError(ValueError):
    def __init__(self, code: str, message: str, details: dict[str, str] | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


def generate_story_script(payload: dict[str, Any]) -> dict[str, Any]:
    story_id = str(payload.get("storyId", "")).strip()
    if not story_id:
        raise ScriptError("VALIDATION_ERROR", "storyId 不能为空。")

    story = load_story(story_id)
    if story is None:
        raise ScriptError("STORY_NOT_FOUND", "找不到这个故事。")
    if story.get("status") not in {
        "timeline_confirmed",
        "script_generated",
        "preview_generated",
        "exported",
    }:
        raise ScriptError("TIMELINE_NOT_CONFIRMED", "请先确认图形化故事主线。")
    if len(story.get("timeline", [])) != 9:
        raise ScriptError("TIMELINE_NOT_CONFIRMED", "请先确认完整的图形化故事主线。")

    try:
        pages = get_story_provider().create_script_pages(story)
    except ProviderError as error:
        raise ScriptError(error.code, error.message, error.details) from error
    _validate_script_pages(pages)

    story["pages"] = pages
    story["pagePolicy"] = {
        "mode": "story_first_bounded",
        "minPages": MIN_STORY_PAGES,
        "maxPages": MAX_STORY_PAGES,
        "maxPanels": MAX_STORY_PANELS,
        "panelsPerPage": {"min": 1, "max": 4},
    }
    story["status"] = "script_generated"
    story["updatedAt"] = datetime.now(timezone.utc).isoformat()
    save_story(story_id, story)

    return {
        "storyId": story_id,
        "pageCount": len(pages),
        "pages": pages,
        "status": "script_generated",
    }


def _validate_script_pages(pages: list[dict[str, Any]]) -> None:
    if not page_count_in_range(len(pages)):
        raise ScriptError(
            "SCRIPT_CONSTRAINT_FAILED",
            "分镜脚本页数必须在 16-48 页之间。",
            {"pageCount": str(len(pages))},
        )

    panel_total = 0
    for page in pages:
        panels = page.get("panels", [])
        panel_total += len(panels)
        if not 1 <= len(panels) <= 4:
            raise ScriptError(
                "SCRIPT_CONSTRAINT_FAILED",
                "每页必须包含 1-4 个分镜。",
                {"pageNumber": str(page.get("pageNumber"))},
            )
        for panel in panels:
            for line in panel.get("dialogue", []):
                if len(str(line.get("text", ""))) > 18:
                    raise ScriptError(
                        "SCRIPT_CONSTRAINT_FAILED",
                        "每条对白必须保持短句。",
                        {"panelId": str(panel.get("id"))},
                    )
    if panel_total > MAX_STORY_PANELS:
        raise ScriptError(
            "SCRIPT_CONSTRAINT_FAILED",
            "单个故事最多允许 96 个分镜。",
            {"panelCount": str(panel_total)},
        )
