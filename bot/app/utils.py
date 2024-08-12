from datetime import datetime, timedelta

def format_datetime(dt: datetime) -> str:
    dt_plus_3 = dt + timedelta(hours=3)

    formatted_dt = dt_plus_3.strftime('%H:%M %d-%m-%Y')

    return formatted_dt