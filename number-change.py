#!/usr/bin/env python3
import sys
from pathlib import Path

def rename_prefix(folder_path: Path, old_prefix: str = "01", new_prefix: str = "02"):
    if not folder_path.is_dir():
        print(f"Error: {folder_path!r} is not a directory.")
        return

    for path in folder_path.iterdir():
        if path.is_file() and path.name.startswith(old_prefix):
            new_name = new_prefix + path.name[len(old_prefix):]
            new_path = path.with_name(new_name)

            # Check for potential name collision
            if new_path.exists():
                print(f"Skipping {path.name!r}: {new_name!r} already exists.")
                continue

            print(f"Renaming {path.name!r} → {new_name!r}")
            path.rename(new_path)

if __name__ == "__main__":
    # You can pass the folder as an argument, otherwise defaults to "02_statistics"
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("02_statistics")
    rename_prefix(folder)
