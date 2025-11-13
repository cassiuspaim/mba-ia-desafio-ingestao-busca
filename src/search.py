from __future__ import annotations
import os
from typing import Iterable, List, Tuple

from dotenv import load_dotenv
import psycopg
from pgvector.psycopg import register_vector

# --- OpenAI ---
from openai import OpenAI as _OpenAIClient

# --- Gemini ---
import google.generativeai as genai

# EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
# CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-5-nano")

load_dotenv()

# ========= Provider selection =========
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai").lower()

# OpenAI defaults (override via env se quiser)
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-5-nano")

# Gemini defaults
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "models/embedding-001")
GEMINI_CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-2.5-flash-lite")


# ========= OpenAI helpers =========
def _openai_client() -> _OpenAIClient:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY não encontrado (.env).")
    
    return _OpenAIClient(api_key=api_key)

def _openai_embed(text: str) -> List[float]:
    client = _openai_client()
    resp = client.embeddings.create(
        model=OPENAI_EMBEDDING_MODEL,
        input=text)
    
    return resp.data[0].embedding

def _openai_chat(messages: list[dict]) -> str:
    client = _openai_client()
    resp = client.chat.completions.create(
        model=OPENAI_CHAT_MODEL,
        messages=messages)
    
    return resp.choices[0].message.content

# ========= Gemini helpers =========
def _gemini_configure() -> None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY não encontrado (.env).")
    
    genai.configure(api_key=api_key)

def _gemini_embed(text: str) -> List[float]:
    _gemini_configure()
    out = genai.embed_content(
        model=GEMINI_EMBEDDING_MODEL,
        content=text,
        task_type="retrieval_document",
    )

    return list(out["embedding"])

def _gemini_chat(messages: list[dict]) -> str:
    _gemini_configure()

    parts: list[str] = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        parts.append(f"{role.upper()}:\n{content}")

    prompt = "\n\n".join(parts)

    model = genai.GenerativeModel(GEMINI_CHAT_MODEL)
    resp = model.generate_content(prompt)

    return getattr(resp, "text", "") or ""

# ========= Facade usado pelo projeto =========
def embed_text(text: str) -> List[float]:
    if AI_PROVIDER == "gemini":
        return _gemini_embed(text)
    # default: openai
    return _openai_embed(text)

def chat_completion(messages: list[dict]) -> str:
    if AI_PROVIDER == "gemini":
        return _gemini_chat(messages)
    # default: openai
    return _openai_chat(messages)

# ========= Postgres / pgvector =========
def get_conn() -> psycopg.Connection:
    dsn = {
        "host": os.getenv("PG_HOST","localhost"),
        "port": int(os.getenv("PG_PORT","5432")),
        "dbname": os.getenv("PG_DATABASE","rag"),
        "user": os.getenv("PG_USER","postgres"),
        "password": os.getenv("PG_PASSWORD","postgres"),
    }
    conn = psycopg.connect(**dsn)
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    register_vector(conn)
    return conn

import textwrap

def ensure_schema(conn: psycopg.Connection, dim: int) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS rag_chunks (
            id BIGSERIAL PRIMARY KEY,
            doc_id TEXT NOT NULL,
            chunk_index INT NOT NULL,
            content TEXT NOT NULL,
            embedding vector({dim})
        );
        """
    )
    conn.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE c.relname = 'idx_rag_chunks_embedding' AND n.nspname = 'public'
            ) THEN
                CREATE INDEX idx_rag_chunks_embedding
                ON rag_chunks USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);
            END IF;
        END$$;
        """
    )
    conn.commit()

def clear_document(conn: psycopg.Connection, doc_id: str) -> None:
    conn.execute("DELETE FROM rag_chunks WHERE doc_id = %s;", (doc_id,))
    conn.commit()

def insert_chunks(
    conn: psycopg.Connection,
    doc_id: str,
    rows: Iterable[Tuple[int, str, List[float]]]
) -> None:
    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO rag_chunks (doc_id, chunk_index, content, embedding)
            VALUES (%s,%s,%s,%s)
            """, 
            [(doc_id, i, content, vec) for i, content, vec in rows]),
    conn.commit()

def search_topk(conn: psycopg.Connection, query_vec: List[float], k: int = 10):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT content, chunk_index, (embedding <-> %s::vector) AS distance
            FROM rag_chunks
            ORDER BY embedding <-> %s::vector
            LIMIT %s;
            """, 
            (query_vec, query_vec, k),
        )
        return cur.fetchall()
