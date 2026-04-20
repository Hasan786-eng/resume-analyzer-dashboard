import streamlit as st
import PyPDF2
import docx
import re
import matplotlib.pyplot as plt

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(page_title="HireFlow ATS", layout="wide")

st.title("🚀 HireFlow ATS - Clean Resume Intelligence System")

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
# CLEAN LINE NORMALIZATION
# -------------------------------
def normalize_lines(text):
    return [line.strip() for line in text.split("\n") if len(line.strip()) > 2]

# -------------------------------
# SMART SECTION PARSER (FIXED)
# -------------------------------
def parse_resume(text):

    sections = {
        "skills": [],
        "education": [],
        "languages": [],
        "personal": []
    }

    current = None

    for line in normalize_lines(text):
        l = line.lower()

        # detect headers properly
        if "skill" in l:
            current = "skills"
            continue
        elif "education" in l or "qualification" in l:
            current = "education"
            continue
        elif "language" in l:
            current = "languages"
            continue

        # personal detection (email/phone/name)
        if "email" in l or "phone" in l or "@" in l:
            sections["personal"].append(line)
            continue

        if current:
            sections[current].append(line)

    return sections

# -------------------------------
# CLEAN SKILLS ONLY (NO JUNK WORDS)
# -------------------------------
def clean_items(list_data):

    text = " ".join(list_data)
    words = re.findall(r"[a-zA-Z]+", text.lower())

    stopwords = {
        "and","the","in","with","for","to","of","is","are","was",
        "skills","skill","experience","education","known","using",
        "bca","year","student","class","college","university"
    }

    return [w for w in words if w not in stopwords and len(w) > 2]

# -------------------------------
# MAIN
# -------------------------------
if file and job_desc:

    text = extract_text(file)
    sections = parse_resume(text)

    skills = clean_items(sections["skills"])
    education = clean_items(sections["education"])
    languages = clean_items(sections["languages"])

    # -------------------------------
    # CLEAN DISPLAY (NO RAW LISTS)
    # -------------------------------
    st.subheader("👤 Personal Details")
    st.write(sections["personal"] if sections["personal"] else "Not Found")

    st.subheader("🧠 Skills (Clean)")
    st.write(sorted(set(skills)))

    st.subheader("🎓 Education")
    st.write(sections["education"])

    st.subheader("🌐 Languages")
    st.write(languages)

    # -------------------------------
    # FIXED GRAPH (REAL VALUES ONLY)
    # -------------------------------
    st.subheader("📊 HireFlow ATS Breakdown (Clean)")

    labels = ["Skills", "Education", "Languages"]
    values = [
        len(set(skills)),
        len(set(education)),
        len(set(languages))
    ]

    fig, ax = plt.subplots()

    bars = ax.bar(labels, values)

    for bar in bars:
        bar.set_color("#7B2CBF")

    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")

    plt.ylim(0, max(values) + 5)

    st.pyplot(fig)

else:
    st.info("Upload resume + job description")
