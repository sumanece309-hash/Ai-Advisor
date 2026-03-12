import os

import streamlit as st
from openai import OpenAI


def get_secret(name: str, default: str = "") -> str:
    if name in st.secrets:
        return st.secrets[name]
    return os.getenv(name, default)


OPENAI_API_KEY = get_secret("OPENAI_API_KEY")
SENDGRID_API_KEY = get_secret("SENDGRID_API_KEY")
FROM_EMAIL = get_secret("FROM_EMAIL")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

APP_CONFIG = {
    "page_title": "Excelsior Career Advisor",
    "page_icon": "🎓",
    "layout": "wide",
    "initial_sidebar_state": "collapsed",
}