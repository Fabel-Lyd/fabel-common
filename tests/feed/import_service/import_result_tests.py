from typing import Dict, List
import pytest
from fabelcommon.json.json_files import read_json_data
from fabelcommon.feed.import_service.import_result import ImportResult
from fabelcommon.feed.import_service.import_result_item import ImportResultItem
from fabelcommon.feed.import_service.import_status import ImportStatus

TEST_DATA_DIRECTORY: str = 'tests/feed/import_service/data/import_result/'


@pytest.mark.parametrize(
    'import_report_path, expected_result_report_path, expected_status, expected_created_items',
    [
        (
            TEST_DATA_DIRECTORY + 'import_report_ok.json',
            TEST_DATA_DIRECTORY + 'expected_result_report_ok.json',
            ImportStatus.OK,
            [
                ImportResultItem('33391', 'P_9999999'),
                ImportResultItem('33390', 'P_9999998')
            ]
        ),
        (
            TEST_DATA_DIRECTORY + 'import_report_warning.json',
            TEST_DATA_DIRECTORY + 'expected_result_report_warning.json',
            ImportStatus.WARNING,
            [
                ImportResultItem('33391', 'P_9999999'),
                ImportResultItem('33390', 'P_9999998')
            ]
        ),
        (
            TEST_DATA_DIRECTORY + 'import_report_error.json',
            TEST_DATA_DIRECTORY + 'expected_result_report_error.json',
            ImportStatus.ERROR,
            [
                ImportResultItem('33391', 'P_9999999'),
                ImportResultItem('33389', 'P_9999997')
            ]
        ),
        (
            TEST_DATA_DIRECTORY + 'import_report_missing.json',
            TEST_DATA_DIRECTORY + 'expected_result_report_missing.json',
            ImportStatus.ERROR,
            []
        )
    ]
)
def test_import_result(
        import_report_path: str,
        expected_result_report_path: str,
        expected_status: ImportStatus,
        expected_created_items: List[ImportResultItem]
) -> None:

    import_report: Dict = read_json_data(import_report_path)
    expected_report: Dict = read_json_data(expected_result_report_path)

    import_result: ImportResult = ImportResult(import_report)

    assert import_result.status == expected_status
    assert import_result.created_items == expected_created_items
    assert import_result.report == expected_report
