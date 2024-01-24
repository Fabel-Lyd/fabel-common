import freezegun
from datetime import datetime
import pytz
from fabelcommon.datetime.datetime_now_utc import datetime_now_utc


@freezegun.freeze_time('2023-11-24 16:36:29')
def test_datetime_now_utc() -> None:
    test_datetime: datetime = datetime_now_utc()

    assert test_datetime.year == 2023
    assert test_datetime.month == 11
    assert test_datetime.day == 24

    assert test_datetime.hour == 16
    assert test_datetime.minute == 36
    assert test_datetime.second == 29

    assert test_datetime.tzinfo == pytz.timezone('UTC')
