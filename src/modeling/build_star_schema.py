"""
Build the DuckDB star schema for the Edinburgh Airbnb dataset
"""

from pathlib import Path

import duckdb
import pandas as pd

RAW_DIR = Path("data/raw/edinburgh")
PROCESSED_DIR = Path("data/processed/edinburgh")
DB_PATH = PROCESSED_DIR / "edinburgh_airbnb.duckdb"
SCHEMA_PATH = Path("sql/schema.sql")

def get_bathroom_column(listings: pd.DataFrame) -> pd.DataFrame:
    """Return a numeric bathroom column"""
    if "bathrooms" in listings.columns and listings["bathrooms"].notna().any():
        return listings["bathrooms"]
    return listings["bathrooms_text"].astype(str).str.extract(r"([\d.]+)")[0].astype(float)

def build_dim_date(con: duckdb.DuckDBPyConnection) -> None:
    """Create the date dimension table"""
    date_range = con.sql(
        f"SELECT MIN(date) AS min_date, MAX(date) AS max_date "
        f"FROM read_csv_auto('{RAW_DIR / 'calendar.csv'}')"
    ).df()
    min_date, max_date = date_range.iloc[0]["min_date"], date_range.iloc[0]["max_date"]

    dim_date_df = pd.DataFrame({"date": pd.date_range(min_date, max_date)})
    dim_date_df["year"] = dim_date_df["date"].dt.year
    dim_date_df["month"] = dim_date_df["date"].dt.month
    dim_date_df["month_name"] = dim_date_df["date"].dt.month_name()
    dim_date_df["day_of_week"] = dim_date_df["date"].dt.dayofweek
    dim_date_df["day_name"] = dim_date_df["date"].dt.day_name()
    dim_date_df["is_weekend"] = dim_date_df["day_of_week"].isin([5, 6])
    dim_date_df["quarter"] = dim_date_df["date"].dt.quarter

    con.register("dim_date_df", dim_date_df)
    con.execute("INSERT INTO dim_date SELECT * FROM dim_date_df")
    con.unregister("dim_date_df")

def build_dim_host(con: duckdb.DuckDBPyConnection, listings: pd.DataFrame) -> None:
    cols = ["host_id", "host_since", "host_tenure_years", "host_is_superhost",
            "host_response_rate", "host_listings_count"]
    dim_host_df = listings[cols].drop_duplicates(subset="host_id").copy()
    dim_host_df["host_since"] = pd.to_datetime(dim_host_df["host_since"], errors="coerce")
    dim_host_df["host_is_superhost"] = dim_host_df["host_is_superhost"].map({"t": True, "f": False})

    con.register("dim_host_df", dim_host_df)
    con.execute("INSERT INTO dim_host SELECT * FROM dim_host_df")
    con.unregister("dim_host_df")

def build_dim_neighbourhood(con: duckdb.DuckDBPyConnection, listings: pd.DataFrame) -> None:
    cols = ["neighbourhood_cleansed", "neighbourhood_median_price",
            "neighbourhood_avg_rating", "neighbourhood_listing_count"]
    dim_neighbourhood_df = listings[cols].drop_duplicates(subset="neighbourhood_cleansed")

    con.register("dim_neighbourhood_df", dim_neighbourhood_df)
    con.execute("INSERT INTO dim_neighbourhood SELECT * FROM dim_neighbourhood_df")
    con.unregister("dim_neighbourhood_df")

def build_dim_listing(con: duckdb.DuckDBPyConnection, listings: pd.DataFrame) -> None:
    listings = listings.copy()
    listings["bathrooms_numeric"] = get_bathroom_column(listings)

    cols = ["id", "name", "host_id", "neighbourhood_cleansed", "latitude", "longitude",
            "room_type", "property_type_group", "accommodates", "bedrooms",
            "bathrooms_numeric", "minimum_nights", "maximum_nights"]
    dim_listing_df = listings[cols].rename(
        columns={"id": "listing_id", "bathrooms_numeric": "bathrooms"}
    )

    con.register("dim_listing_df", dim_listing_df)
    con.execute("INSERT INTO dim_listing SELECT * FROM dim_listing_df")
    con.unregister("dim_listing_df")

def build_fact_listing_snapshot(con: duckdb.DuckDBPyConnection, listings: pd.DataFrame) -> None:
    cols = ["id", "price_clean", "price_is_outlier", "occupancy_rate",
            "estimated_annual_revenue", "review_count_computed", "reviews_per_month",
            "price_per_bedroom", "is_potential_duplicate", "coord_outside_expected_bbox"]
    fact_df = listings[cols].rename(columns={
        "id": "listing_id",
        "price_clean": "price",
        "review_count_computed": "review_count"
    })

    con.register("fact_listing_snapshot_df", fact_df)
    con.execute("INSERT INTO fact_listing_snapshot SELECT * FROM fact_listing_snapshot_df")
    con.unregister("fact_listing_snapshot_df")

def build_fact_calendar_daily(con: duckdb.DuckDBPyConnection) -> None:
    """Load daily calendar data into the fact table"""
    con.execute(f"""
        INSERT INTO fact_calendar_daily
        SELECT
            c.listing_id,
            c.date,
            TRY_CAST(regexp_replace(c.price, '[^0-9.]', '', 'g') AS DOUBLE) AS price,
            (c.available = 't') AS available
        FROM read_csv_auto('{RAW_DIR / "calendar.csv"}') c
        JOIN dim_listing d
            ON c.listing_id = d.listing_id
    """)

def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()    # remove existing database before rebuilding

    con = duckdb.connect(str(DB_PATH))
    con.execute(SCHEMA_PATH.read_text())

    listings = pd.read_csv(PROCESSED_DIR / "listings_master.csv", low_memory=False)

    build_dim_date(con)
    build_dim_host(con, listings)
    build_dim_neighbourhood(con, listings)
    build_dim_listing(con, listings)
    build_fact_listing_snapshot(con, listings)
    build_fact_calendar_daily(con)

    print("Star schema built. Row counts:")
    for table in ["dim_host", "dim_neighbourhood", "dim_listing", "dim_date",
                  "fact_listing_snapshot", "fact_calendar_daily"]:
        count = con.sql(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:25s} {count:>10,}")

    orphans = con.sql("""
        SELECT COUNT(*) FROM fact_listing_snapshot f
        LEFT JOIN dim_listing d ON f.listing_id = d.listing_id
        WHERE d.listing_id IS NULL
    """).fetchone()[0]
    print(f"\nfact_listing_snapshot rows with no matching dim_listing: {orphans}")

    con.close()
    print(f"\nSaved: {DB_PATH}")

if __name__ == "__main__":
    main()