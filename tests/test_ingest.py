# tests/test_ingest.py
# Tests for PDF ingestion using environment variable PDF_PATH.
# We mock PdfReader to avoid relying on real PDF files.

import os
import builtins
import types
import pytest

import ingest  # the module under test


def test_raises_when_pdf_path_unset(monkeypatch):
    """Should raise ValueError when PDF_PATH is missing."""
    monkeypatch.delenv("PDF_PATH", raising=False)
    with pytest.raises(ValueError):
        ingest.ingest_pdf()


def test_raises_when_file_missing(monkeypatch, tmp_path):
    """Should raise FileNotFoundError when path does not exist."""
    fake_path = tmp_path / "missing.pdf"
    monkeypatch.setenv("PDF_PATH", str(fake_path))
    with pytest.raises(FileNotFoundError):
        ingest.ingest_pdf()


def test_reads_pdf_via_pypdf_and_concatenates(monkeypatch, tmp_path):
    """
    Should call PdfReader with the env path and concatenate page texts
    with blank lines between pages, skipping empty pages.
    """
    # Arrange: env var points to some path (existence will be checked; create empty file)
    pdf_path = tmp_path / "doc.pdf"
    pdf_path.write_bytes(b"%PDF-FAKE")  # content not used; we mock PdfReader

    monkeypatch.setenv("PDF_PATH", str(pdf_path))

    # Build a fake PdfReader and fake pages with extract_text
    class FakePage:
        def __init__(self, text):
            self._text = text

        def extract_text(self):
            return self._text

    class FakeReader:
        def __init__(self, path):
            # Assert the path passed into PdfReader is the env var
            assert str(path) == str(pdf_path)
            self.pages = [FakePage("Hello"), FakePage(""), FakePage("World")]

    # Patch PdfReader in the ingest module's namespace
    monkeypatch.setattr(ingest, "PdfReader", FakeReader)

    # Act
    out = ingest.ingest_pdf()

    # Assert
    assert out == "Hello\n\nWorld"
