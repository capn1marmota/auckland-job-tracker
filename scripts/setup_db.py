import os
import json
import math
import glob
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))


def clean_record(record: dict) -> dict:
    """Replace every NaN / inf / float nan with None so JSON is happy."""
    cleaned = {}
    for k, v in record.items():
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            cleaned[k] = None
        elif v != v:          # NaN check via self-inequality
            cleaned[k] = None
        elif str(v) in ("nan", "NaT", "None", "null"):
            cleaned[k] = None
        else:
            cleaned[k] = v
    return cleaned


def upload_adzuna_jobs():
    files = sorted(glob.glob("raw/adzuna_jobs_*.csv"))
    if not files:
        print("No Adzuna CSV found. Run fetch_seek.py first.")
        return

    df = pd.read_csv(files[-1])

    # Convert date column
    df["date_posted"] = pd.to_datetime(
        df["date_posted"], errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    # Convert numeric salary columns — NaN becomes None
    for col in ["salary_min", "salary_max"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Convert entire dataframe NaN → None
    df = df.where(pd.notna(df), other=None)

    records = [clean_record(r) for r in df.to_dict(orient="records")]

    # Final safety check — serialise to JSON and back to guarantee no NaN
    records = json.loads(json.dumps(records, default=lambda x: None))

    print(f"Uploading {len(records)} job postings to Supabase...")
    batch_size = 100
    uploaded = 0

    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        try:
            supabase.table("job_postings").upsert(
                batch, on_conflict="title,company,source"
            ).execute()
            uploaded += len(batch)
            print(f"  Batch {i // batch_size + 1}: {uploaded} records uploaded")
        except Exception as e:
            print(f"  Batch error: {e}")
            # Print first offending record to diagnose
            for r in batch:
                for k, v in r.items():
                    if isinstance(v, float):
                        print(f"    Suspect field → {k}: {v}")
                break

    print(f"\nDone — {uploaded} job postings in Supabase")


def upload_mbie_monthly():
    df = pd.read_csv("raw/mbie_monthly_series.csv")
    df.columns = [c.strip().lower().replace("-", "_").replace(" ", "_")
                  for c in df.columns]

    upload_df = pd.DataFrame({
        "actual_date":   pd.to_datetime(
            df["actual_date"], dayfirst=True, errors="coerce"
        ).dt.strftime("%Y-%m-%d"),
        "totals":        pd.to_numeric(df["totals"], errors="coerce"),
        "annual_change": pd.to_numeric(df["annual_change"], errors="coerce"),
        "skilled_index": pd.to_numeric(
            df.get("skilledindex", df.get("skilled_index")), errors="coerce"
        ),
    })

    upload_df = upload_df.where(pd.notna(upload_df), other=None)
    records = json.loads(
        json.dumps(upload_df.to_dict(orient="records"), default=lambda x: None)
    )

    print(f"Uploading {len(records)} MBIE monthly rows to Supabase...")
    try:
        supabase.table("mbie_monthly").upsert(
            records, on_conflict="actual_date"
        ).execute()
        print(f"Done — {len(records)} MBIE rows in Supabase")
    except Exception as e:
        print(f"Error: {e}")


def verify():
    jobs = supabase.table("job_postings").select("id", count="exact").execute()
    mbie = supabase.table("mbie_monthly").select("id", count="exact").execute()
    print(f"\n── SUPABASE VERIFICATION ──")
    print(f"job_postings : {jobs.count} rows")
    print(f"mbie_monthly : {mbie.count} rows")


if __name__ == "__main__":
    upload_adzuna_jobs()
    upload_mbie_monthly()
    verify()