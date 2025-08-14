#!/usr/bin/env python3
"""
Script to rename Microglia##_Statistics folders to ##_Statistics
and to rename any CSV files within, stripping any prefix before the number (handles typos).
"""
import os
import re
import argparse

def rename_microglia(spots_dir):
    # Iterate over entries in the SPOTS directory
    for entry in os.listdir(spots_dir):
        old_dir_path = os.path.join(spots_dir, entry)
        if not os.path.isdir(old_dir_path):
            continue

        # Detect original Microglia##_Statistics pattern
        m_old = re.match(r'^Microglia(\d+)_Statistics$', entry)
        if m_old:
            num = m_old.group(1)
            new_dir_name = f"{num}_Statistics"
            new_dir_path = os.path.join(spots_dir, new_dir_name)

            os.rename(old_dir_path, new_dir_path)
            print(f"Renamed directory: '{entry}' -> '{new_dir_name}'")
        else:
            # Detect already-renamed ##_Statistics pattern
            m_new = re.match(r'^(\d+)_Statistics$', entry)
            if m_new:
                num = m_new.group(1)
                new_dir_path = old_dir_path
            else:
                # Skip unrelated dirs
                continue

        # Rename files inside the directory
        for fname in os.listdir(new_dir_path):
            old_file_path = os.path.join(new_dir_path, fname)
            if not os.path.isfile(old_file_path):
                continue

            # Match any prefix, capture number and VALUE
            m2 = re.match(r'^.*?(\d+)_(.+)\.csv$', fname)
            if m2:
                num2 = m2.group(1)
                value = m2.group(2)
                new_file_name = f"{num2}_{value}.csv"
                new_file_path = os.path.join(new_dir_path, new_file_name)

                if fname != new_file_name:
                    os.rename(old_file_path, new_file_path)
                    print(f"  Renamed file: '{fname}' -> '{new_file_name}'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Rename Microglia##_Statistics directories and CSV files"
    )
    parser.add_argument(
        "spots_dir",
        nargs='?', 
        default="SPOTS",
        help="Path to the SPOTS directory"
    )
    args = parser.parse_args()
    if not os.path.isdir(args.spots_dir):
        print(f"Error: '{args.spots_dir}' is not a directory.")
    else:
        rename_microglia(args.spots_dir)
