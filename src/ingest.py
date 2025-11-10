# src/ingest.py
# PDF ingestion with character-level chunking using LangChain splitters.

import os
from typing import List, Optional

from dotenv import load_dotenv
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()


def read_pdf_text(path: Optional[str] = None) -> str:
    """
    Read and concatenate all text from a PDF.
    Priority of path resolution:
      1) explicit `path` argument
      2) environment variable PDF_PATH
    Raises:
      ValueError if no path is provided.
      FileNotFoundError if the resolved path does not exist.
    """
    resolved = path or os.getenv("PDF_PATH")
    if not resolved:
        raise ValueError("PDF_PATH is not set (env) and no explicit path was provided.")
    if not os.path.exists(resolved):
        raise FileNotFoundError(f"PDF file not found: {resolved}")

    reader = PdfReader(resolved)
    parts: List[str] = []
    for page in reader.pages:
        txt = page.extract_text() or ""
        txt = txt.strip()
        if txt:
            parts.append(txt)
    return "\n\n".join(parts)


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> List[str]:
    """
    Split text into character-based chunks with overlap using
    LangChain's RecursiveCharacterTextSplitter.
    - chunk_size: max characters per chunk
    - chunk_overlap: number of overlapping characters between adjacent chunks
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        # Try to respect paragraph and line boundaries first, then spaces, then raw chars
        separators=["\n\n", "\n", " ", ""],
    )
    return splitter.split_text(text)


def ingest_pdf(
    path: Optional[str] = None,
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> List[str]:
    """
    High-level ingestion: read PDF text and return character-level chunks.
    """
    text = read_pdf_text(path=path)
    return chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)


if __name__ == "__main__":
    # Simple CLI: read + chunk + report
    try:
        chunks = ingest_pdf()
        print(f"[ingest] Produced {len(chunks)} chunks; "
              f"avg len={sum(map(len, chunks))/max(len(chunks),1):.1f}")
    except Exception as e:
        print(f"[ingest] Error: {e}")
        raise
