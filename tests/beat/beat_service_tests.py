import json
import pytest
from requests import HTTPError
from rest_framework import status
from fabelcommon.beat.beat_service import BeatService
import requests


def test_get_token(requests_mock):

    requests_mock.post(
        'https://api.fabel.no/v2/oauth2/token',
        status_code=status.HTTP_200_OK,
        text=json.dumps({'access_token': 'token-generated'}))

    beat_service = BeatService('dummy_client_id', 'dummy_secret')
    access_token = beat_service.get_token()
    assert access_token == 'token-generated'


def test_create_headers():
    headers = BeatService.create_headers('dummy_token')
    expected_headers = {
        'Authorization': 'Bearer dummy_token',
        'Content-Type': 'application/json'}
    assert headers == expected_headers


def test_failure_is_handled(requests_mock):

    class Sample(BeatService):
        def failing_call(self):
            response = requests.get('http://failing-endpoint')
            response.raise_for_status()

    requests_mock.get(
        'http://failing-endpoint',
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    sample = Sample('dummy_client_id', 'dummy_secretet')
    with pytest.raises(HTTPError):
        sample.failing_call()
