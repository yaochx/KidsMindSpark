from __future__ import annotations

from flask import Blueprint, jsonify, request

from ..services.mock_image_service import MockImageError, generate_mock_images

comic_bp = Blueprint("comic", __name__, url_prefix="/api/comic")


@comic_bp.post("/mock-images")
def mock_images():
    payload = request.get_json(silent=True) or {}

    try:
        result = generate_mock_images(payload)
    except MockImageError as error:
        status_code = 400
        if error.code == "STORY_NOT_FOUND":
            status_code = 404
        return (
            jsonify(
                {
                    "error": {
                        "code": error.code,
                        "message": error.message,
                        "details": error.details,
                    }
                }
            ),
            status_code,
        )

    return jsonify(result), 201
