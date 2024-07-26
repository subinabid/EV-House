"""Get the family members from the Google Sheet.

Google sheet has the following columns:
    0. Sl
    1. Name
    2. Gender
    3. aka
    4. VitalStatus
    5. DoB
    6. Age2015 - Ignore this column
    7. Age2024 - Use this column till DoB is available
    8. Phone
    9. EmailId
    10. BloodGroup
    11. Parent
    12. Spouse

Functions:
    get_family_members: Get the family members from the Google Sheet.
    dump_family_members_json: Get the family members from the Google Sheet and create JSON file.
"""

import os.path
import json

from google.auth.transport import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv(".env")  # Load environment variables from .env file
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SPREADSHEET_ID = os.getenv("ENV_SPREADSHEET_ID")
RANGE_NAME = os.getenv("ENV_RANGE_NAME")


def get_family_members():
    """Get the family members from the Google Sheet."""

    creds = None

    # The file token.json stores the user's access and refresh tokens, and
    # is created automatically when the authorization flow completes
    # for the first time
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
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
        family_members = result.get("values", [])
        return family_members

    except HttpError as err:
        print(err)


def dump_family_members_json():
    """Get the family members from the Google Sheet and create JSON file."""
    family_members = get_family_members()
    json.dump(family_members, open("family_members.json", "w"), indent=4)


def main():
    """Get the family members from the Google Sheet."""
    family_members = get_family_members()
    for member in family_members:
        print(member)


if __name__ == "__main__":
    main()
