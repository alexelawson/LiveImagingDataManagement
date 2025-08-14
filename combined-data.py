from pathlib import Path
import pandas as pd
import re  # only used for safe_sheet_name

# -------- CONFIG --------
ROOT = Path("/Users/alexlawson/Masters-Data-Final/Live-imaging/Results/Statistics/Combined Stats")
OUT_XLSX = "/Users/alexlawson/Masters-Data-Final/Live-imaging/Results/Statistics/Combined Stats/combined_stats_by_type.xlsx"
OUT_LONG_CSV = "/Users/alexlawson/Masters-Data-Final/Live-imaging/Results/Statistics/Combined Stats/combined_stats_long.csv"

def infer_labels(rel_parts):
    """
    Expect order relative to ROOT:
      [0] Treatment, [1] Sex, [2] MouseID
    Take folder names exactly as they appear (no case mapping, no regex).
    """
    if len(rel_parts) < 3:
        return {"Treatment": None, "Sex": None, "MouseID": None}

    treat = rel_parts[0]
    sex   = rel_parts[1]
    mouse = rel_parts[2]
    return {"Treatment": treat, "Sex": sex, "MouseID": mouse}

def safe_sheet_name(name, used):
    cleaned = re.sub(r'[:\\/*?\[\]]', "_", str(name))
    cleaned = cleaned[:31] if len(cleaned) > 31 else cleaned
    base = cleaned or "Sheet"
    final = base
    i = 2
    while final in used:
        suffix = f"_{i}"
        final = (base[: 31 - len(suffix)] + suffix) if len(base) + len(suffix) > 31 else base + suffix
        i += 1
    used.add(final)
    return final

# -------- DISCOVER & LOAD --------
csv_paths = list(ROOT.rglob("*.csv"))
if not csv_paths:
    raise SystemExit(f"No CSV files found under {ROOT.resolve()}")

by_type, all_rows = {}, []

for p in csv_paths:
    try:
        df = pd.read_csv(p)
    except Exception as e:
        try:
            df = pd.read_csv(p, encoding="latin1")
        except Exception:
            print(f"Skipping unreadable file: {p} ({e})")
            continue

    dtype = p.stem
    rel_parts = p.relative_to(ROOT).parts
    labels = infer_labels(rel_parts)

    # (Optional) quick sanity check
    # print("DEBUG", rel_parts, "->", labels)

    # Remove any pre-existing metadata columns to prevent duplicates/stomping
    for meta in ["MouseID", "Treatment", "Sex", "DataType", "SourceFile"]:
        if meta in df.columns:
            df.drop(columns=[meta], inplace=True)

    # Insert fresh metadata
    df.insert(0, "MouseID", labels["MouseID"])
    df.insert(1, "Treatment", labels["Treatment"])
    df.insert(2, "Sex", labels["Sex"])
    df.insert(3, "DataType", dtype)
    df.insert(4, "SourceFile", str(p.as_posix()))

    by_type.setdefault(dtype, []).append(df)
    all_rows.append(df)

# -------- SAVE LONG CSV --------
# pd.concat(all_rows, ignore_index=True, sort=True).to_csv(OUT_LONG_CSV, index=False)

# -------- SAVE WORKBOOK (one sheet per type) --------
with pd.ExcelWriter(OUT_XLSX, engine="xlsxwriter") as writer:
    used_names = set()
    for dtype, frames in sorted(by_type.items()):
        big = pd.concat(frames, ignore_index=True, sort=True)
        sheet = safe_sheet_name(dtype, used_names)
        big.to_excel(writer, sheet_name=sheet, index=False)

print(f"Wrote {OUT_XLSX} and {OUT_LONG_CSV}")
