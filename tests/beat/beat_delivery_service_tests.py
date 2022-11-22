import json
import io
from typing import Dict, Tuple
from fabelcommon.beat.beat_delivery_api_service import BeatDeliveryApiService
from fabelcommon.http.verbs import HttpVerb


def test_send_request_success(requests_mock):

    requests_mock.post(
        'https://beat-delivery/oauth',
        text=json.dumps({'access_token': 'test_token'})
    )

    expected_delivery_data = {"delivery_id": 12345}

    mocked_beat_request = requests_mock.post(
        'https://beat-delivery',
        text=json.dumps(expected_delivery_data)
    )

    beat_delivery_api_service = BeatDeliveryApiService(
        'test_client_id',
        'test_client_secret',
        'https://beat-delivery',
        '/oauth'
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
