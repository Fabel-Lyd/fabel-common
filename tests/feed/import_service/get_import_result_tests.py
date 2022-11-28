from typing import Dict, Optional, Type
import pytest
import json
from fabelcommon.json.json_files import read_json_data
from fabelcommon.feed.import_service import FeedImport
from fabelcommon.feed.import_service.import_result import ImportResult

TEST_DATA_DIRECTORY: str = 'tests/feed/import_service/data/get_import_result'


@pytest.mark.parametrize(
    'status_report_path, expected_result_type',
    [
        (
            f'{TEST_DATA_DIRECTORY}/import_status_report_finished.json',
            ImportResult
        ),
        (
            f'{TEST_DATA_DIRECTORY}/import_status_report_in_progress.json',
            type(None)
        )
    ]
)
def test_get_import_report(
        status_report_path: str,
        expected_result_type: Type,
        requests_mock
) -> None:

    status_report: Dict = read_json_data(status_report_path)

    requests_mock.post(
        'https://lydbokforlaget-feed.isysnet.no/token-server/oauth/token',
        text=json.dumps({'access_token': 'test_token'})
    )
    requests_mock.get(
        'https://lydbokforlaget-feed.isysnet.no/import/import/'
        'test_guid/status?includeNewProducts=true&includeUpdatedAndDeletedProducts=true',
        text=json.dumps(status_report)
    )

    feed_import: FeedImport = FeedImport('test_username', 'test_password')
    import_result: Optional[ImportResult] = feed_import.get_import_result('test_guid')

    assert type(import_result) == expected_result_type
