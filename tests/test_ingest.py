# tests/test_ingest.py
# Tests for PDF ingestion and character-level chunking with overlap.

import os
import pytest
import ingest


def test_chunk_text_basic_sizes():
    text = "A" * 2400  # 2400 chars
    chunks = ingest.chunk_text(text, chunk_size=1000, chunk_overlap=150)
    # With RecursiveCharacterTextSplitter:
    # - Chunk 0: pos 0 to 1000 (1000 chars)
    # - Chunk 1: pos (1000-150)=850 to 850+1000=1850 (1000 chars)
    # - Chunk 2: pos (1850-150)=1700 to 2400 (700 chars)
    assert len(chunks) == 3
    assert len(chunks[0]) == 1000
    assert len(chunks[1]) == 1000
    # last chunk: 2400 - 1700 = 700 chars
    assert len(chunks[2]) == 700

    # Overlap check: last 150 chars of chunk[i] == first 150 chars of chunk[i+1]
    assert chunks[0][-150:] == chunks[1][:150]
    assert chunks[1][-150:] == chunks[2][:150]


def test_ingest_pdf_returns_chunks_with_env_path(monkeypatch, tmp_path):
    # Arrange an env PDF_PATH and a fake PdfReader
    pdf_path = tmp_path / "doc.pdf"
    pdf_path.write_bytes(b"%PDF-FAKE")

    monkeypatch.setenv("PDF_PATH", str(pdf_path))

    class FakePage:
        def __init__(self, text): self._text = text
        def extract_text(self): return self._text

    class FakeReader:
        def __init__(self, path):
            assert str(path) == str(pdf_path)
            self.pages = [FakePage("Hello " * 120), FakePage("World " * 120)]
    monkeypatch.setattr(ingest, "PdfReader", FakeReader)

    # Act
    chunks = ingest.ingest_pdf(chunk_size=1000, chunk_overlap=150)

    # Assert
    assert isinstance(chunks, list) and len(chunks) >= 1
    assert all(isinstance(c, str) for c in chunks)
    # sanity: every chunk length <= 1000
    assert all(len(c) <= 1000 for c in chunks)


def test_read_pdf_text_raises_value_error_when_path_missing(monkeypatch):
    """Should raise ValueError when PDF_PATH is not set and no path argument provided."""
    monkeypatch.delenv("PDF_PATH", raising=False)
    with pytest.raises(ValueError, match="PDF_PATH is not set"):
        ingest.read_pdf_text()


def test_read_pdf_text_raises_file_not_found_when_file_missing(monkeypatch, tmp_path):
    """Should raise FileNotFoundError when the specified path does not exist."""
    fake_path = tmp_path / "nonexistent.pdf"
    monkeypatch.setenv("PDF_PATH", str(fake_path))
    with pytest.raises(FileNotFoundError, match="PDF file not found"):
        ingest.read_pdf_text()
