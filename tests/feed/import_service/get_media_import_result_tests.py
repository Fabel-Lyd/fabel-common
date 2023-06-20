from typing import List
import json
import pytest
from rest_framework import status
from fabelcommon.feed.import_service.media_import_result import MediaImportResult
from fabelcommon.json.json_files import read_json_data
from fabelcommon.feed.import_service import FeedImport


TEST_DATA_DIRECTORY: str = 'tests/feed/import_service/data/get_media_import_result'


@pytest.mark.parametrize(
    'filename, expected_finished, expected_errors, expected_was_successful',
    [
        (
            'media_import_result_finished_success.json',
            True,
            [],
            True
        ),
        (
            'media_import_result_finished_error.json',
            True,
            ['Error message'],
            False
        )
    ]
)
def test_get_media_import_result_finished(
        filename: str,
        expected_finished: bool,
        expected_errors: List[str],
        expected_was_successful: bool,
        requests_mock
) -> None:

    requests_mock.post(
        'https://lydbokforlaget-feed.isysnet.no/token-server/oauth/token',
        text=json.dumps({'access_token': 'test_token'})
    )
    requests_mock.get(
        url='https://lydbokforlaget-feed.isysnet.no/media/import/status?guid=test_guid',
        status_code=status.HTTP_200_OK,
        text=json.dumps(read_json_data(f'{TEST_DATA_DIRECTORY}/{filename}'))
    )

    feed_import: FeedImport = FeedImport('test_username', 'test_password')
    media_import_result: MediaImportResult = feed_import.get_media_import_result('test_guid')

    assert media_import_result.finished == expected_finished
    assert media_import_result.errors == expected_errors
