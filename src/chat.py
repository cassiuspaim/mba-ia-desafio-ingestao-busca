from __future__ import annotations
import traceback, readline
from search import embed_text, search_topk, get_conn, chat_completion

PROMPT_TEMPLATE = (
    "CONTEXTO:\n{context}\n\n"
    "REGRAS:\n"
    "- Responda somente com base no CONTEXTO.\n"
    "- Se a informação não estiver explicitamente no CONTEXTO, responda:\n"
    "  \"Não tenho informações necessárias para responder sua pergunta.\"\n"
    "- Nunca invente ou use conhecimento externo.\n"
    "- Nunca produza opiniões ou interpretações além do que está escrito.\n\n"
    "EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:\n"
    "Pergunta: \"Qual é a capital da França?\"\n"
    "Resposta: \"Não tenho informações necessárias para responder sua pergunta.\"\n\n"
    "Pergunta: \"Quantos clientes temos em 2024?\"\n"
    "Resposta: \"Não tenho informações necessárias para responder sua pergunta.\"\n\n"
    "Pergunta: \"Você acha isso bom ou ruim?\"\n"
    "Resposta: \"Não tenho informações necessárias para responder sua pergunta.\"\n\n"
    "PERGUNTA DO USUÁRIO:\n{question}\n\n"
    "RESPONDA A \"PERGUNTA DO USUÁRIO\""
)

def build_prompt(context_chunks: list[str], question: str) -> str:
    context = "\n\n".join(context_chunks)
    return PROMPT_TEMPLATE.format(context=context, question=question)

def main():
    try:
        conn = get_conn()
    except Exception:
        print("❌ Falha ao conectar no Postgres:"); traceback.print_exc(); return
    print("💬 CLI pronto. Digite sua pergunta (Ctrl+C para sair).\n")
    try:
        while True:
            try:
                q = input("> ").strip()
                if not q: continue
                try:
                    q_vec = embed_text(q)
                except Exception:
                    print("❌ Falha ao gerar embedding da pergunta:"); traceback.print_exc(); continue
                try:
                    rows = search_topk(conn, q_vec, k=10)
                except Exception:
                    print("❌ Falha ao consultar o banco (busca vetorial):"); traceback.print_exc(); continue
                context_chunks = [r[0] for r in rows]
                prompt = build_prompt(context_chunks, q)
                try:
                    messages = [
                        {"role": "system", "content": "Você segue estritamente o contexto fornecido."},
                        {"role": "user", "content": prompt},
                    ]
                    answer = chat_completion(messages)
                except Exception:
                    print("❌ Falha ao chamar a LLM:"); traceback.print_exc(); continue
                print("\n🧠 Resposta:\n" + (answer or "(vazio)") + "\n")
            except (EOFError, KeyboardInterrupt):
                print("\n👋 Encerrado."); break
    finally:
        try: conn.close()
        except Exception: pass

if __name__ == "__main__":
    main()
