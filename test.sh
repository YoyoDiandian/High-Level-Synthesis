#!/bin/bash

# Define constants
OUTPUT_DIR="testOutput"
EXAMPLES=("dotprod" "gcd" "sum")

# Create output directory if it doesn't exist
mkdir -p "${OUTPUT_DIR}"

# Run tests for each example
for example in "${EXAMPLES[@]}"; do
    echo "Processing ${example}..."
    if ! sh autorun.sh "example/${example}.ll" "${OUTPUT_DIR}"; then
        echo "Error processing ${example}"
        exit 1
    fi
done

echo "============================="
echo "Testing completed successfully!"
echo "Output files are available in the ${OUTPUT_DIR} directory."