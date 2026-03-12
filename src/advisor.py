from src.config import client


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