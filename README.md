# RAG – Ingestão, Busca Vetorial e Chat com OpenAI/Gemini

Este projeto implementa um pipeline completo para:

- Ingestão de documentos PDF  
- Geração de embeddings (OpenAI ou Gemini)  
- Armazenamento vetorial com PostgreSQL + pgVector  
- Chat via linha de comando utilizando RAG (Retrieval Augmented Generation)

O sistema responde **apenas com base no PDF ingerido**, sem conhecimento externo.

---

# 🧩 1. Configurar `.env`

Crie um arquivo `.env` na raiz do projeto.  
Use o `.env.example` como referência.

Preencha:

```
OPENAI_API_KEY=sua_chave
GEMINI_API_KEY=sua_chave
AI_PROVIDER=openai  # ou gemini
```

---

# 🐘 2. Subir o banco PostgreSQL + pgVector

```
docker compose up -d
```

---

# 📥 3. Rodar a ingestão do PDF

```
python src/ingest.py
```

---

# 💬 4. Rodar o chat

```
python src/chat.py
```

---

# 🔄 5. Resetar o banco (obrigatório ao trocar provedor)

Se você mudar `AI_PROVIDER`, precisa recriar o banco:

```
docker compose down -v
docker compose up -d
python src/ingest.py
```

---

# 📂 Estrutura do Projeto

```
.
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── document.pdf
└── src/
    ├── ingest.py
    ├── search.py
    └── chat.py
```

---

# 🛠 Comandos úteis

| Ação | Comando |
|------|---------|
| Parar containers | docker compose down |
| Parar + apagar volume | docker compose down -v |
| Ver logs | docker compose logs -f postgres |
| Acessar banco | docker exec -it postgres_rag psql -U postgres -d rag |

---

# 🧪 Fluxo completo

```
cp .env.example .env
nano .env
docker compose up -d
python src/ingest.py
python src/chat.py
```

---

# 📌 Observações

- O chat só responde com base no PDF.
- Sempre resete o banco ao trocar o provedor de IA.
