from typing import Dict, Optional
import json
from fabelcommon.json.json_files import read_json_data
from fabelcommon.feed.import_service import FeedImport
from fabelcommon.feed.import_service.import_result import ImportResult

TEST_DATA_DIRECTORY: str = 'tests/feed/import_service/data/get_import_result'


def test_get_import_report_finished(requests_mock) -> None:
    status_report: Dict = read_json_data(f'{TEST_DATA_DIRECTORY}/import_status_report_finished.json')

    requests_mock.post(
        'https://lydbokforlaget-feed.isysnet.no/token-server/oauth/token',
        text=json.dumps({'access_token': 'test_token'})
    )
    requests_mock.get(
        'https://lydbokforlaget-feed.isysnet.no/import/import/'
        'test_guid/status?includeNewProducts=true&includeUpdatedAndDeletedProducts=true&page=0',
        text=json.dumps(status_report[0])
    )
    requests_mock.get(
        'https://lydbokforlaget-feed.isysnet.no/import/import/'
        'test_guid/status?includeNewProducts=true&includeUpdatedAndDeletedProducts=true&page=1',
        text=json.dumps(status_report[1])
    )

    feed_import: FeedImport = FeedImport('test_username', 'test_password')
    import_result: Optional[ImportResult] = feed_import.get_import_result('test_guid')

    assert isinstance(import_result, ImportResult)
    assert len(import_result.created_items) == 5


def test_get_import_report_in_progress(requests_mock) -> None:
    status_report: Dict = read_json_data(f'{TEST_DATA_DIRECTORY}/import_status_report_in_progress.json')
    requests_mock.post(
        'https://lydbokforlaget-feed.isysnet.no/token-server/oauth/token',
        text=json.dumps({'access_token': 'test_token'})
    )
    requests_mock.get(
        'https://lydbokforlaget-feed.isysnet.no/import/import/'
        'test_guid/status?includeNewProducts=true&includeUpdatedAndDeletedProducts=true&page=0',
        text=json.dumps(status_report)
    )

    feed_import: FeedImport = FeedImport('test_username', 'test_password')
    import_result: Optional[ImportResult] = feed_import.get_import_result('test_guid')

    assert import_result is None
