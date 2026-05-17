from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from ..providers.mock_provider import create_outline
from ..storage.json_store import save_story

SUPPORTED_AGES = {"小学 1-4 年级", "小学 5-6 年级"}
SUPPORTED_STYLES = {
    "chinese_color_comic",
    "japanese_color_manga",
    "mixed_east_asian_color_comic",
}


class StoryValidationError(ValueError):
    def __init__(self, code: str, message: str, details: dict[str, str] | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


def create_story_outline(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = _validate_outline_payload(payload)
    story_id = f"story_{uuid4().hex[:12]}"
    outline = create_outline(normalized, story_id)
    now = datetime.now(timezone.utc).isoformat()

    story = {
        "id": story_id,
        "title": normalized["title"],
        "concept": normalized["concept"],
        "safeConcept": outline["safeConcept"],
        "targetAge": normalized["targetAge"],
        "visualStyle": normalized["visualStyle"],
        "status": "outlined",
        "characters": outline["characters"],
        "timeline": [],
        "pages": [],
        "images": [],
        "exportJobs": [],
        "createdAt": now,
        "updatedAt": now,
    }
    save_story(story_id, story)

    return outline


def _validate_outline_payload(payload: dict[str, Any]) -> dict[str, str]:
    title = str(payload.get("title", "")).strip()
    concept = str(payload.get("concept", "")).strip()
    target_age = str(payload.get("targetAge", "")).strip()
    visual_style = str(payload.get("visualStyle", "")).strip()
    details: dict[str, str] = {}

    if not title:
        details["title"] = "标题不能为空。"
    if len(concept) < 8:
        details["concept"] = "故事概念至少需要 8 个字。"
    if target_age not in SUPPORTED_AGES:
        raise StoryValidationError(
            "AGE_UNSUPPORTED",
            "当前 MVP 仅支持小学阶段读者。",
            {"targetAge": "请选择小学 1-4 年级或小学 5-6 年级。"},
        )
    if visual_style not in SUPPORTED_STYLES:
        details["visualStyle"] = "请选择支持的漫画风格。"
    if details:
        raise StoryValidationError("VALIDATION_ERROR", "请求参数不符合要求。", details)

    return {
        "title": title,
        "concept": concept,
        "targetAge": target_age,
        "visualStyle": visual_style,
    }
