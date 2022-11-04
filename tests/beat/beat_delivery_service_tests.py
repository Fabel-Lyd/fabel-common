import json
from rest_framework import status
from fabelcommon.beat.beat_delivery_service import BeatDeliveryService


def test_get_access_token(requests_mock):
    requests_mock.post(
        url='https://ds.test.beat.delivery/v1/auth',
        status_code=status.HTTP_200_OK,
        text=json.dumps({'access_token': 'fake_access_token'}))

    beat_delivery_service = BeatDeliveryService('fabel_test_username', 'fabel_test_password')
    user_token = beat_delivery_service.get_beat_access_token()

    assert user_token == 'fake_access_token'


def test_beat_create_header():

    headers = BeatDeliveryService(
        'fabel_test_username',
        'fabel_test_password'
    ).create_header('fake_access_token')

    assert headers == {'Authorization': f'Bearer fake_access_token'}
