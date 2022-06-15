from typing import Dict
import pytest
from fabelcommon.feed.export_service import FeedExport
from fabelcommon.json.json_files import read_json_data


def test_get_book_successful(mocker) -> None:
    test_data: Dict = read_json_data('tests/feed/export_service/data/book_successful.json')

    mocker.patch.object(
        FeedExport,
        attribute="_FeedExport__send_request",
        side_effect=test_data['response_data']
    )

    feed_export: FeedExport = FeedExport('fake_client_id', 'fake_client_secret')
    book: Dict = feed_export.get_book('00001')

    assert book == test_data['expected']


@pytest.mark.parametrize(
    'data_file_name, exception_message',
    [
        ('tests/feed/export_service/data/book_duplicate.json', 'Multiple books with ISBN 00001 found in Feed'),
        ('tests/feed/export_service/data/book_not_found.json', 'Book with ISBN 00001 not found in Feed'),
    ])
def test_get_book_failed(data_file_name: str, exception_message: str, mocker) -> None:
    test_data: Dict = read_json_data(data_file_name)

    mocker.patch.object(
        FeedExport,
        attribute="_FeedExport__send_request",
        side_effect=test_data['response_data']
    )

    feed_export: FeedExport = FeedExport('fake_client_id', 'fake_client_secret')

    with pytest.raises(Exception) as exception_info:
        feed_export.get_book('00001')

    assert str(exception_info.value) == exception_message
