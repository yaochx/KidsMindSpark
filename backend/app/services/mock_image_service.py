from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..providers.config import ProviderConfigError, get_image_provider
from ..storage.json_store import load_story, save_story


class MockImageError(ValueError):
    def __init__(self, code: str, message: str, details: dict[str, str] | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


def generate_mock_images(payload: dict[str, Any]) -> dict[str, Any]:
    story_id = str(payload.get("storyId", "")).strip()
    if not story_id:
        raise MockImageError("VALIDATION_ERROR", "storyId 不能为空。")

    story = load_story(story_id)
    if story is None:
        raise MockImageError("STORY_NOT_FOUND", "找不到这个故事。")
    if story.get("status") not in {"script_generated", "preview_generated", "exported"}:
        raise MockImageError("SCRIPT_REQUIRED", "请先生成固定 32 页分镜脚本。")

    pages = story.get("pages", [])
    _validate_pages_for_preview(pages)

    try:
        images = get_image_provider().create_images(story)
    except ProviderConfigError as error:
        raise MockImageError(error.code, error.message, error.details) from error

    story["pages"] = pages
    story["images"] = images
    story["status"] = "preview_generated"
    story["updatedAt"] = datetime.now(timezone.utc).isoformat()
    save_story(story_id, story)

    return {
        "storyId": story_id,
        "images": images,
        "status": "preview_generated",
    }


def _validate_pages_for_preview(pages: list[dict[str, Any]]) -> None:
    if len(pages) != 32:
        raise MockImageError(
            "SCRIPT_REQUIRED",
            "漫画预览需要固定 32 页分镜脚本。",
            {"pageCount": str(len(pages))},
        )

    for page in pages:
        panels = page.get("panels", [])
        if not 1 <= len(panels) <= 4:
            raise MockImageError(
                "SCRIPT_REQUIRED",
                "每页必须包含 1-4 个分镜。",
                {"pageNumber": str(page.get("pageNumber"))},
            )
