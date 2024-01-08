import json
from typing import Dict
import pytest
from requests import HTTPError
from rest_framework import status
from fabelcommon.feed.import_service import FeedImport

FEED_BASE_URL: str = 'https://lydbokforlaget-feed.isysnet.no'
TEST_DATA: Dict = {
    "url": "https://sr.bokbasen.io/coverimage/9788203395819/os/jpg"
}
TEST_MEDIA_CODE: str = 'test_media_code'
TEST_FILE_NAME: str = 'test_cover.jpg'


def test_update_media_success(requests_mock) -> None:
    requests_mock.post(
        url='https://lydbokforlaget-feed.isysnet.no/token-server/oauth/token',
        text=json.dumps({'access_token': 'test_token'})
    )
    media_update_call = requests_mock.put(
        url=f'{FEED_BASE_URL}/media/import/replace/url?importCode={TEST_MEDIA_CODE}&fileName={TEST_FILE_NAME}',
        status_code=status.HTTP_200_OK
    )
    feed_import: FeedImport = FeedImport('test_username', 'test_password')
    feed_import.update_media(
        media_code=TEST_MEDIA_CODE,
        file_name=TEST_FILE_NAME,
        data=TEST_DATA
    )
    assert media_update_call.last_request.text == json.dumps(TEST_DATA)


def test_update_media_fail(requests_mock) -> None:
    requests_mock.post(
        url='https://lydbokforlaget-feed.isysnet.no/token-server/oauth/token',
        text=json.dumps({'access_token': 'test_token'})
    )
    requests_mock.put(
        url=f'{FEED_BASE_URL}/media/import/replace/url?importCode={TEST_MEDIA_CODE}&fileName={TEST_FILE_NAME}',
        status_code=status.HTTP_400_BAD_REQUEST,
        text='No media with id=39156 found.'
    )
    feed_import: FeedImport = FeedImport('test_username', 'test_password')
    with pytest.raises(HTTPError) as http_error:
        feed_import.update_media(
            media_code=TEST_MEDIA_CODE,
            file_name=TEST_FILE_NAME,
            data=TEST_DATA
        )
    assert str(http_error.value) == (
        'Error 400 '
        'calling https://lydbokforlaget-feed.isysnet.no/media/import/replace/url?importCode=test_media_code&fileName=test_cover.jpg, '
        'details: No media with id=39156 found.'
    )
