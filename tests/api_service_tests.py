import json
from typing import List, Dict, Optional, Any
from urllib.parse import parse_qs
import pytest
from freezegun import freeze_time
from requests import HTTPError, Response
from rest_framework import status
from fabelcommon.access_token_key import AccessTokenKey
from fabelcommon.api_service import ApiService
from fabelcommon.http.verbs import HttpVerb


class ApiTestService(ApiService):

    @property
    def _access_token_key(self) -> AccessTokenKey:
        return AccessTokenKey.ACCESS_TOKEN

    @property
    def _token_request_data(self) -> Dict:
        return {
            'grant_type': 'client_credentials',
            'client_id': self._client_id,
            'client_secret': self._client_secret,
        }

    @property
    def _token_request_auth(self) -> Optional[Any]:
        return None

    def _create_authorization_header(self, access_token: str) -> Dict[str, str]:
        return {
            'Authorization': f'Bearer {access_token}'
        }

    def __init__(self) -> None:
        super().__init__(
            client_id='fake_client_id',
            client_secret='fake_client_secret',
            base_url='http://localhost/',
            auth_path='/auth')

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
    assert response_content == test_data


def test_send_multiple_requests_using_cached_token(requests_mock):

    auth_request_mock = requests_mock.post(
        'http://localhost/auth',
        text=json.dumps({'access_token': 'fake_access_token'})
    )

    requests_mock.post(
        'http://localhost/post1',
        text=json.dumps({'content': None}))

    feed_api_test: ApiTestService = ApiTestService()

    feed_api_test.send_request(
        path='http://localhost/post1',
        headers_to_add=None
    )
    feed_api_test.send_request(
        path='http://localhost/post1',
        headers_to_add=None
    )
    assert auth_request_mock.call_count == 1, 'Token should be cached and there should be only one call to fetch access token'


def test_send_multiple_requests_refreshing_token(
        requests_mock,
        mocker
):
    auth_request_mock = requests_mock.post(
        'http://localhost/auth',
        text=json.dumps({'access_token': 'fake_access_token'})
    )

    requests_mock.post(
        'http://localhost/post1',
        text=json.dumps({'content': None}))

    feed_api_test: ApiTestService = ApiTestService()

    with freeze_time("2012-01-14 12:00:00"):
        feed_api_test.send_request(
            path='http://localhost/post1',
            headers_to_add=None
        )

    with freeze_time("2012-01-14 13:00:00"):
        feed_api_test.send_request(
            path='http://localhost/post1',
            headers_to_add=None
        )

    assert auth_request_mock.call_count == 2, 'There should be two call to fetch token because token should be refreshed'


def test_raise_for_error_create_token(requests_mock):
    requests_mock.post(
        'http://localhost/auth',
        text='{"error":"invalid_grant","error_description":"Invalid username and password combination"}',
        status_code=status.HTTP_401_UNAUTHORIZED
    )

    api_test_service: ApiTestService = ApiTestService()

    with pytest.raises(HTTPError) as exception_info:
        api_test_service.send_request('/some-endpoint')

    exception_text: str = str(exception_info.value)
    assert 'details:' in exception_text


def test_raise_for_error_send_request(requests_mock):

    requests_mock.post(
        'http://localhost/auth',
        text=json.dumps({'access_token': 'fake_access_token'})
    )

    requests_mock.post(
        'http://localhost/some-endpoint',
        text='{"error":"exception","error_description":"Unable to add payment method"}',
        status_code=status.HTTP_403_FORBIDDEN
    )

    api_test_service: ApiTestService = ApiTestService()

    with pytest.raises(HTTPError) as exception_info:
        api_test_service.send_request('/some-endpoint')

    exception_text: str = str(exception_info.value)
    assert 'details:' in exception_text
