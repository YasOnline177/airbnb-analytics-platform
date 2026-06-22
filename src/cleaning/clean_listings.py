"""
Cleans and standardizes the raw Edinburgh listings dataset, based on findings from profiling and quality checks
"""

from pathlib import Path
import pandas as pd
from src.ingestion.quality_checks import find_near_duplicate_listings, iqr_outliers

RAW_DIR = Path("data/raw/edinburgh")
PROCESSED_DIR = Path("data/processed/edinburgh")
DROPPED_LOG_PATH = Path("reports/dropped_rows_log.csv")

EDINBURGH_LAT_RANGE = (55.80, 56.05)
EDINBURGH_LON_RANGE = (-3.35, -2.95)

def clean_price(df: pd.DataFrame) -> pd.DataFrame:
    df["price_clean"] = df["price"].astype(str).str.replace(r"[^\d.]", "", regex=True)
    df["price_clean"] = pd.to_numeric(df["price_clean"], errors="coerce")
    return df

def drop_invalid_price_rows(df: pd.DataFrame) -> pd.DataFrame:
    invalid_mask = df["price_clean"].isna() | (df["price_clean"] <= 0)
    n_invalid = invalid_mask.sum()

    if n_invalid > 0:
        DROPPED_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        df.loc[invalid_mask, ["id", "name", "price"]].assign(
            reason="price missing or <= 0"
        ).to_csv(DROPPED_LOG_PATH, index=False)
        print(f"Dropped {n_invalid} rows with missing/invalid price. Logged to {DROPPED_LOG_PATH}")

    return df.loc[~invalid_mask].copy()

def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    for col in ["host_since", "first_review", "last_review"]:
        if col not in df.columns:
            continue
        before = df[col].notna().sum()
        df[col] = pd.to_datetime(df[col], errors="coerce")
        lost = before - df[col].notna().sum()
        if lost > 0:
            print(f"  {col}: {lost} value could not be parsed as dates -> set to null")
    return df

def bucket_property_type(value) -> str:
    value = str(value).lower()
    if "entire" in value:
        return "Entire place"
    if "private room" in value:
        return "Private room"
    if "shared room" in value:
        return "Shared room"
    if "hotel" in value:
        return "Hotel room"
    return "Other"

def standardize_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    df["room_type"] = df["room_type"].astype(str).str.strip()
    df["property_type_group"] = df["property_type"].apply(bucket_property_type)
    df["neighbourhood_cleansed"] = df["neighbourhood_cleansed"].astype(str).str.strip()
    return df

def standardize_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    # Round coordinates to 5 decimal places to keep them consistent
    df["latitude"] = df["latitude"].round(5)
    df["longitude"] = df["longitude"].round(5)

    outside_bbox = (
        ~df["latitude"].between(*EDINBURGH_LAT_RANGE)
        | ~df["longitude"].between(*EDINBURGH_LON_RANGE)
    )
    df["coord_outside_expected_bbox"] = outside_bbox

    n_outside = outside_bbox.sum()
    if n_outside > 0:
        print(f"\n{n_outside} listings flagged outside the Edinburgh bounding box (not removed):")
        print(
            df.loc[outside_bbox, ["id", "latitude", "longitude", "neighbourhood_cleansed"]]
            .head(10)
            .to_string(index=False)
        )        

    return df

def flag_outliers(df: pd.DataFrame) -> pd.DataFrame:
    for col, flag_col in [
        ("price_clean", "price_is_outlier"),
        ("minimum_nights", "minimum_nights_is_outlier"),
        ("number_of_reviews", "number_of_reviews_is_outlier"),
    ]:
        df[flag_col] = False
        non_null = df[col].notna()
        df.loc[non_null, flag_col] = iqr_outliers(df.loc[non_null, col])
    return df

def flag_near_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    near_dupes = find_near_duplicate_listings(df.assign(price_numeric=df["price_clean"]))
    duplicate_ids = set(near_dupes["listing_id_a"]).union(near_dupes["listing_id_b"])
    df["is_potential_duplicate"] = df["id"].isin(duplicate_ids)
    print(f"{len(duplicate_ids)} listings flagged as potential duplicates for review")
    return df

def main():
    df = pd.read_csv(RAW_DIR / "listings.csv", low_memory=False)
    print(f"Loaded {len(df):,} raw listings.\n")

    df = clean_price(df)
    df = drop_invalid_price_rows(df)
    df = parse_dates(df)
    df = standardize_categoricals(df)
    df = standardize_coordinates(df)
    df = flag_outliers(df)
    df = flag_near_duplicates(df)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output_path = PROCESSED_DIR / "listings_clean.csv"
    df.to_csv(output_path, index=False)

    print(f"\nSaved cleaned dataset: {output_path}")
    print(f"Final row count: {len(df):,}")
    print(f"Final column count: {len(df.columns)}")

if __name__ == "__main__":
    main()