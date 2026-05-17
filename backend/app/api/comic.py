from __future__ import annotations

from flask import Blueprint, jsonify, request, send_file

from ..services.mock_image_service import (
    MockImageError,
    create_generation_job,
    generate_mock_images,
    select_panel_image,
)
from ..storage.image_store import image_path_for_id

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


@comic_bp.post("/generation-jobs")
def generation_jobs():
    payload = request.get_json(silent=True) or {}
    try:
        result = create_generation_job(payload)
    except MockImageError as error:
        return _error_response(error)
    return jsonify(result), 201


@comic_bp.put("/images/select")
def select_image():
    payload = request.get_json(silent=True) or {}
    try:
        result = select_panel_image(payload)
    except MockImageError as error:
        return _error_response(error)
    return jsonify(result), 200


@comic_bp.get("/images/<image_id>")
def generated_image(image_id: str):
    image_path = image_path_for_id(image_id)
    if image_path is None:
        return (
            jsonify(
                {
                    "error": {
                        "code": "IMAGE_NOT_FOUND",
                        "message": "找不到这张图片。",
                        "details": {},
                    }
                }
            ),
            404,
        )
    return send_file(image_path, mimetype="image/png")


def _error_response(error: MockImageError):
    status_code = 400
    if error.code in {"STORY_NOT_FOUND", "IMAGE_NOT_FOUND"}:
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
