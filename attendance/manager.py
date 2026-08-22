from database.database import (
    get_today_attendance,
    create_entry,
    create_exit,
)


def process_attendance(person_id, date, current_time):
    attendance = get_today_attendance(person_id, date)

    # No attendance record today
    if attendance is None:
        attendance_id = create_entry(
            person_id,
            date,
            current_time
        )

        return "IN", attendance_id

    attendance_id = attendance[0]
    exit_time = attendance[4]

    # Entry exists, but person has not exited
    if exit_time is None:
        create_exit(
            attendance_id,
            current_time
        )

        return "OUT", attendance_id

    # Both IN and OUT already exist
    return "IGNORE", attendance_id
