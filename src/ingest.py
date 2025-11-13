from __future__ import annotations
import os
from typing import List
from dotenv import load_dotenv
from pypdf import PdfReader
from search import embed_text, get_conn, ensure_schema, clear_document, insert_chunks

load_dotenv()
CHUNK_SIZE = 1000
OVERLAP = 150

def read_pdf_text(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"PDF não encontrado: {path}")
    reader = PdfReader(path)
    parts: List[str] = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts)

def split_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> list[str]:
    chunks: list[str] = []
    n = len(text); start = 0
    while start < n:
        end = min(start + chunk_size, n)
        chunks.append(text[start:end])
        if end == n: break
        start = max(0, end - overlap)
    return chunks

def main():
    pdf_path = os.getenv("PDF_PATH", "document.pdf")
    doc_id = os.path.basename(pdf_path)
    text = read_pdf_text(pdf_path)
    chunks = split_text(text, CHUNK_SIZE, OVERLAP)
    if chunks:
        sample = chunks[0]
    else:
        sample = ""
    dim = len(embed_text(sample))
    conn = get_conn()
    ensure_schema(conn, dim)
    clear_document(conn, doc_id)
    rows = [(i, c, embed_text(c)) for i, c in enumerate(chunks)]
    if rows:
        insert_chunks(conn, doc_id, rows)
        with conn.cursor() as cur:
            cur.execute("ANALYZE rag_chunks;");
            conn.commit()
    conn.close()
    print(f"✅ Ingestão concluída. Chunks: {len(chunks)}")

if __name__ == "__main__":
    main()
