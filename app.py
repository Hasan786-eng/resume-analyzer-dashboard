import streamlit as st
import PyPDF2
import docx
import re
import pandas as pd
from collections import Counter

# -------------------------------
# PAGE CONFIG (SAAS STYLE)
# -------------------------------
st.set_page_config(
    page_title="HR SaaS ATS Platform",
    page_icon="📊",
    layout="wide"
)

# -------------------------------
# SIDEBAR (SAAS NAV)
# -------------------------------
st.sidebar.title("📊 HR SaaS ATS")
st.sidebar.markdown("Smart Resume Screening Platform")

st.sidebar.markdown("---")
st.sidebar.info("Upload multiple resumes and rank candidates automatically.")

# -------------------------------
# HEADER
# -------------------------------
st.title("🚀 SaaS HR ATS Platform")
st.markdown("Upload multiple resumes and compare candidates instantly.")

# -------------------------------
# JOB DESCRIPTION
# -------------------------------
job_desc = st.text_area("📌 Paste Job Description (Required for ATS scoring)")

# -------------------------------
# MULTIPLE FILE UPLOAD
# -------------------------------
uploaded_files = st.file_uploader(
    "Upload Resumes (Multiple PDF/DOCX)",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

# -------------------------------
# CLEAN FUNCTION
# -------------------------------
def clean_text(txt):
    txt = re.sub(r'[^a-zA-Z ]', ' ', txt)
    return txt.lower().split()

# -------------------------------
# EXTRACT TEXT
# -------------------------------
def extract_text(file):
    text = ""

    if file.type == "application/pdf":
        pdf = PyPDF2.PdfReader(file)
        for page in pdf.pages:
            text += page.extract_text() or ""

    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        for para in doc.paragraphs:
            text += para.text + " "

    return text

# -------------------------------
# PROCESS
# -------------------------------
results = []

if uploaded_files and job_desc:

    job_words = set(clean_text(job_desc))

    for file in uploaded_files:

        text = extract_text(file)
        resume_words = set(clean_text(text))

        # Remove junk words
        stopwords = {
            "the","and","to","of","in","a","is","for","on","with",
            "this","that","it","as","are","was","but","be","by","or",
            "an","at","from","you","your"
        }

        resume_words = {w for w in resume_words if w not in stopwords and len(w) > 2}

        matched = resume_words.intersection(job_words)
        missing = job_words - resume_words

        score = round((len(matched) / len(job_words)) * 100, 2) if job_words else 0

        # Simple AI-like summary
        if score > 70:
            verdict = "Strong Match"
        elif score > 40:
            verdict = "Moderate Match"
        else:
            verdict = "Weak Match"

        results.append({
            "Candidate": file.name,
            "ATS Score": score,
            "Matched Skills": len(matched),
            "Missing Skills": len(missing),
            "Verdict": verdict
        })

    # -------------------------------
    # DATAFRAME
    # -------------------------------
    df = pd.DataFrame(results)
    df = df.sort_values(by="ATS Score", ascending=False)

    # -------------------------------
    # DASHBOARD
    # -------------------------------
    st.subheader("🏆 Candidate Ranking")

    st.dataframe(df, use_container_width=True)

    # -------------------------------
    # BEST CANDIDATE
    # -------------------------------
    st.subheader("🥇 Top Candidate")

    top = df.iloc[0]

    st.success(f"""
    👤 {top['Candidate']}  
    📊 ATS Score: {top['ATS Score']}%  
    🧠 Verdict: {top['Verdict']}
    """)

    # -------------------------------
    # DOWNLOAD REPORT
    # -------------------------------
    csv = df.to_csv(index=False).encode('utf-8')

    st.download_button(
        "⬇️ Download HR Report (CSV)",
        csv,
        "ats_report.csv",
        "text/csv"
    )

else:
    st.info("📌 Upload resumes + paste job description to start SaaS analysis.")
