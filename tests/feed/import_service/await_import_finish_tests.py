from typing import Dict, List, Optional, Callable
import pytest
from fabelcommon.json.json_files import read_json_data
from fabelcommon.feed.import_service import FeedImport
from fabelcommon.feed.import_service.import_result import ImportResult

TEST_DATA_DIRECTORY: str = 'tests/feed/import_service/data/await_import_finish/'


@pytest.fixture
def patch_get_import_report(mocker):
    def __object_patch(status_reports: List[List[Dict]]):
        mocker.patch.object(
            FeedImport,
            attribute=FeedImport.get_import_result.__name__,
            side_effect=[ImportResult(status_report) for status_report in status_reports]
        )
    return __object_patch


@pytest.mark.parametrize(
    'import_status_reports',
    [
        read_json_data(f'{TEST_DATA_DIRECTORY}/1.json'),
        read_json_data(f'{TEST_DATA_DIRECTORY}/2.json')
    ]
)
def test_await_import_finish_successful(
        import_status_reports: List[List[Dict]],
        patch_get_import_report: Callable
) -> None:

    patch_get_import_report(import_status_reports)

    feed_import: FeedImport = FeedImport('test_username', 'test_password')
    import_result: Optional[ImportResult] = feed_import.await_import_finish('test_guid', 1, 2, 20)

    assert type(import_result) == ImportResult


def test_await_import_finish_failed(mocker) -> None:
    status_report: Dict = read_json_data(f'{TEST_DATA_DIRECTORY}/in_progress.json')
    mocker.patch.object(
        FeedImport,
        attribute=FeedImport.get_import_result.__name__,
        return_value=ImportResult([status_report])
    )

    feed_import: FeedImport = FeedImport('test_username', 'test_password')

    with pytest.raises(Exception) as exception:
        feed_import.await_import_finish('test_guid', 1, 2, 20)

    assert str(exception.value) == 'Feed product import did not return finished status (queried 2 times with 1 s interval)'
