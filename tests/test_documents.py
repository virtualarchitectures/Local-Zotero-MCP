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
