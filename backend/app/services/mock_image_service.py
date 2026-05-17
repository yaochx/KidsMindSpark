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
        "imageAssets": story.get("imageAssets", []),
        "imageCount": len(images),
        "status": "preview_generated",
    }


def create_generation_job(payload: dict[str, Any]) -> dict[str, Any]:
    story_id = str(payload.get("storyId", "")).strip()
    if not story_id:
        raise MockImageError("VALIDATION_ERROR", "storyId 不能为空。")

    story = load_story(story_id)
    if story is None:
        raise MockImageError("STORY_NOT_FOUND", "找不到这个故事。")
    pages = story.get("pages", [])
    _validate_pages_for_preview(pages)

    max_images = _generation_budget(payload.get("maxImages", 12))
    selected_by_panel = {
        str(image.get("panelId")): image for image in story.get("images", [])
    }
    candidate_panels = [
        panel
        for page in pages
        for panel in page.get("panels", [])
        if payload.get("forceNew") or panel.get("id") not in selected_by_panel
    ][:max_images]

    job_items: list[dict[str, Any]] = []
    images: list[dict[str, Any]] = []
    for panel in candidate_panels:
        panel_id = str(panel.get("id", ""))
        try:
            result = generate_mock_images(
                {
                    "storyId": story_id,
                    "panelId": panel_id,
                    "forceNew": bool(payload.get("forceNew")),
                }
            )
            image = result["images"][0] if result.get("images") else {}
            images.append(image)
            job_items.append(
                {
                    "panelId": panel_id,
                    "status": image.get("status", "generated"),
                    "imageId": image.get("id", ""),
                    "fromCache": bool(image.get("fromCache")),
                    "retryCount": 0,
                }
            )
        except MockImageError as error:
            job_items.append(
                {
                    "panelId": panel_id,
                    "status": "failed",
                    "imageId": "",
                    "fromCache": False,
                    "retryCount": 0,
                    "error": error.message,
                }
            )

    story = load_story(story_id) or story
    now = datetime.now(timezone.utc).isoformat()
    job = {
        "id": f"job_{now.replace(':', '').replace('-', '').replace('.', '')}",
        "storyId": story_id,
        "status": "completed",
        "budget": {
            "maxImages": max_images,
            "maxRetriesPerPanel": 0,
        },
        "items": job_items,
        "createdAt": now,
        "completedAt": now,
    }
    story.setdefault("generationJobs", []).append(job)
    story["updatedAt"] = now
    save_story(story_id, story)

    return {
        "storyId": story_id,
        "job": job,
        "images": images,
        "imageAssets": story.get("imageAssets", []),
        "status": "generation_job_completed",
    }


def select_panel_image(payload: dict[str, Any]) -> dict[str, Any]:
    story_id = str(payload.get("storyId", "")).strip()
    panel_id = str(payload.get("panelId", "")).strip()
    image_id = str(payload.get("imageId", "")).strip()
    if not story_id or not panel_id or not image_id:
        raise MockImageError("VALIDATION_ERROR", "storyId、panelId 和 imageId 不能为空。")

    story = load_story(story_id)
    if story is None:
        raise MockImageError("STORY_NOT_FOUND", "找不到这个故事。")
    image = _find_image_asset(story.get("imageAssets", []), panel_id, image_id)
    if image is None:
        raise MockImageError("IMAGE_NOT_FOUND", "找不到可选择的候选图。")

    for page in story.get("pages", []):
        for panel in page.get("panels", []):
            if panel.get("id") == panel_id:
                panel["imageId"] = image_id
                panel["selectedImageId"] = image_id

    story["images"] = _merge_images(story.get("images", []), [image])
    story["updatedAt"] = datetime.now(timezone.utc).isoformat()
    save_story(story_id, story)
    return {
        "storyId": story_id,
        "image": image,
        "images": story["images"],
        "imageAssets": story.get("imageAssets", []),
        "status": "image_selected",
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


def _generation_budget(raw_max_images: object) -> int:
    try:
        max_images = int(raw_max_images)
    except (TypeError, ValueError) as error:
        raise MockImageError("VALIDATION_ERROR", "maxImages 必须是 1-24 的整数。") from error
    if not 1 <= max_images <= 24:
        raise MockImageError("VALIDATION_ERROR", "maxImages 必须是 1-24 的整数。")
    return max_images


def _find_image_asset(
    image_assets: list[dict[str, Any]], panel_id: str, image_id: str
) -> dict[str, Any] | None:
    for image in image_assets:
        if image.get("panelId") == panel_id and image.get("id") == image_id:
            return image
    return None


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
