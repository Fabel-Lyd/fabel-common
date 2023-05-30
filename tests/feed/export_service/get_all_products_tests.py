from typing import Dict, List
import json
from fabelcommon.json.json_files import read_json_data, read_json_as_text
from fabelcommon.feed.export_service import FeedExport


TEST_DATA_DIRECTORY: str = 'tests/feed/export_service/data/get_all_products'

PAGE_SIZE: int = 100


def test_get_all_products(requests_mock) -> None:
    expected_result: List[Dict] = read_json_data(f'{TEST_DATA_DIRECTORY}/expected.json')

    requests_mock.post(
        'https://lydbokforlaget-feed.isysnet.no/token-server/oauth/token',
        text=json.dumps({'access_token': 'test_token'})
    )

    for page in range(3):
        requests_mock.post(
            f'https://lydbokforlaget-feed.isysnet.no/export/export?changesOnly=false&size={PAGE_SIZE}&page={page}',
            text=read_json_as_text(f'{TEST_DATA_DIRECTORY}/exported_product_{page + 1}.json')
        )

    feed_export: FeedExport = FeedExport('test_username', 'test_password')
    actual_result: List[Dict] = feed_export.get_all_products()

    assert expected_result == actual_result
