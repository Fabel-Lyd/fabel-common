from typing import Dict
import pytest
from fabelcommon.feed.export_service import FeedExport
from fabelcommon.json.json_files import read_json_data


TEST_DATA_DIRECTORY: str = 'tests/feed/export_service/data/get_book'
TEST_ISBN: str = '00001'


def test_get_book_successful(mocker) -> None:
    test_data: Dict = read_json_data(f'{TEST_DATA_DIRECTORY}/successful_found.json')

    expected_endpoint: str = f'https://lydbokforlaget-feed.isysnet.no/export/export?changesOnly=false&productTypeImportCodes=ERP&productNo={TEST_ISBN}'

    test_request = mocker.patch.object(
        FeedExport,
        attribute="_FeedExport__send_product_export_request",
        return_value=test_data['response_data']
    )

    feed_export: FeedExport = FeedExport('fake_client_id', 'fake_client_secret')
    book: Dict = feed_export.get_book(TEST_ISBN)

    actual_endpoint: str = test_request.call_args.args[0]

    assert expected_endpoint == actual_endpoint
    assert book == test_data['expected']


@pytest.mark.parametrize(
    'data_file_name, exception_message',
    [
        ('failed_duplicate.json', f'Multiple books with ISBN "{TEST_ISBN}" found in Feed'),
        ('failed_not_found.json', f'Book with ISBN "{TEST_ISBN}" not found in Feed'),
    ])
def test_get_book_failed(data_file_name: str, exception_message: str, mocker) -> None:
    test_data: Dict = read_json_data(f'{TEST_DATA_DIRECTORY}/{data_file_name}')

    mocker.patch.object(
        FeedExport,
        attribute="_FeedExport__send_product_export_request",
        return_value=test_data['response_data']
    )

    feed_export: FeedExport = FeedExport('fake_client_id', 'fake_client_secret')

    with pytest.raises(Exception) as exception_info:
        feed_export.get_book(TEST_ISBN)

    assert str(exception_info.value) == exception_message
