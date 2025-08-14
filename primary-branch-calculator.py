#!/usr/bin/env python3
import pandas as pd

# === User-defined parameters ===
BRANCH_POINTS_PATH = "/Users/alexlawson/Masters-Data-Final/Live-imaging/Results/Statistics/Combined Stats/CON/Unknown/AL51/Filament_No._Segment_Branch_Pts.csv"
TERMINAL_POINTS_PATH = "/Users/alexlawson/Masters-Data-Final/Live-imaging/Results/Statistics/Combined Stats/CON/Unknown/AL51/Filament_No._Segment_Terminal_Pts.csv"
TOTAL_LENGTH_PATH = "/Users/alexlawson/Masters-Data-Final/Live-imaging/Results/Statistics/Combined Stats/CON/Unknown/AL51/Filament_Length.csv"
OUTPUT_PATH = "/Users/alexlawson/Masters-Data-Final/Live-imaging/Results/Statistics/Combined Stats/CON/Unknown/AL51/Primary_Branch_Stats.csv"

# Column names
ID_COL = "MicrogliaID"
UNIQUE_ID_COL = "Unique_ID"   # if absent, we’ll derive it
CATEGORY_COL = "Category"
FRAME_COL = "Frame"
BRANCH_COL = "Filament No. Segment Branch Pts"
TERMINAL_COL = "Filament No. Segment Terminal Pts"
TOTALLEN_COL = "Filament Length (sum)"
PRIMARY_COUNT_COL = "PrimaryBranches"
AVG_PRIMARY_LEN_COL = "AvgPrimaryBranchLength"


def _pick_col(cols, candidates):
    for c in candidates:
        if c in cols:
            return c
    return None

def _normalize(df, value_col):
    """
    Keep only the needed columns and normalize metadata columns so merges are clean.
    Ensures we have UNIQUE_ID_COL and CATEGORY_COL (fill from variants or fallback).
    """
    cols = df.columns
    # Resolve potential variants
    uid_src = _pick_col(cols, [UNIQUE_ID_COL, "UniqueID", "Unique Id", "Unique ID"])
    cat_src = _pick_col(cols, [CATEGORY_COL, "Class", "Type"])

    # Base subset (don’t coerce types)
    need = [ID_COL, FRAME_COL, value_col]
    out = df[need].copy()

    # Unique_ID: prefer explicit column, else fall back to MicrogliaID
    out[UNIQUE_ID_COL] = df[uid_src] if uid_src else df[ID_COL]

    # Category: keep if present; else NaN
    out[CATEGORY_COL] = df[cat_src] if cat_src else pd.NA

    # Drop rows missing the essentials for this measure
    out = out.dropna(subset=[ID_COL, FRAME_COL, value_col])
    return out

def calculate_primary_branch_length_stats():
    # 1) Load & normalize each input
    df_branch = _normalize(pd.read_csv(BRANCH_POINTS_PATH), BRANCH_COL)
    df_term   = _normalize(pd.read_csv(TERMINAL_POINTS_PATH), TERMINAL_COL)
    df_length = _normalize(pd.read_csv(TOTAL_LENGTH_PATH), TOTALLEN_COL)

    # 2) Merge terminal and branch counts
    df_counts = pd.merge(
        df_term,
        df_branch,
        on=[ID_COL, FRAME_COL],
        how="inner",
        suffixes=("", "_branch")
    )

    # Coalesce metadata after merge (prefer left, then right)
    for col in (UNIQUE_ID_COL, CATEGORY_COL):
        alt = f"{col}_branch"
        if alt in df_counts:
            df_counts[col] = df_counts[col].where(df_counts[col].notna(), df_counts[alt])
            df_counts.drop(columns=[alt], inplace=True, errors="ignore")

    # 3) Primary branch count
    df_counts[PRIMARY_COUNT_COL] = df_counts[TERMINAL_COL] - df_counts[BRANCH_COL]

    # 4) Merge in total length
    df_stats = pd.merge(
        df_counts,
        df_length[[ID_COL, FRAME_COL, TOTALLEN_COL, UNIQUE_ID_COL, CATEGORY_COL]],
        on=[ID_COL, FRAME_COL],
        how="inner",
        suffixes=("", "_len")
    )

    # Coalesce metadata again (term/branch vs length)
    for col in (UNIQUE_ID_COL, CATEGORY_COL):
        alt = f"{col}_len"
        if alt in df_stats:
            df_stats[col] = df_stats[col].where(df_stats[col].notna(), df_stats[alt])
            df_stats.drop(columns=[alt], inplace=True, errors="ignore")

    # 5) Average primary branch length (avoid divide-by-zero)
    df_stats[AVG_PRIMARY_LEN_COL] = df_stats[TOTALLEN_COL] / df_stats[PRIMARY_COUNT_COL].where(
        df_stats[PRIMARY_COUNT_COL] != 0
    )

    # 6) Select and save
    result = df_stats[[UNIQUE_ID_COL, CATEGORY_COL, ID_COL, FRAME_COL, PRIMARY_COUNT_COL, AVG_PRIMARY_LEN_COL]]
    result.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved primary branch stats to {OUTPUT_PATH}")
    print(result.head())


if __name__ == "__main__":
    calculate_primary_branch_length_stats()
