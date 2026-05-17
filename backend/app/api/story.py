from __future__ import annotations

from flask import Blueprint, jsonify, request

from ..services.story_service import StoryValidationError, create_story_outline
from ..services.script_service import ScriptError, generate_story_script
from ..services.timeline_service import (
    TimelineError,
    generate_story_timeline,
    update_story_timeline,
)

story_bp = Blueprint("story", __name__, url_prefix="/api/story")


@story_bp.post("/outline")
def outline():
    payload = request.get_json(silent=True) or {}

    try:
        result = create_story_outline(payload)
    except StoryValidationError as error:
        status_code = 400
        if error.code == "AGE_UNSUPPORTED":
            status_code = 422
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


@story_bp.post("/timeline")
def timeline():
    payload = request.get_json(silent=True) or {}

    try:
        result = generate_story_timeline(payload)
    except TimelineError as error:
        return _timeline_error_response(error)

    return jsonify(result), 201


@story_bp.put("/timeline")
def update_timeline():
    payload = request.get_json(silent=True) or {}

    try:
        result = update_story_timeline(payload)
    except TimelineError as error:
        return _timeline_error_response(error)

    return jsonify(result)


@story_bp.post("/script")
def script():
    payload = request.get_json(silent=True) or {}

    try:
        result = generate_story_script(payload)
    except ScriptError as error:
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


def _timeline_error_response(error: TimelineError):
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
