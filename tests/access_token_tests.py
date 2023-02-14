import pytest
from fabelcommon.access_token import AccessToken


@pytest.mark.parametrize(
    'expires_in, is_valid',
    [
        (600, True),
        (0, False),
        (-600, False)
    ])
def test_expired_access_token(expires_in: int, is_valid: bool):
    access_token = AccessToken(
        access_token_value='fake-token',
        expires_in=expires_in,
        user_id=None
    )

    assert access_token.is_valid is is_valid
