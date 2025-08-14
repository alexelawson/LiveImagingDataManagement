#!/usr/bin/env python3
import pandas as pd
import numpy as np

# --- Hard-coded paths ---
INPUT_CSV  = "/Users/alexlawson/Masters-Data-Final/Live-imaging/Results/Statistics/al47/Filaments/Combined/Filament_No._Sholl_Intersections.csv"
OUTPUT_CSV = "/Users/alexlawson/Masters-Data-Final/Live-imaging/Results/Statistics/Combined Stats/CON/Unknown/AL47/Filament_No._Sholl_Intersections.csv"

# --- Load data ---
df = pd.read_csv(INPUT_CSV)

# --- Helper: find a column by any of several candidate names ---
def pick_col(cols, candidates):
    for c in candidates:
        if c in cols:
            return c
    return None

# Column name resolution (robust to small naming differences)
cols = df.columns
col_intersections = pick_col(cols, ["Filament No. Sholl Intersections", "Filament No. Sholl Intersections ", "Sholl Intersections"])
col_radius        = pick_col(cols, ["Radius", "Radius "])
col_frame         = pick_col(cols, ["Frame", "frame"])
col_mgid          = pick_col(cols, ["MicrogliaID", "Microglia Id", "Microglia ID"])
col_unique        = pick_col(cols, ["UniqueID", "Unique_ID", "Unique Id", "Unique ID"])
col_category      = pick_col(cols, ["Category", "Class", "Type"])

required = [col_intersections, col_radius, col_frame, col_mgid]
missing = [name for name in ["intersections","radius","frame","MicrogliaID"]
           if [col_intersections, col_radius, col_frame, col_mgid][["intersections","radius","frame","MicrogliaID"].index(name)] is None]
if missing:
    raise ValueError(f"Missing required column(s): {missing}. Found columns: {list(cols)}")

# --- Compute stats without forced numeric coercion ---
# (Assumes those columns are already numeric in your CSV; if not, this will raise clearly.)
records = []
grouped = df.groupby([col_mgid, col_frame], sort=True)

for (mid, frame), g in grouped:
    ints = g[col_intersections].to_numpy()
    rads = g[col_radius].to_numpy()

    total = np.sum(ints)
    peak  = np.max(ints)

    # index of first occurrence of the peak
    peak_ix = int(np.argmax(ints)) if ints.size else None
    radius_at_peak = float(rads[peak_ix]) if (ints.size and peak_ix is not None) else np.nan

    # Pull UniqueID / Category (if present) — take the first non-null value in the group
    unique_val = None
    if col_unique is not None:
        uniq_vals = g[col_unique].dropna().unique()
        if uniq_vals.size > 0:
            unique_val = uniq_vals[0]

    category_val = None
    if col_category is not None:
        cat_vals = g[col_category].dropna().unique()
        if cat_vals.size > 0:
            category_val = cat_vals[0]

    rec = {
        "MicrogliaID": mid,
        "Frame": frame,
        "total_intersections": total,
        "peak_intersections": peak,
        "radius_at_peak": radius_at_peak,
    }
    if col_unique is not None:
        rec["UniqueID"] = unique_val
    if col_category is not None:
        rec["Category"] = category_val

    records.append(rec)

# --- Build summary DataFrame ---
base_cols = ["MicrogliaID","Frame","total_intersections","peak_intersections","radius_at_peak"]
extra_cols = []
if col_unique is not None:   extra_cols.append("UniqueID")
if col_category is not None: extra_cols.append("Category")

summary = pd.DataFrame.from_records(records, columns=base_cols + extra_cols)

# --- Save and show ---
summary.to_csv(OUTPUT_CSV, index=False)
print(f"✅ Summary written to {OUTPUT_CSV}")
print(summary.head())
