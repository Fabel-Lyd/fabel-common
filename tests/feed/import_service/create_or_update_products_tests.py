import json
from typing import Dict, List
from fabelcommon.json.json_files import read_json_data
from fabelcommon.feed.import_service.import_service import FeedImport


def test_create_or_update_products(mocker) -> None:
    test_data: Dict = read_json_data('tests/feed/import_service/data/product_import.json')

    product_import_list: List[Dict] = test_data['product_import_list']

    expected_endpoint: str = 'https://lydbokforlaget-feed.isysnet.no/import/import'
    expected_payload: str = json.dumps(test_data['expected_payload'])

    test_request = mocker.patch.object(
        FeedImport,
        attribute='_FeedImport__send_request'
    )

    feed_import: FeedImport = FeedImport('fake_client_id', 'fake_client_secret')
    feed_import.create_or_update_products(product_import_list)

    actual_endpoint: str = test_request.call_args.args[0]
    actual_payload: str = test_request.call_args.args[1]

    assert expected_endpoint == actual_endpoint
    assert expected_payload == actual_payload
