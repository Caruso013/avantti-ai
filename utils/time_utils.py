import os
from datetime import datetime, timedelta
from typing import Tuple
from zoneinfo import ZoneInfo

TZ_SP = ZoneInfo("America/Sao_Paulo")


def meeting_time_window(meeting_time: str) -> Tuple[datetime, datetime]:
    meeting_duration = int(os.getenv("MEETING_DURATION"))
    format = "%Y-%m-%dT%H:%M:%S" if "T" in meeting_time else "%Y-%m-%d %H:%M"
    start_time = datetime.strptime(meeting_time, format).astimezone(TZ_SP)
    end_time = start_time + timedelta(minutes=meeting_duration)

    return (start_time, end_time)
