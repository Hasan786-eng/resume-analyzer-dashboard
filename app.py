import streamlit as st
import PyPDF2
import docx
import re
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(page_title="HireFlow ATS", layout="wide")

st.title("🚀 HireFlow ATS - Smart Resume Analyzer")
st.markdown("AI-powered resume understanding + ATS scoring system")

# -------------------------------
# INPUTS
# -------------------------------
job_desc = st.text_area("📌 Paste Job Description")

uploaded_files = st.file_uploader(
    "📂 Upload Resumes",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

# -------------------------------
# TEXT CLEANER
# -------------------------------
def clean(text):
    text = re.sub(r'[^a-zA-Z ]', ' ', text)
    return text.lower().split()

# -------------------------------
# EXTRACT TEXT
# -------------------------------
def extract(file):
    text = ""
    if file.type == "application/pdf":
        pdf = PyPDF2.PdfReader(file)
        for p in pdf.pages:
            text += p.extract_text() or ""

    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        for para in doc.paragraphs:
            text += para.text + " "
    return text

# -------------------------------
# SCORE ENGINE (REALISTIC)
# -------------------------------
def calculate_score(resume_words, job_words):

    resume_set = set(resume_words)
    job_set = set(job_words)

    matched = resume_set.intersection(job_set)

    # breakdown logic
    skill_score = len(matched) / len(job_set) if job_set else 0

    experience_keywords = ["experience","worked","developed","built","managed","led"]
    exp_score = sum([1 for w in resume_set if w in experience_keywords]) / 5

    education_keywords = ["bachelor","master","degree","university","college"]
    edu_score = sum([1 for w in resume_set if w in education_keywords]) / 5

    keyword_density = len(resume_set) / 200  # normalization

    final_score = (
        skill_score * 0.5 +
        exp_score * 0.2 +
        edu_score * 0.1 +
        keyword_density * 0.2
    ) * 100

    return round(min(final_score, 100), 2), matched

# -------------------------------
# PROCESS
# -------------------------------
results = []

if uploaded_files and job_desc:

    job_words = clean(job_desc)

    for file in uploaded_files:

        text = extract(file)
        resume_words = clean(text)

        score, matched = calculate_score(resume_words, job_words)

        results.append({
            "Candidate": file.name,
            "ATS Score": score,
            "Matched Skills": len(matched),
        })

    df = pd.DataFrame(results).sort_values(by="ATS Score", ascending=False)

    # -------------------------------
    # TABLE
    # -------------------------------
    st.subheader("🏆 Candidate Ranking")
    st.dataframe(df, use_container_width=True)

    # -------------------------------
    # TOP CANDIDATE
    # -------------------------------
    top = df.iloc[0]

    st.success(f"""
    🥇 Top Candidate: {top['Candidate']}
    📊 ATS Score: {top['ATS Score']}%
    """)

    # -------------------------------
    # GRAPH - SCORE DISTRIBUTION
    # -------------------------------
    st.subheader("📊 Score Distribution")

    fig, ax = plt.subplots()
    ax.bar(df["Candidate"], df["ATS Score"])
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)

else:
    st.info("Upload resumes + job description to analyze")
