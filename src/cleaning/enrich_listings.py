"""
Entiches cleaned listings with calendar-derived occupancy and revenue metrics and review-derived engagement metrics.
"""

from pathlib import Path

import duckdb
import pandas as pd

RAW_DIR = Path("data/raw/edinburgh")
PROCESSED_DIR = Path("data/processed/edinburgh")

# Use the dataset snapshot date rather than the execution date to ensure reproducible review recency calculations
SNAPSHOT_DATE = "2025-09-21"

def compute_calendar_metrics() -> pd.DataFrame:
    query = f"""
        SELECT
            listing_id,
            COUNT(*) AS total_nights,
            SUM(CASE WHEN available = 'f' THEN 1 ELSE 0 END) AS booked_nights
        FROM read_csv_auto('{RAW_DIR / "calendar.csv"}')
        GROUP BY listing_id
    """
    df = duckdb.sql(query).to_df()
    df["occupancy_rate"] = df["booked_nights"] / df["total_nights"]
    return df

def compute_review_metrics() -> pd.DataFrame:
    query = f"""
        SELECT
            listing_id,
            COUNT(*) AS review_count_computed,
            MIN(date) AS first_review_date_computed,
            MAX(date) AS last_review_date_computed
        FROM read_csv_auto('{RAW_DIR / "reviews.csv"}')
        GROUP BY listing_id
    """
    df = duckdb.sql(query).to_df()
    df["last_review_date_computed"] = pd.to_datetime(df["last_review_date_computed"])
    df["days_since_last_review"] = (
        pd.Timestamp(SNAPSHOT_DATE) - df["last_review_date_computed"]
    ).dt.days

    return df

def main():
    listings = pd.read_csv(PROCESSED_DIR / "listings_clean.csv", low_memory=False)

    calendar_metrics = compute_calendar_metrics().rename(columns={"listing_id": "id"})
    review_metrics = compute_review_metrics().rename(columns={"listing_id": "id"})

    enriched = listings.merge(calendar_metrics, on="id", how="left")
    enriched = enriched.merge(review_metrics, on="id", how="left")

    enriched["estimated_annual_revenue"] = enriched["booked_nights"]
    # Listings with no reviews do not appear in reviews.csv so 0 is valid value
    enriched["review_count_computed"] = enriched["review_count_computed"].fillna(0).astype(int)

    output_path = PROCESSED_DIR / "listings_enriched.csv"
    enriched.to_csv(output_path, index=False)

    print(f"Enriched {len(enriched):,} listings")
    print(f"Listings with no calendar match: {enriched['total_nights'].isna().sum()}")
    print(f"Listings with zero reviews: {(enriched['review_count_computed'] == 0).sum()}")

    if "number_of_reviews" in enriched.columns:
        diff = (enriched["review_count_computed"] - enriched["number_of_reviews"]).abs()
        print(f"Median difference vs listings.csv's own review count: {diff.median()}")

    print(f"Saved: {output_path}")

if __name__ == "__main__":
    main()