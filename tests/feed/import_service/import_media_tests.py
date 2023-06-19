import json
from typing import Dict
from requests import HTTPError
import pytest
from rest_framework import status
from fabelcommon.feed.import_service import FeedImport


PAYLOAD_DATA_SUCCESS: Dict = {
    "fileName": "9788234001635.jpg",
    "sourceId": "string",
    "url": "https://sr.bokbasen.io/coverimage/9788234001635/os/jpg",
    "products": [
        {
            "identifier": {
                "importCode": "32781",
                "productNo": "9788234001635"
            },
            "mediaRoleCodes": [
                "main_web"
            ]
        }
    ],
    "name": "9788234001635.jpg",
}

PAYLOAD_DATA_MISSING_DATA: Dict = {
    "fileName": "9788234001635.jpg",
    "sourceId": "string",
    "products": [
        {
            "mediaRoleCodes": [
                "main_web"
            ]
        }
    ],
    "name": "9788234001635.jpg"
}


def test_import_feed_media_success(requests_mock) -> None:
    requests_mock.post(
        'https://lydbokforlaget-feed.isysnet.no/token-server/oauth/token',
        text=json.dumps({'access_token': 'test_token'})
    )
    requests_mock.post(
        'https://lydbokforlaget-feed.isysnet.no/media/import/upload/url',
        status_code=status.HTTP_200_OK,
        text='guid'
    )

    data: Dict = PAYLOAD_DATA_SUCCESS

    feed_import: FeedImport = FeedImport('test_username', 'test_password')
    response = feed_import.import_media(data)

    assert response == 'guid'


def test_import_feed_media_missing_url(requests_mock) -> None:
    requests_mock.post(
        'https://lydbokforlaget-feed.isysnet.no/token-server/oauth/token',
        text=json.dumps({'access_token': 'test_token'})
    )

    requests_mock.post(
        'https://lydbokforlaget-feed.isysnet.no/media/import/upload/url',
        status_code=status.HTTP_400_BAD_REQUEST,
        text=json.dumps({"message": "No URL specified"})
    )

    expected_text = \
        'Error 400 calling https://lydbokforlaget-feed.isysnet.no/media/import/upload/url, ' \
        'details: {"message": "No URL specified"}'

    data: Dict = PAYLOAD_DATA_MISSING_DATA

    feed_import: FeedImport = FeedImport('test_username', 'test_password')

    with pytest.raises(HTTPError) as exception:
        feed_import.import_media(data)

    assert str(exception.value) == expected_text
