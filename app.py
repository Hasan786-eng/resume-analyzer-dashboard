import streamlit as st
import PyPDF2
import docx
import re
import matplotlib.pyplot as plt
from collections import Counter

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(page_title="HireFlow ATS", layout="wide")

st.title("🚀 HireFlow ATS - Skill Intelligence Dashboard")

# ---------------------------
# FILE INPUT
# ---------------------------
file = st.file_uploader("📂 Upload Resume (PDF / DOCX)", type=["pdf", "docx"])

# ---------------------------
# EXTRACT TEXT
# ---------------------------
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

    return text.lower()

# ---------------------------
# CLEAN WORDS
# ---------------------------
def get_words(text):
    return re.findall(r"[a-zA-Z]+", text)

# ---------------------------
# MAIN
# ---------------------------
if file:

    resume_text = extract_text(file)
    words = get_words(resume_text)

    word_freq = Counter(words)

    # remove noise words (stopwords)
    stopwords = {
        "and","the","in","with","for","to","of","is","are","was",
        "a","an","on","at","by","this","that","it","as","be",
        "skills","experience","education","resume","name","email"
    }

    filtered = {
        k: v for k, v in word_freq.items()
        if k not in stopwords and len(k) > 2
    }

    # ---------------------------
    # TOP SKILLS SELECTION
    # ---------------------------
    top_skills = dict(sorted(filtered.items(), key=lambda x: x[1], reverse=True)[:12])

    skills = list(top_skills.keys())
    counts = list(top_skills.values())

    # convert frequency → score (0–100 scaling)
    max_count = max(counts) if counts else 1
    scores = [round((c / max_count) * 100) for c in counts]

    # ---------------------------
    # DISPLAY TEXT
    # ---------------------------
    st.subheader("🧠 Extracted Skills (From Resume)")

    for s in skills:
        st.write("•", s)

    # ---------------------------
    # GRAPH
    # ---------------------------
    st.subheader("📊 Skill Strength Analysis (Out of 100)")

    fig, ax = plt.subplots(figsize=(10, 5))

    bars = ax.bar(skills, scores)

    for bar in bars:
        bar.set_color("#7B2CBF")

    ax.set_ylim(0, 100)
    ax.set_ylabel("Skill Strength Score")
    ax.set_title("HireFlow - Resume Skill Intelligence")

    plt.xticks(rotation=45, ha="right")

    st.pyplot(fig)

else:
    st.info("Upload a resume to generate skill analysis")
