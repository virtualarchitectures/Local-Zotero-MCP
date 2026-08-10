import os

import pymupdf
import pytest

from zotero_mcp import documents


@pytest.fixture
def sample_pdf(tmp_path):
    doc = pymupdf.open()
    for text in ("Page one text", "Page two text"):
        page = doc.new_page()
        page.insert_text((72, 72), text)
    path = tmp_path / "sample.pdf"
    doc.save(str(path))
    doc.close()
    return str(path)


@pytest.fixture
def sample_pdf_with_running_header_footer(tmp_path):
    doc = pymupdf.open()
    for page_number, body in enumerate(
        ("First body text", "Second body text", "Third body text"), start=1
    ):
        page = doc.new_page(width=595, height=842)
        page.insert_text((72, 30), "My Book Title")  # running header
        page.insert_text((72, 400), body)
        page.insert_text((72, 800), f"Page {page_number} of 3")  # running footer
    path = tmp_path / "sample_with_header_footer.pdf"
    doc.save(str(path))
    doc.close()
    return str(path)


@pytest.fixture
def sample_pdf_with_side_watermark_and_alternating_page_numbers(tmp_path):
    doc = pymupdf.open()
    for page_number, body in enumerate(
        ("First body text", "Second body text", "Third body text", "Fourth body text"),
        start=1,
    ):
        page = doc.new_page(width=595, height=842)
        page.insert_text((72, 400), body)
        # Running watermark rotated to run up the right edge of the page.
        page.insert_text((585, 700), "Downloaded from example.org", rotate=90)
        # Outer-corner page numbers: punctuation/position alternates by page.
        if page_number % 2:
            page.insert_text((500, 30), f"{page_number} of 4  |")
        else:
            page.insert_text((72, 30), f"|  {page_number} of 4")
    path = tmp_path / "sample_with_watermark.pdf"
    doc.save(str(path))
    doc.close()
    return str(path)


def test_read_document(monkeypatch, sample_pdf):
    monkeypatch.setattr(
        documents, "resolve_attachment_path", lambda key, library="user": sample_pdf
    )
    result = documents.read_document("ABCD1234")
    assert result["total_pages"] == 2
    assert result["start_page"] == 1
    assert result["end_page"] == 2
    assert "Page one text" in result["text"]
    assert "Page two text" in result["text"]


def test_read_document_pagination(monkeypatch, sample_pdf):
    monkeypatch.setattr(
        documents, "resolve_attachment_path", lambda key, library="user": sample_pdf
    )
    result = documents.read_document("ABCD1234", start_page=2, max_pages=1)
    assert result["start_page"] == 2
    assert result["end_page"] == 2
    assert "Page two text" in result["text"]
    assert "Page one text" not in result["text"]


def test_read_document_invalid_start_page(monkeypatch, sample_pdf):
    monkeypatch.setattr(
        documents, "resolve_attachment_path", lambda key, library="user": sample_pdf
    )
    with pytest.raises(ValueError, match="start_page must be between 1 and 2"):
        documents.read_document("ABCD1234", start_page=5)


def test_convert_document_to_txt(monkeypatch, sample_pdf, tmp_path):
    monkeypatch.setattr(
        documents, "resolve_attachment_path", lambda key, library="user": sample_pdf
    )
    output_path = str(tmp_path / "out" / "sample.txt")
    result = documents.convert_document("ABCD1234", output_path, output_format="txt")
    assert result == output_path
    assert "Page one text" in open(output_path).read()


def test_convert_document_to_pdf(monkeypatch, sample_pdf, tmp_path):
    monkeypatch.setattr(
        documents, "resolve_attachment_path", lambda key, library="user": sample_pdf
    )
    output_path = str(tmp_path / "converted.pdf")
    documents.convert_document("ABCD1234", output_path, output_format="pdf")
    converted = pymupdf.open(output_path)
    assert converted.page_count == 2
    assert "Page one text" in converted[0].get_text()


def test_convert_document_to_existing_directory(monkeypatch, sample_pdf, tmp_path):
    monkeypatch.setattr(
        documents, "resolve_attachment_path", lambda key, library="user": sample_pdf
    )
    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()
    result = documents.convert_document("ABCD1234", str(dest_dir), output_format="txt")
    assert result == str(dest_dir / "sample.txt")
    assert "Page one text" in open(result).read()


def test_convert_document_to_directory_with_trailing_slash(
    monkeypatch, sample_pdf, tmp_path
):
    monkeypatch.setattr(
        documents, "resolve_attachment_path", lambda key, library="user": sample_pdf
    )
    dest_dir = str(tmp_path / "newdir") + os.sep
    result = documents.convert_document("ABCD1234", dest_dir, output_format="txt")
    assert result == dest_dir + "sample.txt"
    assert "Page one text" in open(result).read()


def test_read_document_keeps_headers_footers_by_default(
    monkeypatch, sample_pdf_with_running_header_footer
):
    monkeypatch.setattr(
        documents,
        "resolve_attachment_path",
        lambda key, library="user": sample_pdf_with_running_header_footer,
    )
    result = documents.read_document("ABCD1234")
    assert "My Book Title" in result["text"]
    assert "Page 1 of 3" in result["text"]
    assert "First body text" in result["text"]


def test_read_document_removes_running_header_footer(
    monkeypatch, sample_pdf_with_running_header_footer
):
    monkeypatch.setattr(
        documents,
        "resolve_attachment_path",
        lambda key, library="user": sample_pdf_with_running_header_footer,
    )
    result = documents.read_document("ABCD1234", remove_headers_footers=True)
    assert "My Book Title" not in result["text"]
    assert "Page 1 of 3" not in result["text"]
    assert "First body text" in result["text"]
    assert "Second body text" in result["text"]
    assert "Third body text" in result["text"]


def test_convert_document_txt_removes_running_header_footer(
    monkeypatch, sample_pdf_with_running_header_footer, tmp_path
):
    monkeypatch.setattr(
        documents,
        "resolve_attachment_path",
        lambda key, library="user": sample_pdf_with_running_header_footer,
    )
    output_path = str(tmp_path / "out.txt")
    documents.convert_document(
        "ABCD1234", output_path, output_format="txt", remove_headers_footers=True
    )
    text = open(output_path).read()
    assert "My Book Title" not in text
    assert "Page 2 of 3" not in text
    assert "Second body text" in text


def test_convert_document_pdf_rejects_remove_headers_footers(
    monkeypatch, sample_pdf_with_running_header_footer, tmp_path
):
    monkeypatch.setattr(
        documents,
        "resolve_attachment_path",
        lambda key, library="user": sample_pdf_with_running_header_footer,
    )
    output_path = str(tmp_path / "out.pdf")
    with pytest.raises(ValueError, match="remove_headers_footers"):
        documents.convert_document(
            "ABCD1234", output_path, output_format="pdf", remove_headers_footers=True
        )


def test_read_document_removes_rotated_side_watermark(
    monkeypatch, sample_pdf_with_side_watermark_and_alternating_page_numbers
):
    monkeypatch.setattr(
        documents,
        "resolve_attachment_path",
        lambda key, library="user": (
            sample_pdf_with_side_watermark_and_alternating_page_numbers
        ),
    )
    result = documents.read_document("ABCD1234", remove_headers_footers=True)
    assert "Downloaded from example.org" not in result["text"]
    assert "First body text" in result["text"]


def test_read_document_removes_page_numbers_despite_alternating_punctuation(
    monkeypatch, sample_pdf_with_side_watermark_and_alternating_page_numbers
):
    monkeypatch.setattr(
        documents,
        "resolve_attachment_path",
        lambda key, library="user": (
            sample_pdf_with_side_watermark_and_alternating_page_numbers
        ),
    )
    result = documents.read_document("ABCD1234", remove_headers_footers=True)
    for page_number in range(1, 5):
        assert f"{page_number} of 4" not in result["text"]
    assert "First body text" in result["text"]
    assert "Second body text" in result["text"]
    assert "Third body text" in result["text"]
    assert "Fourth body text" in result["text"]
