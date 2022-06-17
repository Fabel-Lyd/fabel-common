from typing import Dict, List
from fabelcommon.json.json_files import read_json_data
import pytest
from fabelcommon.feed.export_service import FeedExport
from fabelcommon.feed.export_service import ProductType


@pytest.mark.parametrize(
    'product_type, search_parameters, data_file_name',
    [
        (ProductType.PERSON, ['a', 'b'], 'tests/feed/export_service/data/get_products_by_name/successful_found.json'),
        (ProductType.PERSON, ['a'], 'tests/feed/export_service/data/get_products_by_name/successful_not_found.json'),
        (ProductType.BOOK, ['a', 'b'], 'tests/feed/export_service/data/get_products_by_name/successful_books_with_same_name.json'),
    ])
def test_get_products_by_name(
        product_type: ProductType,
        search_parameters: List[str],
        data_file_name: str,
        mocker
) -> None:

    test_data: Dict = read_json_data(data_file_name)

    mocker.patch.object(
        FeedExport,
        attribute='_FeedExport__send_request',
        side_effect=test_data['response_data']
    )

    feed_export = FeedExport('fake_client_id', 'fake_client_secret')
    products_found: List[Dict] = feed_export.get_products_by_name(search_parameters, product_type)

    assert products_found == test_data['expected']


def test_get_products_by_name_duplicate_person(mocker) -> None:
    test_data: Dict = read_json_data('tests/feed/export_service/data/get_products_by_name/failed_duplicate_person.json')

    mocker.patch.object(
        FeedExport,
        attribute="_FeedExport__send_request",
        side_effect=test_data['response_data']
    )

    feed_export: FeedExport = FeedExport('fake_client_id', 'fake_client_secret')

    with pytest.raises(Exception) as exception_info:
        feed_export.get_products_by_name(['a'], ProductType.PERSON)

    assert str(exception_info.value) == 'Multiple persons named "a" found in Feed'
