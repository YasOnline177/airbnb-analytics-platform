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