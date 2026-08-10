"""Tools for reading and converting PDF/EPUB attachments, via PyMuPDF."""

from __future__ import annotations

import os
from typing import Literal

import pymupdf

from zotero_mcp.app import mcp
from zotero_mcp.library import resolve_attachment_path

_REFLOW_LAYOUT = {"width": 450, "height": 650, "fontsize": 11}


def _open_document(path: str) -> pymupdf.Document:
    try:
        doc = pymupdf.open(path)
    except Exception as exc:
        raise ValueError(f"Could not open {path}: {exc}") from exc
    if doc.is_reflowable:
        doc.layout(**_REFLOW_LAYOUT)
    return doc


@mcp.tool()
def read_document(
    item_key: str, start_page: int = 1, max_pages: int = 20, library: str = "user"
) -> dict:
    """Read the text content of a PDF or EPUB attachment.

    Args:
        item_key: The attachment item's Zotero key.
        start_page: First page to read (1-indexed).
        max_pages: Maximum number of pages to return in one call — page
            through a longer document by calling again with a higher
            start_page.
        library: "user" for your personal library (default), or a group ID
            to access a group library synced locally.
    """
    doc = _open_document(resolve_attachment_path(item_key, library=library))
    total_pages = doc.page_count
    if start_page < 1 or start_page > total_pages:
        doc.close()
        raise ValueError(f"start_page must be between 1 and {total_pages}.")
    end_page = min(start_page + max_pages - 1, total_pages)
    text = "\n\n".join(
        doc[page_number - 1].get_text()
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
    library: str = "user",
) -> str:
    """Convert a PDF or EPUB attachment to another format and save it to disk.

    Args:
        item_key: The attachment item's Zotero key.
        output_path: Filesystem path to write the converted file to. If this
            is an existing directory (or ends with a path separator), the
            file is saved inside it using the attachment's own filename.
        output_format: "pdf" or "txt".
        library: "user" for your personal library (default), or a group ID
            to access a group library synced locally.
    """
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
        text = "\n\n".join(page.get_text() for page in doc)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)

    doc.close()
    return output_path
