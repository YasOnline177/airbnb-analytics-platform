"""
Downloads the Edinburgh Inside Airbnb dataset.
"""

import gzip
import shutil
from pathlib import Path

import requests

CITY = "edinburgh"
SNAPSHOT_DATE = "2025-09-21"
BASE_URL = f"https://data.insideairbnb.com/united-kingdom/scotland/{CITY}/{SNAPSHOT_DATE}"

FILES = {
    "listings.csv.gz": f"{BASE_URL}/data/listings.csv.gz",
    "calendar.csv.gz": f"{BASE_URL}/data/calendar.csv.gz",
    "reviews.csv.gz": f"{BASE_URL}/data/reviews.csv.gz",
    "neighbourhoods.csv": f"{BASE_URL}/visualisations/neighbourhoods.csv",
    "neighbourhoods.geojson": f"{BASE_URL}/visualisations/neighbourhoods.geojson",
}

RAW_DIR = Path("data/raw/edinburgh")

def download_file(url: str, destination: Path) -> None:
    print(f"Downloading {url} -> {destination}")
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    destination.write_bytes(response.content)

def extract_gz(gz_path: Path) -> Path:
    csv_path = gz_path.with_suffix("")  # strips the .gz
    print(f"Extracting {gz_path} -> {csv_path}")
    with gzip.open(gz_path, "rb") as f_in, open(csv_path, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    return csv_path

def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for filename, url in FILES.items():
        destination = RAW_DIR / filename
        download_file(url, destination)
        if filename.endswith(".gz"):
            extract_gz(destination)

    print("\nDone. Files in data/raw/edinburgh/:")
    for f in sorted(RAW_DIR.iterdir()):
        size_kb = f.stat().st_size / 1024
        print(f"  {f.name:30s} {size_kb:>10.1f} KB")

if __name__ == "__main__":
    main()