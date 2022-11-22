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
        request_headers={
            'range': 'releases=0-6',
            'Authorization': 'Bearer test_token',
            'Content-Type': 'application/json'
        }
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
