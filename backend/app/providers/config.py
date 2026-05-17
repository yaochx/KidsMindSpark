from __future__ import annotations

import os

from .errors import ProviderConfigError
from .image import ImageProvider, MockImageProvider, OpenAIImageProvider
from .story import MockStoryProvider, OpenAIStoryProvider, StoryProvider

DEFAULT_STORY_PROVIDER = "mock"
DEFAULT_IMAGE_PROVIDER = "mock"


def get_story_provider() -> StoryProvider:
    provider_name = os.environ.get("STORY_PROVIDER", DEFAULT_STORY_PROVIDER).strip()
    if provider_name == "mock":
        return MockStoryProvider()
    if provider_name == "openai":
        return OpenAIStoryProvider()
    raise ProviderConfigError(
        "PROVIDER_CONFIG_ERROR",
        "未知的 StoryProvider 配置。",
        {"STORY_PROVIDER": provider_name},
    )


def get_image_provider() -> ImageProvider:
    provider_name = os.environ.get("IMAGE_PROVIDER", DEFAULT_IMAGE_PROVIDER).strip()
    if provider_name == "mock":
        return MockImageProvider()
    if provider_name == "openai_image":
        return OpenAIImageProvider()
    raise ProviderConfigError(
        "PROVIDER_CONFIG_ERROR",
        "未知的 ImageProvider 配置。",
        {"IMAGE_PROVIDER": provider_name},
    )
