# 🐍 Python Environment Setup (macOS/Linux) for `mba-ia-desafio-ingestao-busca`

This guide standardizes how to install and use **Python 3.11.9** with **pyenv**, create an isolated virtual environment, install project dependencies from `requirements.txt`, and manage PostgreSQL + pgVector using the included **Makefile**.

It reflects the exact steps used by the first developer to get a clean, reproducible setup.

---

## Table of Contents

- [Why pyenv + venv](#why-pyenv--venv)
- [Prerequisites](#prerequisites)
- [Install pyenv with Homebrew](#install-pyenv-with-homebrew)
- [Install Python 3.11.9](#install-python-3119)
- [Set the Project Python Version](#set-the-project-python-version)
- [Verify the Setup](#verify-the-setup)
- [Optional: pyenv-doctor](#optional-pyenv-doctor)
- [Create and Use a Virtual Environment](#create-and-use-a-virtual-environment)
- [Install Dependencies](#install-dependencies)
- [Manage PostgreSQL + pgVector (Makefile)](#manage-postgresql--pgvector-makefile)
- [Environment Variables](#environment-variables)
- [Quick Sanity Checks](#quick-sanity-checks)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)

---

## Why pyenv + venv

- **pyenv** ensures everyone uses the **same Python version** (`3.11.9` here), avoiding system Python conflicts.
- **venv** isolates **project dependencies** so they don’t leak into your global environment.

---

## Prerequisites

- **Homebrew** (macOS/Linux):
  ```bash
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  exec "$SHELL"
  ```
- **Xcode Command Line Tools** (macOS):
  ```bash
  xcode-select --install
  ```

---

## Install pyenv with Homebrew

```bash
brew update
brew install pyenv
```

Add pyenv init lines to your shell profile.

**Zsh (default on macOS):**
```bash
echo -e '\n# Pyenv setup' >> ~/.zshrc
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
exec "$SHELL"
```

**Bash:**
```bash
echo -e '\n# Pyenv setup' >> ~/.bashrc
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
exec "$SHELL"
```

> **Why this matters:** Without these lines, your shell won’t see `pyenv`, and the system Python may take precedence.

---

## Install Python 3.11.9

```bash
pyenv install 3.11.9
```

> This compiles Python from source and can take **3–10 minutes** depending on your machine.

---

## Set the Project Python Version

From the project root (example path below—adjust to your clone location):
```bash
cd ~/repositories/mba-ia-desafio-ingestao-busca
pyenv local 3.11.9
```

This creates a `.python-version` in the repo so the correct Python is auto-selected when you enter the directory.

---

## Verify the Setup

```bash
python --version
which python
pyenv versions
```

**Expected:**
- `Python 3.11.9`
- `which python` points to `~/.pyenv/shims/python`
- An asterisk `*` near `3.11.9` in `pyenv versions`

---

## Optional: pyenv-doctor

Diagnose your environment to ensure Python builds cleanly:

```bash
mkdir -p "$(pyenv root)/plugins"
git clone https://github.com/pyenv/pyenv-doctor.git "$(pyenv root)/plugins/pyenv-doctor"
pyenv doctor
```

**Success message:**
```
Congratulations! You are ready to build pythons!
```

---

## Create and Use a Virtual Environment

Create a per-project virtual environment:

```bash
cd ~/repositories/mba-ia-desafio-ingestao-busca
python -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` in your prompt. To deactivate later:
```bash
deactivate
```

---

## Install Dependencies

With the virtual environment **active**:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- LangChain stack (`langchain`, `langchain-community`, `langchain-postgres`, etc.)
- OpenAI and Google GenAI clients
- PostgreSQL drivers (`psycopg`, `psycopg2-binary`, `asyncpg`)
- `pgvector` Python client
- Common utilities (`pydantic`, `tiktoken`, `SQLAlchemy`, etc.)

> **Note:** The project already provides a `requirements.txt`. Always prefer using it to ensure everyone has the same dependency set.

---

## Manage PostgreSQL + pgVector (Makefile)

This project provides a **Makefile** that simplifies managing Docker Compose services for PostgreSQL and pgVector.

### 🟢 Start all containers
```bash
make up
```
Starts PostgreSQL and the bootstrap container that creates the `vector` extension.

### 🩺 Check database health
```bash
make check-health
```
Checks if the PostgreSQL container is `healthy`.

### 🔴 Stop and remove containers
```bash
make down
```
Stops and removes all running containers.

### 🔄 Restart containers
```bash
make restart
```
Restarts all containers cleanly.

### 🧠 Connect to the database (psql shell)
```bash
make psql
```
Opens an interactive PostgreSQL shell inside the container.

### 🧾 View logs in real time
```bash
make logs
```
Streams logs from the PostgreSQL service.

### 📄 Run document ingestion
```bash
make ingest
```
Runs the document ingestion process (`ingest.py`) inside the application container.
The container is created temporarily and removed automatically after execution.

### 🧼 Remove all containers, volumes, and images
```bash
make clean
```

Removes containers, volumes, and local images created by the project.
> The Makefile internally calls Docker Compose commands to manage services defined in `docker-compose.yml` and provides an easy way to execute ingestion tasks.

---

## Environment Variables

Create a local `.env` in the project root if your app expects API keys or database URLs:

```dotenv
# Database (for psycopg/SQLAlchemy/LangChain Postgres)
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag

# If using async drivers:
# ASYNC_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/rag

# OpenAI (if you use OpenAI models)
OPENAI_API_KEY=sk-...

# Google Generative AI (if you use Gemini via langchain-google-genai)
GOOGLE_API_KEY=...
```

> Match the variable names to what your code reads (e.g., via `python-dotenv` or `pydantic-settings`).

---

## Quick Sanity Checks

**1) Python / packages:**
```bash
python -c "import sys; print(sys.version)"
python -c "import langchain; print('LangChain OK')"
python -c "import psycopg; print('psycopg OK')"
python -c "import pgvector; print('pgvector OK')"
```

**2) Database connectivity (sync, psycopg):**
```bash
python - <<'PY'
import psycopg
conn = psycopg.connect("dbname=rag user=postgres password=postgres host=localhost port=5432")
with conn.cursor() as cur:
    cur.execute("SELECT version()")
    print(cur.fetchone())
    cur.execute("SELECT extname FROM pg_extension WHERE extname='vector'")
    print("pgvector installed?", bool(cur.fetchone()))
conn.close()
PY
```

You should see a Postgres version and `pgvector installed? True`.

---

## Troubleshooting

- **`python` still points to system path** (`/usr/bin/python`):
  - Ensure the pyenv lines are in your shell profile (`~/.zshrc` or `~/.bashrc`)
  - Run `exec "$SHELL"` or open a new terminal
  - Check `which python` → should be `~/.pyenv/shims/python`

- **`pyenv install` takes long / fails:**
  - Install Xcode CLTs: `xcode-select --install` (macOS)
  - Ensure you have `brew` and that `brew doctor` is clean
  - Re-run `pyenv install 3.11.9`

- **Cannot connect to Postgres:**
  - `make check-health` → ensure Postgres is healthy
  - Confirm port 5432 isn’t in use
  - Verify credentials `postgres:postgres@localhost:5432/rag`
  - If using another Postgres, ensure `CREATE EXTENSION vector;`

- **`pgvector` missing in DB:**
  - Run:
    ```bash
    make psql
    ```
    then inside the `psql` shell:
    ```sql
    CREATE EXTENSION IF NOT EXISTS vector;
    ```

---

## FAQ

**Q: Why Python 3.11.9?**  
A: It’s a stable version compatible with LangChain and the listed dependencies in `requirements.txt`, and used by this project by default.

**Q: Do I need to run pyenv commands in the project folder?**  
A: Only `pyenv local 3.11.9` must be run from the project folder (it writes `.python-version`). Other `pyenv` commands can run anywhere.

**Q: Do I need Docker?**  
A: Recommended. The repo provides a ready-to-run Postgres + pgVector image, managed easily through the Makefile.

---

**You’re set.**  
From here, activate the venv, ensure Postgres is healthy (`make check-health`), and proceed with ingestion and semantic search development.
