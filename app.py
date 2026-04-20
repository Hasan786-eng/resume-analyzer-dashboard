import streamlit as st
import PyPDF2
import docx
import re
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(page_title="HireFlow ATS", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    .stApp { background-color: #f4f0fa; }

    .profile-card {
        background: linear-gradient(135deg, #6a0dad, #9b59b6);
        border-radius: 16px; padding: 24px; color: white;
        text-align: center; box-shadow: 0 8px 32px rgba(106,13,173,0.18);
        margin-bottom: 16px;
    }
    .profile-card h2 { color: white; font-size: 1.4rem; margin: 8px 0 2px; }
    .profile-card p  { color: #e8d5f5; font-size: 0.85rem; margin: 3px 0; }

    .section-card {
        background: white; border-radius: 14px; padding: 18px 22px;
        box-shadow: 0 2px 16px rgba(106,13,173,0.07);
        margin-bottom: 16px; border-left: 4px solid #7b2cbf;
    }
    .section-card h3 { color: #6a0dad; font-size: 1rem; font-weight: 600; margin-bottom: 10px; }

    .skill-pill {
        display: inline-block; background: #ede7f6; color: #4B0082;
        border-radius: 20px; padding: 4px 13px; font-size: 0.8rem;
        font-weight: 500; margin: 3px 3px; border: 1px solid #c5a8e8;
    }
    .big-title {
        background: linear-gradient(135deg, #6a0dad, #9b59b6);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 2.2rem; font-weight: 700; letter-spacing: -1px;
    }
    .subtitle { color: #888; font-size: 0.92rem; margin-top: -6px; margin-bottom: 22px; }
    hr { border: none; border-top: 1px solid #e0d5f5; margin: 18px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-title">🚀 HireFlow ATS</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Resume Intelligence — Profile · Skills · Language · Interests</p>', unsafe_allow_html=True)

# ---------------------------
# DATABASES
# ---------------------------
SKILLS_DB = [
    "python", "java", "javascript", "typescript", "c", "c++", "c#", "r", "swift",
    "kotlin", "go", "rust", "php", "ruby", "scala", "matlab", "perl",
    "html", "css", "react", "angular", "vue", "nodejs", "django", "flask",
    "fastapi", "spring", "express", "bootstrap", "tailwind",
    "sql", "mysql", "postgresql", "mongodb", "sqlite", "oracle", "nosql",
    "excel", "tableau", "power bi", "looker", "data analysis", "data visualization",
    "data science", "data engineering", "statistics", "pandas", "numpy",
    "matplotlib", "seaborn", "plotly",
    "machine learning", "deep learning", "nlp", "computer vision",
    "tensorflow", "pytorch", "keras", "scikit-learn", "opencv",
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git",
    "github", "gitlab", "ci/cd", "terraform", "linux", "bash",
    "devops", "microservices", "rest api", "graphql",
    "spark", "hadoop", "kafka", "airflow", "dbt",
    "jira", "agile", "scrum", "figma", "photoshop", "illustrator",
    "wordpress", "shopify", "seo", "adobe", "power bi desktop", "power bi service",
]

LANGUAGES = [
    "english", "hindi", "french", "german", "spanish", "arabic", "chinese",
    "mandarin", "japanese", "korean", "portuguese", "russian", "urdu",
    "bengali", "tamil", "telugu", "kannada", "malayalam", "marathi",
    "gujarati", "punjabi", "yoruba", "hausa", "swahili", "italian",
]

INTERESTS = [
    "technology", "tech", "reading", "gaming", "sports", "music", "travel",
    "photography", "cooking", "art", "design", "writing", "research",
    "coding", "programming", "finance", "investing", "teaching", "mentoring",
    "fitness", "yoga", "movies", "animation", "robotics", "entrepreneurship",
    "data", "analytics", "visualization", "open source", "blogging",
]

# ---------------------------
# FILE INPUT
# ---------------------------
file = st.file_uploader("📂 Upload Resume (PDF / DOCX)", type=["pdf", "docx"])

# ---------------------------
# HELPERS
# ---------------------------
def extract_text(file):
    text = ""
    if file.type == "application/pdf":
        pdf = PyPDF2.PdfReader(file)
        for p in pdf.pages:
            text += p.extract_text() or ""
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        d = docx.Document(file)
        for para in d.paragraphs:
            text += para.text + "\n"
    return text

def match_list(text_lower, db):
    found = {}
    for item in db:
        pattern = r'\b' + re.escape(item) + r'\b'
        hits = re.findall(pattern, text_lower)
        if hits:
            found[item] = len(hits)
    return found

def extract_personal(text):
    info = {}
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    # Name — first proper-noun-looking line (2-4 capitalized words)
    skip_kw = {"resume", "curriculum", "vitae", "profile", "summary",
                "experience", "education", "skills", "contact", "objective"}
    for line in lines[:15]:
        words = line.split()
        if 2 <= len(words) <= 4:
            if all(w[0].isupper() for w in words if w.isalpha() and len(w) > 1):
                if not any(w.lower() in skip_kw for w in words):
                    info["name"] = line
                    break

    # Email
    m = re.search(r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}', text)
    if m:
        info["email"] = m.group()

    # Phone
    m = re.search(r'(\+?\d[\d\s\-().]{8,}\d)', text)
    if m:
        raw = m.group().strip()
        if len(re.sub(r'\D', '', raw)) >= 7:
            info["phone"] = raw

    # LinkedIn
    m = re.search(r'linkedin\.com/in/[\w\-]+', text, re.IGNORECASE)
    if m:
        info["linkedin"] = m.group()

    # GitHub
    m = re.search(r'github\.com/[\w\-]+', text, re.IGNORECASE)
    if m:
        info["github"] = m.group()

    # Location
    m = re.search(
        r'\b(bangalore|bengaluru|mumbai|delhi|hyderabad|chennai|pune|kolkata|'
        r'new york|london|dubai|singapore|toronto|sydney|berlin|paris|'
        r'[A-Z][a-z]+,\s*[A-Z]{2,})\b', text, re.IGNORECASE)
    if m:
        info["location"] = m.group()

    # Job title
    title_pat = (
        r'(data\s+visualization\s+engineer|data\s+engineer|software\s+engineer|'
        r'web\s+developer|data\s+scientist|data\s+analyst|ml\s+engineer|'
        r'devops\s+engineer|product\s+manager|ui\s*/\s*ux\s+designer|'
        r'full\s*stack\s+developer|backend\s+developer|frontend\s+developer|'
        r'business\s+analyst|machine\s+learning\s+engineer|ai\s+engineer|'
        r'cloud\s+engineer|software\s+developer|systems\s+engineer)'
    )
    m = re.search(title_pat, text, re.IGNORECASE)
    if m:
        info["title"] = m.group().strip().title()

    return info

def purple_style(ax, fig):
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    for spine in ['left', 'bottom']:
        ax.spines[spine].set_color('#e0d5f5')
    ax.tick_params(colors='#555', labelsize=9)
    ax.yaxis.label.set_color('#4B0082')
    ax.xaxis.label.set_color('#4B0082')
    ax.title.set_color('#4B0082')

def get_purples(n, light=0.4, dark=0.92):
    return [plt.cm.colors.to_hex(c) for c in plt.cm.Purples(np.linspace(light, dark, max(n, 1)))]

# ---------------------------
# MAIN
# ---------------------------
if file:
    raw_text      = extract_text(file)
    text_lower    = raw_text.lower()
    personal      = extract_personal(raw_text)
    skills_found  = match_list(text_lower, SKILLS_DB)
    langs_found   = match_list(text_lower, LANGUAGES)
    ints_found    = match_list(text_lower, INTERESTS)

    # ── ROW 1: Profile card  +  Skill bar chart ─────────────────────────────
    col_p, col_s = st.columns([1, 2.2])

    with col_p:
        name     = personal.get("name",     "Candidate")
        title    = personal.get("title",    "Professional")
        email    = personal.get("email",    "")
        phone    = personal.get("phone",    "")
        loc      = personal.get("location", "")
        linkedin = personal.get("linkedin", "")
        github   = personal.get("github",   "")

        st.markdown(f"""
        <div class="profile-card">
            <div style="font-size:3rem">👤</div>
            <h2>{name}</h2>
            <p>🏷️ {title}</p>
            {"<p>📧 " + email + "</p>" if email else ""}
            {"<p>📞 " + phone + "</p>" if phone else ""}
            {"<p>📍 " + loc + "</p>" if loc else ""}
            {"<p>🔗 " + linkedin + "</p>" if linkedin else ""}
            {"<p>💻 " + github + "</p>" if github else ""}
        </div>
        """, unsafe_allow_html=True)

        if skills_found:
            pills = "".join(
                f'<span class="skill-pill">{s.title()}</span>'
                for s in list(skills_found.keys())[:18]
            )
            st.markdown(f"""
            <div class="section-card">
                <h3>⚡ All Detected Skills</h3>
                {pills}
            </div>""", unsafe_allow_html=True)

    with col_s:
        if skills_found:
            top    = dict(sorted(skills_found.items(), key=lambda x: x[1], reverse=True)[:15])
            labels = list(top.keys())[::-1]
            vals   = list(top.values())[::-1]
            colors = get_purples(len(labels))

            fig, ax = plt.subplots(figsize=(7.5, max(4, len(labels) * 0.52)))
            bars = ax.barh(labels, vals, color=colors[::-1], height=0.62,
                           edgecolor='white', linewidth=0.7)
            for bar, v in zip(bars, vals):
                ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                        str(v), va='center', ha='left', fontsize=8, color='#4B0082', fontweight='600')
            ax.set_xlabel("Frequency in Resume", fontsize=9)
            ax.set_title("📊 Skill Frequency Analysis", fontweight='bold', fontsize=11, pad=12)
            purple_style(ax, fig)
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.warning("⚠️ No known technical skills found. Check the resume content.")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── ROW 2: Language Proficiency  +  Area of Interest ────────────────────
    col_l, col_i = st.columns(2)

    with col_l:
        st.markdown('<div class="section-card"><h3>🌐 Language Proficiency</h3>', unsafe_allow_html=True)
        if langs_found:
            ll     = list(langs_found.keys())
            lv     = list(langs_found.values())
            max_l  = max(lv)
            lpct   = [round((v / max_l) * 100) for v in lv]
            lcolors = get_purples(len(ll), 0.4, 0.88)

            fig2, ax2 = plt.subplots(figsize=(5, max(2.5, len(ll) * 0.58)))
            ax2.barh([x.title() for x in ll[::-1]], lpct[::-1],
                     color=lcolors[::-1], height=0.55, edgecolor='white', linewidth=0.7)
            for i, pct in enumerate(lpct[::-1]):
                ax2.text(pct + 1, i, f'{pct}%', va='center', fontsize=8,
                         color='#4B0082', fontweight='600')
            ax2.set_xlim(0, 120)
            ax2.set_xlabel("Relative Proficiency (%)", fontsize=9)
            ax2.set_title("Language Proficiency", fontweight='bold', fontsize=10, pad=10)
            purple_style(ax2, fig2)
            plt.tight_layout()
            st.pyplot(fig2)
        else:
            st.info("💬 No languages detected. Add a 'Languages' section to your resume (e.g. English, Hindi).")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_i:
        st.markdown('<div class="section-card"><h3>💡 Areas of Interest</h3>', unsafe_allow_html=True)
        if ints_found:
            il     = list(ints_found.keys())
            iv     = list(ints_found.values())
            icolors = get_purples(len(il), 0.3, 0.92)

            fig3, ax3 = plt.subplots(figsize=(5, 4))
            wedges, texts, autotexts = ax3.pie(
                iv,
                labels=[x.title() for x in il],
                autopct='%1.0f%%',
                colors=icolors,
                startangle=140,
                pctdistance=0.76,
                wedgeprops=dict(width=0.58, edgecolor='white', linewidth=1.8)
            )
            for t in texts:
                t.set_fontsize(8)
                t.set_color('#4B0082')
            for at in autotexts:
                at.set_fontsize(7)
                at.set_color('white')
                at.set_fontweight('bold')
            ax3.set_title("Interest Distribution", fontweight='bold', fontsize=10,
                          pad=10, color='#4B0082')
            fig3.patch.set_facecolor('white')
            plt.tight_layout()
            st.pyplot(fig3)
        else:
            st.info("🎯 No interests detected. Add an 'Interests' or 'Hobbies' section to your resume.")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="text-align:center; padding:60px 20px; background:white;
                border-radius:16px; border: 2px dashed #c5a8e8; margin-top:20px;">
        <div style="font-size:3.5rem">📄</div>
        <h3 style="color:#6a0dad; font-family:Poppins,sans-serif;">Upload your resume to get started</h3>
        <p style="color:#999; font-family:Poppins,sans-serif;">Supports PDF and DOCX · Extracts skills, profile, languages & interests</p>
    </div>
    """, unsafe_allow_html=True)
