import json
from typing import Dict, List
from fabelcommon.json.json_files import read_json_data, read_json_as_text
from fabelcommon.feed.export_service import FeedExport
from fabelcommon.feed.export_service.feed_attribute import FeedAttribute


TEST_DATA_DIRECTORY: str = 'tests/feed/export_service/data/get_books_by_attributes'
TEST_PAGE_SIZE: int = 1
TEST_PAGE: int = 0


def test_get_books_by_attributes(requests_mock) -> None:
    expected_payload: str = json.dumps({
        "attributes": [
            {
                "importCode": "lydfil-salgsstatus",
                "value": "Utgått"
            },
            {
                "importCode": "lydfil-salgsstatus",
                "value": "I salg"
            },
            {
                "importCode": "lydfil-salgsstatus",
                "value": "Kommer"
            }
        ]
    })
    expected_result: List[Dict] = read_json_data(f'{TEST_DATA_DIRECTORY}/expected_result.json')

    requests_mock.post(
        'https://lydbokforlaget-feed.isysnet.no/token-server/oauth/token',
        text=json.dumps({'access_token': 'test_access_token'})
    )
    test_request = requests_mock.post(
        f'https://lydbokforlaget-feed.isysnet.no/export/export?changesOnly=false&productTypeImportCodes=ERP&size={TEST_PAGE_SIZE}&page={TEST_PAGE}',
        text=read_json_as_text(f'{TEST_DATA_DIRECTORY}/feed_response.json')
    )

    feed_export: FeedExport = FeedExport('test_username', 'test_password')
    actual_result: List[Dict] = feed_export.get_books_by_attributes(
        [
            FeedAttribute('lydfil-salgsstatus', 'Utgått'),
            FeedAttribute('lydfil-salgsstatus', 'I salg'),
            FeedAttribute('lydfil-salgsstatus', 'Kommer')
        ],
        TEST_PAGE_SIZE,
        TEST_PAGE
    )

    actual_payload: str = test_request.last_request.text

    assert actual_payload == expected_payload
    assert actual_result == expected_result
