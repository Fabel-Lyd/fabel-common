import json
from urllib.parse import urlparse
import pytest
from requests import HTTPError
from rest_framework import status
from fabelcommon.feed.api_service import FeedApiService
from fabelcommon.http.verbs import HttpVerb


def test_send_request_successful(requests_mock):
    auth_request_mock = requests_mock.post(
        'https://lydbokforlaget-feed.isysnet.no/token-server/oauth/token',
        text=json.dumps({'access_token': 'fake_access_token'})
    )
    requests_mock.post(
        'https://example.com/index.html',
        request_headers={
            'Authorization': 'Bearer fake_access_token',
            'Content-Type': 'application/json'
        },
        text=json.dumps({'content': [1, 2, 3]}))

    feed_api_service = FeedApiService('fake_client_id', 'fake_client_secret')
    response = feed_api_service.send_request(HttpVerb.POST, 'https://example.com/index.html')

    auth_request = auth_request_mock.request_history[0]
    auth_request_body = urlparse.parse_qs(auth_request.text)

    assert auth_request_body['grant_type'] == 'client_credentials'
    assert 'Basic' in auth_request.headers.get("Authorization")
    assert response == [1, 2, 3]


def test_send_request_failed(requests_mock):
    requests_mock.post(
        'https://lydbokforlaget-feed.isysnet.no/token-server/oauth/token',
        text=json.dumps({'access_token': 'fake_access_token'})
    )
    requests_mock.post('https://example.com/index.html', status_code=status.HTTP_400_BAD_REQUEST)

    feed_api_service = FeedApiService('fake_client_id', 'fake_client_secret')

    with pytest.raises(HTTPError):
        feed_api_service.send_request(HttpVerb.POST, 'https://example.com/index.html')
