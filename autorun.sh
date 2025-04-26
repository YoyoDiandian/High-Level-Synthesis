#!/bin/bash
# Automation script for HLS parser, CDFG generator, and Verilog simulation
# Usage: ./autorun.sh <input_file>

# Exit on any error
set -e

# Check if input argument is provided
if [ $# -lt 1 ] || [ $# -gt 2 ]; then
    echo "Error: Invalid number of arguments"
    echo "Usage: $0 <input_file> [output_directory]"
    exit 1
fi

# Store the absolute path to the project root directory
ROOT_DIR=$(pwd)
INPUT_FILE="$1"
BASENAME=$(basename "$INPUT_FILE" .ll)

# Directory structure (all paths relative to ROOT_DIR)
PARSER_DIR="parser"
EXAMPLE_DIR="example"
if [ $# -eq 2 ]; then
    OUTPUT_DIR="${2%/}"
else
    OUTPUT_DIR="output"
    echo "Notice: No output directory specified. Using default: $OUTPUT_DIR"
    echo ""
fi
PARSE_RESULT_DIR="$OUTPUT_DIR/parseResult"
VERILOG_DIR="$OUTPUT_DIR/verilog_code"
WAVE_PATH="$OUTPUT_DIR/waveform"
OUTPUTFLOW_DIR="$OUTPUT_DIR/outputFlow"
TESTBENCH_DIR="$EXAMPLE_DIR/testbench"

# File paths
PARSE_RESULT="${BASENAME}_parseResult.txt"
PARSE_RESULT_PATH="$PARSE_RESULT_DIR/$PARSE_RESULT"
VERILOG_FILE="$VERILOG_DIR/$BASENAME.v"
TESTBENCH_FILE="$TESTBENCH_DIR/${BASENAME}_tb.v"
WAVE_OUTPUT="$WAVE_PATH/${BASENAME}_wave"
WAVE_FILE="$WAVE_PATH/${BASENAME}_wave.vcd"

# Create necessary directories if they don't exist
mkdir -p "$PARSE_RESULT_DIR"
mkdir -p "$VERILOG_DIR"
mkdir -p "$WAVE_PATH"
mkdir -p "$OUTPUTFLOW_DIR"

echo "============================="
echo "Step 1: Running parser..."
echo "============================="
cd "$ROOT_DIR/$PARSER_DIR"

if ! ./hls "$ROOT_DIR/$INPUT_FILE" "$ROOT_DIR/$PARSE_RESULT_PATH"; then
    echo "First attempt failed. Running make clean and rebuilding..."
    make clean
    make
    if ! ./hls "$ROOT_DIR/$INPUT_FILE" "$ROOT_DIR/$PARSE_RESULT_PATH"; then
        echo "Error: Parser execution failed after rebuild"
        exit 1
    fi
fi
rm -f *.o

echo "✅ Parser completed successfully"
echo "Parse result saved to: $PARSE_RESULT_PATH"

echo ""
echo "============================="
echo "Step 2: Running high level synthesis..."
echo "============================="
cd "$ROOT_DIR"
if ! python3 main.py "$PARSE_RESULT_PATH" "$OUTPUT_DIR"; then
    echo "Error: CDFG generation failed"
    rm -f "$PARSE_RESULT_PATH"
    cd "$ROOT_DIR/$PARSER_DIR"
    make clean
    exit 1
fi

echo "✅ High level synthesis completed successfully"
echo "Output flow file saved to: $OUTPUT_DIR/outputFlow.txt"
echo "Verilog file generated at: $VERILOG_FILE"

echo ""
echo "============================="
echo "Step 3: Compiling Verilog code..."
echo "============================="
if ! iverilog -o "$WAVE_OUTPUT" "$VERILOG_FILE" "$TESTBENCH_FILE"; then
    echo "Error: Verilog compilation failed"
    exit 1
fi
echo "✅ Verilog compilation completed"

echo ""
echo "============================="
echo "Step 4: Generating waveform file..."
echo "============================="
cd "$ROOT_DIR/$WAVE_PATH"
if ! vvp -n "$(basename "$WAVE_OUTPUT")"; then
    echo "Error: Waveform generation failed"
    exit 1
fi

# Cleanup temporary files
rm -f "$(basename "$WAVE_OUTPUT")"

if [ -f "$(basename "$WAVE_FILE")" ]; then
    echo "✅ Waveform file generated successfully"
    echo "Waveform file available at: $WAVE_FILE"
else
    echo "Warning: Expected waveform file not found"
fi

echo ""
echo "============================="
echo "All processes completed successfully!"
echo "============================="

echo "Output files:"
echo "1. Parse result: $PARSE_RESULT_PATH"
echo "2. Output flow file: $OUTPUT_DIR/"$BASENAME"_outputFlow.txt"
echo "3. Verilog file: $VERILOG_FILE"
echo "4. Waveform file: $WAVE_FILE"
echo "============================="
echo ""