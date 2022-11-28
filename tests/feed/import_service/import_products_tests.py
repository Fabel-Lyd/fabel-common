from typing import Dict, List
import pytest
import json
from fabelcommon.json.json_files import read_json_data
from fabelcommon.feed.import_service import FeedImport
from fabelcommon.feed.import_service.import_mode import ImportMode

TEST_DATA_DIRECTORY: str = 'tests/feed/import_service/data/import_products/'


def test_import_products(mocker) -> None:
    import_persons: List[Dict] = read_json_data(TEST_DATA_DIRECTORY + 'import_persons.json')

    test_request = mocker.patch.object(
        FeedImport,
        attribute='_FeedImport__send_request',
        return_value='guid'
    )

    expected_endpoint: str = 'https://lydbokforlaget-feed.isysnet.no/import/import'
    expected_payload: str = json.dumps(read_json_data(TEST_DATA_DIRECTORY + 'expected_payload.json'))

    feed_import: FeedImport = FeedImport('fake_client_id', 'fake_client_secret')

    feed_import.import_products(
        formatted_products=import_persons,
        import_mode=ImportMode.CREATE_OR_UPDATE
    )

    actual_endpoint: str = test_request.call_args.args[0]
    actual_payload: str = test_request.call_args.args[1]

    assert actual_endpoint == expected_endpoint
    assert actual_payload == expected_payload


def test_import_products_empty_list():
    feed_import: FeedImport = FeedImport('fake_client_id', 'fake_client_secret')

    with pytest.raises(Exception) as exception:
        feed_import.import_products(
            formatted_products=[],
            import_mode=ImportMode.CREATE_OR_UPDATE
        )

    assert str(exception.value) == 'List of products to be imported is empty'
