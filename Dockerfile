# Define the base image
ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim as base

# Create a non-root user and group
RUN groupadd -r logscanner && useradd -r -g logscanner logscanner

WORKDIR /app

# Copy dependency files and project configuration
COPY pyproject.toml README.md ./

# Copy application code
COPY src/ ./src/

# Install the application
RUN pip install --no-cache-dir .

# Change ownership of the working directory to the non-root user
RUN chown -R logscanner:logscanner /app

# Switch to the non-root user
USER logscanner

# Set the entrypoint to the command defined in pyproject.toml
ENTRYPOINT ["logscanner"]