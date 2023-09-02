.PHONY: docs

run:
	poetry run python sem.py

docs:
	poetry run mkdocs build
	poetry run mkdocs serve
