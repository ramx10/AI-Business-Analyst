import pandas as pd
import json
import os

EXPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)


def export_to_csv(df, path):
    df.to_csv(path, index=False)


def export_to_excel(df, path, sheet_name="Data"):
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)


def export_to_tableau_hyper(df, path):
    import pantab
    pantab.frame_to_hyper(df, path, table="export")


def export_to_tableau_tde(df, path):
    export_to_tableau_hyper(df, path.replace(".tde", ".hyper"))


def export_to_powerbi(df, path):
    export_to_parquet(df, path)


def export_to_parquet(df, path):
    df.to_parquet(path, index=False)


def export_to_json(df, path, orient="records"):
    df.to_json(path, orient=orient, indent=2)


def export_to_google_sheets(df, credentials_json, spreadsheet_id, sheet_name="Export"):
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(credentials_json), scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(spreadsheet_id)
    try:
        worksheet = sheet.worksheet(sheet_name)
    except Exception:
        worksheet = sheet.add_worksheet(title=sheet_name, rows="1000", cols="26")
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())


def get_export_formats():
    return [
        {"id": "csv", "name": "CSV", "icon": "⊡", "description": "Universal plain-text format", "extension": ".csv"},
        {"id": "excel", "name": "Excel (.xlsx)", "icon": "▣", "description": "Microsoft Excel workbook", "extension": ".xlsx"},
        {"id": "parquet", "name": "Parquet", "icon": "▣", "description": "Columnar storage (Apache Parquet)", "extension": ".parquet"},
        {"id": "json", "name": "JSON", "icon": "≡", "description": "Structured JSON records", "extension": ".json"},
        {"id": "tableau_hyper", "name": "Tableau Hyper", "icon": "≡", "description": "Tableau data extract format", "extension": ".hyper"},
        {"id": "powerbi", "name": "Power BI (Parquet)", "icon": "▣", "description": "Power BI-compatible format", "extension": ".parquet"},
        {"id": "google_sheets", "name": "Google Sheets", "icon": "✦", "description": "Push to Google Sheets (requires credentials)", "extension": ""},
    ]
