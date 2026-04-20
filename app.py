import streamlit as st
import PyPDF2
import docx
import re
import matplotlib.pyplot as plt

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(page_title="HireFlow ATS", layout="wide")

st.title("🚀 HireFlow ATS - Smart Resume Analyzer")

# -------------------------------
# INPUTS
# -------------------------------
job_desc = st.text_area("📌 Paste Job Description")
file = st.file_uploader("📂 Upload Resume", type=["pdf", "docx"])

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
# CLEAN FIELD EXTRACTION
# -------------------------------
def extract_details(text):

    email = re.findall(r'[\w\.-]+@[\w\.-]+', text)
    phone = re.findall(r'\+?\d[\d\s-]{8,15}', text)

    # LinkedIn
    linkedin = re.findall(r'linkedin\.com\/in\/[a-zA-Z0-9-_/]+', text)

    # NAME (first meaningful line)
    lines = [l.strip() for l in text.split("\n") if len(l.strip()) > 2]
    name = lines[0] if lines else "Unknown"

    return {
        "name": name,
        "email": email[0] if email else "Not Found",
        "phone": phone[0] if phone else "Not Found",
        "linkedin": linkedin[0] if linkedin else "Not Found"
    }

# -------------------------------
# ROLE PREDICTION (SIMPLE LOGIC)
# -------------------------------
def predict_role(text):

    text = text.lower()

    if "python" in text and "sql" in text and "excel" in text:
        return "Data Analyst"
    elif "aws" in text or "docker" in text or "devops" in text:
        return "Cloud / DevOps Engineer"
    elif "java" in text:
        return "Software Developer"
    else:
        return "General IT Profile"

# -------------------------------
# WORD SET
# -------------------------------
def words(text):
    return set(re.findall(r"[a-zA-Z]+", text.lower()))

# -------------------------------
# ATS SCORE
# -------------------------------
def ats_score(job_words, resume_words):

    match = job_words.intersection(resume_words)

    score = (len(match) / len(job_words)) * 100 if job_words else 0

    return round(min(score, 100), 2), match

# -------------------------------
# MAIN
# -------------------------------
if file and job_desc:

    text = extract_text(file)

    details = extract_details(text)

    role = predict_role(text)

    job_words = words(job_desc)
    resume_words = words(text)

    score, matched = ats_score(job_words, resume_words)

    # -------------------------------
    # CLEAN HEADER CARD (LIKE YOU WANT)
    # -------------------------------
    st.subheader("👤 Candidate Profile")

    st.markdown(f"""
### {details['name']}

📧 {details['email']}  
📱 {details['phone']}  
🔗 {details['linkedin']}

🎯 **Predicted Role:** {role}
""")

    # -------------------------------
    # ATS SCORE
    # -------------------------------
    st.subheader("📊 ATS Score")

    st.metric("Score", f"{score}/100")

    st.write("Matched Keywords:", list(matched)[:20])

    # -------------------------------
    # GRAPH (ONLY 3 BOXES)
    # -------------------------------
    st.subheader("📊 Skill Breakdown")

    labels = ["Skills", "Education", "Languages"]

    values = [
        min(len(resume_words & job_words) * 5, 100),
        min(len(resume_words) * 0.2, 100),
        min(len(resume_words) * 0.1, 100)
    ]

    fig, ax = plt.subplots()

    bars = ax.bar(labels, values)

    for bar in bars:
        bar.set_color("#7B2CBF")

    ax.set_ylim(0, 100)

    st.pyplot(fig)

else:
    st.info("Upload resume and paste job description")
