# 🧰 Makefile for mba-ia-desafio-ingestao-busca
# Simplifies Docker Compose management and health checking

DOCKER_COMPOSE = docker compose
SERVICE_NAME = postgres
CONTAINER_NAME = postgres_rag

# 🟢 Start all services (Postgres + pgVector extension)
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
