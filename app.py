from datetime import datetime, UTC

import streamlit as st

from src.advisor import recommend_cert, make_prompt, generate_report_text
from src.config import APP_CONFIG
from src.email_utils import send_email_with_pdf
from src.pdf_utils import create_pdf_bytes
from src.resources import RESOURCES
from src.sheets import save_lead_to_gsheet
from src.styles import GLOBAL_CSS, HERO_HTML
from src.ui import render_feature_cards, render_form_and_sidebar


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
    name = form_data["name"]
    email = form_data["email"]
    role = form_data["role"]
    years_exp = form_data["years_exp"]
    industry = form_data["industry"]
    salary_range = form_data["salary_range"]
    goal = form_data["goal"]
    timeline = form_data["timeline"]
    time_per_week = form_data["time_per_week"]
    consent = form_data["consent"]

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