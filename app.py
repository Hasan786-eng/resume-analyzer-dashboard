import streamlit as st
import PyPDF2
import docx
from sklearn.feature_extraction.text import CountVectorizer
import matplotlib.pyplot as plt

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(page_title="Resume Analyzer", layout="wide")

st.title("📄 Resume Analyzer Dashboard")

st.markdown("Upload your resume (PDF or DOCX) to analyze keywords and stats.")

# -------------------------------
# File Upload
# -------------------------------
uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

text = ""

# -------------------------------
# Extract Text
# -------------------------------
if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""

    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(uploaded_file)
        for para in doc.paragraphs:
            text += para.text

# -------------------------------
# Analysis
# -------------------------------
if text and text.strip():

    st.subheader("📊 Resume Insights")

    col1, col2 = st.columns(2)

    word_count = len(text.split())
    col1.metric("Total Words", word_count)

    vectorizer = CountVectorizer(stop_words='english', max_features=10)
    X = vectorizer.fit_transform([text])

    words = vectorizer.get_feature_names_out()
    counts = X.toarray()[0]

    col2.metric("Top Keywords Found", len(words))

    # -------------------------------
    # Graph Section (FIXED)
    # -------------------------------
    st.subheader("📈 Top Keywords Frequency")

    fig, ax = plt.subplots(figsize=(10, 5))  # improved size

    ax.bar(words, counts)

    ax.set_xlabel("Keywords")
    ax.set_ylabel("Frequency")
    ax.set_title("Most Important Keywords in Resume")

    plt.xticks(rotation=45, ha='right')  # FIX alignment
    plt.tight_layout()  # prevent overlap

    st.pyplot(fig, use_container_width=True)

else:
    st.info("Upload a resume to see analysis.")
