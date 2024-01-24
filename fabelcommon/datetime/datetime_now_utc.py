from datetime import datetime
import pytz


def datetime_now_utc() -> datetime:
    return datetime.now(pytz.timezone('UTC'))
