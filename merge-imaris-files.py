import os
import glob
import pandas as pd

def merge_microglia_stats(suffix, root_dir='.'):
    """
    Merge microglia stats CSV files across multiple folders.

    Each microglia folder should be named <MicrogliaID>_Statistics
    and contain files named <MicrogliaID>_<suffix>.csv.

    Parameters:
    - suffix (str): the datafile suffix (e.g., 'Length', 'Volume').
    - root_dir (str): path to the parent directory.

    Returns:
    - combined DataFrame if files are found, else None.
    """
    # Build file search pattern
    pattern = os.path.join(root_dir, "*_Statistics", f"*_{suffix}.csv")
    files = glob.glob(pattern)
    if not files:
        print(f"No files found for suffix '{suffix}' in '{root_dir}'.")
        return None

    dfs = []
    for file_path in files:
        # Extract microglia ID from filename (before the suffix)
        microglia_id = os.path.basename(file_path).split(f"_{suffix}.csv")[0]
        print(f"Loading: {file_path} (Microglia ID: {microglia_id})")

        # Read CSV skipping the first three rows (blank, metric name, separators)
        df = pd.read_csv(file_path, skiprows=3)
        # Add column for microglia ID
        df['MicrogliaID'] = microglia_id
        dfs.append(df)

    # Concatenate all dataframes
    combined_df = pd.concat(dfs, ignore_index=True)

    # Save to CSV
    output_csv = os.path.join(root_dir, f"combined_{suffix}.csv")
    combined_df.to_csv(output_csv, index=False)
    print(f"Combined data saved to {output_csv}")

    return combined_df


if __name__ == "__main__":
    # Prompt user for inputs
    suffix = input("Enter the datafile suffix (e.g. 'Length'): ").strip()
    root_dir = input("Enter the parent directory (default is current directory): ").strip() or '.'
    merge_microglia_stats(suffix, root_dir)