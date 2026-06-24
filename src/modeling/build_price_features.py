"""
Builds the feature matrix for the price prediction models.
"""

import numpy as np
import pandas as pd

AMENITY_KEYWORDS = {
    "has_wifi": "wifi",
    "has_kitchen": "kitchen",
    "has_parking": "free parking",
    "has_washer": "washer",
    "has_aircon": "air conditioning",
    "has_workspace": "dedicated workspace",
    "has_elevator": "elevator",
    "has_pool_or_hottub": "pool|hot tub",
}

TOP_N_NEIGHBOURHOODS = 15


def add_amenity_flags(df: pd.DataFrame) -> pd.DataFrame:
    # Create binary amenity flags from the amenities text field
    amenities_lower = df["amenities"].astype(str).str.lower()
    for flag_col, keyword in AMENITY_KEYWORDS.items():
        df[flag_col] = amenities_lower.str.contains(keyword, regex=True).astype(int)
    return df


def encode_neighbourhood(df: pd.DataFrame) -> pd.DataFrame:
    # Keep only the most common neighbourhoods and group the rest as "Other"
    top_neighbourhoods = df["neighbourhood_cleansed"].value_counts().head(TOP_N_NEIGHBOURHOODS).index
    df["neighbourhood_top"] = np.where(
        df["neighbourhood_cleansed"].isin(top_neighbourhoods),
        df["neighbourhood_cleansed"],
        "Other",
    )
    return df


def build_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    df = df.copy()
    df = add_amenity_flags(df)
    df = encode_neighbourhood(df)

    # Preserve listings with no reviews by imputing the median score and adding an indicator flag
    df["has_no_reviews"] = df["review_scores_rating"].isna().astype(int)
    df["review_scores_rating"] = df["review_scores_rating"].fillna(df["review_scores_rating"].median())
    df["host_is_superhost"] = (df["host_is_superhost"].map({"t": 1, "f": 0}).fillna(0).astype(int))

    df["is_entire_home"] = (df["room_type"] == "Entire home/apt").astype(int)
    # Interaction term between property capacity and entire-home listings
    df["entire_home_x_accommodates"] = df["is_entire_home"] * df["accommodates"]

    before = len(df)
    df = df.dropna(subset=["host_tenure_years", "bedrooms", "bathroom_numeric", "price_clean"])
    print(f"Dropped {before - len(df)} rows with missing core fields for modeling.")

    # Exclude neighbourhood_median_price to avoid target leakage
    numeric_features = [
        "accommodates", "bedrooms", "bathroom_numeric", "minimum_nights",
        "review_scores_rating", "host_tenure_years", "distance_from_centre_km",
        "entire_home_x_accommodates",
    ]
    binary_features = ["host_is_superhost", "has_no_reviews"] + list(AMENITY_KEYWORDS.keys())

    room_type_dummies = pd.get_dummies(df["room_type"], prefix="room", drop_first=True)
    property_type_dummies = pd.get_dummies(df["property_type_group"], prefix="ptype", drop_first=True)
    neighbourhood_dummies = pd.get_dummies(df["neighbourhood_top"], prefix="nbhd", drop_first=True)

    X = pd.concat([
        df[numeric_features],
        df[binary_features].astype(int),
        room_type_dummies.astype(int),
        property_type_dummies.astype(int),
        neighbourhood_dummies.astype(int),
    ], axis=1)

    y = np.log1p(df["price_clean"])

    return X, y