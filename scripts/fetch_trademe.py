import requests
from requests_oauthlib import OAuth1
import pandas as pd
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

auth = OAuth1(
    os.getenv("TRADEME_CONSUMER_KEY"),
    os.getenv("TRADEME_CONSUMER_SECRET"),
    os.getenv("TRADEME_OAUTH_TOKEN"),
    os.getenv("TRADEME_OAUTH_SECRET"),
)

# Sandbox base URL — switch to trademe.co.nz once you get production approval
BASE_URL = "https://api.tmsandbox.co.nz/v1"

KEYWORDS = [
    "data analyst", "business analyst", "reporting analyst",
    "junior analyst", "finance analyst", "power bi", "sql",
]

def fetch_trademe_jobs(keywords: list):
    all_jobs = []

    for keyword in keywords:
        print(f"\nSearching Trade Me: '{keyword}'...")
        params = {
            "search_string": keyword,
            "region":        1,       # Auckland
            "rows":          50,
            "sort_order":    "Default",
        }
        try:
            r = requests.get(
                f"{BASE_URL}/Search/Jobs.json",
                auth=auth, params=params, timeout=15
            )
            r.raise_for_status()
            data = r.json()
            listings = data.get("List", [])
            print(f"  Found {len(listings)} listings")

            for job in listings:
                all_jobs.append({
                    "title":         job.get("Title", ""),
                    "company":       job.get("CompanyName", ""),
                    "location":      job.get("Region", ""),
                    "salary_min":    job.get("PayBandMinimum", None),
                    "salary_max":    job.get("PayBandMaximum", None),
                    "job_type":      job.get("JobType", ""),
                    "listing_id":    str(job.get("ListingId", "")),
                    "date_posted":   job.get("StartDate", "")[:10],
                    "url":           f"https://www.trademe.co.nz/a/jobs/listing/{job.get('ListingId','')}",
                    "keyword":       keyword,
                    "source":        "trademe",
                    "scraped_at":    datetime.now().isoformat(),
                })
            time.sleep(1)

        except Exception as e:
            print(f"  Error: {e}")

    df = pd.DataFrame(all_jobs)
    if not df.empty:
        df.drop_duplicates(subset=["listing_id"], inplace=True)
    return df


if __name__ == "__main__":
    df = fetch_trademe_jobs(KEYWORDS)

    if not df.empty:
        output = f"raw/trademe_jobs_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(output, index=False)
        print(f"\n✅ {len(df)} Trade Me jobs saved to {output}")
        print(df[["title", "company", "salary_min", "salary_max"]].head(10))
    else:
        print("\n⚠️  No results — sandbox may have limited data, that's normal")