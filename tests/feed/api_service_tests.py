import json
from typing import List, Dict
from urllib.parse import parse_qs
import pytest
from requests import HTTPError, Response
from rest_framework import status
from fabelcommon.feed.api_service import FeedApiService
from fabelcommon.http.verbs import HttpVerb


class FeedApiTest(FeedApiService):
    def __init__(self) -> None:
        super().__init__('fake_client_id', 'fake_client_secret')

    def send_request(self) -> List[Dict]:
        response: Response = self._send_request(HttpVerb.POST, 'https://example.com/index.html')
        return response.json()['content']


def test_send_request_successful(requests_mock) -> None:
    test_data: List[Dict] = [
        {
            "one": 1,
            "two": 2
        }
    ]

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
        text=json.dumps({'content': test_data}))

    feed_api_test: FeedApiTest = FeedApiTest()
    response_content: List[Dict] = feed_api_test.send_request()

    auth_request = auth_request_mock.request_history[0]
    auth_request_body: Dict = parse_qs(auth_request.text)

    assert auth_request_body['grant_type'][0] == 'client_credentials'
    assert 'Basic' in auth_request.headers.get("Authorization")
    assert response_content == test_data


def test_send_request_failed(requests_mock) -> None:
    requests_mock.post(
        'https://lydbokforlaget-feed.isysnet.no/token-server/oauth/token',
        text=json.dumps({'access_token': 'fake_access_token'})
    )
    requests_mock.post('https://example.com/index.html', status_code=status.HTTP_400_BAD_REQUEST)

    feed_api_test: FeedApiTest = FeedApiTest()

    with pytest.raises(HTTPError):
        feed_api_test.send_request()
