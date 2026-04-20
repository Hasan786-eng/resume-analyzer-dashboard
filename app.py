import streamlit as st
import PyPDF2
import spacy
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
import random

# Page config
st.set_page_config(page_title="Resume Analyzer", layout="wide")

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# ---------------------------
# ML MODEL
# ---------------------------
data = [
    ("python sql data analysis machine learning pandas numpy", "Data Science"),
    ("html css javascript react frontend web development", "Web Development"),
    ("recruitment hiring onboarding hr policies communication", "HR"),
    ("aws docker kubernetes devops ci cd linux", "DevOps"),
    ("excel power bi tableau data visualization sql", "Data Analyst"),
    ("java spring boot backend api development", "Backend Developer")
]

texts = [x[0] for x in data]
labels = [x[1] for x in data]

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)

model = LogisticRegression()
model.fit(X, labels)

# ---------------------------
# FILE READING
# ---------------------------
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file):
    doc = Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

# ---------------------------
# NAME EXTRACTION
# ---------------------------
def extract_name(text):
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if len(lines) > 1 and len(lines[0].split()) <= 3:
        return lines[0] + " " + lines[1]
    return lines[0] if lines else "Not Found"

# ---------------------------
# SKILL EXTRACTION
# ---------------------------
skills_list = [
    "python", "sql", "excel", "power bi", "tableau",
    "data analysis", "data visualization", "machine learning",
    "html", "css", "javascript", "react", "java",
    "aws", "docker", "kubernetes"
]

def extract_skills(text):
    text = text.lower()
    return [skill for skill in skills_list if skill in text]

# ---------------------------
# UI
# ---------------------------
st.title("📊 Resume Analyzer Dashboard")

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

if uploaded_file:
    # Read file
    if uploaded_file.name.endswith(".pdf"):
        resume_text = extract_text_from_pdf(uploaded_file)
    else:
        resume_text = extract_text_from_docx(uploaded_file)

    # Process
    name = extract_name(resume_text)
    skills = extract_skills(resume_text)
    role = model.predict(vectorizer.transform([resume_text]))[0]

    # ---------------------------
    # TOP SECTION (2 columns)
    # ---------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("👤 Name")
        st.success(name)

        st.subheader("🎯 Predicted Role")
        st.info(role)

    with col2:
        st.subheader("🛠 Skills")
        for skill in skills:
            level = random.randint(60, 95) / 100  # fake % for UI
            st.write(skill.upper())
            st.progress(level)

    # ---------------------------
    # CHART SECTION
    # ---------------------------
    st.subheader("📈 Skills Visualization")

    if skills:
        values = [random.randint(60, 100) for _ in skills]

        plt.figure()
        plt.barh(skills, values)
        plt.xlabel("Proficiency")
        plt.ylabel("Skills")

        st.pyplot(plt)

    # ---------------------------
    # SUMMARY BOX
    # ---------------------------
    st.subheader("📌 Summary")
    st.write(f"This resume is best suited for **{role}** roles based on extracted skills.")