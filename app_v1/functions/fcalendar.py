import calendar
from datetime import time
from ..db.appointments_crud import get_appointments_by_date


def add_appointments(client, date, hour):
    pass


def check_schedules(db, date):
    appointments = get_appointments_by_date(db, date)

    available_times = [{"8:00": 1}, {"9:00": 1}, {"10:00": 1}, {"11:00": 1}, {"13:00": 1}, {"14:00": 1}, {"15:00": 1},
                       {"16:00": 1}, {"17:00": 1}, {"18:00": 1}]

    for appointment in appointments:

        match appointment.time:
            case time(8):
                available_time = available_times[0]
                available_time["8:00"] = 0
            case time(9):
                available_time = available_times[1]
                available_time["9:00"] = 0
            case time(10):
                available_time = available_times[2]
                available_time["10:00"] = 0
            case time(11):
                available_time = available_times[3]
                available_time["11:00"] = 0
            case time(13):
                available_time = available_times[4]
                available_time["13:00"] = 0
            case time(14):
                available_time = available_times[5]
                available_time["14:00"] = 0
            case time(15):
                available_time = available_times[6]
                available_time["15:00"] = 0
            case time(16):
                available_time = available_times[7]
                available_time["16:00"] = 0
            case time(17):
                available_time = available_times[8]
                available_time["17:00"] = 0
            case time(18):
                available_time = available_times[9]
                available_time["18:00"] = 0
            case other:
                pass

    marked_times = [time_h for time_dict in available_times for time_h, value in time_dict.items() if value == 1]

    return marked_times
