import os
import pandas as pd

def update_all_csvs_in_folder(folder_path):
    # Create the 'Updated' subfolder inside the given folder
    updated_folder = os.path.join(folder_path, "Updated")
    os.makedirs(updated_folder, exist_ok=True)

    # Loop through each file in the folder
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".csv"):
            file_path = os.path.join(folder_path, filename)

            # Read CSV
            df = pd.read_csv(file_path)

            # Apply transformations
            df.rename(columns={'MicrogliaID': 'Unique_ID'}, inplace=True)
            df[['Frame', 'MicrogliaID']] = df['Unique_ID'].str.extract(r'Frame_(\d+)_(\d+)')
            df['Frame'] = df['Frame'].astype(int)
            df['MicrogliaID'] = df['MicrogliaID'].astype(int)

            # Build new file path
            base_name, ext = os.path.splitext(filename)
            updated_filename = f"{base_name}_updated{ext}"
            updated_path = os.path.join(updated_folder, updated_filename)

            # Save updated CSV
            df.to_csv(updated_path, index=False)
            print(f"Processed and saved: {updated_filename}")

# Example usage
folder = "/Users/alexlawson/Masters-Data-Final/Live-imaging/Results/Statistics/al51/Filaments/Summary"
update_all_csvs_in_folder(folder)
