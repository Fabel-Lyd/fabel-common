import json
from typing import List, Dict, Optional
from urllib.parse import parse_qs
import pytest
from requests import HTTPError, Response
from rest_framework import status
from fabelcommon.api_service import ApiService
from fabelcommon.http.verbs import HttpVerb


class ApiTestService(ApiService):
    def __init__(self) -> None:
        super().__init__('fake_client_id', 'fake_client_secret', 'http://localhost/', '/auth')

    def send_request(
            self,
            path: str,
            headers_to_add: Optional[Dict[str, str]] = None
    ) -> List[Dict]:
        response: Response = self._send_request(
            verb=HttpVerb.POST,
            path=path,
            headers_to_add=headers_to_add)
        return response.json()['content']


@pytest.mark.parametrize(
    'path, expected_path, headers_to_add',
    [
        ('http://localhost/post1', 'http://localhost/post1', {}),
        ('post2', 'http://localhost/post2', {}),
        ('/post3', 'http://localhost/post3', {}),
        ('/post4/', 'http://localhost/post4/', {}),
        ('/post5/', 'http://localhost/post5/', {'Content-Type': 'application/json'}),
        ('', 'http://localhost/', {}),
        ('/', 'http://localhost/', {}),
    ]
)
def test_send_request_successful(
        requests_mock,
        path,
        expected_path,
        headers_to_add

) -> None:
    test_data: List[Dict] = [
        {
            "one": 1,
            "two": 2
        }
    ]

    auth_request_mock = requests_mock.post(
        'http://localhost/auth',
        text=json.dumps({'access_token': 'fake_access_token'})
    )

    headers = {
        'Authorization': 'Bearer fake_access_token'
    }
    headers.update(headers_to_add)

    requests_mock.post(
        expected_path,
        request_headers=headers,
        text=json.dumps({'content': test_data}))

    feed_api_test: ApiTestService = ApiTestService()
    response_content: List[Dict] = feed_api_test.send_request(
        path=path,
        headers_to_add=headers_to_add
    )

    auth_request = auth_request_mock.request_history[0]
    auth_request_body: Dict = parse_qs(auth_request.text)

    assert auth_request_body['grant_type'][0] == 'client_credentials'
    assert 'Basic' in auth_request.headers.get("Authorization")
    assert response_content == test_data


def test_send_request_failed(requests_mock) -> None:
    requests_mock.post(
        'http://localhost/auth',
        text=json.dumps({'access_token': 'fake_access_token'})
    )
    requests_mock.post('http://localhost/post', status_code=status.HTTP_400_BAD_REQUEST)

    feed_api_test: ApiTestService = ApiTestService()

    with pytest.raises(HTTPError):
        feed_api_test.send_request(path='http://localhost/post')
