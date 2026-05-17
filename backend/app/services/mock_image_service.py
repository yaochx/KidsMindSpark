from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..providers.config import get_image_provider
from ..providers.errors import ProviderError
from ..providers.image import ImageGenerationTarget
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
    target = _build_generation_target(payload)

    try:
        provider = get_image_provider()
        if provider.name != "mock" and target is None:
            raise MockImageError(
                "IMAGE_TARGET_REQUIRED",
                "真实图像生成必须指定 panelId 或 pageNumber，不能默认生成完整 32 页。",
            )
        images = provider.create_images(story, target)
    except ProviderError as error:
        raise MockImageError(error.code, error.message, error.details) from error

    story["pages"] = pages
    story["images"] = _merge_images(story.get("images", []), images)
    story["status"] = "preview_generated"
    story["updatedAt"] = datetime.now(timezone.utc).isoformat()
    save_story(story_id, story)

    return {
        "storyId": story_id,
        "images": images,
        "imageCount": len(images),
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


def _build_generation_target(payload: dict[str, Any]) -> ImageGenerationTarget | None:
    panel_id = str(payload.get("panelId", "")).strip()
    raw_page_number = payload.get("pageNumber")

    if panel_id and raw_page_number not in {None, ""}:
        raise MockImageError(
            "VALIDATION_ERROR",
            "panelId 和 pageNumber 只能选择一个。",
        )
    if panel_id:
        return ImageGenerationTarget(panel_id=panel_id)
    if raw_page_number in {None, ""}:
        return None

    try:
        page_number = int(raw_page_number)
    except (TypeError, ValueError) as error:
        raise MockImageError(
            "VALIDATION_ERROR",
            "pageNumber 必须是 1-32 的整数。",
        ) from error
    if not 1 <= page_number <= 32:
        raise MockImageError(
            "VALIDATION_ERROR",
            "pageNumber 必须是 1-32 的整数。",
        )
    return ImageGenerationTarget(page_number=page_number)


def _merge_images(
    existing_images: list[dict[str, Any]], new_images: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    by_panel_id = {
        str(image.get("panelId")): image
        for image in existing_images
        if str(image.get("panelId", "")).strip()
    }
    for image in new_images:
        by_panel_id[str(image.get("panelId"))] = image
    return list(by_panel_id.values())
