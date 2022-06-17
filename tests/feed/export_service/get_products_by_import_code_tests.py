from typing import Dict, List
import pytest
from fabelcommon.feed.export_service import FeedExport
from fabelcommon.json.json_files import read_json_data
from fabelcommon.feed.export_service import ProductType


TEST_DATA_DIRECTORY: str = 'tests/feed/export_service/data/get_products_by_import_code'


@pytest.mark.parametrize(
    'data_file_name, product_type, search_parameters',
    [
        ('successful_found.json', ProductType.PERSON, ['99991', '99992']),
        ('successful_not_found.json', ProductType.PERSON, ['99991']),
    ])
def test_get_products_by_import_code_successful(
        data_file_name: str,
        product_type: ProductType,
        search_parameters: List[str],
        mocker
) -> None:

    test_data: Dict = read_json_data(f'{TEST_DATA_DIRECTORY}/{data_file_name}')
    concatenated_search_parameters: str = ','.join(search_parameters)

    expected_endpoint: str = f'https://lydbokforlaget-feed.isysnet.no/export/export?changesOnly=false&productTypeImportCodes={product_type.value}&importCodes={concatenated_search_parameters}&size=500&page=0'

    test_request = mocker.patch.object(
        FeedExport,
        attribute='_FeedExport__send_request',
        return_value=test_data['response_data']
    )

    feed_export: FeedExport = FeedExport('fake_client_id', 'fake_client_secret')
    products_found: List[Dict] = feed_export.get_products_by_import_code(search_parameters, product_type)

    actual_endpoint: str = test_request.call_args.args[0]

    assert expected_endpoint == actual_endpoint
    assert products_found == test_data['expected']
