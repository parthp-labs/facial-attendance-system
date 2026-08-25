from database.database import (
    get_today_attendance,
    create_entry,
    create_exit,
    AttendanceAlreadyExistsError,
    DatabaseError
)
from datetime import datetime, timedelta
COOLDOWN_SECONDS = 3600


def process_attendance(
    person_id,
    date,
    current_time,
    database_path=None
):
    try:
        attendance = get_today_attendance(person_id, date, database_path)

        try:
            if attendance is None:
                attendance_id = create_entry(
                    person_id,
                    date,
                    current_time,
                    database_path
                )

                return "IN", attendance_id, "INSIDE"
        except AttendanceAlreadyExistsError:
            attendance = get_today_attendance(person_id, date, database_path)

            if attendance is not None:
                return "IGNORE", attendance[0], "INSIDE"

            return "ERROR", None, "ERROR"
        except DatabaseError as e:
            print(f"Database error: {e}")

            return "ERROR", None, "ERROR"
        except Exception as e:
            print(f"Error creating entry: {e}")

            # Another process/frame may have created the entry simultaneously.
            attendance = get_today_attendance(person_id, date, database_path)

            if attendance is not None:
                attendance_id = attendance[0]
                return "IGNORE", attendance_id, "INSIDE"

            return "ERROR", None, "ERROR"

        attendance_id = attendance[0]
        entry_time = attendance[3]
        exit_time = attendance[4]

        elapsed = current_datetime - entry_datetime

        if exit_time is not None:
            return "IGNORE", attendance_id, "EXITED"

        if entry_time is None:
            print(f"Invalid attendance record "f"for person {person_id}")

            return ("ERROR", attendance_id, "ERROR")

        try:
            # Calculate time since entry
            entry_datetime = datetime.strptime(
                entry_time,
                "%H:%M:%S"
            )

            current_datetime = datetime.strptime(
                current_time,
                "%H:%M:%S"
            )
        except ValueError as e:
            print(f"Invalid time format: {e}")

            return ("ERROR", attendance_id, "ERROR")

        if current_datetime < entry_datetime:
            print("Current time is earlier than entry time.")

            return ("ERROR", attendance_id)

        elapsed = current_datetime - entry_datetime

        if elapsed < timedelta(seconds=COOLDOWN_SECONDS):
            return "IGNORE", attendance_id, "INSIDE"

        try:
            create_exit(attendance_id, current_time, database_path)

            return "OUT", attendance_id, "EXITED"
        except Exception as e:
            print(f"Error creating exit: {e}")

            return ("ERROR", attendance_id, "ERROR")
    except Exception as e:
        print(f"Attendance processing error: {e}")

        return "ERROR", None
