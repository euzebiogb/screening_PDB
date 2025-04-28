import argparse
import os
import csv
from rdkit import Chem
from rdkit.Chem import AllChem
from datetime import datetime
import sys
import multiprocessing as mp
from queue import Empty
import random
import time

def process_molecule(args):
    """Process a single molecule"""
    mol_count, mol_name, sdf_string, sphere_radius = args
    try:
        mol = Chem.MolFromMolBlock(sdf_string, sanitize=False)
        if mol is None:
            print(f"\nMolecule #{mol_count}: Failed to create molecule object")
            sys.stdout.flush()
            return None

        try:
            Chem.SanitizeMol(mol)
        except Exception as san_e:
            print(f"\nMolecule #{mol_count}: Sanitization failed")
            sys.stdout.flush()
            return None

        # Optimize 3D coordinates
        embed_result = AllChem.EmbedMolecule(mol, randomSeed=0xf00d)
        if embed_result == -1:
            print(f"\nMolecule #{mol_count}: 3D embedding failed")
            sys.stdout.flush()
            return None

        optimize_result = AllChem.UFFOptimizeMolecule(mol, maxIters=200)
        if optimize_result == -1:
            print(f"\nMolecule #{mol_count}: Optimization failed")
            sys.stdout.flush()
            return None

        volume = AllChem.ComputeMolVolume(mol, confId=0)
        sphere_volume = (4/3) * 3.14159 * (sphere_radius ** 3)
        packing_efficiency = 0.64
        sphere_count = int((volume * packing_efficiency) / sphere_volume)
        
        print(f"\nMolecule #{mol_count}")
        print(f"Volume: {volume:.2f} Å³")
        print(f"Sphere count: {sphere_count}")
        sys.stdout.flush()

        return {
            "mol_name": mol_name,
            "volume": f"{volume:.2f}",
            "sphere_count": sphere_count
        }

    except Exception as e:
        print(f"\nMolecule #{mol_count}: Processing error: {str(e)}")
        sys.stdout.flush()
        return None

def read_sdf_molecules(filepath):
    """Read all molecules from SDF file and return as list"""
    molecules = []
    sdf_string = ""
    mol_name = ""
    
    with open(filepath, 'rb') as f:
        for line in f:
            line = line.decode('utf-8', errors='ignore')
            if line.startswith("$$$$"):
                if sdf_string:
                    molecules.append((mol_name, sdf_string))
                sdf_string = ""
                mol_name = ""
            else:
                sdf_string += line
                if not mol_name:
                    mol_name = line.strip()
    return molecules

def process_sdf_files(input_path, output_file, num_processes=4):
    """Processes SDF files using parallel processing"""
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['mol_name', 'volume', 'sphere_count']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        if os.path.isdir(input_path):
            sdf_files = [f for f in os.listdir(input_path) if f.endswith(".sdf")]
            for filename in sdf_files:
                filepath = os.path.join(input_path, filename)
                process_sdf_file(filepath, writer, num_processes)
        elif os.path.isfile(input_path) and input_path.endswith(".sdf"):
            process_sdf_file(input_path, writer, num_processes)
        else:
            raise ValueError("Invalid input path. Provide a directory of SDF file.")

def process_sdf_file(filepath, writer, num_processes):
    """Process a single SDF file with parallel processing"""
    print(f"\nProcessing file: {filepath}")
    sys.stdout.flush()
    
    # Read all molecules
    molecules = read_sdf_molecules(filepath)
    total_mols = len(molecules)
    
    # Keep track of unprocessed molecule indices
    unprocessed_indices = set(range(total_mols))
    
    # Process molecules in parallel
    with mp.Pool(processes=num_processes) as pool:
        while unprocessed_indices:
            # Select 4 random molecules from unprocessed ones
            batch_size = min(4, len(unprocessed_indices))
            batch_indices = random.sample(list(unprocessed_indices), batch_size)
            
            # Remove selected indices from unprocessed set
            unprocessed_indices -= set(batch_indices)
            
            # Prepare batch for processing
            batch = [(i+1, molecules[i][0], molecules[i][1], 1.5) for i in batch_indices]
            
            # Process batch in parallel
            results = pool.map(process_molecule, batch)
            
            # Write results
            for result in results:
                if result is not None:
                    writer.writerow(result)
            
            processed_count = total_mols - len(unprocessed_indices)
            print(f"\nProgress: {processed_count}/{total_mols} molecules processed")
            sys.stdout.flush()
            
            # Small delay to allow for output reading
            time.sleep(0.1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate sphere counts in SDF files.")
    parser.add_argument("-f", "--folder", required=True, help="Path to the directory or SDF file.")
    parser.add_argument("-o", "--output", required=True, help="Path to the output CSV file.")
    parser.add_argument("-p", "--processes", type=int, default=4, help="Number of parallel processes")
    args = parser.parse_args()

    start_time = datetime.now()
    print("Starting process...")
    sys.stdout.flush()
    
    process_sdf_files(args.folder, args.output, args.processes)
    
    print(f"\nProcess completed in {(datetime.now() - start_time).total_seconds():.1f}s")
    sys.stdout.flush()
