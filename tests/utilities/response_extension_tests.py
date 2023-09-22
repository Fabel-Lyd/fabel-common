import pytest
import requests
from requests import HTTPError, Response
from rest_framework import status
from fabelcommon.utilities.response_extension import ResponseExtension


def test_response_extension(requests_mock):

    requests_mock.get(
        'http://localhost/some-endpoint',
        text='{"error":"exception","error_description":"Unable to add payment method"}',
        status_code=status.HTTP_403_FORBIDDEN
    )

    response = requests.get('http://localhost/some-endpoint')
    with pytest.raises(HTTPError) as exception_info:
        ResponseExtension.raise_for_error(response)

    exception: HTTPError = exception_info.value

    expected_text = \
        'Error 403 calling http://localhost/some-endpoint, ' \
        'details: {"error":"exception","error_description":"Unable to add payment method"}'
    assert str(exception) == expected_text
    assert isinstance(exception.response, Response)
