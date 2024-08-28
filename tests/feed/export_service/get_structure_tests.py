import json
from typing import List, Dict
from fabelcommon.feed.export_service import FeedExport
from fabelcommon.json.json_files import read_json_data


TEST_DATA_DIRECTORY: str = 'tests/feed/export_service/data/get_structure'


def test_get_structure(requests_mock) -> None:
    exported_data: List[Dict] = read_json_data(f'{TEST_DATA_DIRECTORY}/exported_structures.json')
    import_code: str = 'sjanger'

    requests_mock.post(
        'https://lydbokforlaget-feed.isysnet.no/token-server/oauth/token',
        text=json.dumps({'access_token': 'fake_access_token'})
    )
    requests_mock.get(
        'https://lydbokforlaget-feed.isysnet.no/export/structure/structures/sjanger',
        text=json.dumps(exported_data)
    )

    feed_export: FeedExport = FeedExport('test_username', 'test_password')
    assert feed_export.get_structure(import_code) == exported_data
