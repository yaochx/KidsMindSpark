from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..providers.mock_provider import create_script_pages
from ..storage.json_store import load_story, save_story


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

    pages = create_script_pages(story)
    _validate_script_pages(pages)

    story["pages"] = pages
    story["status"] = "script_generated"
    story["updatedAt"] = datetime.now(timezone.utc).isoformat()
    save_story(story_id, story)

    return {
        "storyId": story_id,
        "pageCount": 32,
        "pages": pages,
        "status": "script_generated",
    }


def _validate_script_pages(pages: list[dict[str, Any]]) -> None:
    if len(pages) != 32:
        raise ScriptError(
            "SCRIPT_CONSTRAINT_FAILED",
            "分镜脚本必须正好 32 页。",
            {"pageCount": str(len(pages))},
        )

    for page in pages:
        panels = page.get("panels", [])
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
