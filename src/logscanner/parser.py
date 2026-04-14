"""
Parses Squid Proxy access logs line by line.

Contains structures and functions for mapping raw string lines
to strongly typed `LogEntry` objects.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

logger = logging.getLogger(__name__)


# Define a dataclass to represent a log entry
# Frozen and slots for immutability and memory efficiency
@dataclass (frozen=True, slots=True)
class LogEntry:
    """
    Represents a single log entry from the Squid Proxy access log.

    The fields are based on the typical Squid log format, which
    includes:
    - timestamp: The time when the request was made as a float 
      representing seconds since epoch (e.g., 1157689324.156).
    - header_size: The size of the request header in bytes (e.g., 1372).
    - client_ip: The IP address of the client making the request
      (e.g., "10.105.21.199").
    - http_response: The HTTP response returned by the server
      (e.g., "TCP_MISS/200").
    - response_size: The size of the response in bytes. (e.g., 399).
    - http_method: The HTTP method used in the request (e.g., GET).
    - url: The URL requested by the client 
      (e.g., "https://www.google-analytics.com/__utm.gif").
    - username: The username associated with the request (if any). 
      (“e.g., badeyek").
    - access_type_dst_ip: The access type and destination IP
      (e.g., "DIRECT/66.102.9.147").
    - response_type: The type of response (e.g., "image/gif").
    
    """

    timestamp: float
    header_size: int
    client_ip: str
    http_response: str
    response_size: int
    http_method: str
    url: str
    username: str
    access_type_dst_ip: str
    response_type: str


# Parse a log line into a LogEntry dataclass instance
def parse_line(line: str) -> LogEntry:
    """
    Parse a single line of Squid Proxy log into a LogEntry object.
    
    Args:
        line: The raw text line from the log file.
        
    Returns:
        A structured LogEntry dataclass containing the fields.
    """
    parts = line.strip().split()
    
    # Basic validation to ensure we have the expected number of fields
    if len(parts) < 10:
        raise ValueError(f"Log line has insufficient fields: {line}")
    
    try:
        return LogEntry(
            timestamp=float(parts[0]),
            header_size=int(parts[1]),
            client_ip=parts[2],
            http_response=parts[3],
            response_size=int(parts[4]),
            http_method=parts[5],
            url=parts[6],
            username=parts[7],
            access_type_dst_ip=parts[8],
            response_type=parts[9]
        )
    except (ValueError, IndexError) as e:
        raise ValueError(f"Error parsing log line: {line}. Error: {e}")


def parse_logs(file_paths: list[Path]) -> Iterator[LogEntry]:
    """Read log files line by line, yielding parsed LogEntry objects.

    For now, it only handles plain text files.
    """
    for file_path in file_paths:
        try:
            with (
                open(file_path, 'rt', encoding='utf-8', errors='replace') as f
            ):
                for line_number, line in enumerate(f, start=1):
                    if not line.strip():
                        continue    # Skip empty lines

                    try:
                        entry = parse_line(line)
                        if entry is not None:
                            yield entry
                    except ValueError as e:
                        logger.warning(
                            f"File {file_path}, Line {line_number}: {e}. "
                            "Skipping."
                        )
                        continue
                    except Exception as e:
                        logger.error(
                            f"Unexpected error parsing line {line_number} "
                            f"in file {file_path}: {e}"
                        )
                        continue

        except OSError as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            continue
        except Exception as e:
            logger.error(
                f"Unexpected error while handling file {file_path}: {e}"
            )
            continue