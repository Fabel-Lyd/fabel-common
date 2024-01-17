import pytest
import requests
from requests import HTTPError, Response
from rest_framework import status
from fabelcommon.utilities.response_extension import ResponseExtension


@pytest.mark.parametrize(
    'additional_info_mapping, expected_text',
    [
        (
            {},
            'Error 403 calling http://localhost/some-endpoint,'
            ' details: {"error":"exception","error_description":"Unable to add payment method"}'
        ),
        (
            {
                403: 'Forbidden',
                500: 'Internal server error'
            },
            ('Error 403 calling http://localhost/some-endpoint, details: '
             '{"error":"exception","error_description":"Unable to add payment method"}, '
             "additional info: Forbidden")

        )
    ]
)
def test_response_extension(requests_mock, additional_info_mapping, expected_text) -> None:
    requests_mock.get(
        url='http://localhost/some-endpoint',
        text='{"error":"exception","error_description":"Unable to add payment method"}',
        status_code=status.HTTP_403_FORBIDDEN
    )

    response = requests.get('http://localhost/some-endpoint')
    with pytest.raises(HTTPError) as http_error:
        ResponseExtension.raise_for_error(response=response, additional_info_mapping=additional_info_mapping)

    exception: HTTPError = http_error.value

    assert str(exception) == expected_text
    assert isinstance(exception.response, Response)
