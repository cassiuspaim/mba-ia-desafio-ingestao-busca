# tests/test_ingest.py
# Tests for PDF ingestion using environment variable PDF_PATH.
# We mock PdfReader to avoid relying on real PDF files.

import pytest
import ingest  # the module under test


# ============================================================================
# Fixtures and Helpers
# ============================================================================

class FakePage:
    """Mock page object for PdfReader."""
    def __init__(self, text):
        self._text = text

    def extract_text(self):
        return self._text


class FakeReader:
    """Mock PdfReader with configurable pages."""
    def __init__(self, path, pages_content):
        self.path = path
        self.pages = [FakePage(text) for text in pages_content]

    def __init__(self, path):
        # This will be overridden by the factory
        pass


def create_fake_reader(pages_content):
    """Factory to create a FakeReader with specific page content."""
    class CustomFakeReader:
        def __init__(self, path):
            self.path = path
            self.pages = [FakePage(text) for text in pages_content]
    return CustomFakeReader


# ============================================================================
# Validation Tests (Input Errors)
# ============================================================================

@pytest.mark.parametrize("path_value,env_value", [
    (None, None),           # Both missing
    (None, ""),             # Env is empty string
    ("", None),             # Arg is empty string
    ("", ""),               # Both empty strings
])
def test_raises_value_error_when_path_missing(monkeypatch, path_value, env_value):
    """Should raise ValueError when PDF_PATH is not provided via argument or environment."""
    if env_value is None:
        monkeypatch.delenv("PDF_PATH", raising=False)
    else:
        monkeypatch.setenv("PDF_PATH", env_value)
    
    with pytest.raises(ValueError, match="PDF_PATH is not set"):
        ingest.ingest_pdf(path_value)


@pytest.mark.parametrize("missing_filename", [
    "nonexistent.pdf",
    "missing/path/file.pdf",
    "../outside/file.pdf",
])
def test_raises_file_not_found_when_file_missing(monkeypatch, tmp_path, missing_filename):
    """Should raise FileNotFoundError when the specified path does not exist."""
    fake_path = tmp_path / missing_filename
    monkeypatch.setenv("PDF_PATH", str(fake_path))
    
    with pytest.raises(FileNotFoundError, match="PDF file not found"):
        ingest.ingest_pdf()


# ============================================================================
# PDF Extraction Tests (Table-Driven / Parametrized)
# ============================================================================

@pytest.mark.parametrize("pages_content,expected_output,test_description", [
    # Basic cases
    (["Hello", "World"], "Hello\n\nWorld", "two_pages_with_content"),
    (["Single page"], "Single page", "single_page"),
    (["First", "Second", "Third"], "First\n\nSecond\n\nThird", "three_pages"),
    
    # Empty page handling
    (["Hello", "", "World"], "Hello\n\nWorld", "empty_page_in_middle"),
    (["", "Content", ""], "Content", "empty_pages_at_edges"),
    (["", "", ""], "", "all_pages_empty"),
    ([], "", "no_pages"),
    
    # Whitespace handling
    (["  Hello  ", "  World  "], "Hello\n\nWorld", "pages_with_leading_trailing_spaces"),
    (["   ", "Content", "   "], "Content", "pages_with_only_spaces"),
    (["\n\nHello\n\n", "\n\nWorld\n\n"], "Hello\n\nWorld", "pages_with_newlines"),
    (["\t\tTab\t\t"], "Tab", "pages_with_tabs"),
    
    # Special characters and formatting
    (["Hello!", "World?"], "Hello!\n\nWorld?", "pages_with_punctuation"),
    (["Line 1\nLine 2", "Line 3\nLine 4"], "Line 1\nLine 2\n\nLine 3\nLine 4", "pages_with_internal_newlines"),
    (["", "Test", "", "Data", ""], "Test\n\nData", "multiple_empty_pages_scattered"),
    
    # Edge cases
    (["A"], "A", "single_character"),
    (["", "A", ""], "A", "single_character_with_empty_pages"),
    (["Multiple\n\nBlank\n\n\nLines"], "Multiple\n\nBlank\n\n\nLines", "page_with_multiple_blank_lines"),
])
def test_pdf_text_extraction_scenarios(monkeypatch, tmp_path, pages_content, expected_output, test_description):
    """
    Table-driven test for various PDF text extraction scenarios.
    Tests different combinations of page content, empty pages, and whitespace handling.
    """
    # Arrange: Create fake PDF file
    pdf_path = tmp_path / f"test_{test_description}.pdf"
    pdf_path.write_bytes(b"%PDF-FAKE")
    monkeypatch.setenv("PDF_PATH", str(pdf_path))
    
    # Mock PdfReader with the specified pages
    monkeypatch.setattr(ingest, "PdfReader", create_fake_reader(pages_content))
    
    # Act
    result = ingest.ingest_pdf()
    
    # Assert
    assert result == expected_output, f"Failed for scenario: {test_description}"


# ============================================================================
# Path Resolution Tests
# ============================================================================

def test_explicit_path_argument_takes_precedence_over_env(monkeypatch, tmp_path):
    """Should use explicit path argument even when PDF_PATH env is set."""
    # Create two different PDF files
    env_pdf = tmp_path / "env.pdf"
    arg_pdf = tmp_path / "arg.pdf"
    env_pdf.write_bytes(b"%PDF-ENV")
    arg_pdf.write_bytes(b"%PDF-ARG")
    
    monkeypatch.setenv("PDF_PATH", str(env_pdf))
    
    # Mock PdfReader to track which path was used
    pages_content = ["Content from argument path"]
    
    class PathTrackingReader:
        def __init__(self, path):
            self.path = path
            # Verify the correct path was used
            assert str(path) == str(arg_pdf), f"Expected {arg_pdf}, got {path}"
            self.pages = [FakePage(text) for text in pages_content]
    
    monkeypatch.setattr(ingest, "PdfReader", PathTrackingReader)
    
    # Act
    result = ingest.ingest_pdf(str(arg_pdf))
    
    # Assert
    assert result == "Content from argument path"


def test_uses_env_variable_when_no_explicit_path(monkeypatch, tmp_path):
    """Should use PDF_PATH environment variable when no explicit path is provided."""
    pdf_path = tmp_path / "from_env.pdf"
    pdf_path.write_bytes(b"%PDF-ENV")
    
    monkeypatch.setenv("PDF_PATH", str(pdf_path))
    
    # Mock PdfReader
    pages_content = ["Content from environment"]
    
    class PathTrackingReader:
        def __init__(self, path):
            assert str(path) == str(pdf_path), f"Expected {pdf_path}, got {path}"
            self.pages = [FakePage(text) for text in pages_content]
    
    monkeypatch.setattr(ingest, "PdfReader", PathTrackingReader)
    
    # Act
    result = ingest.ingest_pdf()
    
    # Assert
    assert result == "Content from environment"
