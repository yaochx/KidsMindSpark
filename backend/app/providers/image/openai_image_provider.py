from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any
from uuid import uuid4

from ...storage.image_store import save_base64_png
from ..errors import ProviderCallError, ProviderConfigError, ProviderResponseError
from .base import ImageGenerationTarget
from .prompt_builder import build_panel_image_prompt, build_panel_prompt_hash

OPENAI_IMAGES_URL = "https://api.openai.com/v1/images/generations"
DEFAULT_OPENAI_IMAGE_MODEL = "gpt-image-1"
DEFAULT_OPENAI_IMAGE_SIZE = "1024x1024"


class OpenAIImageProvider:
    name = "openai_image"

    def __init__(self) -> None:
        self.api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not self.api_key:
            raise ProviderConfigError(
                "PROVIDER_CONFIG_ERROR",
                "缺少 OPENAI_API_KEY，无法启用 OpenAI ImageProvider。",
                {"OPENAI_API_KEY": "请在后端环境变量中配置，不要写入前端或 Git。"},
            )
        self.model = os.environ.get("OPENAI_IMAGE_MODEL", DEFAULT_OPENAI_IMAGE_MODEL).strip()
        self.size = os.environ.get("OPENAI_IMAGE_SIZE", DEFAULT_OPENAI_IMAGE_SIZE).strip()
        self.timeout = float(os.environ.get("OPENAI_IMAGE_TIMEOUT", "120"))

    def create_images(
        self, story: dict[str, Any], target: ImageGenerationTarget | None = None
    ) -> list[dict[str, Any]]:
        if target is None:
            raise ProviderConfigError(
                "IMAGE_TARGET_REQUIRED",
                "真实图像生成必须指定 panelId 或 pageNumber，不能默认生成整本故事。",
            )

        panel_items = _select_panels(story, target)
        images: list[dict[str, Any]] = []
        for page, panel in panel_items:
            prompt = build_panel_image_prompt(story, page, panel)
            prompt_hash = build_panel_prompt_hash(prompt)
            image_id = f"img_{panel['id']}_{prompt_hash[:8]}_{uuid4().hex[:8]}"
            try:
                image_path = self._generate_png(image_id, prompt)
                status = "generated"
                error_message = None
            except ProviderCallError as error:
                image_path = ""
                status = "failed"
                error_message = error.message

            panel["imageId"] = image_id
            image = {
                "id": image_id,
                "panelId": panel["id"],
                "provider": self.name,
                "status": status,
                "uri": image_path,
                "prompt": prompt,
                "promptHash": prompt_hash,
                "width": 1024,
                "height": 1024,
                "style": story.get("visualStyle", "mixed_east_asian_color_comic"),
            }
            if error_message:
                image["error"] = error_message
            images.append(image)

        return images

    def _generate_png(self, image_id: str, prompt: str) -> str:
        request_body = {
            "model": self.model,
            "prompt": prompt,
            "size": self.size,
            "n": 1,
        }
        data = json.dumps(request_body, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            OPENAI_IMAGES_URL,
            data=data,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                response_data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            raise ProviderCallError(
                "PROVIDER_CALL_FAILED",
                "OpenAI ImageProvider 请求失败。",
                {"status": str(error.code)},
            ) from error
        except (urllib.error.URLError, TimeoutError) as error:
            raise ProviderCallError(
                "PROVIDER_CALL_FAILED",
                "OpenAI ImageProvider 网络请求失败。",
            ) from error
        except json.JSONDecodeError as error:
            raise ProviderResponseError(
                "PROVIDER_RESPONSE_INVALID",
                "OpenAI ImageProvider 返回了无法解析的响应。",
            ) from error

        b64_json = _extract_b64_image(response_data)
        return save_base64_png(image_id, b64_json)


def _select_panels(
    story: dict[str, Any], target: ImageGenerationTarget
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    selected: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for page in story.get("pages", []):
        if target.page_number and page.get("pageNumber") != target.page_number:
            continue
        for panel in page.get("panels", []):
            if target.panel_id and panel.get("id") != target.panel_id:
                continue
            selected.append((page, panel))

    if not selected:
        raise ProviderResponseError(
            "IMAGE_TARGET_NOT_FOUND",
            "找不到要生成图片的分镜。",
        )
    return selected


def _extract_b64_image(response_data: dict[str, Any]) -> str:
    data = response_data.get("data")
    if not isinstance(data, list) or not data:
        raise ProviderResponseError(
            "PROVIDER_RESPONSE_INVALID",
            "OpenAI ImageProvider 响应中缺少图片数据。",
        )
    b64_json = data[0].get("b64_json") if isinstance(data[0], dict) else None
    if not isinstance(b64_json, str) or not b64_json.strip():
        raise ProviderResponseError(
            "PROVIDER_RESPONSE_INVALID",
            "OpenAI ImageProvider 响应中缺少 base64 图片。",
        )
    return b64_json
