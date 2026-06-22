-- Start schema for Edinburgh Airbnb dataset

CREATE TABLE dim_host (
    host_id BIGINT PRIMARY KEY,
    host_since DATE,
    host_tenure_years DOUBLE,
    host_is_superhost BOOLEAN,
    host_response_rate VARCHAR,
    host_listings_count INTEGER   
);

CREATE TABLE dim_neighbourhood (
    neighbourhood_cleansed VARCHAR PRIMARY KEY,
    neighbourhood_median_price DOUBLE,
    neighbourhood_avg_rating DOUBLE, 
    neighbourhood_listing_count INTEGER
);

CREATE TABLE dim_listing (
    listing_id BIGINT PRIMARY KEY,
    name VARCHAR,
    host_id BIGINT REFERENCES dim_host(host_id),
    neighbourhood_cleansed VARCHAR REFERENCES dim_neighbourhood(neighbourhood_cleansed),
    latitude DOUBLE,
    longitude DOUBLE,
    room_type VARCHAR,
    property_type_group VARCHAR,
    accommodates INTEGER,
    bedrooms DOUBLE,
    bathrooms DOUBLE,
    minimum_nights INTEGER,
    maximum_nights INTEGER
);

CREATE TABLE dim_date (
    date DATE PRIMARY KEY,
    year INTEGER,
    month INTEGER,
    month_name VARCHAR,
    day_of_week INTEGER,
    day_name VARCHAR,
    is_weekend BOOLEAN,
    quarter INTEGER
);

CREATE TABLE fact_listing_snapshot (
    listing_id BIGINT PRIMARY KEY REFERENCES dim_listing(listing_id),
    price DOUBLE,
    price_is_outlier BOOLEAN,
    occupancy_rate DOUBLE,
    estimated_annual_revenue DOUBLE,
    review_count INTEGER,
    reviews_per_month DOUBLE,
    price_per_bedroom DOUBLE, 
    is_potential_duplicate BOOLEAN,
    coord_outside_expected_bbox BOOLEAN
);

CREATE TABLE fact_calendar_daily (
    listing_id BIGINT REFERENCES dim_listing(listing_id),
    date DATE REFERENCES dim_date(date),
    price DOUBLE,
    available BOOLEAN,
    PRIMARY KEY (listing_id, date)
);