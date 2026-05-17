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
from .openai_image_provider import _select_panels
from .prompt_builder import build_panel_image_prompt, build_panel_prompt_hash

DOUBAO_SEEDREAM_IMAGES_URL = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
DEFAULT_DOUBAO_SEEDREAM_MODEL = "doubao-seedream-4-0-250828"
DEFAULT_DOUBAO_SEEDREAM_SIZE = "1024x1024"
DEFAULT_DOUBAO_SEEDREAM_RESPONSE_FORMAT = "b64_json"


class DoubaoSeedreamImageProvider:
    name = "doubao_seedream"

    def __init__(self) -> None:
        self.api_key = os.environ.get("DOUBAO_SEEDREAM_API_KEY", "").strip()
        if not self.api_key:
            raise ProviderConfigError(
                "PROVIDER_CONFIG_ERROR",
                "缺少 DOUBAO_SEEDREAM_API_KEY，无法启用豆包 Seedream ImageProvider。",
                {
                    "DOUBAO_SEEDREAM_API_KEY": (
                        "请在后端环境变量中配置，不要写入前端或 Git。"
                    )
                },
            )
        self.endpoint = os.environ.get(
            "DOUBAO_SEEDREAM_ENDPOINT", DOUBAO_SEEDREAM_IMAGES_URL
        ).strip()
        self.model = os.environ.get(
            "DOUBAO_SEEDREAM_MODEL", DEFAULT_DOUBAO_SEEDREAM_MODEL
        ).strip()
        self.size = os.environ.get("DOUBAO_SEEDREAM_SIZE", DEFAULT_DOUBAO_SEEDREAM_SIZE).strip()
        self.response_format = os.environ.get(
            "DOUBAO_SEEDREAM_RESPONSE_FORMAT", DEFAULT_DOUBAO_SEEDREAM_RESPONSE_FORMAT
        ).strip()
        self.timeout = float(os.environ.get("DOUBAO_SEEDREAM_TIMEOUT", "120"))

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
        width, height = _image_dimensions(self.size)
        for page, panel in panel_items:
            prompt = build_panel_image_prompt(story, page, panel)
            prompt_hash = build_panel_prompt_hash(prompt)
            image_id = f"img_{panel['id']}_{prompt_hash[:8]}_{uuid4().hex[:8]}"
            try:
                image_uri = self._generate_image(image_id, prompt)
                status = "generated"
                error_message = None
            except ProviderCallError as error:
                image_uri = ""
                status = "failed"
                error_message = error.message

            panel["imageId"] = image_id
            image = {
                "id": image_id,
                "panelId": panel["id"],
                "provider": self.name,
                "status": status,
                "uri": image_uri,
                "prompt": prompt,
                "promptHash": prompt_hash,
                "width": width,
                "height": height,
                "style": story.get("visualStyle", "mixed_east_asian_color_comic"),
            }
            if error_message:
                image["error"] = error_message
            images.append(image)

        return images

    def _generate_image(self, image_id: str, prompt: str) -> str:
        request_body = {
            "model": self.model,
            "prompt": prompt,
            "size": self.size,
            "response_format": self.response_format,
        }
        data = json.dumps(request_body, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            self.endpoint,
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
                "豆包 Seedream ImageProvider 请求失败。",
                {"status": str(error.code)},
            ) from error
        except (urllib.error.URLError, TimeoutError) as error:
            raise ProviderCallError(
                "PROVIDER_CALL_FAILED",
                "豆包 Seedream ImageProvider 网络请求失败。",
            ) from error
        except json.JSONDecodeError as error:
            raise ProviderResponseError(
                "PROVIDER_RESPONSE_INVALID",
                "豆包 Seedream ImageProvider 返回了无法解析的响应。",
            ) from error

        return _extract_image_uri(image_id, response_data)


def _extract_image_uri(image_id: str, response_data: dict[str, Any]) -> str:
    image_item = _first_image_item(response_data)
    b64_json = image_item.get("b64_json")
    if isinstance(b64_json, str) and b64_json.strip():
        return save_base64_png(image_id, b64_json)

    image_url = image_item.get("url") or image_item.get("image_url")
    if isinstance(image_url, dict):
        image_url = image_url.get("url")
    if isinstance(image_url, str) and image_url.strip():
        return image_url

    raise ProviderResponseError(
        "PROVIDER_RESPONSE_INVALID",
        "豆包 Seedream ImageProvider 响应中缺少图片数据。",
    )


def _first_image_item(response_data: dict[str, Any]) -> dict[str, Any]:
    for key in ("data", "images"):
        value = response_data.get(key)
        if isinstance(value, list) and value:
            item = value[0]
            if isinstance(item, dict):
                return item
            if isinstance(item, str):
                return {"url": item}
    raise ProviderResponseError(
        "PROVIDER_RESPONSE_INVALID",
        "豆包 Seedream ImageProvider 响应中缺少图片数据。",
    )


def _image_dimensions(size: str) -> tuple[int, int]:
    normalized = size.lower().strip()
    if "x" not in normalized:
        return 1024, 1024
    width_text, height_text = normalized.split("x", maxsplit=1)
    try:
        width = int(width_text)
        height = int(height_text)
    except ValueError:
        return 1024, 1024
    if width <= 0 or height <= 0:
        return 1024, 1024
    return width, height
