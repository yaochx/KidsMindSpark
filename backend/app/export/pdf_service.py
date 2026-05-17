from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from ..storage.json_store import DATA_DIR, load_story, save_story
from .pdf_writer import build_comic_pdf

EXPORTS_DIR = DATA_DIR / "exports"


class ExportError(ValueError):
    def __init__(self, code: str, message: str, details: dict[str, str] | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


def export_story_pdf(story_id: str, export_format: str) -> tuple[bytes, str]:
    if export_format != "a4_preview_pdf":
        raise ExportError(
            "VALIDATION_ERROR",
            "MVP 仅支持 A4 PDF 预览。",
            {"format": export_format},
        )

    story = load_story(story_id)
    if story is None:
        raise ExportError("STORY_NOT_FOUND", "找不到这个故事。")
    if story.get("status") not in {"preview_generated", "exported"}:
        raise ExportError("PREVIEW_REQUIRED", "请先生成彩色漫画预览。")

    pages = story.get("pages", [])
    images = story.get("images", [])
    if len(pages) != 32 or not images:
        raise ExportError("PREVIEW_REQUIRED", "PDF 导出需要 32 页漫画预览和 mock 图片。")

    try:
        pdf_bytes = build_comic_pdf(story)
        output_path = _write_pdf_file(story_id, pdf_bytes)
        _record_export_job(story, story_id, output_path)
        save_story(story_id, story)
        return pdf_bytes, output_path.name
    except Exception as error:  # pragma: no cover - surfaced through API in MVP
        raise ExportError("EXPORT_FAILED", "PDF 生成失败。", {"reason": str(error)}) from error


def _write_pdf_file(story_id: str, pdf_bytes: bytes) -> Path:
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = EXPORTS_DIR / f"{story_id}_a4_preview.pdf"
    output_path.write_bytes(pdf_bytes)
    return output_path


def _record_export_job(story: dict[str, Any], story_id: str, output_path: Path) -> None:
    now = datetime.now(timezone.utc).isoformat()
    story.setdefault("exportJobs", []).append(
        {
            "id": f"export_{uuid4().hex[:12]}",
            "storyId": story_id,
            "format": "a4_preview_pdf",
            "status": "completed",
            "outputUri": f"/exports/{output_path.name}",
            "createdAt": now,
            "completedAt": now,
        }
    )
    story["status"] = "exported"
    story["updatedAt"] = now
