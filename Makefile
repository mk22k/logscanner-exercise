.PHONY: install dev test lint build-docker

# Run all checks (linting, security, and tests)
all: lint test

# Install the application for normal usage
install:
	pip install .

# Install the application with development dependencies
dev:
	pip install ".[dev]"

# Run tests
test:
	pytest

# Run linters and security checks
lint:
	ruff check .
	bandit -c pyproject.toml -r src/

# Build the Docker image
build-docker:
	docker build -t logscanner-app .

# Run the application via Docker using local files
# Usage: make run-docker ARGS="/data/access.log /data/results.json"
run-docker:
	docker run --rm -u $$(id -u):$$(id -g) -v "$$(pwd):/data" logscanner-app $(ARGS)
