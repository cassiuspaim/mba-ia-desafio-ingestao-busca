# ingest.py
# Minimal ingestion module that reads a PDF path from env (PDF_PATH),
# extracts text using PyPDF, and returns the concatenated text.

import os
from typing import Optional

from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv()


def ingest_pdf(path: Optional[str] = None) -> str:
    """
    Ingest a PDF by extracting text from all pages.

    Priority of path resolution:
    1) explicit `path` argument if provided;
    2) environment variable PDF_PATH.

    Returns:
        str: concatenated text from all pages separated by a blank line.

    Raises:
        ValueError: if PDF_PATH is not provided (via arg or env).
        FileNotFoundError: if the resolved path does not exist.
    """
    resolved = path or os.getenv("PDF_PATH")
    if not resolved:
        raise ValueError("PDF_PATH is not set (env) and no explicit path was provided.")

    if not os.path.exists(resolved):
        raise FileNotFoundError(f"PDF file not found: {resolved}")

    reader = PdfReader(resolved)
    texts = []
    for page in reader.pages:
        txt = page.extract_text() or ""
        txt = txt.strip()
        if txt:
            texts.append(txt)

    return "\n\n".join(texts)


if __name__ == "__main__":
    # Simple CLI behavior: run and print a short summary.
    try:
        content = ingest_pdf()
        print(f"[ingest] Extracted {len(content)} characters.")
    except Exception as e:
        print(f"[ingest] Error: {e}")
        raise
