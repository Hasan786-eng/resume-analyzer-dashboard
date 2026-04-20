import streamlit as st
import PyPDF2
import docx
import re
import matplotlib.pyplot as plt

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(page_title="HireFlow ATS", layout="wide")
st.title("🚀 HireFlow ATS - Skill Intelligence Dashboard")

# ---------------------------
# PREDEFINED SKILLS LIST
# ---------------------------
SKILLS_DB = [
    # Programming Languages
    "python", "java", "javascript", "typescript", "c", "c++", "c#", "r", "swift",
    "kotlin", "go", "rust", "php", "ruby", "scala", "matlab", "perl",
    # Web
    "html", "css", "react", "angular", "vue", "nodejs", "django", "flask",
    "fastapi", "spring", "express", "bootstrap", "tailwind",
    # Data & Analytics
    "sql", "mysql", "postgresql", "mongodb", "sqlite", "oracle", "nosql",
    "excel", "tableau", "power bi", "looker", "data analysis", "data visualization",
    "data science", "data engineering", "statistics", "pandas", "numpy",
    "matplotlib", "seaborn", "plotly",
    # ML / AI
    "machine learning", "deep learning", "nlp", "computer vision",
    "tensorflow", "pytorch", "keras", "scikit-learn", "opencv",
    "reinforcement learning", "neural networks",
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git",
    "github", "gitlab", "ci/cd", "terraform", "linux", "bash",
    "devops", "microservices", "rest api", "graphql",
    # Tools & Others
    "spark", "hadoop", "kafka", "airflow", "dbt",
    "jira", "agile", "scrum", "figma", "photoshop",
]

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
# MATCH SKILLS
# ---------------------------
def match_skills(text):
    found = {}
    for skill in SKILLS_DB:
        # count how many times the skill appears (handles multi-word skills too)
        pattern = r'\b' + re.escape(skill) + r'\b'
        matches = re.findall(pattern, text)
        if matches:
            found[skill] = len(matches)
    return found

# ---------------------------
# MAIN
# ---------------------------
if file:
    resume_text = extract_text(file)
    matched = match_skills(resume_text)

    if not matched:
        st.warning("No known skills found in the resume. Try a different file.")
    else:
        # Sort by frequency, take top 15
        top_skills = dict(sorted(matched.items(), key=lambda x: x[1], reverse=True)[:15])
        skills = list(top_skills.keys())
        counts = list(top_skills.values())

        # ---------------------------
        # DISPLAY SKILLS TEXT
        # ---------------------------
        st.subheader("🧠 Detected Skills (From Resume)")
        cols = st.columns(3)
        for i, skill in enumerate(skills):
            cols[i % 3].write(f"• {skill}")

        # ---------------------------
        # HORIZONTAL BAR CHART (like your original!)
        # ---------------------------
        st.subheader("📊 Skill Frequency in Resume")

        fig, ax = plt.subplots(figsize=(10, max(5, len(skills) * 0.55)))

        # Reverse so highest count is at the top
        skills_rev = skills[::-1]
        counts_rev = counts[::-1]

        bars = ax.barh(skills_rev, counts_rev, color="#1f77b4", height=0.6)

        ax.set_xlabel("Frequency")
        ax.set_ylabel("Skills")
        ax.set_title("HireFlow - Resume Skill Intelligence")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        plt.tight_layout()
        st.pyplot(fig)

else:
    st.info("Upload a resume to generate skill analysis")
