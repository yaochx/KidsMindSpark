from __future__ import annotations

import importlib
import tempfile
import unittest
from pathlib import Path


class MvpFlowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self._patch_data_dirs(Path(self.temp_dir.name))

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

    def _patch_data_dirs(self, data_dir: Path) -> None:
        modules = [
            "backend.app.storage.json_store",
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


if __name__ == "__main__":
    unittest.main()
