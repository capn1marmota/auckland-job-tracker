import requests
import pandas as pd
import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

APP_ID  = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

BASE_URL = "https://api.adzuna.com/v1/api/jobs/nz/search"

KEYWORDS = [
    "data analyst",
    "business analyst",
    "reporting analyst",
    "sql analyst",
    "junior analyst",
    "finance analyst",
    "operations analyst",
    "power bi",
]

def fetch_adzuna_jobs(keywords: list, location="Auckland", pages=3):
    all_jobs = []

    for keyword in keywords:
        print(f"\nSearching Adzuna: '{keyword}'...")

        for page in range(1, pages + 1):
            params = {
                "app_id":        APP_ID,
                "app_key":       APP_KEY,
                "results_per_page": 50,
                "what":          keyword,
                "where":         location,
                "content-type":  "application/json",
                "sort_by":       "date",
            }

            try:
                r = requests.get(
                    f"{BASE_URL}/{page}",
                    params=params,
                    timeout=15
                )
                r.raise_for_status()
                data = r.json()
                results = data.get("results", [])

                if not results:
                    break

                for job in results:
                    salary_min = job.get("salary_min", None)
                    salary_max = job.get("salary_max", None)
                    all_jobs.append({
                        "title":        job.get("title", ""),
                        "company":      job.get("company", {}).get("display_name", ""),
                        "location":     job.get("location", {}).get("display_name", ""),
                        "salary_min":   round(salary_min) if salary_min else None,
                        "salary_max":   round(salary_max) if salary_max else None,
                        "category":     job.get("category", {}).get("label", ""),
                        "contract_type":job.get("contract_type", ""),
                        "date_posted":  job.get("created", "")[:10],
                        "description":  job.get("description", "")[:400],
                        "url":          job.get("redirect_url", ""),
                        "keyword":      keyword,
                        "source":       "adzuna",
                        "scraped_at":   datetime.now().isoformat(),
                    })

                print(f"  Page {page}: {len(results)} results (total so far: {len(all_jobs)})")
                time.sleep(1)

            except Exception as e:
                print(f"  Error on page {page}: {e}")
                break

    df = pd.DataFrame(all_jobs)
    if not df.empty:
        df.drop_duplicates(subset=["title", "company"], inplace=True)
        df.reset_index(drop=True, inplace=True)
    return df


def preview_salary_data(df):
    """Quick insight into what salary data we captured"""
    has_salary = df[df["salary_min"].notna()]
    print(f"\n── SALARY DATA ──")
    print(f"Jobs with salary info: {len(has_salary)} / {len(df)}")
    if not has_salary.empty:
        print(f"Average min salary: ${has_salary['salary_min'].mean():,.0f}")
        print(f"Average max salary: ${has_salary['salary_max'].mean():,.0f}")
        print("\nTop roles by salary:")
        print(has_salary[["title", "company", "salary_min", "salary_max"]]
              .sort_values("salary_min", ascending=False)
              .head(10).to_string(index=False))


if __name__ == "__main__":
    if not APP_ID or not APP_KEY:
        print("❌ Missing ADZUNA_APP_ID or ADZUNA_APP_KEY in .env file")
        print("   Register free at: https://developer.adzuna.com")
        exit(1)

    df = fetch_adzuna_jobs(KEYWORDS)

    if not df.empty:
        output = f"raw/adzuna_jobs_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(output, index=False)
        print(f"\n✅ {len(df)} unique jobs saved to {output}")
        preview_salary_data(df)
    else:
        print("\n⚠️  No jobs returned. Check your API credentials in .env")
