dev:
	docker compose up -d
test:
	uv run pytest
gate: test
	uv run ruff check
