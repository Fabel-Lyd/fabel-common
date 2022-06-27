from typing import Dict, List
from fabelcommon.json.json_files import read_json_data
import pytest
from fabelcommon.feed.export_service import FeedExport
from fabelcommon.feed.export_service import ProductType
from fabelcommon.feed.export_service.exceptions import DuplicatePersonException


TEST_DATA_DIRECTORY: str = 'tests/feed/export_service/data/get_products_by_name'


@pytest.mark.parametrize(
    'data_file_name, product_type, search_parameters',
    [
        ('successful_found.json', ProductType.PERSON, ['a', 'b']),
        ('successful_not_found.json', ProductType.PERSON, ['a']),
        ('successful_books_with_same_name.json', ProductType.BOOK, ['a', 'b']),
    ])
def test_get_products_by_name_successful(
        data_file_name: str,
        product_type: ProductType,
        search_parameters: List[str],
        mocker
) -> None:

    test_data: Dict = read_json_data(f'{TEST_DATA_DIRECTORY}/{data_file_name}')

    expected_endpoint_partial: str = f'https://lydbokforlaget-feed.isysnet.no/export/export?changesOnly=false&productTypeImportCodes={product_type.value}&name='

    test_request = mocker.patch.object(
        FeedExport,
        attribute='_FeedExport__send_request',
        side_effect=test_data['response_data']
    )

    feed_export = FeedExport('fake_client_id', 'fake_client_secret')
    products_found: List[Dict] = feed_export.get_products_by_name(search_parameters, product_type)

    expected_endpoints: List[str] = [expected_endpoint_partial + name for name in search_parameters]
    actual_endpoints: List[str] = [call.args[0] for call in test_request.call_args_list]

    assert expected_endpoints == actual_endpoints
    assert products_found == test_data['expected']


def test_get_products_by_name_failed(mocker) -> None:
    test_data: Dict = read_json_data(f'{TEST_DATA_DIRECTORY}/failed_duplicate_person.json')

    mocker.patch.object(
        FeedExport,
        attribute="_FeedExport__send_request",
        side_effect=test_data['response_data']
    )

    feed_export: FeedExport = FeedExport('fake_client_id', 'fake_client_secret')

    with pytest.raises(DuplicatePersonException) as exception_info:
        feed_export.get_products_by_name(['a'], ProductType.PERSON)

    assert str(exception_info.value) == 'Multiple persons named "a" found in Feed'
