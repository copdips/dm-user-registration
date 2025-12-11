.ONESHELL:
SHELL=/bin/bash
API_FOLDER=app

lint:
	uv run pre-commit autoupdate
	uv run pre-commit run --files $(git ls-files -m -o --exclude-standard)

test:
	uv run pytest

fast-test:
	uv run pytest --ignore=tests/unit/domain/value_objects/test_password.py --ignore=tests/unit/domain/entities/test_user.py
run:
	uv run uvicorn ${API_FOLDER}.main:app --reload

layout:
	git ls-files | grep -v '__init__\.py$$' | tree --fromfile
