from __future__ import annotations

from typing import Any

from .story.mock_story_provider import MockStoryProvider


def make_child_safe_concept(concept: str) -> str:
    return MockStoryProvider().make_child_safe_concept(concept)


def create_outline(payload: dict[str, Any], story_id: str) -> dict[str, Any]:
    return MockStoryProvider().create_outline(payload, story_id)


def create_timeline(story: dict[str, Any]) -> list[dict[str, Any]]:
    return MockStoryProvider().create_timeline(story)


def create_script_pages(story: dict[str, Any]) -> list[dict[str, Any]]:
    return MockStoryProvider().create_script_pages(story)


def _short_narration(page_number: int, panel_index: int) -> str | None:
    return MockStoryProvider()._short_narration(page_number, panel_index)


def _short_dialogue(page_number: int, panel_index: int) -> list[dict[str, str]]:
    return MockStoryProvider()._short_dialogue(page_number, panel_index)
