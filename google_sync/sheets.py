import os
import gspread
from google.oauth2.service_account import Credentials


CREDENTIALS_FILE = "credentials.json"

SPREADSHEET_ID = "1TV7QDnldc1HYOy3NdEhyHmrrDPkarZsSh6JCQtdwna4"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


class SheetsError(Exception):
    """Base error for Google Sheets operations."""
    pass


class SheetConnectionError(SheetsError):
    """Error connecting to Google Sheets API or loading credentials."""
    pass


class SheetNotFoundError(SheetsError):
    """Target worksheet was not found."""
    pass


def get_client():
    if not os.path.exists(CREDENTIALS_FILE):
        raise SheetConnectionError(
            f"Credentials file '{CREDENTIALS_FILE}' not found."
        )

    try:
        credentials = Credentials.from_service_account_file(
            CREDENTIALS_FILE,
            scopes=SCOPES,
        )

        return gspread.authorize(credentials)
    except Exception as e:
        raise SheetConnectionError(
            f"Failed to authorize Google client: {e}"
        ) from e


def get_spreadsheet():
    client = get_client()

    try:
        return client.open_by_key(SPREADSHEET_ID)
    except Exception as e:
        raise SheetConnectionError(
            f"Failed to open spreadsheet '{SPREADSHEET_ID}': {e}"
        ) from e


def get_person_sheet(sheet_id):
    try:
        sheet_id_int = int(sheet_id)
    except (ValueError, TypeError) as e:
        raise SheetNotFoundError(f"Invalid sheet ID '{sheet_id}': {e}") from e

    spreadsheet = get_spreadsheet()

    try:
        worksheet = spreadsheet.get_worksheet_by_id(sheet_id_int)
        if worksheet is None:
            raise SheetNotFoundError(
                f"Worksheet with ID '{sheet_id}' was not found."
            )
        return worksheet
    except (gspread.exceptions.WorksheetNotFound, SheetNotFoundError) as e:
        raise SheetNotFoundError(
            f"Worksheet with ID '{sheet_id}' was not found: {e}"
        ) from e
    except SheetConnectionError:
        raise
    except Exception as e:
        raise SheetsError(
            f"Failed to access worksheet ID '{sheet_id}': {e}"
        ) from e


def add_attendance_entry(
    sheet_id,
    attendance_id,
    date,
    entry_time,
    exit_time=None,
    status="IN",
):
    try:
        worksheet = get_person_sheet(sheet_id)

        worksheet.append_row(
            [attendance_id, date, entry_time, exit_time or "", status]
        )
    except (SheetConnectionError, SheetNotFoundError):
        raise
    except Exception as e:
        raise SheetsError(
            f"Failed to add attendance entry to sheet '{sheet_id}': {e}"
        ) from e


def update_attendance_exit(
    sheet_id,
    attendance_id,
    exit_time,
    status="OUT",
):
    try:
        worksheet = get_person_sheet(sheet_id)

        records = worksheet.get_all_records()

        for row_number, record in enumerate(records, start=2):
            if str(record.get("Attendance ID")) == str(attendance_id):
                worksheet.update_cell(row_number, 4, exit_time)
                worksheet.update_cell(row_number, 5, status)
                return True

        return False
    except (SheetConnectionError, SheetNotFoundError):
        raise
    except Exception as e:
        raise SheetsError(
            f"Failed to update attendance exit in sheet '{sheet_id}': {e}"
        ) from e


def create_person_sheet(name, reuse_existing=True):
    name = str(name).strip()
    if not name:
        raise ValueError("Worksheet name cannot be empty.")

    spreadsheet = get_spreadsheet()

    # Check if a worksheet with this name already exists to prevent duplicate creation errors
    if reuse_existing:
        try:
            worksheet = spreadsheet.worksheet(name)
            print(f"-> Worksheet '{name}' already exists in Google Sheets. Reusing it.")
            return worksheet
        except gspread.exceptions.WorksheetNotFound:
            pass

    try:
        worksheet = spreadsheet.add_worksheet(
            title=name,
            rows=1000,
            cols=5,
        )

        worksheet.append_row(
            ["Attendance ID", "Date", "Entry Time", "Exit Time", "Status"]
        )

        return worksheet
    except gspread.exceptions.APIError as e:
        if "already exists" in str(e).lower() and reuse_existing:
            return spreadsheet.worksheet(name)
        raise SheetsError(
            f"API error creating worksheet '{name}': {e}"
        ) from e
    except Exception as e:
        raise SheetsError(
            f"Failed to create worksheet '{name}': {e}"
        ) from e
