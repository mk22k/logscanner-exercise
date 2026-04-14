"""
Command-line interface for the log scanner application. This module handles argument parsing, input validation, and output formatting. It serves as the entry point for the application when executed from the command line.

"""

import argparse
import json
from pathlib import Path

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
    """Parse command-line arguments, validate inputs, and write results to 
        output file."""
    parser = argparse.ArgumentParser(description="Analyze Squid Proxy access logs")

    # Core I/O arguments
    parser.add_argument("--input", '-i', nargs='+', type=Path, required=True, 
                        help="Path(s) to the log file(s) to be analyzed")
    parser.add_argument("--output", '-o', type=Path, required=True, 
                        help="Path to the output file where results will be saved")

    # Register calculation options
    for flag, help_text in CALCULATION_OPTIONS.items():
        parser.add_argument(f"--{flag}", action="store_true", required=False, 
                            help=help_text)

    args = parser.parse_args()

    # Input file validation. Do not fail if one file is missing
    valid_files = []
    for file in args.input:
        if file.is_file():
            valid_files.append(file)
        else:
            parser.error(f"Input file '{file}' not found. Skipping this file.")
    
    # If no option is selected, show all options
    if not any(getattr(args, flag) for flag in CALCULATION_OPTIONS):
        for flag in CALCULATION_OPTIONS:
            setattr(args, flag, True)

    # Flag extraction
    args_dict = vars(args)
    active_flags = [flag for flag in CALCULATION_OPTIONS if args_dict[flag]]

    print(f"Input files: {args.input}")
    print(f"Output file: {args.output}")
    print(f"Active calculation options: {active_flags}")

    # Dummy data for now (to be replaced by the analyzer)
    placeholder_values = {
        "mfip": "8.8.8.8",
        "lfip": "0.0.0.0",
        "eps": 42,
        "bytes": 123456789
    }
    
    # Build the final dictionary using the descriptive keys
    final_output = {
        OUTPUT_LABELS[flag]: placeholder_values[flag] 
        for flag in active_flags
    }

    try:
        with open(args.output, 'w', encoding='utf-8') as output_file:
            json.dump(final_output, output_file, indent=4)
        print(f"Results successfully written to {args.output}")

    except Exception as e:
        print(f"Error writing the output file: {e}")

if __name__ == "__main__":
    main()