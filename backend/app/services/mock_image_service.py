from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..providers.config import get_image_provider
from ..providers.errors import ProviderError
from ..providers.image import ImageGenerationTarget
from ..providers.image.prompt_builder import (
    build_panel_image_prompt,
    build_panel_prompt_hash,
)
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
        if provider.name == "mock":
            images = provider.create_images(story, target)
            assets = story.get("imageAssets", [])
        else:
            images = _create_real_images_with_cache(story, provider, target, payload)
            assets = _merge_image_assets(story.get("imageAssets", []), images)
    except ProviderError as error:
        raise MockImageError(error.code, error.message, error.details) from error

    story["pages"] = pages
    story["images"] = _merge_images(story.get("images", []), images)
    story["imageAssets"] = assets
    story["status"] = "preview_generated"
    story["updatedAt"] = datetime.now(timezone.utc).isoformat()
    save_story(story_id, story)

    return {
        "storyId": story_id,
        "images": images,
        "imageCount": len(images),
        "status": "preview_generated",
    }


def _create_real_images_with_cache(
    story: dict[str, Any],
    provider,
    target: ImageGenerationTarget,
    payload: dict[str, Any],
) -> list[dict[str, Any]]:
    force_new = bool(payload.get("forceNew"))
    selected_panels = _select_target_panels(story.get("pages", []), target)
    existing_assets = story.get("imageAssets", [])
    images: list[dict[str, Any]] = []

    for page, panel in selected_panels:
        prompt = build_panel_image_prompt(story, page, panel)
        prompt_hash = build_panel_prompt_hash(prompt)
        cache_key = _cache_key(provider, prompt_hash, panel)
        cached_image = None if force_new else _find_cached_image(existing_assets, cache_key)

        if cached_image:
            image = dict(cached_image)
            image["fromCache"] = True
        else:
            generated_images = provider.create_images(
                story, ImageGenerationTarget(panel_id=str(panel.get("id", "")))
            )
            if not generated_images:
                continue
            image = _normalize_real_image(generated_images[0], provider, story, cache_key)
            image["fromCache"] = False

        panel["imageId"] = image["id"]
        panel["selectedImageId"] = image["id"]
        images.append(image)

    return images


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


def _select_target_panels(
    pages: list[dict[str, Any]], target: ImageGenerationTarget
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    selected: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for page in pages:
        if target.page_number and page.get("pageNumber") != target.page_number:
            continue
        for panel in page.get("panels", []):
            if target.panel_id and panel.get("id") != target.panel_id:
                continue
            selected.append((page, panel))
    if not selected:
        raise MockImageError("IMAGE_TARGET_NOT_FOUND", "找不到要生成图片的分镜。")
    return selected


def _cache_key(provider, prompt_hash: str, panel: dict[str, Any]) -> str:
    provider_name = str(getattr(provider, "name", ""))
    model = str(getattr(provider, "model", ""))
    size = str(getattr(provider, "size", ""))
    panel_id = str(panel.get("id", ""))
    return f"{provider_name}:{model}:{size}:{prompt_hash}:{panel_id}"


def _find_cached_image(
    image_assets: list[dict[str, Any]], cache_key: str
) -> dict[str, Any] | None:
    for image in reversed(image_assets):
        if image.get("cacheKey") == cache_key and image.get("status") == "generated":
            return image
    return None


def _normalize_real_image(
    image: dict[str, Any],
    provider,
    story: dict[str, Any],
    cache_key: str,
) -> dict[str, Any]:
    normalized = dict(image)
    image_id = str(normalized.get("id", ""))
    uri = str(normalized.get("uri", ""))
    normalized["storyId"] = story.get("storyId", "")
    normalized["model"] = str(getattr(provider, "model", ""))
    normalized["size"] = str(getattr(provider, "size", ""))
    normalized["cacheKey"] = cache_key
    normalized["createdAt"] = datetime.now(timezone.utc).isoformat()
    if uri and Path(uri).is_absolute():
        normalized["sourceUri"] = uri
        normalized["uri"] = f"/api/comic/images/{image_id}"
    return normalized


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


def _merge_image_assets(
    existing_images: list[dict[str, Any]], new_images: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    by_id = {
        str(image.get("id")): image
        for image in existing_images
        if str(image.get("id", "")).strip()
    }
    for image in new_images:
        by_id[str(image.get("id"))] = image
    return list(by_id.values())
