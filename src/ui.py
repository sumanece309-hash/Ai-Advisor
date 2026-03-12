import streamlit as st


CURRENT_ROLE_OPTIONS = [
    "Student / Fresher",
    "Project Coordinator",
    "Project Manager",
    "Program Manager",
    "Scrum Master",
    "Product Owner",
    "Business Analyst",
    "Senior Business Analyst",
    "PMO Analyst / PMO Lead",
    "Risk Analyst / Risk Manager",
    "Operations Executive",
    "Operations Manager",
    "Quality Analyst",
    "Process Improvement Analyst",
    "IT Support Engineer",
    "Service Desk Analyst",
    "Service Delivery Manager",
    "IT Operations Engineer",
    "System Administrator",
    "Cloud Engineer",
    "DevOps Engineer",
    "Software Engineer / Developer",
    "Data Analyst",
    "Data Scientist",
    "CRM Administrator",
    "Salesforce Administrator",
    "Sales Operations Specialist",
    "Team Lead / Manager",
    "HR / People Manager",
    "Audit / Compliance / Governance Professional",
    "Other",
]

EXPERIENCE_LEVEL_OPTIONS = [
    "Fresher / 0 years",
    "0–2 years",
    "2–5 years",
    "5–8 years",
    "8–12 years",
    "12+ years",
]

TARGET_ROLE_OPTIONS = [
    "Project Manager",
    "Senior Project Manager",
    "Program Manager",
    "Scrum Master",
    "Agile Coach",
    "Product Owner",
    "Business Analyst",
    "Senior Business Analyst",
    "Risk Manager",
    "PMO Lead",
    "DevOps Engineer",
    "Cloud Engineer",
    "Site Reliability Engineer",
    "Salesforce Administrator",
    "CRM Specialist",
    "Data Analyst",
    "Data Scientist",
    "IT Service Manager",
    "Service Delivery Manager",
    "Governance / Compliance / Audit Lead",
    "Process Improvement Specialist",
    "Quality Manager",
    "Team Lead / People Manager",
    "Not sure yet",
    "Other",
]

PREFERRED_AREA_OPTIONS = [
    "Project Management",
    "Agile & Scrum",
    "Business Analysis",
    "Risk Management",
    "Leadership / People Management",
    "Cloud & DevOps",
    "CRM / Salesforce",
    "Data Science & Analytics",
    "IT Service Management",
    "IT Governance / Audit / Control",
    "Process Improvement / Six Sigma",
    "Not Sure / Need Guidance",
    "Other",
]

INDUSTRY_OPTIONS = [
    "IT / Software",
    "SaaS / Product Company",
    "Banking / Financial Services",
    "Insurance",
    "Retail / E-commerce",
    "Manufacturing",
    "Healthcare / Pharma",
    "Telecom",
    "Consulting / Services",
    "Government / Public Sector",
    "Logistics / Supply Chain",
    "Education",
    "Aviation / Airlines",
    "Energy / Utilities",
    "Real Estate / Construction",
    "Other",
]

CAREER_GOAL_OPTIONS = [
    "Get my first job in this domain",
    "Switch to a new career path",
    "Get promoted in my current path",
    "Build stronger practical skills",
    "Gain a globally recognized certification",
    "Move into leadership / management",
    "Specialize in a niche area",
    "Improve salary / job opportunities",
    "Improve team / process efficiency",
    "Not sure, need guidance",
    "Other",
]

WORK_PREFERENCE_OPTIONS = [
    "Leading teams",
    "Planning and delivery",
    "Working with stakeholders",
    "Managing risks",
    "Improving business processes",
    "Solving operational problems",
    "Configuring business systems",
    "Working with data and insights",
    "Automation and infrastructure",
    "Agile team facilitation",
    "Governance / controls / compliance",
    "Communication and conflict handling",
    "Other",
]

CURRENT_SKILL_LEVEL_OPTIONS = [
    "Beginner",
    "Basic working knowledge",
    "Intermediate",
    "Advanced",
    "Expert",
]

EXISTING_CERTIFICATIONS_OPTIONS = [
    "None",
    "CAPM",
    "PMP",
    "PRINCE2",
    "CSM",
    "PMI-ACP",
    "ITIL",
    "Salesforce",
    "Lean Six Sigma Yellow Belt",
    "Lean Six Sigma Green Belt",
    "Lean Six Sigma Black Belt",
    "CCBA",
    "CBAP",
    "COBIT",
    "Other",
]

STUDY_TIME_OPTIONS = [
    "Less than 2 hours",
    "2–4 hours",
    "4–6 hours",
    "6–8 hours",
    "8–12 hours",
    "12+ hours",
]

TIMELINE_OPTIONS = [
    "Immediately / this month",
    "1–2 months",
    "3–4 months",
    "5–6 months",
    "6+ months",
    "Just exploring",
]

BIGGEST_CHALLENGE_OPTIONS = [
    "I do not know which career path fits me",
    "I want promotion but lack credentials",
    "I want to switch domains",
    "I need stronger practical skills",
    "I need leadership credibility",
    "I need better process / operations knowledge",
    "I need stronger analytics skills",
    "I need Agile / project delivery knowledge",
    "I need system / CRM platform knowledge",
    "I need governance / risk knowledge",
    "Other",
]


def _resolve_other(selected_value: str, other_value: str) -> str:
    if selected_value == "Other":
        return other_value.strip()
    return selected_value


def _resolve_multiselect_other(selected_values: list[str], other_value: str) -> list[str]:
    values = [v for v in selected_values if v != "Other"]
    if "Other" in selected_values and other_value.strip():
        values.append(other_value.strip())
    return values


def render_feature_cards():
    feature_col1, feature_col2, feature_col3 = st.columns(3)

    with feature_col1:
        st.markdown(
            """
            <div class="mini-card">
                <div class="mini-title">Smart match</div>
                <div class="mini-copy">Maps role, goals, experience, and interests to the best-fit course.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with feature_col2:
        st.markdown(
            """
            <div class="mini-card">
                <div class="mini-title">High-converting UX</div>
                <div class="mini-copy">Modern, premium interface that feels more like a product than a simple form.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with feature_col3:
        st.markdown(
            """
            <div class="mini-card">
                <div class="mini-title">Action-ready output</div>
                <div class="mini-copy">Shows why a course fits, what the user will study, and what career value it brings.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_form_and_sidebar():
    left, right = st.columns([1.2, 0.8], gap="large")

    with left:
        st.markdown('<div class="section-title">Start your personalized assessment</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-copy">Tell us about your background, interests, and goals. Our AI will compare your profile with the course catalog and recommend the best fit.</div>',
            unsafe_allow_html=True,
        )

        with st.form("advisor_form"):
            st.markdown("### Basic details")
            c1, c2 = st.columns(2)

            with c1:
                name = st.text_input("Full name *", placeholder="Alex Morgan")
                email = st.text_input("Work email *", placeholder="alex@company.com")
                phone_number = st.text_input("Phone number", placeholder="+1 555 123 4567")

            with c2:
                salary_range = st.selectbox(
                    "Current salary range",
                    [
                        "<$50k",
                        "$50k–$75k",
                        "$75k–$100k",
                        "$100k–$130k",
                        "$130k–$160k",
                        "$160k+",
                    ],
                )
                consent = st.checkbox("Email me the report and relevant course resources.")
                timeline = st.selectbox("Target timeline", TIMELINE_OPTIONS)

            st.markdown("### Career background")
            c3, c4 = st.columns(2)

            with c3:
                current_role_selected = st.selectbox("Current role *", CURRENT_ROLE_OPTIONS)
                current_role_other = ""
                if current_role_selected == "Other":
                    current_role_other = st.text_input("Write your current role")

                experience_level = st.selectbox("Experience level *", EXPERIENCE_LEVEL_OPTIONS)

                industry_selected = st.selectbox("Industry *", INDUSTRY_OPTIONS)
                industry_other = ""
                if industry_selected == "Other":
                    industry_other = st.text_input("Write your industry")

            with c4:
                target_role_selected = st.selectbox("Target role *", TARGET_ROLE_OPTIONS)
                target_role_other = ""
                if target_role_selected == "Other":
                    target_role_other = st.text_input("Write your target role")

                preferred_area_selected = st.selectbox("Preferred career track *", PREFERRED_AREA_OPTIONS)
                preferred_area_other = ""
                if preferred_area_selected == "Other":
                    preferred_area_other = st.text_input("Write your preferred career track")

                current_skill_level = st.selectbox("Current skill confidence", CURRENT_SKILL_LEVEL_OPTIONS)

            st.markdown("### Goals and interests")
            c5, c6 = st.columns(2)

            with c5:
                career_goal_selected = st.selectbox("Main career goal *", CAREER_GOAL_OPTIONS)
                career_goal_other = ""
                if career_goal_selected == "Other":
                    career_goal_other = st.text_input("Write your main career goal")

                study_time_selected = st.selectbox("Study time per week", STUDY_TIME_OPTIONS)

            with c6:
                biggest_challenge_selected = st.selectbox("Biggest career challenge", BIGGEST_CHALLENGE_OPTIONS)
                biggest_challenge_other = ""
                if biggest_challenge_selected == "Other":
                    biggest_challenge_other = st.text_input("Write your biggest career challenge")

            work_preference_selected = st.multiselect(
                "What kind of work do you enjoy most?",
                WORK_PREFERENCE_OPTIONS,
                placeholder="Select all that apply",
            )
            work_preference_other = ""
            if "Other" in work_preference_selected:
                work_preference_other = st.text_input("Other work preference")

            existing_certifications_selected = st.multiselect(
                "Existing certifications",
                EXISTING_CERTIFICATIONS_OPTIONS,
                placeholder="Select all that apply",
            )
            existing_certifications_other = ""
            if "Other" in existing_certifications_selected:
                existing_certifications_other = st.text_input("Other certification")

            st.markdown("### Extra context")
            current_skills = st.text_area(
                "Current skills",
                placeholder="Example: stakeholder management, Jira, Scrum basics, SQL, AWS, Excel...",
                height=100,
            )

            additional_notes = st.text_area(
                "Anything else you want the advisor to know?",
                placeholder="Example: I want to move into a higher-paying role in the next 6 months.",
                height=100,
            )

            submitted = st.form_submit_button("Generate My Roadmap")

    with right:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title" style="font-size:1.2rem; margin-top:0;">What the advisor checks</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="mini-copy" style="margin-bottom:0.8rem;">
                The recommendation engine compares your inputs with the course catalog and ranks the best-fit options.
            </div>
            <div class="resource-chip">Role fit</div>
            <div class="resource-chip">Experience fit</div>
            <div class="resource-chip">Industry fit</div>
            <div class="resource-chip">Career goal fit</div>
            <div class="resource-chip">Interest fit</div>
            <div class="resource-chip">Timeline fit</div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()
        st.markdown(
            """
            <div class="mini-title">What users get</div>
            <div class="mini-copy">
                A personalized recommendation, study roadmap, expected learning outcomes, and 2 additional course options.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()
        st.markdown(
            """
            <div class="mini-title">Best for lead generation</div>
            <div class="mini-copy">
                This form collects both contact details and career intent, which makes follow-up more meaningful and higher quality.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    current_role = _resolve_other(current_role_selected, current_role_other)
    industry = _resolve_other(industry_selected, industry_other)
    target_role = _resolve_other(target_role_selected, target_role_other)
    preferred_area = _resolve_other(preferred_area_selected, preferred_area_other)
    career_goal = _resolve_other(career_goal_selected, career_goal_other)
    biggest_career_challenge = _resolve_other(biggest_challenge_selected, biggest_challenge_other)

    work_preference = _resolve_multiselect_other(work_preference_selected, work_preference_other)
    existing_certifications = _resolve_multiselect_other(existing_certifications_selected, existing_certifications_other)

    return {
        "name": name,
        "email": email,
        "phone_number": phone_number,
        "salary_range": salary_range,
        "consent": consent,
        "timeline": timeline,
        "current_role": current_role,
        "experience_level": experience_level,
        "industry": industry,
        "target_role": target_role,
        "preferred_area": preferred_area,
        "current_skill_level": current_skill_level,
        "career_goal": career_goal,
        "study_time_per_week": study_time_selected,
        "biggest_career_challenge": biggest_career_challenge,
        "work_preference": work_preference,
        "existing_certifications": existing_certifications,
        "current_skills": current_skills,
        "additional_notes": additional_notes,
        "submitted": submitted,
    }