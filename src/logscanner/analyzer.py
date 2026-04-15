"""
Calculate required proxy statistics from parsed log entries.

Processes:
- Most frequent IP (mfip)
- Least frequent IP (lfip)
- Events per second (eps)
- Total amount of bytes exchanged (bytes)
"""

from collections import Counter
from typing import Iterator

from logscanner.parser import LogEntry

def analyze_logs(entries: Iterator[LogEntry]) -> dict[str, str | int | float | None]:
    """Analyze a stream of LogEntry objects to compute required statistics."""

    ip_counter = Counter()
    total_bytes = 0
    total_events = 0

    for entry in entries:
        ip_counter[entry.client_ip] += 1
        total_bytes += entry.response_size
        total_events += 1
        if entry.timestamp < min_timestamp:
            min_timestamp = entry.timestamp
        if entry.timestamp > max_timestamp:
            max_timestamp = entry.timestamp

    mfip = ip_counter.most_common()[0][0] if ip_counter else None
    lfip = ip_counter.most_common()[-1][0] if ip_counter else None
    if total_events > 0 and max_timestamp > min_timestamp:
        eps = total_events / (max_timestamp - min_timestamp)
    
    return {
        "mfip": mfip,
        "lfip": lfip,
        "eps": eps,
        "bytes": total_bytes
    }


"""
def analyze_logs(entries: Iterable[LogEntry]) -> dict[str, str | int | float]:
    
    #Consume a stream of LogEntry objects and compute all statistics in O(N).
    
    #Executes a single pass over the generator, maintaining running O(1) totals
    #and a bounded IP frequency counter.
    
    ip_counter: Counter[str] = Counter()
    total_bytes: int = 0
    total_events: int = 0
    min_timestamp: float = float('inf')
    max_timestamp: float = float('-inf')

    # The Hot Loop
    for entry in entries:
        total_bytes += entry.response_size
        ip_counter[entry.client_ip] += 1
        total_events += 1

        if entry.timestamp < min_timestamp:
            min_timestamp = entry.timestamp
            
        if entry.timestamp > max_timestamp:
            max_timestamp = entry.timestamp

    # Post-processing calculations
    eps = 0.0
    if total_events > 0 and max_timestamp > min_timestamp:
        eps = total_events / (max_timestamp - min_timestamp)

    sorted_ips = ip_counter.most_common()
    mfip = sorted_ips[0][0] if sorted_ips else "N/A"
    lfip = sorted_ips[-1][0] if sorted_ips else "N/A"

    return {
        "mfip": mfip,
        "lfip": lfip,
        "eps": round(eps, 4),
        "bytes": total_bytes
    }

"""