from pathlib import Path

import pytest

from logscanner.parser import LogEntry, parse_line, parse_logs

# Sample valid line from Squid log
VALID_LOG_LINE = (
    "1157689312.049   5006 10.105.21.199 TCP_MISS/200 19763 CONNECT "
    "login.yahoo.com:443 badeyek DIRECT/209.73.177.115 -"
)

def test_parse_line_valid():
    """Test parsing a valid log line correctly maps to a LogEntry object."""
    entry = parse_line(VALID_LOG_LINE)
    
    assert isinstance(entry, LogEntry)
    assert entry.timestamp == 1157689312.049
    assert entry.header_size == 5006
    assert entry.client_ip == "10.105.21.199"
    assert entry.http_response == "TCP_MISS/200"
    assert entry.response_size == 19763
    assert entry.http_method == "CONNECT"
    assert entry.url == "login.yahoo.com:443"
    assert entry.username == "badeyek"
    assert entry.access_type_dst_ip == "DIRECT/209.73.177.115"
    assert entry.response_type == "-"

def test_parse_line_invalid_missing_fields():
    """Test parse_line raises ValueError when there are not enough fields."""
    invalid_line = "1157689312.049 5006 10.105.21.199"
    with pytest.raises(ValueError, match="Log line has insufficient fields"):
        parse_line(invalid_line)

def test_parse_line_invalid_types():
    """Test parse_line raises ValueError when numeric fields are invalid."""
    # timestamp is 'not_a_float' instead of a float
    invalid_line = (
        "not_a_float   5006 10.105.21.199 TCP_MISS/200 19763 "
        "CONNECT login.yahoo.com:443 badeyek DIRECT/209.73.177.115 -"
    )
    with pytest.raises(ValueError, match="Error parsing log line"):
        parse_line(invalid_line)

def test_parse_logs_generator(tmp_path: Path, caplog):
    """Test parse_logs yields parsed entries and skips invalid ones."""
    log_file = tmp_path / "test.log"
    log_content = (
        f"{VALID_LOG_LINE}\n"
        "1157689312.049 5006 10.105.21.199\n"  # Invalid, missing fields
        "   \n"  # Empty line, should be skipped
        "invalid_text   5006 10.105.21.199 TCP_MISS/200 19763 "
        "CONNECT login.yahoo.com:443 badeyek DIRECT/209.73.177.115 -\n"
        f"{VALID_LOG_LINE}\n"
    )
    log_file.write_text(log_content)

    import types
    entries_generator = parse_logs([log_file])
    assert isinstance(entries_generator, types.GeneratorType)
    
    entries_list = list(entries_generator)

    # Should only contain the 2 valid entries
    assert len(entries_list) == 2
    assert all(isinstance(entry, LogEntry) for entry in entries_list)
    assert entries_list[0].timestamp == 1157689312.049
    assert entries_list[1].timestamp == 1157689312.049
    
    # Asserting that the invalid lines triggered appropriate warnings
    assert "Skipping" in caplog.text

def test_parse_logs_handles_missing_file(tmp_path: Path, caplog):
    """Test that parse_logs gracefully handles non-existent files."""
    missing_file = tmp_path / "does_not_exist.log"
    
    entries_generator = parse_logs([missing_file])
    entries_list = list(entries_generator)
    
    # Should yield nothing but not crash
    assert len(entries_list) == 0
    assert "Failed to read file" in caplog.text


def test_parse_logs_gzip(tmp_path: Path):
    """Test that parse_logs can read from gzip compressed files natively."""
    import gzip
    
    log_file = tmp_path / "compressed.log.gz"
    
    # Write sample content to a gzip file
    log_content = (
        f"{VALID_LOG_LINE}\n"
        f"{VALID_LOG_LINE}\n"
    )
    
    with gzip.open(log_file, "wt", encoding="utf-8") as f:
        f.write(log_content)
        
    entries_generator = parse_logs([log_file])
    entries_list = list(entries_generator)
    
    # Should correctly extract and parse both valid lines
    assert len(entries_list) == 2
    assert all(isinstance(entry, LogEntry) for entry in entries_list)
    assert entries_list[0].timestamp == 1157689312.049
