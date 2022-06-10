from typing import Dict, List
from fabelcommon.json.json_files import read_json_data
import pytest
from fabelcommon.feed.export.export import FeedExport
from fabelcommon.feed.api_service import FeedApiService
from fabelcommon.feed.export.export import ProductType


@pytest.mark.parametrize(
    'product_type, search_parameters, data_file_name',
    [
        (ProductType.PERSON, ['a', 'b'], 'tests/feed/export/data/persons_by_name.json'),
        (ProductType.PERSON, ['a'], 'tests/feed/export/data/product_not_found.json'),
        (ProductType.BOOK, ['a', 'b'], 'tests/feed/export/data/books_by_name_multiple.json'),
    ])
def test_products_by_name(
        product_type: ProductType,
        search_parameters: List[str],
        data_file_name: str,
        mocker
) -> None:

    test_data: Dict = read_json_data(data_file_name)

    mocker.patch.object(
        FeedApiService,
        attribute='send_request',
        side_effect=test_data['response_data']
    )

    feed_api_service: FeedApiService = FeedApiService('fake_client_id', 'fake_client_secret')

    feed_export = FeedExport(feed_api_service)
    persons_found: List[Dict] = feed_export.products_by_name(search_parameters, product_type)
    assert persons_found == test_data['expected']


def test_persons_by_name_duplicate_person(mocker) -> None:
    test_data: Dict = read_json_data('tests/feed/export/data/persons_by_name_duplicate.json')

    mocker.patch.object(
        FeedApiService,
        attribute='send_request',
        side_effect=test_data['response_data']
    )

    feed_api_service: FeedApiService = FeedApiService('fake_client_id', 'fake_client_secret')

    feed_export: FeedExport = FeedExport(feed_api_service)

    with pytest.raises(Exception) as exception_info:
        feed_export.products_by_name(['a'], ProductType.PERSON)

    assert str(exception_info.value) == 'Multiple persons named "a" found in Feed'
