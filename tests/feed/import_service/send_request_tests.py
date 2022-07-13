from typing import Dict, List
import json
from fabelcommon.json.json_files import read_json_data
from fabelcommon.feed.import_service import FeedImport
from fabelcommon.feed.import_service.import_result import ImportResult

TEST_DATA_DIRECTORY: str = 'tests/feed/import_service/data/send_request/'


def test_send_request_successful(mocker) -> None:
    import_persons: List[Dict] = read_json_data(TEST_DATA_DIRECTORY + 'import_persons.json')
    status_report: Dict = read_json_data(TEST_DATA_DIRECTORY + 'import_status_report.json')

    test_request = mocker.patch.object(
        FeedImport,
        attribute='_FeedImport__send_request',
        return_value='guid'
    )
    mocker.patch.object(
        FeedImport,
        attribute='_FeedImport__get_import_report',
        return_value=ImportResult(status_report)
    )

    expected_endpoint: str = 'https://lydbokforlaget-feed.isysnet.no/import/import'
    expected_payload: str = json.dumps(read_json_data(TEST_DATA_DIRECTORY + 'expected_payload.json'))

    feed_import: FeedImport = FeedImport('fake_client_id', 'fake_client_secret')

    feed_import.create_or_update_products(
        formatted_products=import_persons,
        query_interval_seconds=1,
        max_attempts=1
    )

    actual_endpoint: str = test_request.call_args.args[0]
    actual_payload: str = test_request.call_args.args[1]

    assert actual_endpoint == expected_endpoint
    assert actual_payload == expected_payload
