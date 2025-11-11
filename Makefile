# 🧰 Makefile for mba-ia-desafio-ingestao-busca
# Simplifies Docker Compose management and ingestion commands

DOCKER_COMPOSE = docker compose
SERVICE_NAME = postgres
CONTAINER_NAME = postgres_rag
APP_SERVICE = app

# Centralized dependency installation commands
# These can be reused across different environments
INSTALL_DEPS = pip install -q --upgrade pip && \
	pip install -q -r requirements.txt -r requirements-dev.txt && \
	pip install -q pytest pytest-cov

# 🟢 Start all services (Postgres + pgVector extension + app)
up:
	@echo "🚀 Starting Docker Compose services..."
	$(DOCKER_COMPOSE) up -d
	@echo "✅ Services started."

# 🔴 Stop and remove all containers, networks, and volumes
down:
	@echo "🧹 Stopping and cleaning up containers..."
	$(DOCKER_COMPOSE) down
	@echo "✅ All containers stopped and removed."

# 🔄 Restart containers cleanly
restart: down up

# 🩺 Check PostgreSQL health status
check-health:
	@echo "🔍 Checking PostgreSQL container health..."
	@status=$$(docker inspect -f '{{.State.Health.Status}}' $(CONTAINER_NAME)); \
	if [ "$$status" = "healthy" ]; then \
		echo "✅ PostgreSQL is healthy!"; \
	else \
		echo "⚠️  PostgreSQL not healthy (status: $$status)"; \
		exit 1; \
	fi

# 🧾 View container logs (follow mode)
logs:
	@$(DOCKER_COMPOSE) logs -f $(SERVICE_NAME)

# 🧠 Connect to Postgres via psql inside the container
psql:
	@docker exec -it $(CONTAINER_NAME) psql -U postgres -d rag

# 🧼 Remove volumes and images (CAUTION)
clean:
	@echo "🧨 Removing all Docker volumes and images related to this project..."
	$(DOCKER_COMPOSE) down -v --rmi local
	@echo "✅ Cleanup complete."

# 📄 Run document ingestion process inside the app container
ingest:
	@echo "📥 Running document ingestion inside the app container..."
	$(DOCKER_COMPOSE) run --rm $(APP_SERVICE) python ingest.py
	@echo "✅ Ingestion completed."

# Install dependencies in current environment
# Can be used locally or inside containers
# Uses centralized INSTALL_DEPS variable
deps:
	@echo "📦 Installing Python dependencies..."
	@$(INSTALL_DEPS)
	@echo "✅ Dependencies installed."

# Install dependencies in local virtual environment
deps-local:
	@echo "📦 Setting up local virtual environment..."
	@if [ ! -d .venv ]; then \
		echo "📦 Creating virtual environment..."; \
		python3 -m venv .venv; \
	fi
	@echo "📥 Installing dependencies in .venv..."
	@. .venv/bin/activate && $(MAKE) deps
	@echo "✅ Local dependencies installed."

# Run tests inside the app container (preferred in Dockerized workflow)
# Uses centralized INSTALL_DEPS variable for dependency installation
test: deps-container
	@echo "🧪 Running tests inside the app container..."
	@docker run --rm -v $$(pwd):/app -w /app -e PYTHONPATH=/app/src mba-ia-app:test sh -c "$(INSTALL_DEPS) && pytest"
	@echo "✅ Tests finished."

# Install dependencies inside container (used by test task)
# Builds the container image with base dependencies from requirements.txt
deps-container:
	@echo "📦 Building container with base dependencies..."
	@docker build -t mba-ia-app:test -q . > /dev/null
	@echo "✅ Container ready (dev dependencies will be installed during test run)."

# Run tests locally (creates and activates .venv automatically if needed)
test-local: deps-local
	@echo "🧪 Running tests locally..."
	@. .venv/bin/activate && export PYTHONPATH=src && pytest
	@echo "✅ Tests finished."


