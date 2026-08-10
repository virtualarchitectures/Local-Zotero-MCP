"""Tools for reading and converting PDF/EPUB attachments, via PyMuPDF."""

from __future__ import annotations

import os
import re
from typing import Literal

import pymupdf

from zotero_mcp.app import mcp
from zotero_mcp.library import resolve_attachment_path

_REFLOW_LAYOUT = {"width": 450, "height": 650, "fontsize": 11}

# Fraction of page height/width, from each edge, treated as the margin band
# when detecting running headers and footers.
_MARGIN_FRACTION = 0.12
_MIN_PAGES_FOR_DETECTION = 3


def _open_document(path: str) -> pymupdf.Document:
    try:
        doc = pymupdf.open(path)
    except Exception as exc:
        raise ValueError(f"Could not open {path}: {exc}") from exc
    if doc.is_reflowable:
        doc.layout(**_REFLOW_LAYOUT)
    return doc


def _normalize_line(text: str) -> str:
    """Fold a line down to its repeatable shape: blank out digit runs so
    page numbers ("Page 3 of 20" / "Page 4 of 20") match, and collapse all
    punctuation/whitespace so cosmetic layout differences — e.g. an outer
    running head set as "6 of 7  |" on even pages vs "|  7 of 7" on odd
    pages — normalize to the same pattern.
    """
    text = re.sub(r"\d+", "#", text)
    text = re.sub(r"[^\w#]+", " ", text)
    return " ".join(text.split()).strip().lower()


def _lines_by_block(
    page: pymupdf.Page,
) -> list[list[tuple[str, tuple[float, float, float, float]]]]:
    """Each block's non-empty lines as (text, bbox) tuples, in reading order."""
    blocks = []
    for block in page.get_text("dict")["blocks"]:
        lines = []
        for line in block.get("lines", []):
            text = "".join(span["text"] for span in line["spans"]).strip()
            if text:
                lines.append((text, tuple(line["bbox"])))
        if lines:
            blocks.append(lines)
    return blocks


def _in_margin(
    bbox: tuple[float, float, float, float], width: float, height: float
) -> bool:
    """True if a line's bounding box falls in the page's outer margin band —
    top, bottom, left, or right. Checking all four sides (not just top/
    bottom) catches watermark text rotated to run up the side of the page,
    which still has a small bounding box on one axis even though it's tall
    on the other.
    """
    x0, y0, x1, y1 = bbox
    return (
        y1 <= height * _MARGIN_FRACTION
        or y0 >= height * (1 - _MARGIN_FRACTION)
        or x1 <= width * _MARGIN_FRACTION
        or x0 >= width * (1 - _MARGIN_FRACTION)
    )


def _find_running_lines(doc: pymupdf.Document) -> set[str]:
    """Find normalized line text that recurs in the page margins across most
    pages — i.e. running headers/footers, as opposed to one-off content that
    happens to fall near a page edge.
    """
    if doc.page_count < _MIN_PAGES_FOR_DETECTION:
        return set()

    counts: dict[str, int] = {}
    for page in doc:
        width, height = page.rect.width, page.rect.height
        seen = {
            _normalize_line(text)
            for block in _lines_by_block(page)
            for text, bbox in block
            if _in_margin(bbox, width, height)
        }
        for normalized in seen:
            counts[normalized] = counts.get(normalized, 0) + 1

    threshold = max(3, (doc.page_count + 1) // 2)
    return {text for text, count in counts.items() if count >= threshold}


def _page_text(page: pymupdf.Page, running_lines: set[str]) -> str:
    """Page text, optionally with margin lines matching `running_lines` removed."""
    if not running_lines:
        return page.get_text()

    width, height = page.rect.width, page.rect.height
    paragraphs = []
    for block in _lines_by_block(page):
        kept = [
            text
            for text, bbox in block
            if not (
                _in_margin(bbox, width, height)
                and _normalize_line(text) in running_lines
            )
        ]
        if kept:
            paragraphs.append("\n".join(kept))
    return "\n\n".join(paragraphs)


@mcp.tool()
def read_document(
    item_key: str,
    start_page: int = 1,
    max_pages: int = 20,
    remove_headers_footers: bool = False,
    library: str = "user",
) -> dict:
    """Read the text content of a PDF or EPUB attachment.

    Args:
        item_key: The attachment item's Zotero key.
        start_page: First page to read (1-indexed).
        max_pages: Maximum number of pages to return in one call — page
            through a longer document by calling again with a higher
            start_page.
        remove_headers_footers: If true, detect running headers/footers
            (titles, page numbers, etc. that repeat near the top/bottom of
            most pages) and strip them from the returned text.
        library: "user" for your personal library (default), or a group ID
            to access a group library synced locally.
    """
    doc = _open_document(resolve_attachment_path(item_key, library=library))
    total_pages = doc.page_count
    if start_page < 1 or start_page > total_pages:
        doc.close()
        raise ValueError(f"start_page must be between 1 and {total_pages}.")
    end_page = min(start_page + max_pages - 1, total_pages)
    running_lines = _find_running_lines(doc) if remove_headers_footers else set()
    text = "\n\n".join(
        _page_text(doc[page_number - 1], running_lines)
        for page_number in range(start_page, end_page + 1)
    )
    doc.close()
    return {
        "total_pages": total_pages,
        "start_page": start_page,
        "end_page": end_page,
        "text": text,
    }


@mcp.tool()
def convert_document(
    item_key: str,
    output_path: str,
    output_format: Literal["pdf", "txt"] = "pdf",
    remove_headers_footers: bool = False,
    library: str = "user",
) -> str:
    """Convert a PDF or EPUB attachment to another format and save it to disk.

    Args:
        item_key: The attachment item's Zotero key.
        output_path: Filesystem path to write the converted file to. If this
            is an existing directory (or ends with a path separator), the
            file is saved inside it using the attachment's own filename.
        output_format: "pdf" or "txt".
        remove_headers_footers: If true, detect running headers/footers
            (titles, page numbers, etc. that repeat near the top/bottom of
            most pages) and strip them from the text. Only valid with
            output_format="txt" — PDF output preserves the original pages.
        library: "user" for your personal library (default), or a group ID
            to access a group library synced locally.
    """
    if remove_headers_footers and output_format == "pdf":
        raise ValueError(
            "remove_headers_footers is only supported with output_format="
            "'txt'; PDF output preserves the original pages as-is."
        )

    source_path = resolve_attachment_path(item_key, library=library)
    doc = _open_document(source_path)

    if output_path.endswith(os.sep) or os.path.isdir(output_path):
        filename = os.path.splitext(os.path.basename(source_path))[0]
        output_path = os.path.join(output_path, f"{filename}.{output_format}")

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    if output_format == "pdf":
        if doc.is_pdf:
            doc.save(output_path)
        else:
            with open(output_path, "wb") as f:
                f.write(doc.convert_to_pdf())
    else:
        running_lines = _find_running_lines(doc) if remove_headers_footers else set()
        text = "\n\n".join(_page_text(page, running_lines) for page in doc)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)

    doc.close()
    return output_path
