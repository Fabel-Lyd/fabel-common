import pytest
from datetime import datetime
from pytz import timezone, BaseTzInfo
from fabelcommon.datetime.time_formats import TimeFormats


@pytest.mark.parametrize(
    'time_zone, expected_timestamp',
    [
        (timezone('UTC'), '2024-01-12T20:30:15.000Z'),
        (timezone('EET'), '2024-01-12T18:30:15.000Z')
    ]
)
def test_get_date_time_string_utc_success(
        time_zone: BaseTzInfo,
        expected_timestamp: str
) -> None:

    assert TimeFormats.get_date_time_string_utc(datetime(year=2024, month=1, day=12, hour=20, minute=30, second=15, tzinfo=time_zone)) == expected_timestamp


def test_get_date_time_string_utc_failure() -> None:
    with pytest.raises(ValueError) as exception:
        TimeFormats.get_date_time_string_utc(datetime(year=2024, month=1, day=12, hour=20, minute=30, second=15))

    assert str(exception.value) == 'Provided datetime object contains no time zone info'
