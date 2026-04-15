"""Test suite for the analyzer module."""

from typing import Iterator

from logscanner.analyzer import analyze_logs
from logscanner.parser import LogEntry


def _mock_entry(
    timestamp: float, client_ip: str, response_size: int
) -> LogEntry:
    """Create mock LogEntry objects for testing."""
    return LogEntry(
        timestamp=timestamp,
        header_size=5006,
        client_ip=client_ip,
        http_response="TCP_MISS/200",
        response_size=response_size,
        http_method="CONNECT",
        url="login.yahoo.com:443",
        username="badeyek",
        access_type_dst_ip="DIRECT/209.73.177.115",
        response_type="-",
    )


def test_analyze_logs_empty():
    """Test that an empty stream returns defaults properly without crashing."""
    empty_stream: Iterator[LogEntry] = iter([])
    results = analyze_logs(empty_stream)
    
    assert results["mfip"] is None
    assert results["lfip"] is None
    assert results["eps"] == 0.0
    assert results["bytes"] == 0


def test_analyze_logs_single_entry():
    """Test behavior with exactly one entry. EPS should be 0.0."""
    stream = iter([
        _mock_entry(1157689312.049, "10.105.21.199", 19763)
    ])
    results = analyze_logs(stream)
    
    assert results["mfip"] == "10.105.21.199"
    assert results["lfip"] == "10.105.21.199"
    assert results["eps"] == 0.0
    assert results["bytes"] == 19763


def test_analyze_logs_multiple_entries():
    """Test standard aggregation across multiple entries."""
    stream = iter([
        _mock_entry(10.0, "10.0.0.1", 100),
        _mock_entry(12.0, "10.0.0.2", 200),
        _mock_entry(14.0, "10.0.0.1", 300),  # Most freq IP (2 occurrences)
        _mock_entry(20.0, "10.0.0.3", 400),  # Least freq IP (tied)
    ])
    
    results = analyze_logs(stream)
    
    # 4 events across 10 seconds (20.0 - 10.0), EPS = 4 / 10 = 0.4
    assert results["mfip"] == "10.0.0.1"
    
    # In python 3.11+ Counter tied items are deterministic (retention order)
    # The least freq IPs are .2 and .3. most_common()[-1][0] gives the last
    assert results["lfip"] in ["10.0.0.2", "10.0.0.3"]
    assert results["eps"] == 4 / (20.0 - 10.0)
    assert results["bytes"] == 100 + 200 + 300 + 400


def test_analyze_logs_out_of_order_timestamps():
    """Test that EPS calculation works even if entries are out of order."""
    stream = iter([
        _mock_entry(50.0, "1.1.1.1", 1000),
        _mock_entry(10.0, "1.1.1.2", 1000),  # min_timestamp
        _mock_entry(30.0, "1.1.1.1", 1000),
        _mock_entry(100.0, "1.1.1.3", 1000), # max_timestamp
    ])
    
    results = analyze_logs(stream)
    
    # min=10.0, max=100.0. Duration = 90.0. Events = 4.
    assert results["eps"] == 4 / 90.0
    assert results["bytes"] == 4000
    assert results["mfip"] == "1.1.1.1"
