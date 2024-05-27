import pytest
from freezegun import freeze_time
from fabelcommon.access_token import AccessToken

freeze_time("2012-01-14 12:00:00").start()
access_token = AccessToken(
    access_token_value='fake-token',
    expires_in=300,
    user_id=None,
    refresh_token_value='fake-refresh-token'
)


@pytest.mark.parametrize(
    'current_time, is_valid',
    [
        ("2012-01-14 12:00:01", True),
        ("2012-01-14 12:04:59", True),
        ("2012-01-14 12:05:00", False)
    ])
def test_expired_access_token(current_time: str, is_valid: bool):
    freeze_time(current_time).start()
    assert access_token.is_valid is is_valid
