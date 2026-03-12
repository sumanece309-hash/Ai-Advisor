import json
from pathlib import Path

from openai import OpenAI


def load_courses(path: str = "courses.json") -> list:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


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
    

def recommend_courses_with_ai(profile: dict, client: OpenAI, courses_path: str = "courses.json") -> dict:
    courses = load_courses(courses_path)
    prompt = build_course_advisor_prompt(profile, courses)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "You are a precise career advisor that recommends only from a provided course catalog."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
    )

    return json.loads(response.choices[0].message.content)