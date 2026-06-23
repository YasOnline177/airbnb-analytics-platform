# Decision Log

## Scope

Decided to focus on a single city (Edinburgh) rather than analyze multiple cities. Given the available time, I felt it was more valuable to build a solid data engineering pipeline and produce deeper analysis for one market than to spend time making datasets from different cities comparable.

My priorities for this project are:

1. Dataset familiarisation
2. Data ingestion and cleaning
3. Data modeling
4. Exploratory data analysis
5. Statistical testing
6. One machine learning experiment (price prediction)

## Snapshot Pinning

Pinned the Edinburgh dataset to the 2025-09-21 snapshot in `download_data.py` instead of automatically using the latest available dataset.

Inside Airbnb updates its datasets periodically. Without pinning a specific snapshot, rerunning the pipeline in the future could produce different results because the underlying data may have changed. Pinning the snapshot helps ensure that analyses and report findings remain reproducible.

The trade-off is that the project will not automatically use newer Airbnb data. Updating to a newer snapshot requires changing the configured snapshot date and rerunning the pipeline.

## Data Quality Checks

For outlier detection, I used the IQR (1.5x rule) method instead of z-scores. Airbnb prices are heavily right-skewed, with a small number of very expensive listings, so a method that is less sensitive to extreme values felt more appropriate.

For duplicate detection, I checked for:

- Fully duplicate rows
- Repeated listing IDs
- Potential duplicate listings from the same host using name similarity

I used Python's built-in `difflib` library for the fuzzy matching step. Since comparisons are only made within each host's listings rather than across the entire dataset, a dedicated package such as `rapidfuzz` would have added extra complexity without much benefit.

For location validation, I used an Edinburgh-specific latitude and longitude range rather than a generic coordinate check. This makes it easier to identify listings that have valid coordinates but are clearly outside the city and may indicate data quality issues.

## Cleaning Decisions

Dropped 11 listings with missing or non-positive prices. Price is required for most of the planned analysis, so keeping these rows would have limited their usefulness. All dropped rows were logged to `reports/dropped_rows_log.csv` to keep the cleaning process transparent.

For price outliers, minimum night outliers, potential duplicate listings, and listings outside the expected Edinburgh coordinate range, I chose to flag them rather than remove them. In each case, the records could represent genuine data rather than errors. For example, a very expensive listing could be a luxury property, a high minimum stay could indicate a long-term rental, and a flagged duplicate could simply be multiple units managed by the same host. Keeping these records and adding flag columns preserves the data while allowing later analysis to decide whether they should be excluded.

Grouped `property_type` into five broader categories (entire place, private room, shared room, hotel room, and other) to make analysis and visualizations easier to interpret. The original `property_type` column was kept unchanged so that no information was lost.

## Calendar & Review Enrichment

Computed occupancy rate and estimated annual revenue from `calendar.csv`.

These values should be treated as estimates rather than exact figures because the Inside Airbnb calendar data does not distinguish between nights that were booked and nights that were manually blocked by the host.

Recalculated review counts from `reviews.csv` rather than relying on the `number_of_reviews` field in `listings.csv`. Comparing the two provided a useful validation check after joining the datasets.

Used DuckDB to aggregate the large `calendar.csv` dataset before loading the results into pandas. This avoided loading millions of rows into memory and made the enrichment step much faster.

## Derived Fields & Neighbourhood Aggregates

Calculated `host_tenure_years` and `reviews_per_month` relative to the dataset snapshot date (2025-09-21) rather than the current date. This ensures the results remain consistent if the pipeline is rerun in the future.

Left `reviews_per_month` as null for listings with no reviews, since a review frequency cannot be calculated without any review history. Left `price_per_bedroom` as null for listings with zero bedrooms rather than assigning an arbitrary value or dividing by zero.

Added neighbourhood-level metrics such as median price, average rating, and listing count so that individual listings can be analysed in the context of their local market.

## Star Schema Design

Built two fact tables that share the same dimensions rather than creating one large flat table:

- `fact_listing_snapshot` (one row per listing) for current listing-level metrics
- `fact_calendar_daily` (one row per listing per day) for time-based analysis such as weekday vs weekend pricing

Considered combining calendar data and listing data into a single table, but the grains do not match. Storing everything at the calendar level would duplicate listing attributes hundreds of times, while aggregating calendar data to listing level would lose the daily detail needed for later analysis and hypothesis testing.

Did not implement slowly changing dimensions (SCDs). This project uses a single Airbnb snapshot from 21 September 2025, so there is no historical data to track. Every dimension therefore represents the current state only. If additional quarterly snapshots were added in the future, dimensions such as `dim_host` and `dim_neighbourhood` could be extended with effective dates and SCD Type 2 logic to capture changes over time.

Kept `listings_master.csv` as a separate denormalized dataset alongside the star schema. The flat file is convenient for exploratory analysis in pandas, while the star schema is better suited for SQL analytics and avoids repeatedly storing neighbourhood and host-level attributes on every listing row.

## Calendar Price Data Limitation

While validating the analytical model, I found that the `price` column in `calendar.csv` was null for every row in the Edinburgh snapshot. Querying the raw file directly confirmed this was a source data issue rather than a parsing problem.

This affected two parts of the project:

1. `estimated_annual_revenue` could not be calculated from calendar prices. Instead, revenue was estimated using the listing's snapshot price multiplied by booked nights, assuming prices remain reasonably stable throughout the year.
2. The original weekday vs weekend pricing hypothesis could not be tested because no daily price information was available. This hypothesis was replaced with a neighbourhood price comparison using listing-level prices.

This limitation and workaround are documented so that results are interpreted appropriately.

## Geographic Analysis Tooling

Used latitude/longitude coordinates with matplotlib visualisations and a haversine distance calculation rather than introducing GeoPandas or Folium.

The project already had point coordinates for every listing, and the planned geographic analyses (listing density, spatial distribution of review scores, property-type clustering, and distance-from-centre pricing patterns) only required point-level calculations and visualisation. These questions could be answered effectively using pandas, NumPy, and matplotlib without additional GIS tooling.

GeoPandas was considered, but would have introduced extra dependencies and complexity for features such as spatial joins and polygon-based analysis that were not required for the current project scope. If the Open Innovation section is expanded into an interactive mapping product in future work, GIS tooling such as GeoPandas or Folium would be a natural extension.

## Temporal and Host Analysis Decisions

The Edinburgh snapshot's `calendar.csv` file contains no usable daily price data, making calendar-based price trend analysis impossible. Instead, the temporal analysis focuses on booking and availability rates by month, which are fully populated in the dataset.

The calendar data represents the year ahead of the snapshot date rather than historical activity. As a result, monthly booking rates should be interpreted as a measure of advance booking behaviour rather than historical seasonal demand.

Review volume by month was used as a separate demand proxy based on `reviews.csv`. The final month of the series was interpreted cautiously because the dataset was collected partway through the month and guests often leave reviews days or weeks after their stay, creating an artificial decline at the end of the timeline.

Hosts were segmented into three groups based on portfolio size: single-listing hosts, small operators (2–5 listings), and professional operators (6+ listings). Fixed thresholds were used instead of a clustering approach because the resulting groups are straightforward to interpret and communicate while still capturing meaningful differences in host scale.

## Statistical Test Selection

Used Mann-Whitney U instead of an independent-samples t-test for H1 and H2, and Kruskal-Wallis instead of one-way ANOVA for H4. This decision was based on patterns identified during exploratory analysis: Airbnb prices are heavily right-skewed with extreme outliers, while review scores exhibit a strong ceiling effect with most values clustered near the maximum rating. Assumptions were formally checked in the notebook before finalising the test selection.

Reported Cohen's d and epsilon-squared as additional effect size measures to satisfy the assignment requirements, but placed greater emphasis on rank-based effect sizes because the underlying data do not meet the normality assumptions required for interpreting Cohen's d in the usual way.

Used bootstrap confidence intervals for group means rather than relying on normal-theory confidence intervals. Bootstrap methods make fewer assumptions about the shape of the underlying distribution and are therefore more appropriate for the skewed variables analysed in this project.

For H4, neighbourhoods with 20 or fewer listings were excluded from the analysis. This matches the threshold used elsewhere in the project and reduces the influence of very small neighbourhood samples on the comparison.

Did not run a post-hoc pairwise comparison following the Kruskal-Wallis test. The objective was to establish whether neighbourhood price distributions differed overall, while neighbourhood rankings and geographic analysis had already identified the locations associated with higher and lower prices. A formal post-hoc procedure would be a reasonable extension for future work if specific neighbourhood pairs needed to be compared.

## Correlation & Regression Decisions

Used log1p(price) rather than raw price because listing prices are heavily right-skewed and contain extreme outliers. The transformation reduces skew and produces a more stable target for regression modelling.

Used VIF alongside the correlation matrix to assess multicollinearity. While several property-size variables are strongly correlated, the VIF results confirmed that the overlap was not severe enough to justify removing predictors from the model.

Recomputed distance_from_centre_km in this notebook rather than adding it to the processing pipeline. The feature was originally created for the geographic analysis and was only reused here once it proved useful as a pricing predictor.

Added scipy and statsmodels to requirements.txt after discovering both were being used by the analysis notebooks without being explicitly declared as project dependencies.
