# Edinburgh Listings Data Quality Report

## Duplicate Detection
- Fully duplicated rows: 0
- Duplicated listing IDs: 0
- Near-duplicate listings: 95

## Outlier Summary (IQR method, 1.5x rule)
| Field | # Outliers | % Outliers | Min | Max |
|---|---|---|---|---|
| price | 362 | 7.35 | 18.0 | 18465.0 |
| availability 365 | 0 | 0.0 | 0 | 365 |
| number_of_reviews | 338 | 6.85 | 0 | 1541 |
| minimum_nights | 175 | 3.55 | 1 | 365 |

## Validation Rule Failures
| Rule | # Rows Failing |
|---|---|
| price missing or <= 0 | 11 |
| latitude outside Edinburgh bounding box | 0 |
| longitude outside Edinburgh bounding box | 59 |
| minimum_nights < 1 | 0 |
| maximum_nights < minimum_nights | 0 |
| availability_365 outside [0, 365] | 0 |
| number_of_reviews negative | 0 |
