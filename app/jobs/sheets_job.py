"""
Google Sheets Background Job

Inserts member records into Google Sheets for record keeping.
"""

import json
import os
import gspread
from pathlib import Path
from typing import Any

# Path to service account credentials (local development)
CREDS_PATH = Path(__file__).parent.parent.parent / "gapi_creds.json"
SPREADSHEET_NAME = "AF-API-SHEET"


def get_sheet_client() -> gspread.Client:
    """
    Authenticate and return a gspread client.

    Reads credentials from environment variable (production) or file (local dev).

    Returns:
        gspread.Client: Authenticated client for Google Sheets API
    """
    creds_json = os.getenv("GOOGLE_CREDENTIALS")

    if creds_json:
        # Production: load from environment variable
        creds_dict = json.loads(creds_json)
        return gspread.service_account_from_dict(creds_dict)
    else:
        # Local development: load from file
        return gspread.service_account(filename=str(CREDS_PATH))


def insert_member_record(member_data: dict[str, Any]):
    """
    Insert a member record into the Google Sheet.

    Args:
        member_data: Dictionary containing member information with keys:
            - fullname: Member's full name
            - email: Member's email address
            - location: City/locality
            - phone_number: Contact phone number
            - profession: Member's occupation
            - place_of_profession: Workplace or institution
            - department: List of departments joined (will be joined as string)
            - government_id_picture: URL to government ID image
            - member_picture: URL to member's photo
            - can_attend_events: Availability for events (bool)
            - member_id: AF member id

    Returns:
        bool: True if insertion successful, False otherwise
    """
    try:
        client = get_sheet_client()
        spreadsheet = client.open(SPREADSHEET_NAME)
        sheet = spreadsheet.sheet1  # Default first sheet

        department = member_data.get("department", [])
        if isinstance(department, list):
            department = ", ".join(department)

        row_data = [
            member_data.get("fullname", ""),
            member_data.get("email", ""),
            member_data.get("location", ""),
            member_data.get("phone_number", ""),
            member_data.get("profession", ""),
            member_data.get("place_of_profession", ""),
            department,
            member_data.get("government_id_picture", ""),
            member_data.get("member_picture", ""),
            str(member_data.get("can_attend_events", "")),
            member_data.get("member_id", ""),
        ]

        sheet.append_row(row_data)
        print("Record Inserted into sheet!")

    except Exception as e:
        print(f"Failed to insert member record: {e}")