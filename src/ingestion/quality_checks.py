"""
Data quality checks for the Edinburgh listings dataset: duplicate detection, outlier identification, and validation against domain rules. 
"""

from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw/edinburgh")
REPORT_PATH = Path("reports/data_quality_report.md")

# Approximate Edinburgh boundaries to flag listings with clearly incorrect coordinates
EDINBURGH_LAT_RANGE = (55.80, 56.05)
EDINBURGH_LON_RANGE = (-3.35, -2.95)

def load_listings() -> pd.DataFrame:
    df = pd.read_csv(RAW_DIR / "listings.csv", low_memory=False)
    # Convert price to a numeric value to run quality checks on it
    df["price_numeric"] = (
        df["price"].astype(str).str.replace(r"[^\d.]", "", regex=True)
    )
    df["price_numeric"] = pd.to_numeric(df["price_numeric"], errors="coerce")
    return df

# ------- Duplicate detection -------
 
def find_exact_duplicates(df: pd.DataFrame):
    """Check for fully duplicated rows and repeated listing IDs"""
    full_row_dupes = df[df.duplicated(keep=False)]
    id_dupes = df[df.duplicated(subset=["id"], keep=False)]
    return full_row_dupes, id_dupes

def find_near_duplicate_listings(df: pd.DataFrame, name_similarity_threshold: float = 0.9) -> pd.DataFrame:
    """
    Look for listings from the same host that might actually be the same property. 
    """
    has_name = "name" in df.columns
    near_dupes = []

    for host_id, group in df.groupby("host_id"):
        if len(group) < 2:
            continue
        cols = ["id", "latitude", "longitude", "room_type", "price_numeric"]
        if has_name:
            cols.append("name")
        rows = group[cols].dropna(subset=["latitude", "longitude"]).to_dict("records")

        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):
                a, b = rows[i], rows[j]
                same_location = (
                    round(a["latitude"], 4) == round(b["latitude"], 4)
                    and round(a["longitude"], 4) == round(b["longitude"], 4)
                )
                if not same_location:
                    continue

                if has_name:
                    similarity = SequenceMatcher(None, str(a["name"]), str(b["name"])).ratio()
                    is_match = similarity >= name_similarity_threshold
                else:
                    similarity = None
                    is_match = a["room_type"] == b["room_type"] and a["price_numeric"] == b["price_numeric"]

                if is_match:
                    near_dupes.append((host_id, a["id"], b["id"], similarity))

    return pd.DataFrame(near_dupes, columns=["host_id", "listing_id_a", "listing_id_b", "name_similarity"])

# ------- Outlier detection -------

def iqr_outliers(series: pd.Series) -> pd.Series:
    """Identify potential outliers using the standard 1.5 x IQR rules"""
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return (series < lower) | (series > upper)

def profile_outliers(df: pd.DataFrame) -> dict:
    fields = {
        "price_numeric": "price",
        "availability_365": "availability 365",
        "number_of_reviews": "number_of_reviews",
        "minimum_nights": "minimum_nights"
    }
    results = {}
    for col, label in fields.items():
        if col not in df.columns:
            continue
        clean_series = df[col].dropna()
        mask = iqr_outliers(clean_series)
        results[label] = {
            "n_outliers": int(mask.sum()),
            "pct_outliers": round(mask.mean() * 100, 2),
            "min": clean_series.min(),
            "max": clean_series.max(),
        }
    return results

# ------- Validation rules ------- 

def run_validation_rules(df: pd.DataFrame) -> dict:
    return {
        "price missing or <= 0": (df["price_numeric"].isna() | (df["price_numeric"] <= 0)).sum(),
        "latitude outside Edinburgh bounding box": (~df["latitude"].between(*EDINBURGH_LAT_RANGE)).sum(),
        "longitude outside Edinburgh bounding box": (~df["longitude"].between(*EDINBURGH_LON_RANGE)).sum(),
        "minimum_nights < 1": (df["minimum_nights"] < 1).sum(),
        "maximum_nights < minimum_nights": (df["maximum_nights"] < df["minimum_nights"]).sum(),
        "availability_365 outside [0, 365]": (~df["availability_365"].between(0, 365)).sum(),
        "number_of_reviews negative": (df["number_of_reviews"] < 0).sum(),
    }

def main():
    df = load_listings()

    full_row_dupes, id_dupes = find_exact_duplicates(df)
    near_dupes = find_near_duplicate_listings(df)
    outliers = profile_outliers(df)
    validation = run_validation_rules(df)

    lines = ["# Edinburgh Listings Data Quality Report", ""]

    lines.append("## Duplicate Detection")
    lines.append(f"- Fully duplicated rows: {len(full_row_dupes)}")
    lines.append(f"- Duplicated listing IDs: {len(id_dupes)}")
    lines.append(f"- Near-duplicate listings: {len(near_dupes)}")
    lines.append("")

    lines.append("## Outlier Summary (IQR method, 1.5x rule)")
    lines.append("| Field | # Outliers | % Outliers | Min | Max |")
    lines.append("|---|---|---|---|---|")
    for field , stats in outliers.items():
        lines.append(f"| {field} | {stats['n_outliers']} | {stats['pct_outliers']} | {stats['min']} | {stats['max']} |")
    lines.append("")

    lines.append("## Validation Rule Failures")
    lines.append("| Rule | # Rows Failing |")
    lines.append("|---|---|")
    for rule, count in validation.items():
        lines.append(f"| {rule} | {count} |")
    lines.append("")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")

    print(f"Report written to {REPORT_PATH}")
    if not near_dupes.empty:
        print("\nSample near-duplicate listings found:")
        print(near_dupes.head(10).to_string(index=False))

if __name__ == "__main__":
    main() 