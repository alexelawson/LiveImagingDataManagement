#!/usr/bin/env python3
import pandas as pd

# === User-defined parameters ===
BOUNDING_BOX_PATH = "/Users/alexlawson/Masters-Data-Final/Live-imaging/Results/Statistics/al47/Filaments/Combined/Filament_BoundingBoxOO.csv"  # CSV with columns: MicrogliaID, Frame, BoxX, BoxY, BoxZ
OUTPUT_PATH = "/Users/alexlawson/Masters-Data-Final/Live-imaging/Results/Statistics/Combined Stats/CON/Unknown/AL47/Filament_BoundingBoxOO.csv_calculated.csv"  # Where to save the result

# Column names in the input CSV
ID_COL = "MicrogliaID"
UNIQUE_ID_COL = "Unique_ID"  # if exists, otherwise use ID_COL
FRAME_COL = "Frame"
X_COL = "Filament BoundingBoxOO Length A"  # bounding box length in X
Y_COL = "Filament BoundingBoxOO Length B"  # bounding box length in Y
Z_COL = "Filament BoundingBoxOO Length C"  # bounding box length in Z
CATEGORY= "Category"

# Name of the output column
SURV_COL = "SurveillanceVolume"


def calculate_surveillance_volume():
    """
    Loads bounding box dimensions, computes 3D volume per microglia per frame,
    and saves the result to OUTPUT_PATH.

    Output columns: MicrogliaID, Frame, SurveillanceVolume
    """
    # 1) Load data
    df = pd.read_csv(BOUNDING_BOX_PATH)

    # 2) Clean missing values
    df = df.dropna(subset=[ID_COL, CATEGORY, UNIQUE_ID_COL, FRAME_COL, X_COL, Y_COL, Z_COL])

    # 3) Compute surveillance volume (proxy for surveillance area)
    df[SURV_COL] = df[X_COL] * df[Y_COL] * df[Z_COL]

    # 4) Extract desired columns
    result = df[[SURV_COL, CATEGORY, UNIQUE_ID_COL, FRAME_COL, ID_COL]].copy()

    # 5) Save to CSV
    result.to_csv(OUTPUT_PATH, index=False)
    print(f"Surveillance volume per MicrogliaID and Frame saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    calculate_surveillance_volume()
