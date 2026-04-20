import streamlit as st
import PyPDF2
import docx
import spacy
from sklearn.feature_extraction.text import CountVectorizer
import matplotlib.pyplot as plt

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(page_title="Resume Analyzer", layout="wide")

st.title("📄 Resume Analyzer Dashboard")

# -------------------------------
# Load spaCy model safely
# -------------------------------
@st.cache_resource
def load_model():
    return spacy.load("en_core_web_sm")

nlp = load_model()

# -------------------------------
# File Upload
# -------------------------------
uploaded_file = st.file_uploader("Upload your Resume (PDF or DOCX)", type=["pdf", "docx"])

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
# Analyze Resume
# -------------------------------
if text:

    st.subheader("📊 Analysis")

    col1, col2 = st.columns(2)

    # Word Count
    word_count = len(text.split())
    col1.metric("Total Words", word_count)

    # spaCy Processing
    doc = nlp(text)

    skills = []
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"]:
            skills.append(token.text.lower())

    # Remove duplicates
    skills = list(set(skills))

    col2.metric("Detected Keywords", len(skills))

    # -------------------------------
    # Show Skills
    # -------------------------------
    st.subheader("🧠 Extracted Keywords")
    st.write(", ".join(skills[:50]))

    # -------------------------------
    # Plot Top Words
    # -------------------------------
    st.subheader("📈 Top Keywords Frequency")

    vectorizer = CountVectorizer(stop_words='english', max_features=10)
    X = vectorizer.fit_transform([text])

    words = vectorizer.get_feature_names_out()
    counts = X.toarray()[0]

    fig, ax = plt.subplots()
    ax.bar(words, counts)
    plt.xticks(rotation=45)

    st.pyplot(fig)

else:
    st.info("Upload a resume to start analysis.")
