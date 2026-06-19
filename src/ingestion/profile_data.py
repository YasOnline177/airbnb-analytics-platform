"""
Profiles each raw Edinburgh dataset file and writes a markdown report
summarizing row counts, column types, null rates, and cardinality. 
"""

from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw/edinburgh")
REPORT_PATH = Path("reports/data_profile_report.md")

FILES_TO_PROFILE = [
    "listings.csv",
    "calendar.csv",
    "reviews.csv",
    "neighbourhoods.csv",
]

def profile_file(path: Path) -> str: 
    df = pd.read_csv(path, low_memory=False)
    n_rows, n_cols = df.shape

    lines = [f"## {path.name}", "", f"- Rows: {n_rows:,}", f"- Columns: {n_cols}", ""]
    lines.append("| Column | Dtype | Null % | Unique Values |")
    lines.append("|---|---|---|---|")

    for col in df.columns:
        dtype = str(df[col].dtype)
        null_pct = df[col].isna().mean() * 100
        n_unique = df[col].nunique(dropna=True)
        lines.append(f"| {col} | {dtype} | {null_pct:.1f}% | {n_unique:,} |")

    lines.append("")
    return "\n".join(lines)

def main():
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    sections = ["# Edinburgh Airbnb Data Profile Report", ""]

    for filename in FILES_TO_PROFILE:
        path = RAW_DIR / filename
        if not path.exists():
            print(f"Skipping {filename} (not found at {path})")
            continue
        print(f"Profilling {filename}...")
        sections.append(profile_file(path))

    REPORT_PATH.write_text("\n".join(sections), encoding="utf-8")
    print(f"\nReport written to {REPORT_PATH}")

if __name__ == "__main__":
    main()