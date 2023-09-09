.PHONY: docs

docs:
	poetry run mkdocs build
	poetry run mkdocs serve
