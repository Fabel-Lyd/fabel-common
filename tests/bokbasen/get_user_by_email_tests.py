import json
from typing import Optional
import pytest
from fabelcommon.bokbasen import API_BOKBASEN
from rest_framework import status


BOKBASEN_RESPONSE = {'id': '2445a484-2cd5-444a-b121-9fa98235af6d', 'active': True}
EMAIL: str = 'name@server.domain'
TICKET: dict = {'boknett-TGT': 'fake-token'}


@pytest.mark.parametrize(
    'response_text, expected_result',
    [
        (json.dumps(BOKBASEN_RESPONSE), BOKBASEN_RESPONSE),
        ('{"data": "USER_NOT_FOUND"}', None)
    ]
)
def test_get_user_by_email(
        requests_mock,
        response_text,
        expected_result
) -> None:
    requests_mock.get(
        url='https://idp.dds.boknett.no/validate/name@server.domain',
        status_code=status.HTTP_200_OK,
        text=response_text
    )

    result: Optional[dict] = API_BOKBASEN.Bokskya().get_user_by_email(EMAIL, TICKET)
    assert result == expected_result


def test_get_user_by_email_exception(requests_mock) -> None:
    requests_mock.get(
        url='https://idp.dds.boknett.no/validate/name@server.domain',
        status_code=status.HTTP_400_BAD_REQUEST,
        text='{"data":"PARAMETER_ERROR"}'
    )
    with pytest.raises(Exception) as exception:
        API_BOKBASEN.Bokskya().get_user_by_email(EMAIL, TICKET)
    assert exception.value.args[0] == 'Error validating user'
    assert exception.value.args[1] == 'PARAMETER_ERROR'
