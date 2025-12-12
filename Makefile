.ONESHELL:
SHELL=/bin/bash
API_FOLDER=app

install:
	@command -v uv >/dev/null 2>&1 || { echo "uv is required. Install instructions: https://docs.astral.sh/uv/getting-started/installation/"; exit 1; }
	uv sync
	pre-commit install

lint:
	uv run pre-commit autoupdate
	uv run pre-commit run --files $(git ls-files -m -o --exclude-standard)

test-unit:
	uv run pytest tests/unit

test-integration: start-docker-compose
	uv run pytest tests/integration

test: test-unit test-integration

fast-test: start-docker-compose
	uv run pytest --ignore=tests/unit/domain/value_objects/test_password.py --ignore=tests/unit/domain/entities/test_user.py

run: start-docker-compose
	uv run uvicorn ${API_FOLDER}.main:app --reload

layout:
	git ls-files | grep -v '__init__\.py$$' | tree --fromfile

start-docker-compose:
	docker compose build && docker compose up -d

stop-docker-compose:
	docker compose down

init-db: start-docker-compose
	PGPASSWORD=password psql -h localhost -U user -d registration -f scripts/init_db.sql

sql-shell: start-docker-compose
	PGPASSWORD=password psql -h localhost -U user -d registration
