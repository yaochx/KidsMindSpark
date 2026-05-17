from __future__ import annotations

import importlib
import json
import os
import tempfile
import unittest
from base64 import b64encode
from pathlib import Path
from unittest.mock import patch

from backend.app.config.env_loader import load_dotenv
from backend.app.providers.errors import ProviderResponseError
from backend.app.providers.image.prompt_builder import (
    build_panel_image_prompt,
    build_panel_prompt_hash,
)
from backend.app.providers.story.deepseek_story_provider import DeepSeekStoryProvider
from backend.app.providers.story.openai_story_provider import OpenAIStoryProvider


class MvpFlowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self._patch_data_dirs(Path(self.temp_dir.name))
        os.environ["STORY_PROVIDER"] = "mock"
        os.environ["IMAGE_PROVIDER"] = "mock"

        from backend.app import create_app

        self.client = create_app().test_client()

    def test_full_flow_exports_structured_pdf(self) -> None:
        story_id = self._create_outline()
        timeline = self._create_timeline(story_id)
        self._confirm_timeline(story_id, timeline)
        pages = self._create_script(story_id)

        self.assertEqual(len(pages), 32)
        for page in pages:
            self.assertGreaterEqual(len(page["panels"]), 1)
            self.assertLessEqual(len(page["panels"]), 4)
            for panel in page["panels"]:
                for line in panel["dialogue"]:
                    self.assertLessEqual(len(line["text"]), 18)

        images = self._create_mock_images(story_id)
        panel_count = sum(len(page["panels"]) for page in pages)
        self.assertEqual(len(images), panel_count)

        response = self.client.get(
            f"/api/export/pdf?storyId={story_id}&format=a4_preview_pdf"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/pdf")
        self.assertTrue(response.data.startswith(b"%PDF-"))
        self.assertGreater(len(response.data), 1000)

    def test_script_requires_confirmed_timeline(self) -> None:
        story_id = self._create_outline()

        response = self.client.post("/api/story/script", json={"storyId": story_id})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"]["code"], "TIMELINE_NOT_CONFIRMED")

    def test_export_requires_preview(self) -> None:
        story_id = self._create_outline()
        timeline = self._create_timeline(story_id)
        self._confirm_timeline(story_id, timeline)
        self._create_script(story_id)

        response = self.client.get(
            f"/api/export/pdf?storyId={story_id}&format=a4_preview_pdf"
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"]["code"], "PREVIEW_REQUIRED")

    def test_unknown_story_provider_returns_clear_error(self) -> None:
        with patch.dict(os.environ, {"STORY_PROVIDER": "unknown"}, clear=False):
            response = self.client.post(
                "/api/story/outline",
                json={
                    "title": "三只小猫的森林桃源",
                    "concept": "三只小猫带着木头探险杖去森林冒险。",
                    "targetAge": "小学 1-4 年级",
                    "visualStyle": "mixed_east_asian_color_comic",
                },
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"]["code"], "PROVIDER_CONFIG_ERROR")

    def test_dotenv_loader_reads_values_without_overriding_exports(self) -> None:
        env_path = Path(self.temp_dir.name) / ".env"
        env_path.write_text(
            "\n".join(
                [
                    "STORY_PROVIDER=deepseek",
                    "DEEPSEEK_API_KEY=from-env-file",
                    "IMAGE_PROVIDER=mock",
                    "QUOTED_VALUE=\"hello world\"",
                ]
            ),
            encoding="utf-8",
        )

        with patch.dict(
            os.environ,
            {"DEEPSEEK_API_KEY": "from-shell-export"},
            clear=True,
        ):
            load_dotenv(env_path)

            self.assertEqual(os.environ["STORY_PROVIDER"], "deepseek")
            self.assertEqual(os.environ["DEEPSEEK_API_KEY"], "from-shell-export")
            self.assertEqual(os.environ["IMAGE_PROVIDER"], "mock")
            self.assertEqual(os.environ["QUOTED_VALUE"], "hello world")

    def test_openai_story_provider_requires_api_key(self) -> None:
        with patch.dict(os.environ, {"STORY_PROVIDER": "openai"}, clear=True):
            response = self.client.post(
                "/api/story/outline",
                json={
                    "title": "三只小猫的森林桃源",
                    "concept": "三只小猫带着木头探险杖去森林冒险。",
                    "targetAge": "小学 1-4 年级",
                    "visualStyle": "mixed_east_asian_color_comic",
                },
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"]["code"], "PROVIDER_CONFIG_ERROR")

    def test_openai_story_provider_parses_outline_response(self) -> None:
        api_response = {
            "output": [
                {
                    "type": "message",
                    "content": [
                        {
                            "type": "output_text",
                            "text": json.dumps(
                                {
                                    "title": "三只小猫的森林桃源",
                                    "safeConcept": "三只小猫带着木头探险杖去森林冒险。",
                                    "characters": [
                                        {
                                            "id": "cat_1",
                                            "name": "老大",
                                            "role": "主角",
                                            "description": "稳重的小猫。",
                                            "visualPrompt": "orange kitten leader",
                                        }
                                    ],
                                },
                                ensure_ascii=False,
                            ),
                        }
                    ],
                }
            ]
        }

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
            with patch(
                "backend.app.providers.story.openai_story_provider.urllib.request.urlopen",
                return_value=_FakeOpenAIResponse(api_response),
            ):
                outline = OpenAIStoryProvider().create_outline(
                    {
                        "title": "三只小猫的森林桃源",
                        "concept": "三只小猫拿着猎枪去森林冒险。",
                        "targetAge": "小学 1-4 年级",
                        "visualStyle": "mixed_east_asian_color_comic",
                    },
                    "story_test",
                )

        self.assertEqual(outline["storyId"], "story_test")
        self.assertIn("木头探险杖", outline["safeConcept"])
        self.assertEqual(outline["status"], "outlined")

    def test_openai_story_provider_rejects_invalid_json_text(self) -> None:
        api_response = {"output_text": "不是 JSON"}

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
            with patch(
                "backend.app.providers.story.openai_story_provider.urllib.request.urlopen",
                return_value=_FakeOpenAIResponse(api_response),
            ):
                with self.assertRaises(ProviderResponseError):
                    OpenAIStoryProvider().create_outline(
                        {
                            "title": "三只小猫的森林桃源",
                            "concept": "三只小猫带着木头探险杖去森林冒险。",
                            "targetAge": "小学 1-4 年级",
                            "visualStyle": "mixed_east_asian_color_comic",
                        },
                        "story_test",
                    )

    def test_deepseek_story_provider_requires_api_key(self) -> None:
        with patch.dict(os.environ, {"STORY_PROVIDER": "deepseek"}, clear=True):
            response = self.client.post(
                "/api/story/outline",
                json={
                    "title": "三只小猫的森林桃源",
                    "concept": "三只小猫带着木头探险杖去森林冒险。",
                    "targetAge": "小学 1-4 年级",
                    "visualStyle": "mixed_east_asian_color_comic",
                },
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"]["code"], "PROVIDER_CONFIG_ERROR")

    def test_deepseek_story_provider_parses_outline_response(self) -> None:
        api_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "title": "三只小猫的森林桃源",
                                "safeConcept": "三只小猫带着木头探险杖去森林冒险。",
                                "characters": [],
                            },
                            ensure_ascii=False,
                        )
                    }
                }
            ]
        }

        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}, clear=True):
            with patch(
                "backend.app.providers.story.deepseek_story_provider.urllib.request.urlopen",
                return_value=_FakeOpenAIResponse(api_response),
            ):
                outline = DeepSeekStoryProvider().create_outline(
                    {
                        "title": "三只小猫的森林桃源",
                        "concept": "三只小猫拿着猎枪去森林冒险。",
                        "targetAge": "小学 1-4 年级",
                        "visualStyle": "mixed_east_asian_color_comic",
                    },
                    "story_test",
                )

        self.assertEqual(outline["storyId"], "story_test")
        self.assertIn("木头探险杖", outline["safeConcept"])
        self.assertEqual(outline["status"], "outlined")

    def test_deepseek_story_provider_rejects_invalid_json_text(self) -> None:
        api_response = {"choices": [{"message": {"content": "不是 JSON"}}]}

        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}, clear=True):
            with patch(
                "backend.app.providers.story.deepseek_story_provider.urllib.request.urlopen",
                return_value=_FakeOpenAIResponse(api_response),
            ):
                with self.assertRaises(ProviderResponseError):
                    DeepSeekStoryProvider().create_outline(
                        {
                            "title": "三只小猫的森林桃源",
                            "concept": "三只小猫带着木头探险杖去森林冒险。",
                            "targetAge": "小学 1-4 年级",
                            "visualStyle": "mixed_east_asian_color_comic",
                        },
                        "story_test",
                    )

    def test_panel_prompt_builder_includes_structure_and_dialogue_rules(self) -> None:
        story = {
            "title": "三只小猫的森林桃源",
            "characters": [
                {
                    "id": "cat_eldest",
                    "name": "老大",
                    "role": "主角",
                    "description": "稳重的橘色小猫。",
                    "visualPrompt": "orange kitten with red scarf",
                }
            ],
        }
        page = {
            "pageNumber": 1,
            "title": "森林的邀请",
            "storyBeat": "三只小猫发现发光树叶地图。",
        }
        panel = {
            "id": "panel_001_01",
            "panelNumber": 1,
            "shotType": "medium",
            "sceneDescription": "森林入口，树叶地图发光。",
            "characters": ["老大"],
            "narration": "老大举起木头探险杖。",
            "dialogue": [{"characterId": "老大", "text": "我们出发吧！"}],
            "imagePrompt": "three kittens at a glowing forest entrance",
        }

        prompt = build_panel_image_prompt(story, page, panel)
        prompt_hash = build_panel_prompt_hash(prompt)

        self.assertIn("你正在生成一张儿童彩色漫画单格画面", prompt)
        self.assertIn("第 1 页", prompt)
        self.assertIn("第 1 格", prompt)
        self.assertIn("森林入口，树叶地图发光。", prompt)
        self.assertIn("three kittens at a glowing forest entrance", prompt)
        self.assertIn("orange kitten with red scarf", prompt)
        self.assertIn("气泡内只允许写对白文本", prompt)
        self.assertIn("气泡 1 靠近或尾巴指向 老大", prompt)
        self.assertIn("气泡内只写：我们出发吧！", prompt)
        self.assertNotIn("老大：我们出发吧！", prompt)
        self.assertEqual(len(prompt_hash), 64)

    def test_panel_prompt_builder_disables_text_without_dialogue(self) -> None:
        prompt = build_panel_image_prompt(
            {"title": "无对白测试"},
            {"pageNumber": 2, "title": "安静森林", "storyBeat": "大家安静观察。"},
            {
                "id": "panel_002_01",
                "panelNumber": 1,
                "shotType": "wide",
                "sceneDescription": "安静森林。",
                "characters": ["主角小队"],
                "dialogue": [],
                "imagePrompt": "quiet forest in colorful children's comic style",
            },
        )

        self.assertIn("本格无对白", prompt)
        self.assertIn("不要生成任何文字", prompt)
        self.assertIn("不要生成对白气泡", prompt)

    def test_panel_prompt_builder_requires_image_prompt(self) -> None:
        with self.assertRaises(ProviderResponseError) as raised:
            build_panel_image_prompt(
                {"title": "缺少提示词"},
                {"pageNumber": 1, "title": "第一页", "storyBeat": "测试"},
                {
                    "id": "panel_missing_prompt",
                    "panelNumber": 1,
                    "shotType": "medium",
                    "sceneDescription": "测试场景。",
                    "characters": [],
                    "dialogue": [],
                    "imagePrompt": "",
                },
            )

        self.assertEqual(raised.exception.code, "IMAGE_PROMPT_REQUIRED")

    def test_unknown_image_provider_returns_clear_error(self) -> None:
        story_id = self._create_outline()
        timeline = self._create_timeline(story_id)
        self._confirm_timeline(story_id, timeline)
        self._create_script(story_id)

        with patch.dict(os.environ, {"IMAGE_PROVIDER": "unknown"}, clear=False):
            response = self.client.post("/api/comic/mock-images", json={"storyId": story_id})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"]["code"], "PROVIDER_CONFIG_ERROR")

    def test_openai_image_provider_requires_api_key(self) -> None:
        story_id = self._create_ready_script()

        with patch.dict(
            os.environ,
            {"IMAGE_PROVIDER": "openai_image"},
            clear=True,
        ):
            response = self.client.post(
                "/api/comic/mock-images",
                json={"storyId": story_id, "panelId": "panel_001_01"},
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"]["code"], "PROVIDER_CONFIG_ERROR")

    def test_openai_image_provider_requires_target(self) -> None:
        story_id = self._create_ready_script()

        with patch.dict(
            os.environ,
            {"IMAGE_PROVIDER": "openai_image", "OPENAI_API_KEY": "test-key"},
            clear=True,
        ):
            response = self.client.post("/api/comic/mock-images", json={"storyId": story_id})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"]["code"], "IMAGE_TARGET_REQUIRED")

    def test_openai_image_provider_generates_single_panel(self) -> None:
        story_id = self._create_ready_script()
        api_response = {
            "data": [
                {
                    "b64_json": b64encode(b"fake-png-bytes").decode("ascii"),
                }
            ]
        }

        with patch.dict(
            os.environ,
            {"IMAGE_PROVIDER": "openai_image", "OPENAI_API_KEY": "test-key"},
            clear=True,
        ):
            with patch(
                "backend.app.providers.image.openai_image_provider.urllib.request.urlopen",
                return_value=_FakeOpenAIResponse(api_response),
            ):
                response = self.client.post(
                    "/api/comic/mock-images",
                    json={"storyId": story_id, "panelId": "panel_001_01"},
                )

        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data["imageCount"], 1)
        image = data["images"][0]
        self.assertEqual(image["provider"], "openai_image")
        self.assertEqual(image["status"], "generated")
        self.assertEqual(image["panelId"], "panel_001_01")
        self.assertEqual(len(image["promptHash"]), 64)
        self.assertIn("对白气泡", image["prompt"])
        self.assertIn("气泡内只写：我们一起想办法。", image["prompt"])
        self.assertTrue(Path(image["uri"]).exists())

    def test_openai_image_provider_sends_structured_panel_prompt(self) -> None:
        story_id = self._create_ready_script()
        captured_prompts: list[str] = []
        api_response = {
            "data": [
                {
                    "b64_json": b64encode(b"fake-png-bytes").decode("ascii"),
                }
            ]
        }

        def fake_urlopen(request, timeout):
            captured_prompts.append(json.loads(request.data.decode("utf-8"))["prompt"])
            return _FakeOpenAIResponse(api_response)

        with patch.dict(
            os.environ,
            {"IMAGE_PROVIDER": "openai_image", "OPENAI_API_KEY": "test-key"},
            clear=True,
        ):
            with patch(
                "backend.app.providers.image.openai_image_provider.urllib.request.urlopen",
                side_effect=fake_urlopen,
            ):
                response = self.client.post(
                    "/api/comic/mock-images",
                    json={"storyId": story_id, "panelId": "panel_001_01"},
                )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(captured_prompts), 1)
        self.assertIn("你正在生成一张儿童彩色漫画单格画面", captured_prompts[0])
        self.assertIn("气泡内只允许写对白文本", captured_prompts[0])
        self.assertIn("气泡内只写：我们一起想办法。", captured_prompts[0])
        self.assertNotIn("老大：我们一起想办法。", captured_prompts[0])

    def test_doubao_seedream_image_provider_requires_api_key(self) -> None:
        story_id = self._create_ready_script()

        with patch.dict(
            os.environ,
            {"IMAGE_PROVIDER": "doubao_seedream"},
            clear=True,
        ):
            response = self.client.post(
                "/api/comic/mock-images",
                json={"storyId": story_id, "panelId": "panel_001_01"},
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"]["code"], "PROVIDER_CONFIG_ERROR")

    def test_doubao_seedream_image_provider_requires_target(self) -> None:
        story_id = self._create_ready_script()

        with patch.dict(
            os.environ,
            {
                "IMAGE_PROVIDER": "doubao_seedream",
                "DOUBAO_SEEDREAM_API_KEY": "test-key",
            },
            clear=True,
        ):
            response = self.client.post("/api/comic/mock-images", json={"storyId": story_id})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"]["code"], "IMAGE_TARGET_REQUIRED")

    def test_doubao_seedream_image_provider_generates_single_panel(self) -> None:
        story_id = self._create_ready_script()
        api_response = {
            "data": [
                {
                    "b64_json": b64encode(b"fake-png-bytes").decode("ascii"),
                }
            ]
        }

        with patch.dict(
            os.environ,
            {
                "IMAGE_PROVIDER": "doubao_seedream",
                "DOUBAO_SEEDREAM_API_KEY": "test-key",
            },
            clear=True,
        ):
            with patch(
                (
                    "backend.app.providers.image.doubao_seedream_image_provider."
                    "urllib.request.urlopen"
                ),
                return_value=_FakeOpenAIResponse(api_response),
            ):
                response = self.client.post(
                    "/api/comic/mock-images",
                    json={"storyId": story_id, "panelId": "panel_001_01"},
                )

        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data["imageCount"], 1)
        image = data["images"][0]
        self.assertEqual(image["provider"], "doubao_seedream")
        self.assertEqual(image["status"], "generated")
        self.assertEqual(image["panelId"], "panel_001_01")
        self.assertEqual(len(image["promptHash"]), 64)
        self.assertIn("对白气泡", image["prompt"])
        self.assertTrue(Path(image["uri"]).exists())

    def test_doubao_seedream_provider_sends_structured_panel_prompt(self) -> None:
        story_id = self._create_ready_script()
        captured_prompts: list[str] = []
        api_response = {"data": [{"url": "https://example.test/panel.png"}]}

        def fake_urlopen(request, timeout):
            captured_prompts.append(json.loads(request.data.decode("utf-8"))["prompt"])
            return _FakeOpenAIResponse(api_response)

        with patch.dict(
            os.environ,
            {
                "IMAGE_PROVIDER": "doubao_seedream",
                "DOUBAO_SEEDREAM_API_KEY": "test-key",
                "DOUBAO_SEEDREAM_RESPONSE_FORMAT": "url",
            },
            clear=True,
        ):
            with patch(
                (
                    "backend.app.providers.image.doubao_seedream_image_provider."
                    "urllib.request.urlopen"
                ),
                side_effect=fake_urlopen,
            ):
                response = self.client.post(
                    "/api/comic/mock-images",
                    json={"storyId": story_id, "panelId": "panel_001_01"},
                )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(captured_prompts), 1)
        self.assertIn("只生成一个单格漫画画面", captured_prompts[0])
        self.assertIn("气泡内只写：我们一起想办法。", captured_prompts[0])

    def test_doubao_seedream_image_provider_accepts_url_response(self) -> None:
        story_id = self._create_ready_script()
        api_response = {"data": [{"url": "https://example.test/panel.png"}]}

        with patch.dict(
            os.environ,
            {
                "IMAGE_PROVIDER": "doubao_seedream",
                "DOUBAO_SEEDREAM_API_KEY": "test-key",
                "DOUBAO_SEEDREAM_RESPONSE_FORMAT": "url",
            },
            clear=True,
        ):
            with patch(
                (
                    "backend.app.providers.image.doubao_seedream_image_provider."
                    "urllib.request.urlopen"
                ),
                return_value=_FakeOpenAIResponse(api_response),
            ):
                response = self.client.post(
                    "/api/comic/mock-images",
                    json={"storyId": story_id, "panelId": "panel_001_01"},
                )

        self.assertEqual(response.status_code, 201)
        image = response.get_json()["images"][0]
        self.assertEqual(image["provider"], "doubao_seedream")
        self.assertEqual(image["uri"], "https://example.test/panel.png")

    def _create_outline(self) -> str:
        response = self.client.post(
            "/api/story/outline",
            json={
                "title": "三只小猫的森林桃源",
                "concept": "三只小猫拿着猎枪去森林冒险，最后发现世外桃源。",
                "targetAge": "小学 1-4 年级",
                "visualStyle": "mixed_east_asian_color_comic",
            },
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn("木头探险杖", data["safeConcept"])
        return data["storyId"]

    def _create_timeline(self, story_id: str) -> list[dict]:
        response = self.client.post("/api/story/timeline", json={"storyId": story_id})
        self.assertEqual(response.status_code, 201)
        timeline = response.get_json()["timeline"]
        self.assertEqual(len(timeline), 9)
        return timeline

    def _confirm_timeline(self, story_id: str, timeline: list[dict]) -> None:
        response = self.client.put(
            "/api/story/timeline",
            json={"storyId": story_id, "timeline": timeline, "confirmed": True},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "timeline_confirmed")

    def _create_script(self, story_id: str) -> list[dict]:
        response = self.client.post("/api/story/script", json={"storyId": story_id})
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data["pageCount"], 32)
        self.assertEqual(data["status"], "script_generated")
        return data["pages"]

    def _create_mock_images(self, story_id: str) -> list[dict]:
        response = self.client.post("/api/comic/mock-images", json={"storyId": story_id})
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data["status"], "preview_generated")
        return data["images"]

    def _create_ready_script(self) -> str:
        story_id = self._create_outline()
        timeline = self._create_timeline(story_id)
        self._confirm_timeline(story_id, timeline)
        self._create_script(story_id)
        return story_id

    def _patch_data_dirs(self, data_dir: Path) -> None:
        modules = [
            "backend.app.storage.json_store",
            "backend.app.storage.image_store",
            "backend.app.export.pdf_service",
        ]
        for module_name in modules:
            module = importlib.import_module(module_name)
            if hasattr(module, "DATA_DIR"):
                module.DATA_DIR = data_dir
            if hasattr(module, "STORIES_DIR"):
                module.STORIES_DIR = data_dir / "stories"
            if hasattr(module, "EXPORTS_DIR"):
                module.EXPORTS_DIR = data_dir / "exports"
            if hasattr(module, "IMAGES_DIR"):
                module.IMAGES_DIR = data_dir / "images"


class _FakeOpenAIResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def __enter__(self) -> "_FakeOpenAIResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


if __name__ == "__main__":
    unittest.main()
