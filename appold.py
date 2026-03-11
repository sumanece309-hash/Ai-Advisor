import os
import json
import csv
from datetime import datetime
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors
from datetime import datetime, UTC

import streamlit as st
from dotenv import load_dotenv

from openai import OpenAI
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Optional: email delivery
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "")  # e.g. "reports@excelsiorcertification.com"

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

st.set_page_config(page_title="AI Certification Advisor", page_icon="🎓", layout="centered")

# ---------- Helpers ----------
def load_resources():
    try:
        with open("resources.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

RESOURCES = load_resources()

def recommend_cert(role: str, industry: str, years_exp: int, goal: str):
    """Rule-based MVP recommendation. Keep deterministic."""
    r = (role or "").lower()
    i = (industry or "").lower()
    g = (goal or "").lower()

    # Simple, practical rules (tweak later)
    if "project" in r or "program" in r or "scrum" in r:
        if years_exp >= 3:
            return "PMP"
        else:
            return "PMP"  # still ok; later you can suggest CAPM for <3 yrs
    if "it" in r or "service" in r or "support" in r or "sysadmin" in r:
        return "ITIL"
    if "operations" in r or "quality" in r or "process" in r or "manufact" in i:
        return "Lean Six Sigma"
    if "devops" in r or "sre" in r or "cloud" in r or "developer" in r or "engineer" in r:
        return "DevOps"

    # Goal-based fallback
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
1) Profile Summary (2-3 bullets)
2) Recommended Certification (one line + 3 bullets why it fits)
3) Salary / ROI Perspective (give a realistic range, avoid fake precision, include assumptions)
4) 8-Week Study Roadmap (week-by-week bullets)
5) Common Mistakes to Avoid (5 bullets)
6) Best Free Resources to Start (use only the list below)
7) Next Step (two options: "Self-paced path" and "Talk to an advisor")

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
    """
    Creates a clean PDF:
    - Colored section headings
    - Bullet points
    - Nice spacing
    Assumes report_text has sections like:
      1) Profile Summary
      - bullet
      - bullet
      2) Recommended Certification
      ...
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=48, rightMargin=48,
        topMargin=54, bottomMargin=48
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        spaceAfter=8,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#0B1F44")  # dark navy
    )

    brand_style = ParagraphStyle(
        "BrandStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        textColor=colors.HexColor("#555555"),
        spaceAfter=14
    )

    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12.5,
        textColor=colors.HexColor("#1F6FEB"),  # blue
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#111111")
    )

    # Bullet list style: ListFlowable handles bullets; Paragraph handles wrapping.
    bullet_para_style = ParagraphStyle(
        "BulletPara",
        parent=body_style,
        leftIndent=0,
        spaceBefore=0,
        spaceAfter=0
    )

    story = []
    story.append(Paragraph(title, title_style))
    story.append(Paragraph(f"{branding_line} &nbsp;&nbsp;|&nbsp;&nbsp; Generated: {datetime.utcnow().strftime('%Y-%m-%d')}", brand_style))

    # --- Parse report_text into sections + bullet lines ---
    lines = [ln.rstrip() for ln in report_text.split("\n")]
    sections = []  # list of (heading, [bullets], [plain_paras])

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

        # Detect headings like "1) Profile Summary" or "Profile Summary:"
        is_numbered_heading = (len(ln) > 2 and ln[0].isdigit() and ln[1:3] == ") ")
        is_colon_heading = ln.endswith(":") and len(ln) < 80

        if is_numbered_heading or is_colon_heading:
            flush()
            # Clean heading text
            if is_numbered_heading:
                current_heading = ln.split(") ", 1)[1].strip()
            else:
                current_heading = ln[:-1].strip()
            continue

        # Bullet lines starting with "-", "•", "*"
        if ln.lstrip().startswith(("-", "•", "*")):
            bullet = ln.lstrip()[1:].strip()
            if bullet:
                current_bullets.append(bullet)
            continue

        # Otherwise treat as normal paragraph line
        current_paras.append(ln.strip())

    flush()

    # --- Render sections ---
    for heading, bullets, paras in sections:
        story.append(Paragraph(heading, heading_style))

        # Paragraphs (if any)
        for p in paras:
            story.append(Paragraph(p, body_style))
            story.append(Spacer(1, 6))

        # Bullets (if any)
        if bullets:
            items = []
            for b in bullets:
                items.append(
                    ListItem(
                        Paragraph(b, bullet_para_style),
                        leftIndent=14
                    )
                )
            story.append(
                ListFlowable(
                    items,
                    bulletType="bullet",
                    bulletFontName="Helvetica",
                    bulletFontSize=10,
                    bulletColor=colors.HexColor("#111111"),
                    leftIndent=16
                )
            )
            story.append(Spacer(1, 10))

    # Footer disclaimer
    story.append(Spacer(1, 8))
    story.append(
        Paragraph(
            "Disclaimer: This report is informational and does not guarantee outcomes.",
            ParagraphStyle(
                "Disclaimer",
                parent=styles["Normal"],
                fontSize=9,
                textColor=colors.HexColor("#666666"),
                spaceBefore=10
            )
        )
    )

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def save_lead_csv(row: dict, path="leads.csv"):
    file_exists = os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

def send_email_with_pdf(to_email: str, subject: str, body: str, pdf_bytes: bytes, filename="Certification_Roadmap.pdf"):
    if not SENDGRID_API_KEY or not FROM_EMAIL:
        return False, "SendGrid not configured (SENDGRID_API_KEY / FROM_EMAIL missing)."

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        plain_text_content=body
    )

    encoded = base64.b64encode(pdf_bytes).decode()
    attachment = Attachment(
        FileContent(encoded),
        FileName(filename),
        FileType("application/pdf"),
        Disposition("attachment")
    )
    message.attachment = attachment

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
        return True, "Email sent."
    except Exception as e:
        return False, str(e)

# ---------- UI ----------
st.title("🎓 AI Certification Career Advisor (MVP)")
st.caption("Collect user inputs → recommend the best certification → generate a personalized PDF report.")

with st.form("advisor_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name *")
        email = st.text_input("Email *")
        role = st.text_input("Current role/title *", placeholder="e.g., Project Coordinator, IT Support, DevOps Engineer")
        years_exp = st.number_input("Years of experience *", min_value=0, max_value=40, value=3)
    with col2:
        industry = st.text_input("Industry", placeholder="e.g., Healthcare, Finance, Manufacturing, SaaS")
        salary_range = st.selectbox("Current salary range (USD)", [
            "<$50k", "$50k–$75k", "$75k–$100k", "$100k–$130k", "$130k–$160k", "$160k+"
        ])
        goal = st.text_input("Career goal *", placeholder="e.g., promotion to manager, switch to PM, higher salary")
        time_per_week = st.slider("Study time per week", min_value=2, max_value=20, value=6)
        timeline = st.selectbox("Target timeline", ["1–2 months", "2–3 months", "3–6 months", "6+ months"])

    consent = st.checkbox("I agree to receive my report and relevant certification resources by email.")
    submitted = st.form_submit_button("Generate My Roadmap")

if submitted:
    if not name or not email or not role or not goal:
        st.error("Please fill all required fields (*).")
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
        "timeline": timeline
    }

    chosen = recommend_cert(role, industry, int(years_exp), goal)
    res_list = RESOURCES.get(chosen, [])

    st.info(f"Recommended track: **{chosen}**")

    prompt = make_prompt(profile, chosen, res_list)
    report_text = generate_report_text(prompt)

    if report_text.startswith("ERROR:"):
        st.error(report_text)
        st.stop()

    title = "Your Personalized Certification Roadmap"
    pdf_bytes = create_pdf_bytes(title=title, report_text=report_text, branding_line="Excelsior Certification")

    # Save lead (source tagging)
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
        "source": "ai_assessment_v1"
    }
    save_lead_csv(lead_row)

    st.subheader("✅ Your Report (Preview)")
    st.text_area("Report text", report_text, height=320)

    st.download_button(
        label="⬇️ Download PDF",
        data=pdf_bytes,
        file_name=f"Excelsior_{chosen}_Roadmap_{name.replace(' ','_')}.pdf",
        mime="application/pdf"
    )

    # Email (optional)
    if consent:
        ok, msg = send_email_with_pdf(
            to_email=email,
            subject="Your Personalized Certification Roadmap",
            body="Hi! Attached is your personalized certification roadmap. Reply to this email if you'd like help choosing the best learning path.",
            pdf_bytes=pdf_bytes
        )
        if ok:
            st.success("📧 Sent to your email.")
        else:
            st.warning(f"Email not sent: {msg}")

    st.markdown("---")
    st.write("Next step CTA idea: add a 'Book a free strategy call' button with a tracked link.")
