from __future__ import annotations

import base64
import os
from pathlib import Path

DATA_DIR = Path(os.environ.get("MINDSPARK_DATA_DIR", Path(__file__).resolve().parents[2] / "data"))
IMAGES_DIR = DATA_DIR / "images"


def save_base64_png(image_id: str, b64_json: str) -> str:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    image_path = IMAGES_DIR / f"{image_id}.png"
    image_path.write_bytes(base64.b64decode(b64_json))
    return str(image_path)
