from __future__ import annotations

import base64
import os
import re
from pathlib import Path

DATA_DIR = Path(os.environ.get("MINDSPARK_DATA_DIR", Path(__file__).resolve().parents[2] / "data"))
IMAGES_DIR = DATA_DIR / "images"
IMAGE_ID_PATTERN = re.compile(r"^img_[A-Za-z0-9_.-]+$")


def save_base64_png(image_id: str, b64_json: str) -> str:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    image_path = IMAGES_DIR / f"{image_id}.png"
    image_path.write_bytes(base64.b64decode(b64_json))
    return str(image_path)


def image_path_for_id(image_id: str) -> Path | None:
    if not IMAGE_ID_PATTERN.fullmatch(image_id):
        return None
    image_path = IMAGES_DIR / f"{image_id}.png"
    try:
        image_path.relative_to(IMAGES_DIR)
    except ValueError:
        return None
    if not image_path.exists() or not image_path.is_file():
        return None
    return image_path
