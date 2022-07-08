from typing import Dict, List
import pytest
import json
from fabelcommon.json.json_files import read_json_data
from fabelcommon.feed.import_service import FeedImport
from fabelcommon.feed.import_service.import_result import ImportResult
from fabelcommon.feed.import_service.import_result_item import ImportResultItem
from fabelcommon.feed.import_service.import_status import ImportStatus

TEST_DATA_DIRECTORY: str = 'tests/feed/import_service/data/await_import_finish/'


@pytest.fixture
def patch_create_or_update_products(mocker):
    def __factory():
        mocker.patch.object(
            FeedImport,
            attribute=FeedImport.create_or_update_products.__name__,
            return_value='guid'
        )
    return __factory


@pytest.fixture
def patch_get_import_report(mocker):
    def __factory(status_reports: List[Dict]):
        mocker.patch.object(
            FeedImport,
            attribute='_FeedImport__get_import_report',
            side_effect=status_reports
        )
    return __factory


def test_await_import_finish_successful(
        patch_create_or_update_products,
        patch_get_import_report
) -> None:

    import_persons: List[Dict] = read_json_data(TEST_DATA_DIRECTORY + 'import_persons_ok.json')
    status_reports: List[Dict] = read_json_data(TEST_DATA_DIRECTORY + 'import_status_reports_ok.json')

    patch_create_or_update_products()
    patch_get_import_report(status_reports)

    expected_import_result: ImportResult = ImportResult(
        status=ImportStatus.OK,
        created_items=[
            ImportResultItem(
                import_code='33391',
                product_number='P_9999999',
                status=ImportStatus.OK,
                messages=[]
            ),
            ImportResultItem(
                import_code='33390',
                product_number='P_9999998',
                status=ImportStatus.OK,
                messages=[]
            ),
            ImportResultItem(
                import_code='33389',
                product_number='P_9999997',
                status=ImportStatus.OK,
                messages=[]
            )
        ]
    )

    feed_import: FeedImport = FeedImport('fake_client_id', 'fake_client_secret')
    guid: str = feed_import.create_or_update_products(import_persons)
    actual_import_result: ImportResult = feed_import.await_import_finish(guid=guid, query_interval_seconds=1, max_attempts=2)

    assert actual_import_result == expected_import_result


@pytest.mark.parametrize(
    'import_persons_path, status_reports_path',
    [
        (
            TEST_DATA_DIRECTORY + 'import_persons_error.json',
            TEST_DATA_DIRECTORY + 'import_status_reports_error.json'

        ),
        (
            TEST_DATA_DIRECTORY + 'import_persons_warning.json',
            TEST_DATA_DIRECTORY + 'import_status_reports_warning.json'
        )
    ]
)
def test_await_import_finish_failed(
        import_persons_path: str,
        status_reports_path: str,
        patch_create_or_update_products,
        patch_get_import_report
) -> None:

    import_persons: List[Dict] = read_json_data(import_persons_path)
    status_reports: List[Dict] = read_json_data(status_reports_path)

    patch_create_or_update_products()
    patch_get_import_report(status_reports)

    feed_import: FeedImport = FeedImport('fake_client_id', 'fake_client_secret')
    guid: str = feed_import.create_or_update_products(import_persons)

    with pytest.raises(Exception) as exception:
        feed_import.await_import_finish(guid=guid, query_interval_seconds=1, max_attempts=2)

    assert str(exception.value) == 'Feed product import unsuccessful. Report: ' + json.dumps(status_reports[1])


def test_await_import_finish_timeout(
        patch_create_or_update_products,
        patch_get_import_report
) -> None:

    import_persons: List[Dict] = read_json_data(TEST_DATA_DIRECTORY + 'import_persons_ok.json')
    status_reports: List[Dict] = read_json_data(TEST_DATA_DIRECTORY + 'import_status_reports_timeout.json')

    patch_create_or_update_products()
    patch_get_import_report(status_reports)

    feed_import: FeedImport = FeedImport('fake_client_id', 'fake_client_secret')
    guid: str = feed_import.create_or_update_products(import_persons)

    with pytest.raises(Exception) as exception:
        feed_import.await_import_finish(guid=guid, query_interval_seconds=1, max_attempts=2)

    assert str(exception.value) == 'Feed product import did not return finished status (queried 2 times with 1 s interval)'
