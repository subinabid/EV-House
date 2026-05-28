"""Get the family members from the Google Sheet.

Google sheet has the following columns:
    A(1). Sl
    B(2). Name
    C(3). Gender
    D(4). aka
    E(5). VitalStatus
    F(6). DoB
    G(7). Age2015 - Ignore this column
    H(8). Age2024 - Use this column till DoB is available
    I(9). Phone
    J(10). EmailId
    K(11). BloodGroup
    L(12). Parent
    M(13). Spouse
    Ignore other columns if any

Functions:
    get_family_members: Get the family members from the Google Sheet.
"""

from __future__ import annotations

import os
import json
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv(".env")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SPREADSHEET_ID = os.getenv("ENV_SPREADSHEET_ID", "")
RANGE_NAME = os.getenv("ENV_RANGE_NAME", "")

# Column schema matching the Google Sheet
# Indices are 0-based matching the sheet columns A, B, C, ...
COLUMNS: list[dict[str, str | int]] = [
    {"index": 0, "letter": "A", "name": "Sl", "description": "Serial number"},
    {"index": 1, "letter": "B", "name": "Name", "description": "Full name"},
    {"index": 2, "letter": "C", "name": "Gender", "description": "Male / Female"},
    {"index": 3, "letter": "D", "name": "aka", "description": "Also known as / nickname"},
    {"index": 4, "letter": "E", "name": "VitalStatus", "description": "Blank or 'Late' if deceased"},
    {"index": 5, "letter": "F", "name": "DoB", "description": "Date of birth"},
    {"index": 6, "letter": "G", "name": "Age2015", "description": "Age in 2015 (ignored)"},
    {"index": 7, "letter": "H", "name": "Age2024", "description": "Age in 2024 (used when DoB missing)"},
    {"index": 8, "letter": "I", "name": "Phone", "description": "Phone number"},
    {"index": 9, "letter": "J", "name": "EmailId", "description": "Email address"},
    {"index": 10, "letter": "K", "name": "BloodGroup", "description": "Blood group"},
    {"index": 11, "letter": "L", "name": "Parent", "description": "Sl number of parent"},
    {"index": 12, "letter": "M", "name": "Spouse", "description": "Sl number of spouse (married into family)"},
]


def get_family_members() -> list[list[str]]:
    """Get the family members from the Google Sheet."""

    creds: Credentials | None = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)  # type: ignore[no-untyped-call]

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())  # type: ignore[no-untyped-call]
            except Exception:
                creds = None
        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()
        result = (
            sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
        )
        family_members: list[list[str]] = result.get("values", [])
        return family_members

    except HttpError as err:
        print(err)
        return []


def main() -> None:
    """Get the family members from the Google Sheet and create JSON file."""
    rows = get_family_members()

    # Convert each row from a positional list to a named dict
    members: list[dict[str, str]] = []
    for row in rows:
        member: dict[str, str] = {}
        for col in COLUMNS:
            idx = col["index"] if isinstance(col["index"], int) else int(col["index"])
            member[str(col["name"])] = row[idx] if idx < len(row) else ""
        members.append(member)

    data: dict[str, Any] = {
        "columns": COLUMNS,
        "row_count": len(members),
        "rows": members,
    }
    with open("family_members.json", "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Family members dumped to family_members.json ({len(members)} rows)")


if __name__ == "__main__":
    main()
