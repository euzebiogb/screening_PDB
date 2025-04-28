import pandas as pd
import argparse

def filter_values(input_file, num, output_file):
    # Load the CSV file
    data = pd.read_csv(input_file)

    # Filter rows where sphere_count is close to the specified number (10, 11, 12)
    filtered_data = data[data['sphere_count'].isin([num - 1, num, num + 1])]

    # Save the filtered IDs (mol_name) to a CSV file
    filtered_data[['mol_name']].to_csv(output_file, index=False)
    print(f"Filtered data saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter sphere_count close to a specific number")
    parser.add_argument("-num", type=int, required=True, help="Target number to filter around (e.g., 11)")
    parser.add_argument("-o", type=str, required=True, help="Output file name (e.g., id.csv)")
    args = parser.parse_args()

    # Replace 'count_sphere.csv' with the actual file path
    filter_values("count_sphere.csv", args.num, args.o)
