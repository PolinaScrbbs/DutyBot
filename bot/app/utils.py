from datetime import datetime, timedelta
from typing import List

from database.models import Duty


def format_datetime(dt: datetime) -> str:
    dt_plus_3 = dt + timedelta(hours=3)

    formatted_dt = dt_plus_3.strftime("%H:%M %d-%m-%Y")

    return formatted_dt


async def create_duties_msg(initial_line: str, duties: List[Duty]) -> str:
    msg = initial_line

    for duty in duties:
        attendant_full_name = await duty.attendant.full_name
        duty_date = await duty.formatted_date
        msg += (
            f"👨‍🎓 *@{duty.attendant.username}* ({attendant_full_name})\n"
            f"Дежурил(а) ⏰*{duty_date}*\n\n"
        )

    return msg
