from __future__ import annotations

from typing import Any

from .base import ImageGenerationTarget


class MockImageProvider:
    name = "mock"

    def create_images(
        self, story: dict[str, Any], target: ImageGenerationTarget | None = None
    ) -> list[dict[str, Any]]:
        images: list[dict[str, Any]] = []
        for page in story.get("pages", []):
            if target and target.page_number and page["pageNumber"] != target.page_number:
                continue
            for panel in page["panels"]:
                if target and target.panel_id and panel["id"] != target.panel_id:
                    continue
                image_id = f"img_{panel['id']}"
                panel["imageId"] = image_id
                images.append(
                    {
                        "id": image_id,
                        "panelId": panel["id"],
                        "provider": self.name,
                        "status": "generated",
                        "uri": (
                            "/mock-images/"
                            f"color-comic-placeholder-{page['pageNumber']:03d}-{panel['panelNumber']:02d}.svg"
                        ),
                        "prompt": panel["imagePrompt"],
                        "width": 1024,
                        "height": 768,
                        "style": story.get("visualStyle", "mixed_east_asian_color_comic"),
                    }
                )
        return images
