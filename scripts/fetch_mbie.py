import requests
import pandas as pd
import os

BASE = "https://www.mbie.govt.nz/assets/Data-Files/Business-employment/Employment-skills/Labour-market-reports"

MBIE_FILES = {
    # Monthly (CSV)
    "monthly_series": f"{BASE}/jobs-online-monthly/jol-monthly-unadjusted-series-from-may-2007-january-2026.csv",

    # Quarterly (XLSX)
    "all_vacancies":     f"{BASE}/Jobs-online-quarterly/jobs-online-all-unadjusted-december-2025-quarter-ext.xlsx",
    "by_industry":       f"{BASE}/Jobs-online-quarterly/jobs-online-industry-unadjusted-december-2025-quarterly.xlsx",
    "by_occupation":     f"{BASE}/Jobs-online-quarterly/jobs-online-occupation-unadjusted-december-2025-quarter.xlsx",
    "skilled_unskilled": f"{BASE}/Jobs-online-quarterly/jobs-online-skilled-unskilled-unadjusted-december-2025-quarter.xlsx",
    "by_skill":          f"{BASE}/Jobs-online-quarterly/jobs-online-skill-level-unadjusted-december-2025-quarter.xlsx",

    # Consolidated (best single file — all quarterly data in one CSV)
    "consolidated":      f"{BASE}/Jobs-online-quarterly/jobs-online-all-unadjusted-quarterly-data-consolidated-dec-2025.csv",

    # Detailed occupational breakdown (CSV)
    "detailed_occ":      f"{BASE}/Jobs-online-quarterly/jobs-online-four-digit-december-2025.csv",
}

def download_mbie_data(output_dir="raw"):
    os.makedirs(output_dir, exist_ok=True)
    headers = {"User-Agent": "Mozilla/5.0 (research project)"}

    for name, url in MBIE_FILES.items():
        ext = url.split(".")[-1]
        filename = f"{output_dir}/mbie_{name}.{ext}"
        print(f"Downloading: {name}...")
        try:
            r = requests.get(url, headers=headers, timeout=30)
            r.raise_for_status()
            with open(filename, "wb") as f:
                f.write(r.content)
            print(f"  ✓ Saved: {filename} ({len(r.content)/1024:.1f} KB)")
        except Exception as e:
            print(f"  ✗ Error on {name}: {e}")

def load_and_preview():
    df_monthly = pd.read_csv("raw/mbie_monthly_series.csv")
    print("\n── MONTHLY SERIES (last 10 rows) ──")
    print(df_monthly.tail(10))
    print(f"Shape: {df_monthly.shape}")

    df_consolidated = pd.read_csv("raw/mbie_consolidated.csv")
    print("\n── CONSOLIDATED QUARTERLY (columns) ──")
    print(df_consolidated.columns.tolist())
    print(df_consolidated.tail(5))

if __name__ == "__main__":
    download_mbie_data()
    load_and_preview()
    print("\n✅ MBIE data downloaded and ready.")