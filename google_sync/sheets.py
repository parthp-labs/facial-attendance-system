import gspread
from google.oauth2.service_account import Credentials


CREDENTIALS_FILE = "credentials.json"

SPREADSHEET_ID = "1TV7QDnldc1HYOy3NdEhyHmrrDPkarZsSh6JCQtdwna4"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_client():
    credentials = Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
    )

    return gspread.authorize(credentials)


def get_spreadsheet():
    client = get_client()

    return client.open_by_key(SPREADSHEET_ID)


def get_person_sheet(sheet_id):
    spreadsheet = get_spreadsheet()

    return spreadsheet.get_worksheet_by_id(int(sheet_id))


def add_attendance_entry(sheet_id, attendance_id, date, entry_time, exit_time=None, status="IN",):
    worksheet = get_person_sheet(sheet_id)

    worksheet.append_row(
        [attendance_id, date, entry_time, exit_time or "", status,]
    )


def update_attendance_exit(sheet_id, attendance_id, exit_time, status="OUT"):
    worksheet = get_person_sheet(sheet_id)

    records = worksheet.get_all_records()

    for row_number, record in enumerate(records, start=2):
        if str(record["Attendance ID"]) == str(attendance_id):
            worksheet.update_cell(row_number, 4, exit_time,)

            worksheet.update_cell(row_number, 5, status)

            return True

    return False


def create_person_sheet(name):
    spreadsheet = get_spreadsheet()

    worksheet = spreadsheet.add_worksheet(
        title=name,
        rows=1000,
        cols=4,
    )

    worksheet.append_row(
        ["Attendance ID", "Date", "Entry Time", "Exit Time", "Status",]
    )

    return worksheet
