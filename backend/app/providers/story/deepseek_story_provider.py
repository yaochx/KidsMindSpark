from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from ..errors import ProviderCallError, ProviderConfigError, ProviderResponseError

DEEPSEEK_CHAT_COMPLETIONS_URL = "https://api.deepseek.com/chat/completions"
DEFAULT_DEEPSEEK_STORY_MODEL = "deepseek-v4-flash"

SYSTEM_INSTRUCTIONS = """
你是儿童中式/日式彩色漫画故事生成系统的结构化文本 provider。
必须只输出 JSON，不要输出 Markdown、解释、代码块或多余文本。
所有内容必须适合小学生阅读，避免危险行为、恐怖细节和成人化表达。
如用户概念含有危险物品，请改写为安全的儿童探险道具。
必须保持故事优先但有边界的漫画结构，主线节点适合图形化展示。
返回内容必须是合法 json 对象。
""".strip()


class DeepSeekStoryProvider:
    name = "deepseek"

    def __init__(self) -> None:
        self.api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
        if not self.api_key:
            raise ProviderConfigError(
                "PROVIDER_CONFIG_ERROR",
                "缺少 DEEPSEEK_API_KEY，无法启用 DeepSeek StoryProvider。",
                {"DEEPSEEK_API_KEY": "请在后端环境变量中配置，不要写入前端或 Git。"},
            )
        self.model = os.environ.get(
            "DEEPSEEK_STORY_MODEL", DEFAULT_DEEPSEEK_STORY_MODEL
        ).strip()
        self.timeout = float(os.environ.get("DEEPSEEK_STORY_TIMEOUT", "90"))

    def create_outline(self, payload: dict[str, Any], story_id: str) -> dict[str, Any]:
        result = self._request_json(
            task="生成故事核心设定",
            user_payload={
                "storyId": story_id,
                "title": payload["title"],
                "concept": payload["concept"],
                "targetAge": payload["targetAge"],
                "visualStyle": payload["visualStyle"],
                "requiredOutput": {
                    "storyId": "string",
                    "title": "string",
                    "safeConcept": "string",
                    "characters": [
                        {
                            "id": "string",
                            "name": "string",
                            "role": "string",
                            "description": "string",
                            "visualPrompt": "string",
                        }
                    ],
                    "status": "outlined",
                },
            },
            max_tokens=2500,
        )
        return {
            "storyId": story_id,
            "title": str(result.get("title") or payload["title"]),
            "safeConcept": _require_text(result, "safeConcept"),
            "characters": _list_or_empty(result.get("characters")),
            "status": "outlined",
        }

    def create_timeline(self, story: dict[str, Any]) -> list[dict[str, Any]]:
        node_types = [
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
        result = self._request_json(
            task="生成图形化故事主线",
            user_payload={
                "story": _story_context(story),
                "rules": [
                    "必须生成 9 个节点。",
                    "节点 type 必须按指定顺序使用。",
                    "title 不超过 24 个中文字符。",
                    "summary 不超过 120 个中文字符。",
                    "x 从 0 开始每个节点递增 240，y 固定为 0。",
                ],
                "nodeTypes": node_types,
                "requiredOutput": {
                    "timeline": [
                        {
                            "id": "node_<type>",
                            "type": "one of nodeTypes",
                            "title": "string",
                            "summary": "string",
                            "order": "integer 1-9",
                            "x": "integer",
                            "y": 0,
                            "nextNodeIds": ["next node id or empty array"],
                        }
                    ]
                },
            },
            max_tokens=4500,
        )
        timeline = result.get("timeline")
        if not isinstance(timeline, list):
            raise ProviderResponseError(
                "PROVIDER_RESPONSE_INVALID",
                "DeepSeek StoryProvider 返回的主线不是节点数组。",
            )
        return timeline

    def create_script_pages(self, story: dict[str, Any]) -> list[dict[str, Any]]:
        result = self._request_json(
            task="生成 16-48 页彩色漫画分镜脚本",
            user_payload={
                "story": _story_context(story),
                "timeline": story.get("timeline", []),
                "rules": [
                    "页数必须在 16-48 页之间，由故事表达需要决定。",
                    "整个故事最多 96 个分镜。",
                    "每页必须 1-4 个分镜。",
                    "每条对白不超过 18 个中文字符。",
                    "每个 panel 必须包含 imagePrompt。",
                    "imagePrompt 用英文描述彩色中式/日式儿童漫画画面。",
                    "不要生成纯文字故事，要生成漫画分镜结构。",
                ],
                "requiredOutput": {
                    "pages": [
                        {
                            "pageNumber": "integer, starts at 1",
                            "title": "string",
                            "storyBeat": "string",
                            "panels": [
                                {
                                    "id": "panel_001_01",
                                    "panelNumber": "integer",
                                    "shotType": "wide | medium | closeup | detail | action",
                                    "sceneDescription": "string",
                                    "characters": ["string"],
                                    "narration": "short string or null",
                                    "dialogue": [
                                        {
                                            "characterId": "string",
                                            "text": "short Chinese sentence",
                                        }
                                    ],
                                    "imagePrompt": "English comic image prompt",
                                }
                            ],
                            "pageNote": "string",
                        }
                    ]
                },
            },
            max_tokens=16000,
        )
        pages = result.get("pages")
        if not isinstance(pages, list):
            raise ProviderResponseError(
                "PROVIDER_RESPONSE_INVALID",
                "DeepSeek StoryProvider 返回的分镜不是页面数组。",
            )
        return pages

    def _request_json(
        self, task: str, user_payload: dict[str, Any], max_tokens: int
    ) -> dict[str, Any]:
        request_body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                {
                    "role": "user",
                    "content": (
                        f"任务：{task}\n"
                        "请返回严格 json 对象，且 json 必须符合 requiredOutput 描述。\n"
                        f"{json.dumps(user_payload, ensure_ascii=False)}"
                    ),
                },
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.4,
            "max_tokens": max_tokens,
            "stream": False,
        }
        data = json.dumps(request_body, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            DEEPSEEK_CHAT_COMPLETIONS_URL,
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
                "DeepSeek StoryProvider 请求失败。",
                {"status": str(error.code)},
            ) from error
        except (urllib.error.URLError, TimeoutError) as error:
            raise ProviderCallError(
                "PROVIDER_CALL_FAILED",
                "DeepSeek StoryProvider 网络请求失败。",
            ) from error
        except json.JSONDecodeError as error:
            raise ProviderResponseError(
                "PROVIDER_RESPONSE_INVALID",
                "DeepSeek StoryProvider 返回了无法解析的响应。",
            ) from error

        output_text = _extract_output_text(response_data)
        try:
            parsed = json.loads(output_text)
        except json.JSONDecodeError as error:
            raise ProviderResponseError(
                "PROVIDER_RESPONSE_INVALID",
                "DeepSeek StoryProvider 返回的内容不是合法 JSON。",
            ) from error
        if not isinstance(parsed, dict):
            raise ProviderResponseError(
                "PROVIDER_RESPONSE_INVALID",
                "DeepSeek StoryProvider 返回的 JSON 顶层必须是对象。",
            )
        return parsed


def _extract_output_text(response_data: dict[str, Any]) -> str:
    choices = response_data.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ProviderResponseError(
            "PROVIDER_RESPONSE_INVALID",
            "DeepSeek StoryProvider 响应中缺少 choices。",
        )
    message = choices[0].get("message") if isinstance(choices[0], dict) else None
    content = message.get("content") if isinstance(message, dict) else None
    if isinstance(content, str) and content.strip():
        return content
    raise ProviderResponseError(
        "PROVIDER_RESPONSE_INVALID",
        "DeepSeek StoryProvider 响应中缺少文本输出。",
    )


def _require_text(payload: dict[str, Any], key: str) -> str:
    value = str(payload.get(key, "")).strip()
    if not value:
        raise ProviderResponseError(
            "PROVIDER_RESPONSE_INVALID",
            f"DeepSeek StoryProvider 返回缺少字段：{key}。",
        )
    return value


def _list_or_empty(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _story_context(story: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": story.get("id"),
        "title": story.get("title"),
        "concept": story.get("concept"),
        "safeConcept": story.get("safeConcept"),
        "targetAge": story.get("targetAge"),
        "visualStyle": story.get("visualStyle"),
        "characters": story.get("characters", []),
    }
