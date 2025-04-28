#!/bin/bash

# Exit on any error
set -e

# Check if input file is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <input_file>"
    echo "Supported formats: sdf, mol2, mol, pdb, and other formats supported by Open Babel"
    exit 1
fi

input_file="$1"
input_extension="${input_file##*.}"
basename=$(basename "$input_file" ".$input_extension")

# Check if input file exists
if [ ! -f "$input_file" ]; then
    echo "Error: Input file '$input_file' not found"
    exit 1
fi

# Check for required programs
for cmd in python3 obabel LSalign; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "Error: Required command '$cmd' not found"
        exit 1
    fi
done

# Create a function for cleanup
cleanup() {
    rm -f spheres_input.csv id.csv
    # Remove temporary SDF if it was created
    if [ "$input_extension" != "sdf" ]; then
        rm -f "${basename}.sdf"
    fi
}

# Set trap for cleanup on script exit
trap cleanup EXIT

# Convert to SDF if needed
if [ "$input_extension" != "sdf" ]; then
    echo "Converting input file to SDF format..."
    if ! obabel "$input_file" -O "${basename}.sdf"; then
        echo "Error: Failed to convert input file to SDF format"
        exit 1
    fi
    input_file="${basename}.sdf"
    echo "Conversion successful: ${input_file}"
fi

# Run sphere count analysis
echo "Running sphere count analysis..."
python3 sphere_count.py -f "$input_file" -o spheres_input.csv -p 4

# Debug: Show content of CSV file
echo "Content of spheres_input.csv:"
cat spheres_input.csv
echo "Last line of spheres_input.csv:"
tail -n 1 spheres_input.csv

# Extract sphere count and clean it
if [ ! -f spheres_input.csv ]; then
    echo "Error: spheres_input.csv was not created"
    exit 1
fi

# More robust sphere count extraction
sphere_count=$(awk -F',' '
    END {
        val = $3
        gsub(/[[:space:]]/,"", val)  # Remove all whitespace
        gsub(/[^0-9]/,"", val)       # Remove all non-digits
        print val
    }
' spheres_input.csv)

# Debug output
echo "Raw sphere count value: '$sphere_count'"

# Validate sphere count is a number and not empty
if [ -z "$sphere_count" ]; then
    echo "Error: Empty sphere count obtained"
    exit 1
elif ! [[ "$sphere_count" =~ ^[0-9]+$ ]]; then
    echo "Error: Invalid sphere count obtained: '$sphere_count'"
    exit 1
fi

echo "Processing with sphere count: $sphere_count"

# Generate IDs
echo "Generating IDs..."
python3 get_s_count.py -num "$sphere_count" -o id.csv

# Filter SDF
echo "Filtering SDF file..."
python filter_sdf.py -sdf ./Components-pub_fix.sdf -ids id.csv -o filtered_compounds.sdf

# Convert files to mol2 format
echo "Converting files to mol2 format..."
obabel filtered_compounds.sdf -O filtered.mol2
obabel "$input_file" -O "${basename}.mol2"

# Run LSalign and save results
echo "Running LSalign..."
LSalign "${basename}.mol2" filtered.mol2 > "result_${basename}.txt"

echo "Processing complete. Results saved in result_${basename}.txt"
