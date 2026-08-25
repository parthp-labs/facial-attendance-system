from database.database import (
    get_today_attendance,
    create_entry,
    create_exit,
)
from datetime import datetime, timedelta
COOLDOWN_SECONDS = 3600


def process_attendance(
    person_id,
    date,
    current_time,
    database_path=None
):
    attendance = get_today_attendance(person_id, date, database_path)

    print(attendance)
    if attendance is None:
        attendance_id = create_entry(
            person_id,
            date,
            current_time,
            database_path
        )

        return "IN", attendance_id

    attendance_id = attendance[0]
    entry_time = attendance[3]
    exit_time = attendance[4]

    elapsed = current_datetime - entry_datetime

    if exit_time is not None:
        return "IGNORE", attendance_id

    # Calculate time since entry
    entry_datetime = datetime.strptime(
        entry_time,
        "%H:%M:%S"
    )

    current_datetime = datetime.strptime(
        current_time,
        "%H:%M:%S"
    )

    # Still inside cooldown period
    if elapsed < timedelta(seconds=COOLDOWN_SECONDS):
        return "IGNORE", attendance_id

    # Cooldown has expired → record exit
    create_exit(
        attendance_id,
        current_time,
        database_path
    )

    return "OUT", attendance_id
