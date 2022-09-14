import json
import pytest
from requests import HTTPError
from rest_framework import status
from fabelcommon.beat.beat_api_service import BeatApiService

from fabelcommon.http.verbs import HttpVerb


def test_get_token(requests_mock):

    requests_mock.post(
        'https://api.fabel.no/v2/oauth2/token',
        status_code=status.HTTP_200_OK,
        text=json.dumps({'access_token': 'token-generated'}))

    beat_service = BeatApiService('dummy_client_id', 'dummy_secret')
    access_token = beat_service.get_token()
    assert access_token == 'token-generated'


def test_create_headers():
    headers = BeatApiService.create_headers('dummy_token')
    expected_headers = {
        'Authorization': 'Bearer dummy_token',
        'Content-Type': 'application/json'}
    assert headers == expected_headers


def test_send_request_handle_error(mocker, requests_mock):

    mocker.patch.object(BeatApiService, attribute='get_token', return_value='test_token')
    requests_mock.get(
        'http://failing-endpoint',
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    beat_api_service = BeatApiService('test_client_id', 'test_client_secret')

    with pytest.raises(HTTPError):
        beat_api_service.send_request(
            verb=HttpVerb.GET,
            url='http://failing-endpoint',
            data={})

def test_send_request_success(mocker, requests_mock):

    mocker.patch.object(BeatApiService, attribute='get_token', return_value='test_token')
    requests_mock.get(
        'http://beat-endpoint',
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    beat_api_service = BeatApiService('test_client_id', 'test_client_secret')

    with pytest.raises(HTTPError):
        beat_api_service.send_request(
            verb=HttpVerb.GET,
            url='http://failing-endpoint',
            data={})