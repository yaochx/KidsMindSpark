from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class ImageGenerationTarget:
    panel_id: str | None = None
    page_number: int | None = None


class ImageProvider(Protocol):
    name: str

    def create_images(
        self, story: dict[str, Any], target: ImageGenerationTarget | None = None
    ) -> list[dict[str, Any]]:
        ...
