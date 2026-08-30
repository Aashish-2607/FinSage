from datetime import datetime
from zoneinfo import ZoneInfo


IST = ZoneInfo("Asia/Kolkata")


def format_timestamp(timestamp: str | None) -> str:
    """
    Convert a database UTC timestamp into
    a user-friendly Indian Standard Time string.
    """

    if not timestamp:
        return ""

    utc_time = datetime.fromisoformat(
        timestamp
    ).replace(tzinfo=ZoneInfo("UTC"))

    local_time = utc_time.astimezone(IST)

    return local_time.strftime(
        "%d %b %Y, %I:%M %p"
    )