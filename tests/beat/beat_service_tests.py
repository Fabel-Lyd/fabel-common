import json
from urllib.parse import parse_qs

from fabelcommon.beat.beat_api_service import BeatApiService
from fabelcommon.http.verbs import HttpVerb


def test_send_request_success(requests_mock):
    requests_mock.post(
        'https://api.fabel.no/v2/oauth2/token',
        text=json.dumps({'access_token': 'test_token'})
    )

    mocked_beat_request = requests_mock.post(
        'http://beat-endpoint',
        text='{"releases":[]}',
    )

    beat_api_service = BeatApiService(
        'test_client_id',
        'test_client_secret',
        'https://api.fabel.no'
    )

    response_data = beat_api_service.send_request(
        verb=HttpVerb.POST,
        url='http://beat-endpoint',
        data={'test_data': 'test_value'},
        headers_to_add={'range': 'releases=0-6'}
    )

    assert json.loads(response_data) == {'releases': []}
    assert mocked_beat_request.last_request.text == '{"test_data": "test_value"}'


def test_beat_service_headers():
    headers = BeatApiService(
        'test_client_id',
        'test_client_secret',
        'https://api.fabel.no'
    )._create_authorization_header('test_token')

    assert headers == {'Authorization': 'Bearer test_token'}


def test_beat_service_token_request_data():
    token_request_data = BeatApiService(
        'test_client_id',
        'test_client_secret',
        'https://api.fabel.no'
    )._token_request_data

    assert token_request_data == {
        'grant_type': 'client_credentials',
        'client_id': 'test_client_id',
        'client_secret': 'test_client_secret'
    }


def test_beat_service_token_request_auth():
    token_request_auth = BeatApiService(
        'test_client_id',
        'test_client_secret',
        'https://api.fabel.no'
    )._token_request_auth

    assert token_request_auth is None


def test_beat_service_token_access_token_key():
    access_token_key = BeatApiService(
        'test_client_id',
        'test_client_secret',
        'https://api.fabel.no'
    )._access_token_key

    assert access_token_key.value == 'access_token'


def mock_response(request_object, b):
    data = {
        'client_credentials': {
            'access_token': 'client_secret_token',
            'expires_in': 300
        },
        'password': {
            'access_token': 'password_token',
            'expires_in': 300,
            'user_id': '117'
        }
    }
    grant_type = parse_qs(request_object.text)['grant_type'][0]
    xxx = data[grant_type]
    result = json.dumps(xxx)
    return result


def test_get_password_flow_token(requests_mock):

    requests_mock.post(
        'https://api.fabel.no/v2/oauth2/token',
        text=mock_response
    )

    requests_mock.get(
        'https://api.fabel.no/v2/client-credential-end-point',
        text=json.dumps(
            {}
        )
    )

    beat_api_service = BeatApiService(
        'test_client_id',
        'test_client_secret',
        'https://api.fabel.no'
    )

    # make request to cache token
    beat_api_service.send_request(HttpVerb.GET, '/v2/client-credential-end-point')

    access_token = beat_api_service.get_password_flow_token('user', 'password')

    assert access_token.is_valid is True
    assert access_token.access_token_value == 'password_token'
    assert access_token.user_id == '117'


def test_send_request_with_token(requests_mock):
    data = '{"releases":[]}'

    requests_mock.get(
        'http://beat-endpoint/data',
        text='{"releases":[]}',
    )

    beat_api_service = BeatApiService(
        'test_client_id',
        'test_client_secret',
        'https://api.fabel.no'
    )
    response_data = beat_api_service.send_request_with_token(
        verb=HttpVerb.GET,
        url='http://beat-endpoint/data',
        token_value='test_token')

    assert response_data == data
