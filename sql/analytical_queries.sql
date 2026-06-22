-- Example analytical queries for the Edinburgh Airbnb dataset

-- 1. Average price by room type and superhost status
SELECT
    l.room_type,
    h.host_is_superhost,
    ROUND(AVG(f.price), 2) AS avg_price,
    COUNT(*) AS n_listings
FROM fact_listing_snapshot f
JOIN dim_listing l ON f.listing_id = l.listing_id
JOIN dim_host h ON l.host_id = h.host_id
GROUP BY l.room_type, h.host_is_superhost
ORDER BY l.room_type, h.host_is_superhost;

-- 2. Top 10 neighbourhoods by median price
SELECT
    neighbourhood_cleansed,
    neighbourhood_median_price,
    neighbourhood_listing_count
FROM dim_neighbourhood
ORDER BY neighbourhood_median_price DESC
LIMIT 10;

-- 3. Weekday vs weekend price comparison 
SELECT
    d.is_weekend,
    ROUND(AVG(CASE WHEN c.available = false THEN 1 ELSE 0 END), 3) AS booked_rate,
    COUNT(*) AS n_observations
FROM fact_calendar_daily c
JOIN dim_date d ON c.date = d.date
GROUP BY d.is_weekend;

-- 4. Average occupancy rate by neighbourhood
SELECT
    l.neighbourhood_cleansed,
    ROUND(AVG(f.occupancy_rate), 3) AS avg_occupancy_rate,
    COUNT(*) AS n_listings
FROM fact_listing_snapshot f
JOIN dim_listing l ON f.listing_id = l.listing_id
GROUP BY l.neighbourhood_cleansed
ORDER BY avg_occupancy_rate DESC
LIMIT 10;

-- 5. Price outliers by neighbourhood
SELECT
    l.neighbourhood_cleansed,
    SUM(CASE WHEN f.price_is_outlier THEN 1 ELSE 0 END) AS n_outliers,
    COUNT(*) AS n_listings,
    ROUND(100.0 * SUM(CASE WHEN f.price_is_outlier THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_outliers
FROM fact_listing_snapshot f
JOIN dim_listing l ON f.listing_id = l.listing_id
GROUP BY l.neighbourhood_cleansed
HAVING COUNT(*) > 20  -- exclude very small neighbourhoods
ORDER BY pct_outliers DESC
LIMIT 10;