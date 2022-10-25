from typing import Dict, List
import pytest
import json
from fabelcommon.feed.export_service import FeedExport
from fabelcommon.json.json_files import read_json_data

TEST_DATA_DIRECTORY: str = 'tests/feed/export_service/data/get_data_register'


def test_get_data_register(requests_mock) -> None:
    exported_data: List[Dict] = read_json_data(f'{TEST_DATA_DIRECTORY}/exported_data_register.json')
    expected: Dict = read_json_data(f'{TEST_DATA_DIRECTORY}/expected.json')
    import_code: str = 'bokforlag'

    requests_mock.post(
        'https://lydbokforlaget-feed.isysnet.no/token-server/oauth/token',
        text=json.dumps({'access_token': 'fake_access_token'})
    )
    requests_mock.get(
        f'https://lydbokforlaget-feed.isysnet.no/export/basedata/dataRegisters?importCode={import_code}',
        text=json.dumps(exported_data)
    )

    feed_export: FeedExport = FeedExport('test_username', 'test_password')

    assert feed_export.get_data_register(import_code) == expected


def test_get_data_register_failed(requests_mock):
    import_code: str = 'import-code'

    requests_mock.post(
        'https://lydbokforlaget-feed.isysnet.no/token-server/oauth/token',
        text=json.dumps({'access_token': 'fake_access_token'})
    )
    requests_mock.get(
        f'https://lydbokforlaget-feed.isysnet.no/export/basedata/dataRegisters?importCode={import_code}',
        text=json.dumps([])
    )

    feed_export: FeedExport = FeedExport('test_username', 'test_password')

    with pytest.raises(Exception) as exception:
        feed_export.get_data_register(import_code)

    assert str(exception.value) == f'Data register with import code {import_code} does not exist in Feed'
