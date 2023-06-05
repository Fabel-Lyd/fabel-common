import json
from typing import Dict
import pytest
from rest_framework import status
from fabelcommon.feed.import_service import FeedImport

PAYLOAD_DATA: Dict = {
    "importCode": "test-produsert",
    "lines": [
        {
            "action": "ADD",
            "key": "1",
            "name": {
                "nb": "Test Name",
            },
        }
    ]
}


def test_import_data_register_item_success(requests_mock):

    requests_mock.post(
        'https://lydbokforlaget-feed.isysnet.no/token-server/oauth/token',
        text=json.dumps({'access_token': 'test_token'})
    )

    requests_mock.patch(
        'https://lydbokforlaget-feed.isysnet.no/import/basedata/dataRegisters/test-produsert-av',
        status_code=status.HTTP_200_OK,
        text='[]'
    )

    feed_import: FeedImport = FeedImport('test_username', 'test_password')
    import_register_item = feed_import.import_data_register_items('test-produsert-av', PAYLOAD_DATA)

    assert import_register_item is None


def test_import_data_register_item_fail(requests_mock):

    requests_mock.post(
        'https://lydbokforlaget-feed.isysnet.no/token-server/oauth/token',
        text=json.dumps({'access_token': 'test_token'})
    )

    requests_mock.patch(
        'https://lydbokforlaget-feed.isysnet.no/import/basedata/dataRegisters/test-produsert',
        status_code=status.HTTP_200_OK,
        text='["No data register found with import code test-produsert-av"]'
    )

    feed_import: FeedImport = FeedImport('test_username', 'test_password')
    with pytest.raises(Exception) as exception:
        feed_import.import_data_register_items('test-produsert', PAYLOAD_DATA)

    assert str(exception.value) == "No data register found with import code test-produsert-av"
