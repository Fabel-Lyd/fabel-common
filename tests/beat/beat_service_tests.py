import json
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

    beat_api_service = BeatApiService('test_client_id', 'test_client_secret')

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
        'test_client_secret'
    ).create_header('test_token')

    assert headers == {'Authorization': 'Bearer test_token'}


def test_beat_service_token_request_data():

    token_request_data = BeatApiService(
        'test_client_id',
        'test_client_secret'
    )._token_request_data

    assert token_request_data == {
        'grant_type': 'client_credentials',
        'client_id': 'test_client_id',
        'client_secret': 'test_client_secret'
    }


def test_beat_service_token_request_auth():
    token_request_auth = BeatApiService(
        'test_client_id',
        'test_client_secret'
    )._token_request_auth

    assert token_request_auth is None


def test_beat_service_token_access_token_key():
    access_token_key = BeatApiService(
        'test_client_id',
        'test_client_secret'
    )._access_token_key

    assert access_token_key.value == 'access_token'
