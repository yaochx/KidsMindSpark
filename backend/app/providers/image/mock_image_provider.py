from __future__ import annotations

from typing import Any


class MockImageProvider:
    name = "mock"

    def create_images(self, story: dict[str, Any]) -> list[dict[str, Any]]:
        images: list[dict[str, Any]] = []
        for page in story.get("pages", []):
            for panel in page["panels"]:
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
