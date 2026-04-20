import streamlit as st
import PyPDF2
import docx
import re
import matplotlib.pyplot as plt

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(page_title="HireFlow ATS", layout="wide")

st.title("🚀 HireFlow ATS - Resume Intelligence System")
st.markdown("Structured resume extraction + ATS analysis dashboard")

# -------------------------------
# INPUTS
# -------------------------------
job_desc = st.text_area("📌 Paste Job Description")
uploaded_file = st.file_uploader("📂 Upload Resume (PDF / DOCX)")

# -------------------------------
# TEXT EXTRACTION
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
            text += para.text + "\n"

    return text

# -------------------------------
# SECTION DETECTION (FIXED)
# -------------------------------
def extract_sections(text):

    sections = {
        "skills": [],
        "education": [],
        "experience": [],
        "languages": [],
        "personal": []
    }

    current = None

    for line in text.split("\n"):
        l = line.strip()

        if not l:
            continue

        low = l.lower()

        if "skill" in low:
            current = "skills"
            continue
        elif "education" in low:
            current = "education"
            continue
        elif "experience" in low:
            current = "experience"
            continue
        elif "language" in low:
            current = "languages"
            continue
        elif "name" in low or "email" in low or "phone" in low:
            sections["personal"].append(l)
            continue

        if current:
            sections[current].append(l)

    return sections

# -------------------------------
# CLEAN WORDS
# -------------------------------
def clean_words(text_list):

    text = " ".join(text_list)
    words = re.findall(r"[a-zA-Z]+", text.lower())

    stopwords = {
        "and","in","with","the","a","to","of","for","by","on","is",
        "are","was","it","this","that","as","at","from","you","your",
        "skills","skill","experience","education","known","using",
        "final","year","student","summary"
    }

    return [w for w in words if w not in stopwords and len(w) > 2]

# -------------------------------
# ATS SCORING
# -------------------------------
def ats_score(job_words, resume_words):

    job_set = set(job_words)
    resume_set = set(resume_words)

    matched = job_set.intersection(resume_set)

    score = (len(matched) / len(job_set)) * 100 if job_set else 0

    missing = job_set - resume_set

    return round(score, 2), matched, missing

# -------------------------------
# MAIN LOGIC
# -------------------------------
if uploaded_file and job_desc:

    resume_text = extract_text(uploaded_file)
    sections = extract_sections(resume_text)

    job_words = re.findall(r"[a-zA-Z]+", job_desc.lower())

    # clean sections
    skills = clean_words(sections["skills"])
    education = clean_words(sections["education"])
    languages = clean_words(sections["languages"])

    # ATS score based on skills mainly
    score, matched, missing = ats_score(job_words, skills)

    # -------------------------------
    # METRICS
    # -------------------------------
    col1, col2, col3 = st.columns(3)

    col1.metric("ATS Score", f"{score}%")
    col2.metric("Matched Skills", len(matched))
    col3.metric("Missing Skills", len(missing))

    # -------------------------------
    # STRUCTURED RESUME VIEW
    # -------------------------------
    st.subheader("📄 Structured Resume")

    st.markdown("### 👤 Personal Details")
    st.write(sections["personal"] if sections["personal"] else "Not Found")

    st.markdown("### 🧠 Skills")
    st.write(list(set(skills))[:50])

    st.markdown("### 🎓 Education")
    st.write(sections["education"] if sections["education"] else "Not Found")

    st.markdown("### 🌐 Languages")
    st.write(list(set(languages)))

    # -------------------------------
    # GRAPH (FIXED + CLEAN)
    # -------------------------------
    st.subheader("📊 HireFlow ATS Breakdown")

    labels = ["Skills", "Education", "Languages"]

    values = [
        len(set(skills)),
        len(set(education)),
        len(set(languages))
    ]

    fig, ax = plt.subplots()

    bars = ax.bar(labels, values)

    for bar in bars:
        bar.set_color("#7B2CBF")  # purple

    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")

    plt.ylim(0, max(values) + 5)

    st.pyplot(fig)

    # -------------------------------
    # MISSING SKILLS
    # -------------------------------
    st.subheader("❌ Missing Skills (from Job Description)")
    st.write(list(missing)[:30])

else:
    st.info("Upload resume and paste job description to begin analysis")
