# Airbnb Analytics Platform - Data Engineer Intern Assignment

This is my submission for the Expernetic Data Engineer Intern technical assessment. 
I'm analysing the Edinburgh, Scotland Airbnb market using the public Inside Airbnb dataset. 

## Why Edinburgh, why one city
Given the 1 week timeframe, I chose to go deep on a single city rather than spread thin across several. Edinburgh has a manageable dataset size with full file coverage (listing, calendar, reviews, neighbourhoods), which let me focus on data quality and analysis depth instead of spending time standardizing and comparing data across multiple cities. 

## What's in this repo
- `src/` - pipeline code (ingestion, cleaning, modeling)
- `sql/` - SQL queries against the DuckDB analytical model
- `notebooks/` - exploratory analysis and statistical testing
- `data/` - raw and processed data 
- `reports/` - final PDF report and figures
- `docs/decision_log.md` - engineering decisions and trade-offs made along the way 

## Reproducibility
1. Clone the repo
2. Create a virtual environment and install dependencies:
    python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
3. Download the dataset: python -m src.ingestion.download_data
4. Generate the profiling report: python -m src.ingestion.profile_data