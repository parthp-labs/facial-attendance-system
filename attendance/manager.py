from database.database import (
    get_today_attendance,
    create_entry,
    create_exit,
)


def process_attendance(
    person_id,
    date,
    current_time,
    database_path=None
):
    attendance = get_today_attendance(
        person_id,
        date,
        database_path
    )

    if attendance is None:
        attendance_id = create_entry(
            person_id,
            date,
            current_time,
            database_path
        )

        return "IN", attendance_id

    attendance_id = attendance[0]
    exit_time = attendance[4]

    if exit_time is None:
        create_exit(
            attendance_id,
            current_time,
            database_path
        )

        return "OUT", attendance_id

    return "IGNORE", attendance_id
