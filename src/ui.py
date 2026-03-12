import streamlit as st


def render_feature_cards():
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


def render_form_and_sidebar():
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

    return {
        "name": name,
        "email": email,
        "role": role,
        "years_exp": years_exp,
        "industry": industry,
        "salary_range": salary_range,
        "goal": goal,
        "timeline": timeline,
        "time_per_week": time_per_week,
        "consent": consent,
        "submitted": submitted,
    }