from datetime import datetime


def get_current_datetime():
    return datetime.now()


def get_current_date():
    return get_current_datetime().strftime("%Y-%m-%d")


def get_current_time():
    return get_current_datetime().strftime("%H:%M:%S")
