import streamlit as st
import PyPDF2
import docx
import re
import matplotlib.pyplot as plt
from collections import Counter

# -------------------------------
# CONFIG (SAAS LOOK)
# -------------------------------
st.set_page_config(page_title="HireFlow ATS", layout="wide")

st.title("🚀 HireFlow ATS - Smart Resume Intelligence System")

st.markdown("AI-powered structured resume extraction + ATS analysis")

# -------------------------------
# INPUTS
# -------------------------------
job_desc = st.text_area("📌 Paste Job Description")

uploaded_file = st.file_uploader("📂 Upload Resume (PDF/DOCX)")

# -------------------------------
# EXTRACT TEXT
# -------------------------------
def extract_text(file):
    text = ""

    if file.type == "application/pdf":
        pdf = PyPDF2.PdfReader(file)
        for p in pdf.pages:
            text += p.extract_text() or ""

    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"

    return text

# -------------------------------
# CLEAN TEXT
# -------------------------------
def clean(text):
    return re.findall(r"[a-zA-Z]+", text.lower())

# -------------------------------
# SECTION EXTRACTION (SMART)
# -------------------------------
def extract_sections(text):

    sections = {
        "skills": [],
        "education": [],
        "experience": [],
        "languages": [],
        "personal": []
    }

    lines = text.split("\n")

    for line in lines:
        l = line.lower()

        if "skill" in l:
            sections["skills"].extend(clean(line))

        elif "education" in l or "college" in l or "university" in l:
            sections["education"].extend(clean(line))

        elif "experience" in l or "worked" in l:
            sections["experience"].extend(clean(line))

        elif "language" in l:
            sections["languages"].extend(clean(line))

        elif "name" in l or "email" in l or "phone" in l:
            sections["personal"].append(line.strip())

    return sections

# -------------------------------
# SCORE ENGINE
# -------------------------------
def score_section(resume_set, job_set):
    match = resume_set.intersection(job_set)
    return len(match), len(job_set - resume_set)

# -------------------------------
# PROCESS
# -------------------------------
if uploaded_file and job_desc:

    resume_text = extract_text(uploaded_file)
    sections = extract_sections(resume_text)

    job_words = set(clean(job_desc))

    # -------------------------------
    # SECTION SCORES
    # -------------------------------
    skill_match, skill_missing = score_section(set(sections["skills"]), job_words)
    edu_match, _ = score_section(set(sections["education"]), job_words)
    lang_match, _ = score_section(set(sections["languages"]), job_words)

    # normalize scores
    skill_score = min(skill_match * 10, 100)
    edu_score = min(edu_match * 5, 100)
    lang_score = min(lang_match * 10, 100)

    # -------------------------------
    # LAYOUT
    # -------------------------------
    col1, col2, col3 = st.columns(3)

    col1.metric("Skills Match", f"{skill_score}%")
    col2.metric("Education Match", f"{edu_score}%")
    col3.metric("Language Match", f"{lang_score}%")

    # -------------------------------
    # ATS FINAL SCORE
    # -------------------------------
    final_score = (skill_score * 0.6 + edu_score * 0.25 + lang_score * 0.15)
    st.subheader(f"📊 ATS Final Score: {round(final_score,2)}%")

    # -------------------------------
    # MISSING SKILLS
    # -------------------------------
    missing = job_words - set(sections["skills"])

    st.subheader("❌ Missing Skills")
    st.write(list(missing)[:20])

    # -------------------------------
    # STRUCTURED RESUME VIEW
    # -------------------------------
    st.subheader("📄 Structured Resume Extraction")

    st.markdown("### 👤 Personal Details")
    st.write(sections["personal"])

    st.markdown("### 🧠 Skills")
    st.write(sections["skills"])

    st.markdown("### 🎓 Education")
    st.write(sections["education"])

    st.markdown("### 💼 Experience")
    st.write(sections["experience"])

    st.markdown("### 🌐 Languages")
    st.write(sections["languages"])

    # -------------------------------
    # GRAPH (YOUR REQUIRED DESIGN)
    # -------------------------------
    st.subheader("📊 HireFlow ATS Breakdown Graph")

    labels = ["Skills", "Education", "Language"]
    values = [skill_score, edu_score, lang_score]

    fig, ax = plt.subplots()

    bars = ax.bar(labels, values)

    # purple + white style
    for bar in bars:
        bar.set_color("#7B2CBF")  # purple

    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")

    plt.ylim(0, 100)
    st.pyplot(fig)

else:
    st.info("Upload resume and paste job description")
