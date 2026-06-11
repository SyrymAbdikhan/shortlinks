.PHONY: run test lint format

run:
	docker-compose up --build

test:
	uv run pytest tests/ -v

lint:
	uv run ruff check app/ tests/
	uv run ruff format --check app/ tests/

format:
	uv run ruff format app/ tests/
	uv run ruff check --fix app/ tests/
