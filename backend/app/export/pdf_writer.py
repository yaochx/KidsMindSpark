from __future__ import annotations

import struct
from typing import Any

PAGE_WIDTH = 595
PAGE_HEIGHT = 842
MARGIN = 36


class PdfDocument:
    def __init__(self) -> None:
        self.objects: list[bytes] = []

    def add_object(self, body: bytes) -> int:
        self.objects.append(body)
        return len(self.objects)

    def render(self, catalog_ref: int) -> bytes:
        output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets: list[int] = [0]

        for index, body in enumerate(self.objects, start=1):
            offsets.append(len(output))
            output.extend(f"{index} 0 obj\n".encode("ascii"))
            output.extend(body)
            output.extend(b"\nendobj\n")

        xref_offset = len(output)
        output.extend(f"xref\n0 {len(self.objects) + 1}\n".encode("ascii"))
        output.extend(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
        output.extend(
            (
                f"trailer\n<< /Size {len(self.objects) + 1} "
                f"/Root {catalog_ref} 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n"
            ).encode("ascii")
        )
        return bytes(output)


def build_comic_pdf(story: dict[str, Any]) -> bytes:
    doc = PdfDocument()
    font_ref = doc.add_object(
        b"<< /Type /Font /Subtype /Type0 /BaseFont /STSong-Light "
        b"/Encoding /UniGB-UCS2-H /DescendantFonts [2 0 R] >>"
    )
    doc.add_object(
        b"<< /Type /Font /Subtype /CIDFontType0 /BaseFont /STSong-Light "
        b"/CIDSystemInfo << /Registry (Adobe) /Ordering (GB1) /Supplement 2 >> "
        b"/DW 1000 >>"
    )

    image_refs = _add_image_objects(doc, story.get("images", []))
    page_refs: list[int] = []
    page_bodies: list[tuple[int, bytes]] = []
    pages = story.get("pages", [])
    images_by_panel_id = {
        image["panelId"]: image for image in story.get("images", []) if "panelId" in image
    }

    for page in pages:
        content = _build_page_content(story, page, images_by_panel_id, image_refs)
        content_ref = doc.add_object(
            b"<< /Length "
            + str(len(content)).encode("ascii")
            + b" >>\nstream\n"
            + content
            + b"\nendstream"
        )
        page_ref = doc.add_object(b"")
        page_refs.append(page_ref)
        page_bodies.append((page_ref, _page_body(content_ref, font_ref, image_refs)))

    pages_kids = " ".join(f"{ref} 0 R" for ref in page_refs).encode("ascii")
    pages_ref = doc.add_object(
        b"<< /Type /Pages /Kids ["
        + pages_kids
        + f"] /Count {len(page_refs)} >>".encode("ascii")
    )

    for page_ref, body in page_bodies:
        doc.objects[page_ref - 1] = body.replace(b"__PAGES_REF__", f"{pages_ref} 0 R".encode("ascii"))

    catalog_ref = doc.add_object(f"<< /Type /Catalog /Pages {pages_ref} 0 R >>".encode("ascii"))
    return doc.render(catalog_ref)


def _page_body(content_ref: int, font_ref: int, image_refs: dict[str, tuple[str, int]]) -> bytes:
    xobject_resources = b""
    if image_refs:
        xobject_entries = " ".join(
            f"/{name} {ref} 0 R" for name, ref in image_refs.values()
        ).encode("ascii")
        xobject_resources = b" /XObject << " + xobject_entries + b" >>"
    return (
        b"<< /Type /Page /Parent __PAGES_REF__ "
        + f"/MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] ".encode("ascii")
        + f"/Resources << /Font << /F1 {font_ref} 0 R >>".encode("ascii")
        + xobject_resources
        + b" >> "
        + f"/Contents {content_ref} 0 R >>".encode("ascii")
    )


def _build_page_content(
    story: dict[str, Any],
    page: dict[str, Any],
    images_by_panel_id: dict[str, dict[str, Any]],
    image_refs: dict[str, tuple[str, int]],
) -> bytes:
    commands: list[str] = []
    page_number = int(page.get("pageNumber", 0))
    panels = page.get("panels", [])

    _rect(commands, 0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=(1, 0.99, 0.96), stroke=None)
    _text(commands, MARGIN, PAGE_HEIGHT - 38, 16, f"{story.get('title', 'Comic')} / Page {page_number:02d}")
    _text(commands, MARGIN, PAGE_HEIGHT - 60, 12, str(page.get("title", "")))
    _text(commands, PAGE_WIDTH - 110, PAGE_HEIGHT - 38, 10, "A4 Preview")

    boxes = _panel_boxes(len(panels))
    for index, panel in enumerate(panels):
        x, y, width, height = boxes[index]
        palette = _palette(index)
        _rect(commands, x, y, width, height, fill=(1, 1, 1), stroke=(0.08, 0.08, 0.08))
        image = images_by_panel_id.get(panel.get("id", ""))
        if image and image.get("id") in image_refs:
            _draw_image(
                commands,
                image_refs[str(image.get("id"))][0],
                x + 8,
                y + height * 0.42,
                width - 16,
                height * 0.5,
            )
        else:
            _rect(commands, x + 8, y + height * 0.42, width - 16, height * 0.5, fill=palette, stroke=(0.2, 0.2, 0.2))
        _text(commands, x + 14, y + height - 24, 10, f"Panel {panel.get('panelNumber')} / {panel.get('shotType')}")

        _text(commands, x + 14, y + height - 48, 8, image.get("uri", "mock image") if image else "mock image")
        _wrapped_text(commands, x + 14, y + height * 0.37, width - 28, 9, str(panel.get("sceneDescription", "")), max_lines=3)

        text_y = y + 52
        narration = panel.get("narration")
        if narration:
            _rect(commands, x + 12, text_y, width - 24, 24, fill=(0.1, 0.1, 0.1), stroke=None)
            _text(commands, x + 18, text_y + 8, 8, str(narration), color=(1, 1, 1))
            text_y -= 30

        for line in panel.get("dialogue", [])[:2]:
            dialogue = f"{line.get('characterId', '')}: {line.get('text', '')}"
            _rect(commands, x + 12, text_y, width - 24, 24, fill=(1, 1, 1), stroke=(0.08, 0.08, 0.08))
            _text(commands, x + 18, text_y + 8, 8, dialogue)
            text_y -= 30

    _text(commands, MARGIN, 22, 9, "MVP output: structured color comic preview with mock image panels. Future: exact 32K print layout.")
    return "\n".join(commands).encode("utf-8")


def _add_image_objects(
    doc: PdfDocument, images: list[dict[str, Any]]
) -> dict[str, tuple[str, int]]:
    image_refs: dict[str, tuple[str, int]] = {}
    for index, image in enumerate(images, start=1):
        image_id = str(image.get("id", ""))
        source_uri = str(image.get("sourceUri") or image.get("uri") or "")
        png = _read_pdf_png(source_uri)
        if not image_id or png is None:
            continue
        width, height, color_space, colors, data = png
        body = (
            b"<< /Type /XObject /Subtype /Image "
            + f"/Width {width} /Height {height} ".encode("ascii")
            + f"/ColorSpace /{color_space} /BitsPerComponent 8 ".encode("ascii")
            + b"/Filter /FlateDecode "
            + (
                f"/DecodeParms << /Predictor 15 /Colors {colors} "
                f"/BitsPerComponent 8 /Columns {width} >> "
            ).encode("ascii")
            + f"/Length {len(data)} >>\nstream\n".encode("ascii")
            + data
            + b"\nendstream"
        )
        image_refs[image_id] = (f"Im{index}", doc.add_object(body))
    return image_refs


def _read_pdf_png(source_uri: str) -> tuple[int, int, str, int, bytes] | None:
    if source_uri.startswith(("http://", "https://", "/")):
        return None
    try:
        data = open(source_uri, "rb").read()
    except OSError:
        return None
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        return None

    cursor = 8
    width = height = color_type = None
    idat_parts: list[bytes] = []
    while cursor + 8 <= len(data):
        length = struct.unpack(">I", data[cursor : cursor + 4])[0]
        chunk_type = data[cursor + 4 : cursor + 8]
        chunk_data = data[cursor + 8 : cursor + 8 + length]
        cursor += 12 + length
        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type, compression, filter_method, interlace = (
                struct.unpack(">IIBBBBB", chunk_data)
            )
            if bit_depth != 8 or compression != 0 or filter_method != 0 or interlace != 0:
                return None
        elif chunk_type == b"IDAT":
            idat_parts.append(chunk_data)
        elif chunk_type == b"IEND":
            break

    if not width or not height or not idat_parts:
        return None
    if color_type == 2:
        return width, height, "DeviceRGB", 3, b"".join(idat_parts)
    if color_type == 0:
        return width, height, "DeviceGray", 1, b"".join(idat_parts)
    return None


def _panel_boxes(count: int) -> list[tuple[float, float, float, float]]:
    content_width = PAGE_WIDTH - MARGIN * 2
    top = PAGE_HEIGHT - 88
    bottom = 54
    content_height = top - bottom
    gap = 12

    if count == 1:
        return [(MARGIN, bottom, content_width, content_height)]
    if count == 2:
        panel_height = (content_height - gap) / 2
        return [
            (MARGIN, bottom + panel_height + gap, content_width, panel_height),
            (MARGIN, bottom, content_width, panel_height),
        ]

    columns = 2
    rows = 2
    panel_width = (content_width - gap) / columns
    panel_height = (content_height - gap) / rows
    boxes = []
    for index in range(count):
        row = index // columns
        column = index % columns
        x = MARGIN + column * (panel_width + gap)
        y = bottom + (rows - row - 1) * (panel_height + gap)
        boxes.append((x, y, panel_width, panel_height))
    return boxes


def _rect(
    commands: list[str],
    x: float,
    y: float,
    width: float,
    height: float,
    fill: tuple[float, float, float] | None,
    stroke: tuple[float, float, float] | None,
) -> None:
    if fill:
        commands.append(f"{fill[0]} {fill[1]} {fill[2]} rg")
    if stroke:
        commands.append(f"{stroke[0]} {stroke[1]} {stroke[2]} RG")
    commands.append(f"{x:.2f} {y:.2f} {width:.2f} {height:.2f} re")
    if fill and stroke:
        commands.append("B")
    elif fill:
        commands.append("f")
    else:
        commands.append("S")


def _draw_image(
    commands: list[str],
    image_name: str,
    x: float,
    y: float,
    width: float,
    height: float,
) -> None:
    commands.append("q")
    commands.append(f"{width:.2f} 0 0 {height:.2f} {x:.2f} {y:.2f} cm")
    commands.append(f"/{image_name} Do")
    commands.append("Q")


def _text(
    commands: list[str],
    x: float,
    y: float,
    size: int,
    text: str,
    color: tuple[float, float, float] = (0.08, 0.08, 0.08),
) -> None:
    safe_text = _trim_text(text, 58)
    commands.append(f"{color[0]} {color[1]} {color[2]} rg")
    commands.append("BT")
    commands.append(f"/F1 {size} Tf")
    commands.append(f"1 0 0 1 {x:.2f} {y:.2f} Tm")
    commands.append(f"<{safe_text.encode('utf-16-be').hex().upper()}> Tj")
    commands.append("ET")


def _wrapped_text(
    commands: list[str],
    x: float,
    y: float,
    width: float,
    size: int,
    text: str,
    max_lines: int,
) -> None:
    chars_per_line = max(12, int(width / (size * 0.85)))
    trimmed = _trim_text(text, chars_per_line * max_lines)
    lines = [trimmed[index : index + chars_per_line] for index in range(0, len(trimmed), chars_per_line)]
    for line_index, line in enumerate(lines[:max_lines]):
        _text(commands, x, y - line_index * (size + 4), size, line)


def _trim_text(text: str, limit: int) -> str:
    compact = " ".join(str(text).split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1] + "…"


def _palette(index: int) -> tuple[float, float, float]:
    palettes = [
        (0.98, 0.82, 0.43),
        (0.55, 0.85, 0.74),
        (0.76, 0.78, 0.98),
        (0.95, 0.70, 0.78),
    ]
    return palettes[index % len(palettes)]
