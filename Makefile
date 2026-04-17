.PHONY: check install dev test lint build-docker clean clean-docker

# Run all checks (linting, security, and tests)
check: lint test

# Install the application for normal usage
install:
	pip install .

# Install the application with development dependencies
dev:
	pip install ".[dev]"

# Run tests with coverage reporting
test:
	pytest --cov=src/logscanner --cov-report=term-missing

# Run only CLI tests
test_cli:
	pytest tests/test_cli.py

# Run only parser tests
test_parser:
	pytest tests/test_parser.py

# Run only analyzer tests
test_analyzer:
	pytest tests/test_analyzer.py

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
# Remove Python cache directories and build artifacts
clean:
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +

# Remove the built Docker image
clean-docker:
	docker rmi logscanner-app || true