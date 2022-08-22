from typing import Dict, List
import pytest
from fabelcommon.json.json_files import read_json_data
from fabelcommon.feed.import_service import FeedImport
from fabelcommon.feed.import_service.import_result import ImportResult
from fabelcommon.feed.import_service.import_result_item import ImportResultItem
from fabelcommon.feed.import_service.import_status import ImportStatus

TEST_DATA_DIRECTORY: str = 'tests/feed/import_service/data/create_or_update_products/'


@pytest.fixture
def patch_send_payload(mocker):
    mocker.patch.object(
        FeedImport,
        attribute='_FeedImport__send_payload',
        return_value='guid'
    )


@pytest.fixture
def patch_get_import_report(mocker):
    def __object_patch(status_reports: List[Dict]):
        mocker.patch.object(
            FeedImport,
            attribute='_FeedImport__get_import_report',
            side_effect=[
                ImportResult(status_report) if status_report['finishedTime'] is not None
                else None
                for status_report in status_reports
            ]
        )
    return __object_patch


@pytest.mark.parametrize(
    'import_persons_path, status_reports_path, expected_status, expected_items, expected_report_path',
    [
        (
            TEST_DATA_DIRECTORY + 'import_error/import_persons_error.json',
            TEST_DATA_DIRECTORY + 'import_error/import_status_reports_error.json',
            ImportStatus.ERROR,
            [
                ImportResultItem('33390', 'P_9999999'),
                ImportResultItem('33389', 'P_9999997')
            ],
            TEST_DATA_DIRECTORY + 'import_error/import_result_details_error.json'
        ),
        (
            TEST_DATA_DIRECTORY + 'import_warning/import_persons_warning.json',
            TEST_DATA_DIRECTORY + 'import_warning/import_status_reports_warning.json',
            ImportStatus.WARNING,
            [
                ImportResultItem('33391', 'P_9999999'),
                ImportResultItem('33390', 'P_9999998'),
                ImportResultItem('33389', 'P_9999997')
            ],
            TEST_DATA_DIRECTORY + 'import_warning/import_result_details_warning.json'
        ),
        (
            TEST_DATA_DIRECTORY + 'import_ok/import_persons_ok.json',
            TEST_DATA_DIRECTORY + 'import_ok/import_status_reports_ok.json',
            ImportStatus.OK,
            [
                ImportResultItem('33391', 'P_9999999'),
                ImportResultItem('33390', 'P_9999998'),
                ImportResultItem('33389', 'P_9999997')
            ],
            TEST_DATA_DIRECTORY + 'import_ok/import_result_details_ok.json'
        ),
        (
            TEST_DATA_DIRECTORY + 'import_missing/import_persons_missing.json',
            TEST_DATA_DIRECTORY + 'import_missing/import_status_reports_missing.json',
            ImportStatus.ERROR,
            [],
            TEST_DATA_DIRECTORY + 'import_missing/import_result_details_missing.json'
        )
    ]
)
def test_import_products_successful(
        import_persons_path: str,
        status_reports_path: str,
        expected_status: ImportStatus,
        expected_items: List[ImportResultItem],
        expected_report_path: str,
        patch_send_payload,
        patch_get_import_report
) -> None:

    import_persons: List[Dict] = read_json_data(import_persons_path)
    status_reports: List[Dict] = read_json_data(status_reports_path)
    expected_report: Dict = read_json_data(expected_report_path)

    patch_get_import_report(status_reports)

    feed_import: FeedImport = FeedImport('fake_client_id', 'fake_client_secret')

    actual_import_result: ImportResult = feed_import.create_or_update_products(
        formatted_products=import_persons,
        query_interval_seconds=1,
        max_attempts=2
    )

    assert actual_import_result.status == expected_status
    assert actual_import_result.created_items == expected_items
    assert actual_import_result.report == expected_report


@pytest.mark.parametrize(
    'import_persons_path, status_reports_path, exception_message',
    [
        (
            TEST_DATA_DIRECTORY + 'import_ok/import_persons_ok.json',
            TEST_DATA_DIRECTORY + 'import_status_reports_timeout.json',
            'Feed product import did not return finished status (queried 2 times with 1 s interval)'
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

    patch_get_import_report(status_reports)

    feed_import: FeedImport = FeedImport('fake_client_id', 'fake_client_secret')

    with pytest.raises(Exception) as exception:
        feed_import.create_or_update_products(
            formatted_products=import_persons,
            query_interval_seconds=1,
            max_attempts=2
        )

    assert str(exception.value) == exception_message


def test_create_or_update_products_empty_list():
    feed_import: FeedImport = FeedImport('fake_client_id', 'fake_client_secret')

    with pytest.raises(Exception) as exception:
        feed_import.create_or_update_products(
            formatted_products=[],
            query_interval_seconds=1,
            max_attempts=2
        )

    assert str(exception.value) == 'List of products to be imported is empty'
