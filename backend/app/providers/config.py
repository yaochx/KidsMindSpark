from __future__ import annotations

import os

from .image import ImageProvider, MockImageProvider
from .story import MockStoryProvider, StoryProvider

DEFAULT_STORY_PROVIDER = "mock"
DEFAULT_IMAGE_PROVIDER = "mock"


class ProviderConfigError(ValueError):
    def __init__(self, code: str, message: str, details: dict[str, str] | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


def get_story_provider() -> StoryProvider:
    provider_name = os.environ.get("STORY_PROVIDER", DEFAULT_STORY_PROVIDER).strip()
    if provider_name == "mock":
        return MockStoryProvider()
    raise ProviderConfigError(
        "PROVIDER_CONFIG_ERROR",
        "未知的 StoryProvider 配置。",
        {"STORY_PROVIDER": provider_name},
    )


def get_image_provider() -> ImageProvider:
    provider_name = os.environ.get("IMAGE_PROVIDER", DEFAULT_IMAGE_PROVIDER).strip()
    if provider_name == "mock":
        return MockImageProvider()
    raise ProviderConfigError(
        "PROVIDER_CONFIG_ERROR",
        "未知的 ImageProvider 配置。",
        {"IMAGE_PROVIDER": provider_name},
    )
