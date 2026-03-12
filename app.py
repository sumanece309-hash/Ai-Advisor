import json
from datetime import datetime, UTC

import streamlit as st

from src.config import APP_CONFIG, client
from src.email_utils import send_email_with_pdf
from src.pdf_utils import create_pdf_bytes
from src.sheets import save_lead_to_gsheet
from src.styles import GLOBAL_CSS, HERO_HTML
from src.ui import render_feature_cards, render_form_and_sidebar


def load_courses(path: str = "courses.json") -> list:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def build_course_advisor_prompt(profile: dict, courses: list) -> str:
    return f"""
You are a career course advisor.

Your job is to recommend the best-fit course ONLY from the provided course catalog.
Do not invent courses.
Do not make claims outside the provided catalog.
If two courses are similar, explain the difference clearly.

User profile:
{json.dumps(profile, indent=2)}

Course catalog:
{json.dumps(courses, indent=2)}

Return valid JSON in exactly this shape:
{{
  "primary_recommendation": {{
    "course_id": "string",
    "course_name": "string",
    "why_it_fits": ["bullet 1", "bullet 2", "bullet 3"],
    "what_they_will_study": ["bullet 1", "bullet 2", "bullet 3"],
    "career_benefits": ["bullet 1", "bullet 2", "bullet 3"],
    "possible_limitation": "string",
    "fit_score": 0
  }},
  "alternative_recommendations": [
    {{
      "course_id": "string",
      "course_name": "string",
      "why_it_fits": ["bullet 1", "bullet 2"],
      "fit_score": 0
    }},
    {{
      "course_id": "string",
      "course_name": "string",
      "why_it_fits": ["bullet 1", "bullet 2"],
      "fit_score": 0
    }}
  ],
  "advisor_summary": "string"
}}

Scoring guidance:
- fit_score must be between 1 and 10
- evaluate based on current role, target direction, goals, interests, experience, and study time
- prefer the most career-relevant course, not the most prestigious one
"""


def recommend_courses_with_ai(profile: dict, courses: list) -> dict:
    if not client:
        return {"error": "OPENAI_API_KEY not configured."}

    prompt = build_course_advisor_prompt(profile, courses)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "You are a precise career advisor that recommends only from a provided course catalog.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.2,
    )

    return json.loads(response.choices[0].message.content)


def build_report_text(profile: dict, result: dict) -> str:
    primary = result["primary_recommendation"]
    alternatives = result.get("alternative_recommendations", [])
    summary = result.get("advisor_summary", "")

    lines = []

    lines.append("1) Profile Summary")
    lines.append(f"- Name: {profile['name']}")
    lines.append(f"- Current role: {profile['current_role']}")
    lines.append(f"- Industry: {profile['industry']}")
    lines.append(f"- Years of experience: {profile['years_experience']}")
    lines.append(f"- Career goal: {profile['career_goal']}")
    lines.append(f"- Preferred area: {profile['preferred_area']}")
    lines.append(f"- Study time per week: {profile['study_time_per_week']} hours")
    if profile.get("target_role"):
        lines.append(f"- Target role: {profile['target_role']}")
    if profile.get("current_skills"):
        lines.append(f"- Current skills: {profile['current_skills']}")
    if profile.get("biggest_career_challenge"):
        lines.append(f"- Biggest career challenge: {profile['biggest_career_challenge']}")

    lines.append("")
    lines.append("2) Recommended Certification")
    lines.append(f"- Recommended course: {primary['course_name']}")
    lines.append(f"- Fit score: {primary['fit_score']}/10")
    for item in primary["why_it_fits"]:
        lines.append(f"- {item}")

    lines.append("")
    lines.append("3) Salary / ROI Perspective")
    for item in primary["career_benefits"]:
        lines.append(f"- {item}")

    lines.append("")
    lines.append("4) 8-Week Study Roadmap")
    study_items = primary["what_they_will_study"]
    for i in range(8):
        topic = study_items[i % len(study_items)]
        lines.append(f"- Week {i + 1}: Focus on {topic}")

    lines.append("")
    lines.append("5) Common Mistakes to Avoid")
    lines.append(f"- {primary['possible_limitation']}")
    lines.append("- Choosing a course only by popularity instead of career fit")
    lines.append("- Ignoring whether the course matches your current experience level")
    lines.append("- Not planning weekly study time consistently")

    lines.append("")
    lines.append("6) Best Free Resources to Start")
    lines.append("- Review the course outline before enrolling")
    lines.append("- Compare the recommended course with the alternative options")
    lines.append("- Start with beginner articles and videos around the core topics listed below")
    for item in primary["what_they_will_study"]:
        lines.append(f"- Topic to explore: {item}")

    lines.append("")
    lines.append("7) Next Step")
    lines.append("- Self-paced path")
    lines.append("- Talk to an advisor")

    if alternatives:
        lines.append("")
        lines.append("Additional Good Options:")
        for alt in alternatives:
            lines.append(f"- {alt['course_name']} ({alt['fit_score']}/10)")
            for item in alt["why_it_fits"]:
                lines.append(f"- {item}")

    if summary:
        lines.append("")
        lines.append("Advisor Summary:")
        lines.append(f"- {summary}")

    return "\n".join(lines)


st.set_page_config(
    page_title=APP_CONFIG["page_title"],
    page_icon=APP_CONFIG["page_icon"],
    layout=APP_CONFIG["layout"],
    initial_sidebar_state=APP_CONFIG["initial_sidebar_state"],
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
st.markdown(HERO_HTML, unsafe_allow_html=True)

st.write("")
render_feature_cards()

st.write("")
form_data = render_form_and_sidebar()

if form_data["submitted"]:
    name = form_data.get("name", "")
    email = form_data.get("email", "")
    role = form_data.get("role", "")
    years_exp = form_data.get("years_exp", 0)
    industry = form_data.get("industry", "")
    salary_range = form_data.get("salary_range", "")
    goal = form_data.get("goal", "")
    timeline = form_data.get("timeline", "")
    time_per_week = form_data.get("time_per_week", 0)
    consent = form_data.get("consent", False)

    # New optional fields
    target_role = form_data.get("target_role", "")
    preferred_area = form_data.get("preferred_area", "")
    current_skills = form_data.get("current_skills", "")
    biggest_career_challenge = form_data.get("biggest_career_challenge", "")

    if not name or not email or not role or not goal:
        st.error("Please complete all required fields marked with *.")
        st.stop()

    courses = load_courses("courses.json")
    if not courses:
        st.error("courses.json was not found or is empty.")
        st.stop()

    profile = {
        "name": name,
        "email": email,
        "current_role": role,
        "years_experience": int(years_exp),
        "industry": industry,
        "salary_range": salary_range,
        "career_goal": goal,
        "study_time_per_week": int(time_per_week),
        "timeline": timeline,
        "target_role": target_role,
        "preferred_area": preferred_area,
        "current_skills": current_skills,
        "biggest_career_challenge": biggest_career_challenge,
    }

    with st.spinner("Analyzing your profile and matching the best course..."):
        result = recommend_courses_with_ai(profile, courses)

    if "error" in result:
        st.error(result["error"])
        st.stop()

    primary = result["primary_recommendation"]
    alternatives = result.get("alternative_recommendations", [])
    report_text = build_report_text(profile, result)

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
        "preferred_area": preferred_area,
        "target_role": target_role,
        "recommended_cert": primary["course_name"],
        "fit_score": primary["fit_score"],
        "source": "ai_course_catalog_matcher_v1",
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
        st.markdown(f"## {primary['course_name']}")
        st.markdown(f"**Fit score:** {primary['fit_score']}/10")

        st.markdown("### Why this fits you")
        for item in primary["why_it_fits"]:
            st.markdown(f"- {item}")

        st.markdown("### What you will study")
        for item in primary["what_they_will_study"]:
            st.markdown(f"- {item}")

        st.markdown("### Career benefits")
        for item in primary["career_benefits"]:
            st.markdown(f"- {item}")

        st.markdown(f"**Possible limitation:** {primary['possible_limitation']}")

        if alternatives:
            st.markdown("### Other good options")
            for alt in alternatives:
                st.markdown(f"**{alt['course_name']}** ({alt['fit_score']}/10)")
                for item in alt["why_it_fits"]:
                    st.markdown(f"- {item}")

        st.download_button(
            label="⬇️ Download PDF roadmap",
            data=pdf_bytes,
            file_name=f"Excelsior_{primary['course_id']}_Roadmap_{name.replace(' ', '_')}.pdf",
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
            body="Hi! Attached is your personalized certification roadmap based on your goals, background, and best-fit course match.",
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

if st.button("Test Google Sheet Connection"):
    try:
        test_row = {
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "name": "Test User",
            "email": "test@example.com",
            "role": "Tester",
        }
        save_lead_to_gsheet(test_row)
        st.success("Google Sheet write successful.")
    except Exception as e:
        st.error(f"Google Sheet write failed: {e}")