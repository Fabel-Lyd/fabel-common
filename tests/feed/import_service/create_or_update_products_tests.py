from typing import Dict, List
import pytest
import json
from fabelcommon.json.json_files import read_json_data
from fabelcommon.feed.import_service import FeedImport
from fabelcommon.feed.import_service.import_result import ImportResult
from fabelcommon.feed.import_service.import_result_item import ImportResultItem
from fabelcommon.feed.import_service.import_status import ImportStatus

TEST_DATA_DIRECTORY: str = 'tests/feed/import_service/data/create_or_update_products/'


@pytest.fixture
def patch_send_payload(mocker):
    def __factory():
        mocker.patch.object(
            FeedImport,
            attribute=FeedImport.send_payload.__name__,
            return_value='guid'
        )
    return __factory


@pytest.fixture
def patch_get_import_report(mocker):
    def __factory(status_reports: List[Dict]):
        mocker.patch.object(
            FeedImport,
            attribute='_FeedImport__get_import_report',
            side_effect=[
                ImportResult(status_report) if status_report['finishedTime'] is not None
                else None
                for status_report in status_reports
            ]
        )
    return __factory


def test_create_or_update_products_successful(
        patch_send_payload,
        patch_get_import_report
) -> None:

    import_persons: List[Dict] = read_json_data(TEST_DATA_DIRECTORY + 'import_persons_ok.json')
    status_reports: List[Dict] = read_json_data(TEST_DATA_DIRECTORY + 'import_status_reports_ok.json')

    patch_send_payload()
    patch_get_import_report(status_reports)

    feed_import: FeedImport = FeedImport('fake_client_id', 'fake_client_secret')

    actual_import_result: ImportResult = feed_import.create_or_update_products(
        formatted_products=import_persons,
        query_interval_seconds=1,
        max_attempts=2
    )

    expected_import_status: ImportStatus = ImportStatus.OK
    expected_import_created_items: List[ImportResultItem] = [
        ImportResultItem('33391', 'P_9999999'),
        ImportResultItem('33390', 'P_9999998'),
        ImportResultItem('33389', 'P_9999997')
    ]

    assert actual_import_result.status == expected_import_status
    assert actual_import_result.created_items == expected_import_created_items


@pytest.mark.parametrize(
    'import_persons_path, status_reports_path, exception_message',
    [
        (
            TEST_DATA_DIRECTORY + 'import_persons_error.json',
            TEST_DATA_DIRECTORY + 'import_status_reports_error.json',
            'Feed product import unsuccessful. Report: ' +
            json.dumps(read_json_data(TEST_DATA_DIRECTORY + 'import_result_report_error.json'))
        ),
        (
            TEST_DATA_DIRECTORY + 'import_persons_warning.json',
            TEST_DATA_DIRECTORY + 'import_status_reports_warning.json',
            'Feed product import unsuccessful. Report: ' +
            json.dumps(read_json_data(TEST_DATA_DIRECTORY + 'import_result_report_warning.json'))
        )
    ]
)
def test_create_or_update_products_failed(
        import_persons_path: str,
        status_reports_path: str,
        exception_message: str,
        patch_send_payload,
        patch_get_import_report
) -> None:

    import_persons: List[Dict] = read_json_data(import_persons_path)
    status_reports: List[Dict] = read_json_data(status_reports_path)

    patch_send_payload()
    patch_get_import_report(status_reports)

    feed_import: FeedImport = FeedImport('fake_client_id', 'fake_client_secret')

    with pytest.raises(Exception) as exception:
        feed_import.create_or_update_products(
            formatted_products=import_persons,
            query_interval_seconds=1,
            max_attempts=2
        )

    assert str(exception.value) == exception_message


def test_create_or_update_products_timeout(
        patch_send_payload,
        patch_get_import_report
) -> None:

    import_persons: List[Dict] = read_json_data(TEST_DATA_DIRECTORY + 'import_persons_ok.json')
    status_reports: List[Dict] = read_json_data(TEST_DATA_DIRECTORY + 'import_status_reports_timeout.json')

    patch_send_payload()
    patch_get_import_report(status_reports)

    feed_import: FeedImport = FeedImport('fake_client_id', 'fake_client_secret')

    with pytest.raises(Exception) as exception:
        feed_import.create_or_update_products(
            formatted_products=import_persons,
            query_interval_seconds=1,
            max_attempts=2
        )

    assert str(exception.value) == 'Feed product import did not return finished status (queried 2 times with 1 s interval)'
