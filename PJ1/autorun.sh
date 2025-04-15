#!/bin/bash
# Automation script for HLS parser and CDFG generator
# Usage: ./autorun.sh <input_file>

# Exit on any error
set -e

# Check if input argument is provided
if [ $# -ne 1 ]; then
    echo "Error: Please provide an input file"
    echo "Usage: $0 <input_file>"
    exit 1
fi

# Define constants
PARSER_DIR="parser"
PARSE_RESULT="$(basename "${1%.ll}")_parseResult.txt"
EXAMPLE_DIR="example"
OUTPUT_DIR="output"
PARSE_RESULR_DIR="$OUTPUT_DIR/parseResult"

# Step 1: Run parser
echo "Starting parser..."
cd "$PARSER_DIR" || exit 1
if ! make; then
    echo "Error: Make failed"
    exit 1
fi

if ! ./hls "../$1" "../$PARSE_RESULR_DIR/$PARSE_RESULT"; then
    echo "Error: Parser execution failed"
    exit 1
fi

echo "Parser completed successfully"

# Step 2: Generate CDFG
cd ..
echo ""
echo "Start running python files..."
if ! python3 main.py "$PARSE_RESULR_DIR/$PARSE_RESULT"; then
    echo "Error: CDFG generation failed"
    cd "$OUTPUT_DIR" || exit 1
    rm -f "$PARSE_RESULT"*
    make clean
    exit 1
fi

# Step 3: Cleanup
echo "Cleaning up..."
cd "$PARSER_DIR" || exit 1
# rm -f "$PARSE_RESULT"*
make clean

echo "Process completed successfully"