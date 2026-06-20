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
Pinned the Edinburgh dataset to the 2025-09-21 snapshot in `download_data.py` instead automatically using the latest available dataset.

Inside Airbnb updates its datasets periodically. Without pinning a specific snapshot, rerunning the pipeline in the future could produce different results because the underlying data may have changed. Pinning the snapshot helps ensure that analyses and report findings remain reproducible. 

The trade-off is that the project will not automatically use newer Aitbnb data. Updating to a newer snapshot requires changing the configured snapshot date and rerunning the pipeline. 

## Data  Quality Checks
For outlier detection, I used the IQR (1.5x rule) method instead of z-scores. Airbnb prices are heavily risk-skewed, with a small number of very expensive listings, so a method that is less sensitive to extreme values felt more appropriate. 

For duplicate detection, I checked for: 
    - Fully duplicate rows
    - Repeated listing IDs
    - Potential duplicate listings from the same host using name similarity 

I used Python's built-in `difflib` library for the fuzzy matching step. Since comparisons are only made within each host's listings rather than across the entire dataset, a dedicated package such as `rapidfuzz` would have addded extra complexity without much benefit.

For location validation, I used an Edinburgh-specific latitude and longitude range rather than a generic coordinate check. This makes it easier to identify listings that have valid coordinates but are clearly outside the city and may indicate data quality issues. 

## Cleaning Decisions
Dropped 11 listings with missing or non-positive prices. Price is required for most of the planned analysis, so keeping these rows would have limited their usefulness. All dropped rows were logged to `reports/dropped_rows_log.csv` to keep the cleaning process transparent. 

For price outliers, minimum night outliers, potential duplicate listings, and listings outside the expected Edinburgh coordinate range, I chose to flag them rather than remove them. In each case, the records could represent genuine data rather tha errors. For example, a very expensive listing could be a luxury property, a high minimum stay could indicate a long-term rental, and a flagged duplicate could simply be multiple units managed by the same host. Keeping these records and adding flag columns preserves the data while allowing later analysis to decide whether they should be excluded. 

Grouped `property_type` into five broader categories (entire place, private room, shared room, hotel room, and other) to make analysis and visualizations easier to interpret. The original `property_type` column was kept unchanged so that no information was lost. 