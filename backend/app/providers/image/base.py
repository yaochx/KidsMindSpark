from __future__ import annotations

from typing import Any, Protocol


class ImageProvider(Protocol):
    name: str

    def create_images(self, story: dict[str, Any]) -> list[dict[str, Any]]:
        ...
