from __future__ import annotations

from typing import Any, Protocol


class StoryProvider(Protocol):
    name: str

    def create_outline(self, payload: dict[str, Any], story_id: str) -> dict[str, Any]:
        ...

    def create_timeline(self, story: dict[str, Any]) -> list[dict[str, Any]]:
        ...

    def create_script_pages(self, story: dict[str, Any]) -> list[dict[str, Any]]:
        ...
