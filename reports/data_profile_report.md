# Edinburgh Airbnb Data Profile Report

## listings.csv

- Rows: 4,936
- Columns: 79

| Column | Dtype | Null % | Unique Values |
|---|---|---|---|
| id | int64 | 0.0% | 4,936 |
| listing_url | object | 0.0% | 4,936 |
| scrape_id | int64 | 0.0% | 1 |
| last_scraped | object | 0.0% | 1 |
| source | object | 0.0% | 1 |
| name | object | 0.0% | 4,885 |
| description | object | 1.1% | 4,568 |
| neighborhood_overview | object | 43.8% | 2,433 |
| picture_url | object | 0.0% | 4,899 |
| host_id | int64 | 0.0% | 3,037 |
| host_url | object | 0.0% | 3,037 |
| host_name | object | 0.0% | 1,578 |
| host_since | object | 0.0% | 2,152 |
| host_location | object | 19.2% | 168 |
| host_about | object | 42.4% | 1,521 |
| host_response_time | object | 4.6% | 4 |
| host_response_rate | object | 4.6% | 57 |
| host_acceptance_rate | object | 3.7% | 85 |
| host_is_superhost | object | 2.9% | 2 |
| host_thumbnail_url | object | 0.0% | 2,915 |
| host_picture_url | object | 0.0% | 2,915 |
| host_neighbourhood | object | 69.7% | 43 |
| host_listings_count | float64 | 0.0% | 62 |
| host_total_listings_count | float64 | 0.0% | 80 |
| host_verifications | object | 0.0% | 6 |
| host_has_profile_pic | object | 0.0% | 2 |
| host_identity_verified | object | 0.0% | 2 |
| neighbourhood | object | 43.8% | 1 |
| neighbourhood_cleansed | object | 0.0% | 111 |
| neighbourhood_group_cleansed | float64 | 100.0% | 0 |
| latitude | float64 | 0.0% | 3,983 |
| longitude | float64 | 0.0% | 4,317 |
| property_type | object | 0.0% | 50 |
| room_type | object | 0.0% | 4 |
| accommodates | int64 | 0.0% | 16 |
| bathrooms | float64 | 0.1% | 17 |
| bathrooms_text | object | 0.1% | 26 |
| bedrooms | float64 | 0.1% | 13 |
| beds | float64 | 0.4% | 21 |
| amenities | object | 0.0% | 4,784 |
| price | object | 0.2% | 604 |
| minimum_nights | int64 | 0.0% | 33 |
| maximum_nights | int64 | 0.0% | 102 |
| minimum_minimum_nights | float64 | 0.2% | 33 |
| maximum_minimum_nights | float64 | 0.2% | 53 |
| minimum_maximum_nights | float64 | 0.2% | 92 |
| maximum_maximum_nights | float64 | 0.2% | 90 |
| minimum_nights_avg_ntm | float64 | 0.0% | 149 |
| maximum_nights_avg_ntm | float64 | 0.0% | 372 |
| calendar_updated | float64 | 100.0% | 0 |
| has_availability | object | 0.2% | 1 |
| availability_30 | int64 | 0.0% | 31 |
| availability_60 | int64 | 0.0% | 61 |
| availability_90 | int64 | 0.0% | 91 |
| availability_365 | int64 | 0.0% | 366 |
| calendar_last_scraped | object | 0.0% | 1 |
| number_of_reviews | int64 | 0.0% | 585 |
| number_of_reviews_ltm | int64 | 0.0% | 134 |
| number_of_reviews_l30d | int64 | 0.0% | 22 |
| availability_eoy | int64 | 0.0% | 103 |
| number_of_reviews_ly | int64 | 0.0% | 134 |
| estimated_occupancy_l365d | int64 | 0.0% | 79 |
| estimated_revenue_l365d | float64 | 0.2% | 2,315 |
| first_review | object | 5.8% | 2,050 |
| last_review | object | 5.8% | 422 |
| review_scores_rating | float64 | 5.8% | 119 |
| review_scores_accuracy | float64 | 5.8% | 107 |
| review_scores_cleanliness | float64 | 5.8% | 124 |
| review_scores_checkin | float64 | 5.8% | 108 |
| review_scores_communication | float64 | 5.8% | 101 |
| review_scores_location | float64 | 5.8% | 107 |
| review_scores_value | float64 | 5.8% | 131 |
| license | object | 75.4% | 1,110 |
| instant_bookable | object | 0.0% | 2 |
| calculated_host_listings_count | int64 | 0.0% | 29 |
| calculated_host_listings_count_entire_homes | int64 | 0.0% | 29 |
| calculated_host_listings_count_private_rooms | int64 | 0.0% | 13 |
| calculated_host_listings_count_shared_rooms | int64 | 0.0% | 4 |
| reviews_per_month | float64 | 5.8% | 818 |

## calendar.csv

- Rows: 1,801,640
- Columns: 7

| Column | Dtype | Null % | Unique Values |
|---|---|---|---|
| listing_id | int64 | 0.0% | 4,936 |
| date | object | 0.0% | 365 |
| available | object | 0.0% | 2 |
| price | float64 | 100.0% | 0 |
| adjusted_price | float64 | 100.0% | 0 |
| minimum_nights | int64 | 0.0% | 61 |
| maximum_nights | int64 | 0.0% | 341 |

## reviews.csv

- Rows: 559,087
- Columns: 6

| Column | Dtype | Null % | Unique Values |
|---|---|---|---|
| listing_id | int64 | 0.0% | 4,650 |
| id | int64 | 0.0% | 559,087 |
| date | object | 0.0% | 4,917 |
| reviewer_id | int64 | 0.0% | 522,517 |
| reviewer_name | object | 0.0% | 69,150 |
| comments | object | 0.0% | 547,075 |

## neighbourhoods.csv

- Rows: 111
- Columns: 2

| Column | Dtype | Null % | Unique Values |
|---|---|---|---|
| neighbourhood_group | float64 | 100.0% | 0 |
| neighbourhood | object | 0.0% | 111 |
