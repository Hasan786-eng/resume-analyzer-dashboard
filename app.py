import streamlit as st
import PyPDF2
import docx
from sklearn.feature_extraction.text import CountVectorizer
import matplotlib.pyplot as plt

st.set_page_config(page_title="Resume Analyzer", layout="wide")

st.title("📄 Resume Analyzer Dashboard")

uploaded_file = st.file_uploader("Upload your Resume (PDF or DOCX)", type=["pdf", "docx"])

text = ""

if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""

    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(uploaded_file)
        for para in doc.paragraphs:
            text += para.text

if text:
    st.subheader("📊 Analysis")

    col1, col2 = st.columns(2)

    word_count = len(text.split())
    col1.metric("Total Words", word_count)

    vectorizer = CountVectorizer(stop_words='english', max_features=20)
    X = vectorizer.fit_transform([text])

    words = vectorizer.get_feature_names_out()
    counts = X.toarray()[0]

    col2.metric("Unique Keywords", len(words))

    st.subheader("📈 Top Keywords")

    fig, ax = plt.subplots()
    ax.bar(words, counts)
    plt.xticks(rotation=45)

    st.pyplot(fig)

else:
    st.info("Upload a resume to start analysis.")
