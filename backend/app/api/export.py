from __future__ import annotations

from io import BytesIO

from flask import Blueprint, jsonify, request, send_file

from ..export.pdf_service import ExportError, export_story_pdf

export_bp = Blueprint("export", __name__, url_prefix="/api/export")


@export_bp.get("/pdf")
def pdf():
    story_id = str(request.args.get("storyId", "")).strip()
    export_format = str(request.args.get("format", "a4_preview_pdf")).strip()

    if not story_id:
        return (
            jsonify(
                {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "storyId 不能为空。",
                        "details": {},
                    }
                }
            ),
            400,
        )

    try:
        pdf_bytes, filename = export_story_pdf(story_id, export_format)
    except ExportError as error:
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

    return send_file(
        BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )
