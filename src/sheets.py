import gspread
import streamlit as st
from google.oauth2.service_account import Credentials


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