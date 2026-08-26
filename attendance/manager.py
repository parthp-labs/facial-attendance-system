from database.database import (
    get_today_attendance,
    create_entry,
    create_exit,
    AttendanceAlreadyExistsError,
    DatabaseError,
    DATABASE_PATH,
)
from datetime import datetime, timedelta
COOLDOWN_SECONDS = 30


def process_attendance(
    person_id,
    date,
    current_time,
):
    try:
        """Get Today's Attendance"""
        attendance = get_today_attendance(person_id, date, DATABASE_PATH)

        """No Attendance Today -> New Entry"""
        if attendance is None:
            try:
                attendance_id = create_entry(
                    person_id,
                    date,
                    current_time,
                    DATABASE_PATH
                )

                return (
                    "IN",
                    attendance_id,
                    "INSIDE"
                )
            # Entry already exists
            except AttendanceAlreadyExistsError:
                print("Attendance already exists for", attendance[1])
                attendance = get_today_attendance(
                    person_id, date, DATABASE_PATH)

                if attendance is not None:
                    return ("IGNORE", attendance[0], "INSIDE")

                return ("ERROR", None, "ERROR")
            # Other database error
            except DatabaseError as e:
                print(f"Database error: {e}")

                return ("ERROR", None, "ERROR")

        """Attendance Already Exists"""
        attendance_id = attendance[0]
        entry_time = attendance[3]
        exit_time = attendance[4]

        # Exit entry already exists
        if exit_time is not None:
            return ("IGNORE", attendance_id, "EXITED")

        # Invalid attendance record
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

        # Current time cannot be before entry
        if current_datetime < entry_datetime:
            print("Current time is earlier than entry time.")

            return ("ERROR", attendance_id)

        # Calculating time since entry to compare with cooldown
        elapsed = current_datetime - entry_datetime
        if elapsed < timedelta(seconds=COOLDOWN_SECONDS):
            return ("IGNORE", attendance_id, "INSIDE")

        try:
            create_exit(attendance_id, current_time, DATABASE_PATH)

            return ("OUT", attendance_id, "EXITED")
        except Exception as e:
            print(f"Error creating exit: {e}")

            return ("ERROR", attendance_id, "ERROR")
    except Exception as e:
        print(f"Attendance processing error: {e}")

        return ("ERROR", None, "ERROR")
