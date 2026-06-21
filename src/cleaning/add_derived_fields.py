"""
Add derived features and neighbourhood-level statistics to the cleaned Airbnb dataset
"""

from pathlib import Path

import pandas as pd

PROCESSED_DIR = Path("data/processed/edinburgh")
SNAPSHOT_DATE = "2025-09-21"

def add_host_tenure(df: pd.DataFrame) -> pd.DataFrame:
    df["host_since"] = pd.to_datetime(df["host_since"], errors="coerce")
    df["host_tenure_years"] = (
        pd.Timestamp(SNAPSHOT_DATE) - df["host_since"]
    ).dt.days / 365.25
    return df

def add_review_frequency(df: pd.DataFrame) -> pd.DataFrame:
    df["first_review_date_computed"] = pd.to_datetime(
        df["first_review_date_computed"], errors="coerce"
    )
    months_active = (
        pd.Timestamp(SNAPSHOT_DATE) - df["first_review_date_computed"]
    ).dt.days / 30.44

    df["reviews_per_month"] = df["review_count_computed"] / months_active
    # Review frequency is undefined for listings with no reviews
    df.loc[df["review_count_computed"] == 0, "reviews_per_month"] = pd.NA
    return df

def add_price_per_bedroom(df: pd.DataFrame) -> pd.DataFrame:
    # Avoid deviding by zero for studio listings or listings without bedroom data
    df["price_per_bedroom"] = df["price_clean"] / df["bedrooms"].replace(0, pd.NA)
    return df

def add_neighbourhood_aggregates(df: pd.DataFrame) -> pd.DataFrame:
    agg_cols = {"price_clean": "median"}
    if "review_scores_rating" in df.columns:
        agg_cols["review_scores_rating"] = "mean"

    stats = (
        df.groupby("neighbourhood_cleansed")
        .agg(agg_cols)
        .rename(columns={
            "price_clean": "neighbourhood_median_price",
            "review_scores_rating": "neighbourhood_avg_rating",
        })
    )
    stats["neighbourhood_listing_count"] = df.groupby("neighbourhood_cleansed").size()

    return df.merge(stats, on="neighbourhood_cleansed", how="left")

def main():
    df = pd.read_csv(PROCESSED_DIR / "listings_enriched.csv", low_memory=False)

    df = add_host_tenure(df)
    df = add_review_frequency(df)
    df = add_price_per_bedroom(df)
    df = add_neighbourhood_aggregates(df)

    output_path = PROCESSED_DIR / "listings_master.csv"
    df.to_csv(output_path, index=False)

    print(f"Added derived fields and neighbourhood aggregates to {len(df):,} listings")
    print(f"Neighbourhoods covered: {df['neighbourhood_cleansed'].nunique()}")
    print(f"Listings missing host_tenure_years: {df['host_tenure_years'].isna().sum()}")
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    main()