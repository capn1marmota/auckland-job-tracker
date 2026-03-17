import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from supabase import create_client
from dotenv import load_dotenv
import os
import re
from collections import Counter
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MultiLabelBinarizer

load_dotenv()

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Auckland Job Market Tracker",
    page_icon="🇳🇿",
    layout="wide"
)

# ── DATA LOADING ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)  # refresh every hour
def load_data():
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    jobs = pd.DataFrame(supabase.table("job_postings").select("*").execute().data)
    mbie = pd.DataFrame(supabase.table("mbie_monthly").select("*").execute().data)
    return jobs, mbie

jobs, mbie = load_data()

# ── SKILL EXTRACTION ─────────────────────────────────────────────────────────
SKILLS = {
    "sql": r"\bsql\b", "python": r"\bpython\b", "power bi": r"power bi",
    "excel": r"\bexcel\b", "tableau": r"\btableau\b",
    "r programming": r"\br\b", "machine learning": r"machine learning",
    "snowflake": r"\bsnowflake\b", "dbt": r"\bdbt\b", "etl": r"\betl\b",
    "azure": r"\bazure\b", "aws": r"\baws\b", "git": r"\bgit\b",
    "api": r"\bapi\b", "finance": r"\bfinance\b", "agile": r"\bagile\b",
    "communication": r"\bcommunication\b", "stakeholder": r"\bstakeholder\b",
    "budgeting": r"\bbudgeting\b", "forecasting": r"\bforecasting\b",
}

def extract_skills(text):
    if not isinstance(text, str):
        return []
    text = text.lower()
    return [s for s, p in SKILLS.items() if re.search(p, text)]

jobs["skills_found"] = jobs["description"].apply(extract_skills)

# ── HEADER ───────────────────────────────────────────────────────────────────
st.title("🇳🇿 Auckland Job Market Tracker")
st.caption("Live data from Adzuna · NZ Labour Market data from MBIE · Built by a Chilean analyst in Auckland")

# ── KPI CARDS ────────────────────────────────────────────────────────────────
salary_df = jobs[jobs["salary_min"] >= 30000]
all_skills = [s for sub in jobs["skills_found"] for s in sub]
top_skill  = Counter(all_skills).most_common(1)[0][0] if all_skills else "N/A"

col1, col2, col3, col4 = st.columns(4)
col1.metric("Live Job Listings",     f"{len(jobs)}")
col2.metric("Median Salary",         f"${salary_df['salary_min'].median():,.0f}" if len(salary_df) else "N/A")
col3.metric("Roles with Salary Data",f"{len(salary_df) / len(jobs) * 100:.0f}%")
col4.metric("Most In-Demand Skill",  top_skill.title())

st.divider()

# ── ROW 1: TOP ROLES + SALARY DIST ───────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Top Job Titles")
    top_titles = jobs["title"].str.lower().str.strip().value_counts().head(12)
    fig, ax = plt.subplots(figsize=(7, 5))
    top_titles.sort_values().plot(kind="barh", ax=ax, color="#2563eb")
    ax.set_xlabel("Listings")
    ax.set_title("")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col_right:
    st.subheader("Salary Distribution (Annual NZD)")
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.hist(salary_df["salary_min"], bins=15, color="#16a34a", edgecolor="white")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1000:.0f}k"))
    ax.set_xlabel("Salary")
    ax.set_ylabel("Listings")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

st.divider()

# ── ROW 2: SKILL DEMAND + MARKET TREND ───────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Most In-Demand Skills")
    skill_counts = Counter(all_skills)
    skill_df = pd.DataFrame(skill_counts.items(), columns=["skill", "count"])
    skill_df = skill_df.sort_values("count", ascending=False).head(12)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(skill_df["skill"], skill_df["count"], color="#7c3aed")
    ax.invert_yaxis()
    ax.set_xlabel("Listings Mentioning Skill")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col_right:
    st.subheader("NZ Job Market Trend (2020–Present)")
    mbie["actual_date"] = pd.to_datetime(mbie["actual_date"])
    mbie_recent = mbie[mbie["actual_date"] >= "2020-01-01"].sort_values("actual_date")
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(mbie_recent["actual_date"], mbie_recent["totals"], color="#dc2626", linewidth=2)
    ax.axhline(y=100, color="gray", linestyle="--", alpha=0.5)
    ax.set_ylabel("All Vacancies Index")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

st.divider()

# ── SALARY PREDICTOR ─────────────────────────────────────────────────────────
st.subheader("🎯 Salary Predictor — Enter Your Skills")

model_df = jobs[jobs["salary_min"] >= 30000].copy()
mlb = MultiLabelBinarizer()
X = pd.DataFrame(
    mlb.fit_transform(model_df["skills_found"]),
    columns=mlb.classes_,
    index=model_df.index
)
y = model_df["salary_min"]
model = LinearRegression()
model.fit(X, y)

selected_skills = st.multiselect(
    "Select your skills:",
    options=list(SKILLS.keys()),
    default=["sql", "python", "power bi", "excel", "finance"]
)

if selected_skills:
    vec = mlb.transform([selected_skills])
    pred = model.predict(vec)[0]
    pred = max(50000, pred)  # floor at realistic minimum
    st.success(f"Estimated salary range: **${pred:,.0f} — ${pred * 1.15:,.0f}** NZD/year")

    # Show which of their skills are in demand
    st.caption("Your skills vs market demand:")
    match_df = skill_df[skill_df["skill"].isin(selected_skills)][["skill", "count"]]
    if not match_df.empty:
        st.dataframe(match_df.rename(columns={"count": "listings mentioning this skill"}), hide_index=True)

st.divider()
st.caption("Data refreshes hourly · Source: Adzuna API + MBIE Jobs Online · github.com/capn1marmota/auckland-job-tracker")