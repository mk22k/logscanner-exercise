
from logscanner.cli import main


def test_cli_integration(tmp_path, monkeypatch):
    # Create a sample log file
    log_file = tmp_path / "sample.log"
    output_file = tmp_path / "output.json"
    log_content = (
        "1157689312.049   5006 10.105.21.199 TCP_MISS/200 19763 "
        "CONNECT login.yahoo.com:443 badeyek DIRECT/209.73.177.115 -\n"
        "1157689320.327   2864 10.105.21.199 TCP_MISS/200 10182 "
        "GET http://www.goonernews.com/ badeyek DIRECT/207.58.145.61 text/html"
    )
    log_file.write_text(log_content)
    
    test_args = [
        "--input", str(log_file),
        "--output", str(output_file),
        "--mfip",
        "--lfip",
        "--eps",
        "--bytes"
    ]
    
    # Patch sys.argv to simulate running the CLI with our test arguments
    import json
    import sys
    
    monkeypatch.setattr(sys, 'argv', ['logscanner'] + test_args)
    
    # main() shouldn't raise SystemExit on a successful 0 exit code
    # unless it calls sys.exit(), but argparse might if arguments are bad.
    # A successful run just returns None.
    main()

    # Verify the output file was created and contains the correct JSON
    assert output_file.exists()
    
    with open(output_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
        
    assert results["Most frequent IP"] == "10.105.21.199"
    assert results["Least frequent IP"] == "10.105.21.199"
    assert results["Events per second"] == 2/(1157689320.327 - 1157689312.049)
    assert results["Total amount of bytes exchanged"] == (19763 + 10182)

