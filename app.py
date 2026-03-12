import os
import json
import base64
from datetime import datetime, UTC
from io import BytesIO

import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
from openai import OpenAI
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Attachment, Disposition, FileContent, FileName, FileType, Mail


def get_secret(name: str, default: str = "") -> str:
    if name in st.secrets:
        return st.secrets[name]
    return os.getenv(name, default)


OPENAI_API_KEY = get_secret("OPENAI_API_KEY")
SENDGRID_API_KEY = get_secret("SENDGRID_API_KEY")
FROM_EMAIL = get_secret("FROM_EMAIL")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

st.set_page_config(
    page_title="Excelsior Career Advisor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def load_resources():
    try:
        with open("resources.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


RESOURCES = load_resources()


def get_gsheet_worksheet():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]),
        scopes=scope,
    )
    gc = gspread.authorize(creds)

    sheet_name = st.secrets["google_sheet"]["sheet_name"]
    worksheet_name = st.secrets["google_sheet"]["worksheet"]

    spreadsheet = gc.open(sheet_name)
    worksheet = spreadsheet.worksheet(worksheet_name)
    return worksheet


def save_lead_to_gsheet(row: dict):
    worksheet = get_gsheet_worksheet()
    headers = list(row.keys())
    existing_headers = worksheet.row_values(1)

    if not existing_headers:
        worksheet.append_row(headers)

    worksheet.append_row([str(row.get(h, "")) for h in headers])


def recommend_cert(role: str, industry: str, years_exp: int, goal: str):
    r = (role or "").lower()
    i = (industry or "").lower()
    g = (goal or "").lower()

    if "project" in r or "program" in r or "scrum" in r:
        return "PMP"
    if "it" in r or "service" in r or "support" in r or "sysadmin" in r:
        return "ITIL"
    if "operations" in r or "quality" in r or "process" in r or "manufact" in i:
        return "Lean Six Sigma"
    if "devops" in r or "sre" in r or "cloud" in r or "developer" in r or "engineer" in r:
        return "DevOps"
    if "lead" in g or "manager" in g or "promotion" in g:
        return "PMP"
    if "efficiency" in g or "process" in g:
        return "Lean Six Sigma"
    return "PMP"


def make_prompt(profile: dict, chosen_cert: str, resources: list):
    res_lines = "\n".join([f"- {x['title']}: {x['url']}" for x in resources]) if resources else "None"
    return f"""
You are a US-focused career & certification advisor for working professionals.

Write a concise, highly practical report (max ~900 words) with clear headings and bullet points.
Tone: professional, supportive, not salesy.

User profile:
- Name: {profile['name']}
- Current role: {profile['role']}
- Years of experience: {profile['years_exp']}
- Industry: {profile['industry']}
- Current salary range (USD): {profile['salary_range']}
- Career goal: {profile['goal']}
- Time available per week: {profile['time_per_week']} hours
- Timeline: {profile['timeline']}

Recommended certification: {chosen_cert}

Include these sections EXACTLY:
1) Profile Summary
2) Recommended Certification
3) Salary / ROI Perspective
4) 8-Week Study Roadmap
5) Common Mistakes to Avoid
6) Best Free Resources to Start
7) Next Step

For each section use concise bullets.
For Next Step, provide these two options exactly:
- Self-paced path
- Talk to an advisor

Allowed free resources list:
{res_lines}

Do not invent external links. Do not mention you are an AI.
"""


def generate_report_text(prompt: str) -> str:
    if not client:
        return "ERROR: OPENAI_API_KEY not configured."

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You write structured career advisory reports."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
    )
    return resp.choices[0].message.content.strip()


def create_pdf_bytes(title: str, report_text: str, branding_line: str = "Excelsior Certification"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=48,
        rightMargin=48,
        topMargin=54,
        bottomMargin=48,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        spaceAfter=8,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#102542"),
    )
    brand_style = ParagraphStyle(
        "BrandStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        textColor=colors.HexColor("#667085"),
        spaceAfter=14,
    )
    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12.5,
        textColor=colors.HexColor("#175CD3"),
        spaceBefore=10,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#101828"),
    )
    bullet_para_style = ParagraphStyle(
        "BulletPara",
        parent=body_style,
        leftIndent=0,
        spaceBefore=0,
        spaceAfter=0,
    )

    story = [
        Paragraph(title, title_style),
        Paragraph(
            f"{branding_line} &nbsp;&nbsp;|&nbsp;&nbsp; Generated: {datetime.utcnow().strftime('%Y-%m-%d')}",
            brand_style,
        ),
    ]

    lines = [ln.rstrip() for ln in report_text.split("\n")]
    sections = []
    current_heading = None
    current_bullets = []
    current_paras = []

    def flush():
        nonlocal current_heading, current_bullets, current_paras
        if current_heading:
            sections.append((current_heading, current_bullets[:], current_paras[:]))
        current_heading = None
        current_bullets = []
        current_paras = []

    for ln in lines:
        if not ln.strip():
            continue

        is_numbered_heading = len(ln) > 2 and ln[0].isdigit() and ln[1:3] == ") "
        is_colon_heading = ln.endswith(":") and len(ln) < 80

        if is_numbered_heading or is_colon_heading:
            flush()
            current_heading = ln.split(") ", 1)[1].strip() if is_numbered_heading else ln[:-1].strip()
            continue

        if ln.lstrip().startswith(("-", "•", "*")):
            bullet = ln.lstrip()[1:].strip()
            if bullet:
                current_bullets.append(bullet)
            continue

        current_paras.append(ln.strip())

    flush()

    for heading, bullets, paras in sections:
        story.append(Paragraph(heading, heading_style))
        for p in paras:
            story.append(Paragraph(p, body_style))
            story.append(Spacer(1, 6))

        if bullets:
            items = [ListItem(Paragraph(b, bullet_para_style), leftIndent=14) for b in bullets]
            story.append(
                ListFlowable(
                    items,
                    bulletType="bullet",
                    bulletFontName="Helvetica",
                    bulletFontSize=10,
                    bulletColor=colors.HexColor("#101828"),
                    leftIndent=16,
                )
            )
            story.append(Spacer(1, 10))

    story.append(Spacer(1, 8))
    story.append(
        Paragraph(
            "Disclaimer: This report is informational and does not guarantee outcomes.",
            ParagraphStyle(
                "Disclaimer",
                parent=styles["Normal"],
                fontSize=9,
                textColor=colors.HexColor("#667085"),
                spaceBefore=10,
            ),
        )
    )

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def send_email_with_pdf(
    to_email: str,
    subject: str,
    body: str,
    pdf_bytes: bytes,
    filename="Certification_Roadmap.pdf",
):
    if not SENDGRID_API_KEY or not FROM_EMAIL:
        return False, "SendGrid not configured (SENDGRID_API_KEY / FROM_EMAIL missing)."

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        plain_text_content=body,
    )

    encoded = base64.b64encode(pdf_bytes).decode()
    message.attachment = Attachment(
        FileContent(encoded),
        FileName(filename),
        FileType("application/pdf"),
        Disposition("attachment"),
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
        return True, "Email sent."
    except Exception as e:
        return False, str(e)


st.markdown(
    """
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
        color: white;
        box-shadow: 0 30px 60px rgba(2, 6, 23, 0.20);
        border: 1px solid rgba(255,255,255,0.10);
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
        color: white;
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
        background: white;
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
        background: rgba(255,255,255,0.82);
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
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
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
    """,
    unsafe_allow_html=True,
)

st.write("")
feature_col1, feature_col2, feature_col3 = st.columns(3)

with feature_col1:
    st.markdown(
        """
        <div class="mini-card">
            <div class="mini-title">Smart match</div>
            <div class="mini-copy">Maps role, goals, and experience to a certification track that feels relevant.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with feature_col2:
    st.markdown(
        """
        <div class="mini-card">
            <div class="mini-title">High-converting UX</div>
            <div class="mini-copy">Clean, modern interface that looks more like a premium product than a basic form.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with feature_col3:
    st.markdown(
        """
        <div class="mini-card">
            <div class="mini-title">Action-ready output</div>
            <div class="mini-copy">Preview the report, download a PDF, and optionally email it to the user instantly.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")
left, right = st.columns([1.18, 0.82], gap="large")

with left:
    st.markdown('<div class="section-title">Start your personalized assessment</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">Answer a few quick questions so we can recommend the most suitable certification path and generate a polished roadmap.</div>',
        unsafe_allow_html=True,
    )

    with st.form("advisor_form"):
        c1, c2 = st.columns(2)

        with c1:
            name = st.text_input("Full name *", placeholder="Alex Morgan")
            email = st.text_input("Work email *", placeholder="alex@company.com")
            role = st.text_input("Current role/title *", placeholder="Project Coordinator, IT Support, DevOps Engineer")
            years_exp = st.number_input("Years of experience *", min_value=0, max_value=40, value=3)

        with c2:
            industry = st.text_input("Industry", placeholder="Healthcare, Finance, Manufacturing, SaaS")
            salary_range = st.selectbox(
                "Current salary range (USD)",
                ["<$50k", "$50k–$75k", "$75k–$100k", "$100k–$130k", "$130k–$160k", "$160k+"],
            )
            goal = st.text_input("Career goal *", placeholder="Promotion to manager, switch to PM, higher salary")
            timeline = st.selectbox("Target timeline", ["1–2 months", "2–3 months", "3–6 months", "6+ months"])

        time_per_week = st.slider("Study time available per week", min_value=2, max_value=20, value=6)
        consent = st.checkbox("Email me the report and relevant certification resources.")
        submitted = st.form_submit_button("Generate My Roadmap")

with right:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title" style="font-size:1.2rem; margin-top:0;">What users get</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="mini-copy" style="margin-bottom:0.8rem;">
            A personalized recommendation backed by a practical study plan, useful starter resources, and a clear next step.
        </div>
        <div class="resource-chip">PMP</div>
        <div class="resource-chip">ITIL</div>
        <div class="resource-chip">Lean Six Sigma</div>
        <div class="resource-chip">DevOps</div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown(
        """
        <div class="mini-title">Why this page converts</div>
        <div class="mini-copy">
            It gives visitors something genuinely valuable before asking them to take the next step. That makes it work well for paid ads,
            organic SEO pages, and email follow-up journeys.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown(
        """
        <div class="mini-title">Perfect CTA after the report</div>
        <div class="mini-copy">
            Add a “Book a free strategy call” button or “Compare certification paths” page after report generation.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

if submitted:
    if not name or not email or not role or not goal:
        st.error("Please complete all required fields marked with *.")
        st.stop()

    profile = {
        "name": name,
        "email": email,
        "role": role,
        "years_exp": int(years_exp),
        "industry": industry,
        "salary_range": salary_range,
        "goal": goal,
        "time_per_week": int(time_per_week),
        "timeline": timeline,
    }

    chosen = recommend_cert(role, industry, int(years_exp), goal)
    res_list = RESOURCES.get(chosen, [])

    with st.spinner("Creating your personalized roadmap..."):
        prompt = make_prompt(profile, chosen, res_list)
        report_text = generate_report_text(prompt)

    if report_text.startswith("ERROR:"):
        st.error(report_text)
        st.stop()

    pdf_bytes = create_pdf_bytes(
        title="Your Personalized Certification Roadmap",
        report_text=report_text,
        branding_line="Excelsior Certification",
    )

    lead_row = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "name": name,
        "email": email,
        "role": role,
        "years_exp": int(years_exp),
        "industry": industry,
        "salary_range": salary_range,
        "goal": goal,
        "timeline": timeline,
        "recommended_cert": chosen,
        "source": "ai_assessment_v2_beautiful_ui",
    }

    try:
        save_lead_to_gsheet(lead_row)
    except Exception as e:
        st.warning(f"Lead could not be saved to Google Sheets: {e}")

    st.write("")
    r1, r2 = st.columns([0.95, 1.05], gap="large")

    with r1:
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown('<div class="result-badge">Recommended Track</div>', unsafe_allow_html=True)
        st.markdown(f"## {chosen}")
        st.write("Based on the profile details submitted, this is the best-fit starting point for the user journey.")

        if res_list:
            st.markdown("**Starter resources**")
            for item in res_list:
                st.markdown(f"- [{item['title']}]({item['url']})")

        st.download_button(
            label="⬇️ Download PDF roadmap",
            data=pdf_bytes,
            file_name=f"Excelsior_{chosen}_Roadmap_{name.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with r2:
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown('<div class="result-badge">Report Preview</div>', unsafe_allow_html=True)
        st.text_area("Preview", report_text, height=420, label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)

    if consent:
        ok, msg = send_email_with_pdf(
            to_email=email,
            subject="Your Personalized Certification Roadmap",
            body="Hi! Attached is your personalized certification roadmap. Reply to this email if you'd like help choosing the best learning path.",
            pdf_bytes=pdf_bytes,
        )
        if ok:
            st.success("Your roadmap was also sent by email.")
        else:
            st.warning(f"Email not sent: {msg}")

    st.info("Suggested next conversion step: add a primary CTA button such as ‘Book a free strategy call’.")

st.markdown(
    '<div class="footer-note">Designed for a premium first impression, stronger lead capture, and a smoother certification discovery journey.</div>',
    unsafe_allow_html=True,
)