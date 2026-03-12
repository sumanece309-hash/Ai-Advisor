GLOBAL_CSS = """
<style>
.stApp {
    background:
        radial-gradient(circle at top left, rgba(16,185,129,0.14), transparent 28%),
        radial-gradient(circle at top right, rgba(59,130,246,0.14), transparent 30%),
        linear-gradient(180deg, #f8fbff 0%, #f4f7fb 46%, #eef4ff 100%);
}
.block-container {
    padding-top: 1.6rem;
    padding-bottom: 2rem;
    max-width: 1180px;
}
.hero-card {
    padding: 2.4rem 2.2rem;
    border-radius: 28px;
    background: linear-gradient(135deg, #0f172a 0%, #0b3b8a 55%, #1d4ed8 100%);
    color: #d1d5db;
    box-shadow: 0 30px 60px rgba(2, 6, 23, 0.20);
    border: 1px solid rgba(255,255,255,0.10);
}

.form-section-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #1f2937;  /* dark gray */
    margin-top: 20px;
    margin-bottom: 10px;
}


.hero-kicker {
    display: inline-block;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #dbeafe;
    background: rgba(255,255,255,0.08);
    padding: 0.45rem 0.8rem;
    border-radius: 999px;
    margin-bottom: 1rem;
}
.hero-title {
    font-size: 3rem;
    font-weight: 800;
    line-height: 1.05;
    margin: 0 0 0.8rem 0;
}
.hero-subtitle {
    font-size: 1.06rem;
    line-height: 1.7;
    color: rgba(255,255,255,0.88);
    max-width: 740px;
}
.stat-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1rem;
    margin-top: 1.4rem;
}
.stat-card {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 20px;
    padding: 1rem 1.1rem;
    backdrop-filter: blur(10px);
}
.stat-value {
    color: #d1d5db;
    font-size: 1.15rem;
    font-weight: 800;
    margin-bottom: 0.2rem;
}
.stat-label {
    color: rgba(255,255,255,0.78);
    font-size: 0.92rem;
}
.section-title {
    font-size: 1.55rem;
    font-weight: 800;
    color: #0f172a;
    margin: 0.3rem 0 1rem 0;
}
.section-copy {
    color: #475467;
    font-size: 1rem;
    line-height: 1.7;
    margin-bottom: 1.25rem;
}
.glass-card {
    background: rgba(255,255,255,0.72);
    border: 1px solid rgba(255,255,255,0.75);
    box-shadow: 0 20px 45px rgba(15,23,42,0.08);
    border-radius: 24px;
    padding: 1.4rem;
    backdrop-filter: blur(14px);
}
.mini-card {
    background: #d1d5db;
    border: 1px solid #e4e7ec;
    border-radius: 20px;
    padding: 1.05rem 1rem;
    box-shadow: 0 8px 20px rgba(16,24,40,0.04);
    height: 100%;
}
.mini-title {
    font-size: 1rem;
    font-weight: 700;
    color: #101828;
    margin-bottom: 0.35rem;
}
.mini-copy {
    font-size: 0.93rem;
    color: #475467;
    line-height: 1.6;
}
.result-card {
    background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
    border: 1px solid #dbe7ff;
    box-shadow: 0 18px 40px rgba(23,92,211,0.10);
    border-radius: 26px;
    padding: 1.4rem;
}
.result-badge {
    display: inline-block;
    padding: 0.45rem 0.8rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    color: #175CD3;
    background: #eaf2ff;
    margin-bottom: 0.8rem;
}
.resource-chip {
    display: inline-block;
    padding: 0.45rem 0.7rem;
    border-radius: 999px;
    background: #f2f4f7;
    color: #344054;
    font-size: 0.8rem;
    margin-right: 0.4rem;
    margin-bottom: 0.4rem;
}
[data-testid="stForm"] {
    background: #1F2937;
    border: 1px solid rgba(255,255,255,0.8);
    border-radius: 28px;
    padding: 1.3rem;
    box-shadow: 0 22px 46px rgba(15,23,42,0.08);
    backdrop-filter: blur(12px);
}
.stTextInput > div > div > input,
.stNumberInput input,
.stSelectbox [data-baseweb="select"],
.stTextArea textarea {
    border-radius: 14px !important;
}
.stButton > button,
.stDownloadButton > button,
.stFormSubmitButton > button {
    border-radius: 14px !important;
    font-weight: 700 !important;
    padding: 0.7rem 1rem !important;
    border: 1px solid transparent !important;
    box-shadow: 0 10px 24px rgba(23,92,211,0.18);
}
.footer-note {
    text-align: center;
    color: #667085;
    font-size: 0.92rem;
    padding: 1rem 0 0.5rem 0;
}
@media (max-width: 900px) {
    .hero-title { font-size: 2.25rem; }
    .stat-grid { grid-template-columns: 1fr; }

/* Fix white text inside form section */
[data-testid="stForm"] label,
[data-testid="stForm"] p,
[data-testid="stForm"] div,
[data-testid="stForm"] span,
[data-testid="stForm"] h1,
[data-testid="stForm"] h2,
[data-testid="stForm"] h3,
[data-testid="stForm"] h4,
[data-testid="stForm"] h5,
[data-testid="stForm"] h6 {
    color: #101828 !important;
}

/* Fix section headings */
.section-title,
.section-copy,
.mini-title,
.mini-copy {
    color: #101828 !important;
}

/* Fix selectbox and input label text */
.stSelectbox label,
.stTextInput label,
.stTextArea label,
.stMultiSelect label,
.stCheckbox label {
    color: #101828 !important;
}

/* Fix markdown text in columns/cards */
.element-container,
.stMarkdown,
.stMarkdown p,
.stMarkdown div,
.stMarkdown span {
    color: #101828;
}


}
</style>
"""

HERO_HTML = """
<div class="hero-card">
    <div class="hero-kicker">Career Growth • Certification Guidance • Lead Generation</div>
    <div class="hero-title">Find the right certification for your next career move.</div>
    <div class="hero-subtitle">
        Turn anonymous visitors into qualified leads with a polished assessment that recommends the best-fit certification,
        explains the ROI, and instantly delivers a personalized roadmap PDF.
    </div>
    <div class="stat-grid">
        <div class="stat-card">
            <div class="stat-value">3-minute assessment</div>
            <div class="stat-label">Fast enough for ad traffic and landing page visitors</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">Personalized report</div>
            <div class="stat-label">Useful output that feels premium and worth sharing</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">Lead capture built in</div>
            <div class="stat-label">Save contact and recommendation data for follow-up</div>
        </div>
    </div>
</div>
"""


