import json
import io
from typing import Dict, Tuple
from fabelcommon.beat.beat_delivery_api_service import BeatDeliveryApiService
from fabelcommon.http.verbs import HttpVerb


def test_send_request_success(requests_mock):

    requests_mock.post(
        'https://ds.test.beat.delivery/v1/auth',
        text=json.dumps({'access_token': 'test_token'})
    )

    expected_delivery_data = {"delivery_id": 12345}

    mocked_beat_request = requests_mock.post(
        'https://ds.test.beat.delivery',
        text=json.dumps(expected_delivery_data)
    )

    beat_delivery_api_service = BeatDeliveryApiService(
        'test_client_id',
        'test_client_secret',
        'https://ds.test.beat.delivery',
        '/v1/auth'
    )

    buffer = io.BytesIO(b'<root/>')
    files: Dict[str, Tuple[str, io.BytesIO, str]] = {'onixProducts': ('isbn.xml', buffer, 'text/xml')}

    response_data = beat_delivery_api_service.send_request(
        verb=HttpVerb.POST,
        path='/',
        data={'test_data': 'test_value'},
        files=files
    )

    assert 'multipart/form-data' in mocked_beat_request.last_request.headers['Content-Type']
    assert json.loads(response_data) == expected_delivery_data


def test_beat_delivery_token_request_data():
    token_request_data = BeatDeliveryApiService(
        'test_client_id',
        'test_client_secret'
    )._token_request_data
    assert token_request_data == {
        'username': 'test_client_id',
        'password': 'test_client_secret'
    }


def test_beat_delivery_create_header():

    header = BeatDeliveryApiService(
        'test_client_id',
        'test_client_secret'
    ).create_header('test_token')

    assert header == {'Authorization': 'Bearer test_token'}


def test_beat_delivery_access_token_key():
    access_token_key = BeatDeliveryApiService(
        'test_client_id',
        'test_client_secret'
    )._access_token_key

    assert access_token_key.value == 'access_token'
