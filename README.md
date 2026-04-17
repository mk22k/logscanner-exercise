# Log Scanner

`logscanner` is a command-line tool to analyze the content of Squid Proxy access log files.

This application parses proxy logs and calculates various metrics, outputting the results to a JSON file.

## Features

It calculates the following metrics from Squid Proxy access logs:

- **Most frequent IP** (`--mfip`)
- **Least frequent IP** (`--lfip`)
- **Events per second** (`--eps`)
- **Total amount of bytes exchanged** (`--bytes`)

If no specific flag is provided, all metrics are calculated by default.

## Installation

### Local Installation

You can install the application locally using `pip`. Requires Python 3.11+.

```bash
# Install for normal usage
make install

# Install with development dependencies (testing, linting)
make dev
```

### Docker

You can also build and run the application using Docker, without needing Python installed on your host system:

```bash
# Build the Docker image
make build-docker
```

## Usage

The application requires the log file location(s) and an output file path, followed by the options.

```bash
logscanner input_log_file [additional_input_files...] output_json_file [OPTIONS]
```

### Examples

**Process a single log file and calculate all metrics:**
```bash
logscanner access.log results.json
```

**Process multiple log files and only calculate the total amount of bytes exchanged:**
```bash
logscanner access1.log access2.log access3.log results.json --bytes
```

**Run via Docker:**
```bash
# Assuming log files are in the current directory, which gets mounted to /data
make run-docker ARGS="/data/access.log /data/results.json"
```

## Development

The project uses `pytest` for testing, `ruff` for linting, and `bandit` for security checks.

To run all checks (testing and linting):
```bash
make check
```

Individual commands:
- `make test` - Run the test suite using pytest.
- `make lint` - Run ruff and bandit checks.
