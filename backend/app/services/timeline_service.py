from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..providers.config import ProviderConfigError, get_story_provider
from ..storage.json_store import load_story, save_story

REQUIRED_NODE_TYPES = [
    "opening",
    "hero",
    "goal",
    "companion",
    "obstacle",
    "twist",
    "crisis",
    "resolution",
    "ending",
]


class TimelineError(ValueError):
    def __init__(self, code: str, message: str, details: dict[str, str] | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


def generate_story_timeline(payload: dict[str, Any]) -> dict[str, Any]:
    story_id = str(payload.get("storyId", "")).strip()
    if not story_id:
        raise TimelineError("VALIDATION_ERROR", "storyId 不能为空。")

    story = load_story(story_id)
    if story is None:
        raise TimelineError("STORY_NOT_FOUND", "找不到这个故事。")
    if story.get("status") not in {"outlined", "timeline_confirmed"}:
        raise TimelineError("OUTLINE_REQUIRED", "请先生成故事核心设定。")

    try:
        timeline = get_story_provider().create_timeline(story)
    except ProviderConfigError as error:
        raise TimelineError(error.code, error.message, error.details) from error
    story["timeline"] = timeline
    story["updatedAt"] = datetime.now(timezone.utc).isoformat()
    if story.get("status") != "timeline_confirmed":
        story["status"] = "outlined"
    save_story(story_id, story)

    return {
        "storyId": story_id,
        "timeline": timeline,
        "status": story["status"],
    }


def update_story_timeline(payload: dict[str, Any]) -> dict[str, Any]:
    story_id = str(payload.get("storyId", "")).strip()
    timeline = payload.get("timeline")
    confirmed = bool(payload.get("confirmed", False))

    if not story_id:
        raise TimelineError("VALIDATION_ERROR", "storyId 不能为空。")
    if not isinstance(timeline, list):
        raise TimelineError("TIMELINE_INVALID", "timeline 必须是节点数组。")

    story = load_story(story_id)
    if story is None:
        raise TimelineError("STORY_NOT_FOUND", "找不到这个故事。")
    if story.get("status") not in {"outlined", "timeline_confirmed"}:
        raise TimelineError("OUTLINE_REQUIRED", "请先生成故事核心设定。")

    normalized_timeline = _validate_timeline(timeline)
    story["timeline"] = normalized_timeline
    story["status"] = "timeline_confirmed" if confirmed else "outlined"
    story["updatedAt"] = datetime.now(timezone.utc).isoformat()
    save_story(story_id, story)

    return {
        "storyId": story_id,
        "timeline": normalized_timeline,
        "status": story["status"],
    }


def _validate_timeline(timeline: list[Any]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    seen_types: set[str] = set()

    for raw_node in timeline:
        if not isinstance(raw_node, dict):
            raise TimelineError("TIMELINE_INVALID", "主线节点格式不正确。")

        node_type = str(raw_node.get("type", "")).strip()
        title = str(raw_node.get("title", "")).strip()
        summary = str(raw_node.get("summary", "")).strip()
        node_id = str(raw_node.get("id", "")).strip()

        if node_type not in REQUIRED_NODE_TYPES:
            raise TimelineError("TIMELINE_INVALID", "主线节点类型不完整。")
        if not node_id or not title or not summary:
            raise TimelineError("TIMELINE_INVALID", "主线节点缺少标题或摘要。")
        if len(title) > 24 or len(summary) > 120:
            raise TimelineError("NODE_OVERFLOW", "节点内容过长，不适合图形化展示。")

        seen_types.add(node_type)
        normalized.append(
            {
                "id": node_id,
                "type": node_type,
                "title": title,
                "summary": summary,
                "order": int(raw_node.get("order", len(normalized) + 1)),
                "x": int(raw_node.get("x", len(normalized) * 240)),
                "y": int(raw_node.get("y", 0)),
                "nextNodeIds": [
                    str(next_node_id)
                    for next_node_id in raw_node.get("nextNodeIds", [])
                    if str(next_node_id).strip()
                ],
            }
        )

    missing_types = set(REQUIRED_NODE_TYPES) - seen_types
    if missing_types:
        raise TimelineError(
            "TIMELINE_INVALID",
            "主线缺少必需节点。",
            {"missingTypes": ", ".join(sorted(missing_types))},
        )

    normalized.sort(key=lambda node: node["order"])
    expected_order = list(range(1, len(REQUIRED_NODE_TYPES) + 1))
    actual_order = [node["order"] for node in normalized]
    if actual_order != expected_order:
        raise TimelineError("TIMELINE_INVALID", "主线节点顺序必须从 1 到 9。")

    return normalized
