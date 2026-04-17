"""
Command-line interface for the log scanner application.

This module handles argument parsing, input validation, and output formatting.
It serves as the entry point for the application when executed from the 
command line.

"""

import argparse
import json
from pathlib import Path

from logscanner.analyzer import analyze_logs
from logscanner.parser import parse_logs

# Define calculation options
CALCULATION_OPTIONS = {
    "mfip": "Calculate most frequent IP",
    "lfip": "Calculate least frequent IP",
    "eps": "Calculate events per second",
    "bytes": "Calculate total amount of bytes exchanged"
}

# Map options to output labels
OUTPUT_LABELS = {
    "mfip": "Most frequent IP",
    "lfip": "Least frequent IP",
    "eps": "Events per second",
    "bytes": "Total amount of bytes exchanged"
}


def main() -> None:
    """Parse command-line arguments, validate inputs, and write results."""
    parser = argparse.ArgumentParser(
        description="Analyze Squid Proxy access logs")

    # Core I/O arguments
    parser.add_argument(
        "files",
        nargs='+',
        type=Path,
        help="Input log file(s) followed by the output file path"
    )

    # Register calculation options
    for flag, help_text in CALCULATION_OPTIONS.items():
        parser.add_argument(
            f"--{flag}",
            action="store_true",
            required=False,
            help=help_text
        )

    args = parser.parse_args()

    if len(args.files) < 2:
        parser.error(
            "You must provide at least one input file and one output file."
        )

    input_files = args.files[:-1]
    output_file = args.files[-1]

    # Input file validation. Do not fail if one file is missing
    valid_paths: list[Path] = []
    for file in input_files:
        if file.is_file():
            valid_paths.append(file)
        else:
            parser.error(f"Input file '{file}' not found. Skipping this file.")
    
    # If no option is selected, show all options
    if not any(getattr(args, flag) for flag in CALCULATION_OPTIONS):
        for flag in CALCULATION_OPTIONS:
            setattr(args, flag, True)

    # Flag extraction
    args_dict = vars(args)
    active_flags = [flag for flag in CALCULATION_OPTIONS if args_dict[flag]]

    print(f"Input files: {input_files}")
    print(f"Output file: {output_file}")
    print(f"Active calculation options: {active_flags}")

    log_stream = parse_logs(valid_paths)
    metrics = analyze_logs(log_stream)

    # Build the final dictionary using the descriptive keys
    final_output = {
        OUTPUT_LABELS[flag]: metrics[flag] 
        for flag in active_flags
    }

    try:
        with open(output_file, 'w', encoding='utf-8') as output_file_handle:
            json.dump(final_output, output_file_handle, indent=4)
        print(f"Results successfully written to {output_file}")

    except Exception as e:
        print(f"Error writing the output file: {e}")

if __name__ == "__main__":
    main()