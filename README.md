# Log Scanner

`logscanner` is a command-line tool designed to analyze the content of Squid Proxy access log files and output the results as plain-text JSON.

## Features

It calculates the following metrics from Squid Proxy access logs:

- **Most frequent IP** (`--mfip`)
- **Least frequent IP** (`--lfip`)
- **Events per second** (`--eps`)
- **Total amount of bytes exchanged** (`--bytes`)

Assumptions:
- The "most frequent IP" is the IP address that appears most frequently in the logs as the client IP (Field 3).
- The "least frequent IP" is the IP address that appears least frequently in the logs as the client IP (Field 3).

If multiple IP addresses have the same highest/lowest frequency, one of them will be returned.
- "Events per second" is calculated by dividing the total number of log entries by the time difference between the earliest and latest timestamps in the logs (Fields 1). If the time difference is zero (i.e., all events have the same timestamp), the EPS will be equal to the total number of events.
- "Total amount of bytes exchanged" is calculated by summing the response header size (Field 2) and response size (Field 5) for all log entries.

If no specific flag is provided, all metrics are calculated by default.

## Sample Data & Format

The application expects logs in the standard Squid Proxy access log format (10 fields total). 
**Sample data:** [SecRepo Squid Proxy Access Logs](https://www.secrepo.com/squid/access.log.gz)

**Expected fields:**
1. Timestamp (seconds since epoch)
2. Response header size (bytes)
3. Client IP address
4. HTTP response code
5. Response size (bytes)
6. HTTP request method
7. URL
8. Username
9. Type of access/destination IP address
10. Response type

## Assumptions & Design Decisions

- **Fault Tolerance:** If one input file in a list of files is missing or unreadable, the tool will skip it with a warning rather than crashing completely. Malformed lines in the logs are logged and skipped.
- **Extensibility:** The tool separates the parser, analyzer logic, and CLI into independent modules. This makes it trivial to extend the tool to handle different input log formats or output serializers (e.g., CSV, XML) in the future.
- **Bytes Exchanged:** The "total amount of bytes exchanged" metric is calculated by summing the **Response header size** (Field 2) and **Response size** (Field 5).

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
- `make lint`  Run ruff and bandit checks.
- `make test`  Run the test suite using pytest.
- `make test_cli`  Run tests specifically for the CLI interface.
- `make test_parser`  Run tests specifically for the log parser.
- `make test_analyzer`  Run tests specifically for the metrics calculations.
- `make clean`  Remove Python cache directories and test coverage reports.
- `make clean-docker`  Remove the built Docker image.
