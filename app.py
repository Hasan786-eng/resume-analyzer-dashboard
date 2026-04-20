import streamlit as st
import PyPDF2
import docx
import re
import pandas as pd

# -------------------------------
# PAGE CONFIG (BRANDING)
# -------------------------------
st.set_page_config(
    page_title="HireFlow ATS",
    page_icon="📊",
    layout="wide"
)

# -------------------------------
# SIDEBAR (SAAS BRAND)
# -------------------------------
st.sidebar.title("📊 HireFlow ATS")
st.sidebar.markdown("### AI Resume Screening Platform")
st.sidebar.markdown("---")
st.sidebar.info("Upload resumes and instantly rank candidates using ATS scoring.")

# -------------------------------
# MAIN HEADER
# -------------------------------
st.title("🚀 HireFlow ATS Platform")
st.markdown("Smart AI-powered resume screening and candidate ranking system for HR teams.")

# -------------------------------
# JOB DESCRIPTION INPUT
# -------------------------------
job_desc = st.text_area("📌 Paste Job Description (Required for ATS scoring)")

# -------------------------------
# MULTIPLE FILE UPLOAD
# -------------------------------
uploaded_files = st.file_uploader(
    "📂 Upload Candidate Resumes (PDF / DOCX)",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

# -------------------------------
# CLEAN TEXT FUNCTION
# -------------------------------
def clean_text(txt):
    txt = re.sub(r'[^a-zA-Z ]', ' ', txt)
    return txt.lower().split()

# -------------------------------
# EXTRACT TEXT FUNCTION
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
# PROCESS LOGIC
# -------------------------------
results = []

if uploaded_files and job_desc:

    job_words = set(clean_text(job_desc))

    stopwords = {
        "the","and","to","of","in","a","is","for","on","with",
        "this","that","it","as","are","was","but","be","by","or",
        "an","at","from","you","your"
    }

    for file in uploaded_files:

        text = extract_text(file)
        resume_words = set(clean_text(text))

        resume_words = {
            w for w in resume_words
            if w not in stopwords and len(w) > 2
        }

        matched = resume_words.intersection(job_words)
        missing = job_words - resume_words

        score = round((len(matched) / len(job_words)) * 100, 2) if job_words else 0

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

    df = pd.DataFrame(results).sort_values(by="ATS Score", ascending=False)

    # -------------------------------
    # DASHBOARD VIEW
    # -------------------------------
    st.subheader("🏆 HireFlow Candidate Ranking Dashboard")

    st.dataframe(df, use_container_width=True)

    # TOP CANDIDATE
    top = df.iloc[0]

    st.success(f"""
    🥇 Top Candidate: {top['Candidate']}  
    📊 ATS Score: {top['ATS Score']}%  
    🧠 Verdict: {top['Verdict']}
    """)

    # DOWNLOAD REPORT
    csv = df.to_csv(index=False).encode('utf-8')

    st.download_button(
        "⬇️ Download HireFlow ATS Report",
        csv,
        "hireflow_ats_report.csv",
        "text/csv"
    )

else:
    st.info("📌 Upload resumes and paste job description to start analysis.")
