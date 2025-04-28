from rdkit import Chem
import pandas as pd
import argparse
from tqdm import tqdm

def filter_sdf(input_sdf, id_file, output_sdf):
    # Load the IDs from id.csv
    ids_to_keep = pd.read_csv(id_file)['mol_name'].tolist()

    # Open input SDF and output SDF
    supplier = Chem.SDMolSupplier(input_sdf, removeHs=False)
    writer = Chem.SDWriter(output_sdf)

    total_molecules = len(supplier)  # Get total number of molecules for the progress bar
    count = 0

    with tqdm(total=total_molecules, desc="Filtering Molecules") as pbar:
        for mol in supplier:
            if mol is not None:
                mol_id = mol.GetProp('_Name')  # Assumes ID is stored in the '_Name' property
                if mol_id in ids_to_keep:
                    # Write molecule as-is to the output file
                    writer.write(mol)
                    count += 1
            pbar.update(1)  # Update progress bar for each molecule processed

    writer.close()
    print(f"Filtered {count} molecules into {output_sdf}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter SDF file based on IDs in a CSV file")
    parser.add_argument("-sdf", type=str, required=True, help="Input SDF file with all compounds")
    parser.add_argument("-ids", type=str, required=True, help="CSV file with compound IDs (e.g., id.csv)")
    parser.add_argument("-o", type=str, required=True, help="Output SDF file with filtered compounds")
    args = parser.parse_args()

    filter_sdf(args.sdf, args.ids, args.o)
