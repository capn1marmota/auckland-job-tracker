# 🇳🇿 Auckland Job Market Tracker

**Live app:** https://auckland-job-tracker-escnaavkwztib2fxsq98qh.streamlit.app  
**Author:** Carlos P. Pizarro · Chilean analyst · Auckland, NZ · https://www.linkedin.com/in/carlos-patricio-pizarro-flores-7421bb231

A full end-to-end data pipeline that tracks the Auckland job market in real time — built to answer a personal question: *what skills actually pay in New Zealand, and where should a junior analyst focus?*

---

## What it does

- **Ingests** live job listings from the Adzuna API (Auckland, NZ) and NZ government labour market data from MBIE
- **Stores** everything in a cloud PostgreSQL database (Supabase)
- **Extracts** in-demand skills from job descriptions using NLP
- **Predicts** salary ranges based on skill combinations using Linear Regression
- **Visualises** the full picture in an interactive dashboard deployed on Streamlit Cloud

---

## Key findings (as of March 2026)

- Only **17% of Auckland analyst listings** advertise a salary — most NZ employers don't disclose
- Median advertised salary for analyst roles: **$130,000 NZD**
- Most in-demand skills: **Snowflake, Power BI, Python, SQL**
- **Finance analyst** roles pay ~2.5x more than entry-level data analyst roles
- The NZ job market (AVI index) has recovered for 2 consecutive quarters after 11 quarters of decline

---

## Tech stack

| Layer | Tool |
|---|---|
| Data ingestion | Python, Adzuna API, MBIE open data |
| Storage | Supabase (PostgreSQL) |
| Processing | pandas, scikit-learn |
| NLP | regex-based skill extraction |
| ML model | Linear Regression (salary prediction) |
| Dashboard | Streamlit |
| Deployment | Streamlit Cloud |
| Version control | Git / GitHub |

---

## Project structure

```
auckland-job-tracker/
├── app.py                  # Streamlit dashboard
├── requirements.txt
├── scripts/
│   ├── fetch_mbie.py       # Downloads MBIE government labour data
│   ├── fetch_seek.py       # Adzuna API job scraper
│   ├── setup_db.py         # Uploads data to Supabase
│   └── trademe_auth.py     # Trade Me OAuth setup
├── notebooks/
│   └── 01_exploration.ipynb  # EDA — salary, skills, market trends
└── data/                   # Generated charts
```

---

## How to run locally

```bash
# 1. Clone the repo
git clone https://github.com/capn1marmota/auckland-job-tracker.git
cd auckland-job-tracker

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file with your credentials
cp .env.example .env
# Fill in your API keys

# 5. Run the pipeline
python scripts/fetch_mbie.py
python scripts/fetch_seek.py
python scripts/setup_db.py

# 6. Launch the dashboard
streamlit run app.py
```

---

## Data sources

- **[Adzuna NZ API](https://developer.adzuna.com)** — live job listings with salary data
- **[MBIE Jobs Online](https://www.mbie.govt.nz/business-and-employment/employment-and-skills/labour-market-reports-data-and-analysis/jobs-online/)** — NZ government monthly vacancy index from May 2007 to present
- **[Trade Me Jobs API](https://developer.trademe.co.nz)** — NZ's largest classifieds platform (production access pending)

---

## Known limitations & next steps

- Salary data available for only 17% of listings — NZ employers rarely advertise salary
- ML model trained on small sample (15 listings with salary) — accuracy improves as data accumulates daily
- Some Adzuna listings include hourly/contract rates stored as annual figures — filtered at $30k floor
- **Next:** automate daily refresh via GitHub Actions, add Trade Me data once production approved

---

## Why I built this

I arrived in Auckland in March 2026 on a Chilean working holiday visa with a background in Ingeniería Comercial, SQL, Python, and Power BI. I couldn't find clear, local data on what skills Auckland employers actually want and what they pay — so I built a tool that collects it automatically.

This project is the infrastructure. The insights are the point.