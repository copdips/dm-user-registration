.ONESHELL:
SHELL=/bin/bash
API_FOLDER=app

lint:
	uv run pre-commit autoupdate
	uv run pre-commit run --files $(git ls-files -m -o --exclude-standard)

test:
	uv run pytest
run:
	uv run uvicorn ${API_FOLDER}.main:app --reload

layout:
	git ls-files | grep -v '__init__\.py$$' | tree --fromfile
