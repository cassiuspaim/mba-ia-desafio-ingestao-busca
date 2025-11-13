db_up:
	docker compose up -d

db_erase:
	docker compose down -v

db_logs:
	docker compose logs -f postgres

db_access:
	docker exec -it postgres_rag psql -U postgres -d rag

ingest:
	python src/ingest.py

chat:
	python src/chat.py

unit_tests:
	pip install -r requirements.txt
	pip install pytest pytest-cov   # se ainda não tiver
	pytest --cov=src --cov-report=term-missing