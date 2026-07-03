.PHONY: up down restart logs test lint format migrate build shell clean ps

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

test:
	docker compose exec backend pytest

lint:
	docker compose exec backend ruff check .

format:
	docker compose exec backend ruff format .

migrate:
	docker compose exec backend alembic upgrade head

build:
	docker compose build

shell:
	docker compose exec backend bash

clean:
	docker compose down -v
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

ps:
	docker compose ps
