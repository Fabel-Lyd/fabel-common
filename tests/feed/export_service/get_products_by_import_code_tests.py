from typing import Dict, List
import pytest
from fabelcommon.feed.export_service import FeedExport
from fabelcommon.feed.export_service.expot_attribute import ExportAttribute
from fabelcommon.json.json_files import read_json_data
from fabelcommon.feed.export_service import ProductType

TEST_DATA_DIRECTORY: str = 'tests/feed/export_service/data/get_products_by_import_code'


@pytest.mark.parametrize(
    'data_file_name, product_types, search_parameters, expected_endpoints',
    [
        (
            'two_batches.json',
            [ProductType.PERSON],
            ['99991', '99992', '99993', '99994'],
            [
                'https://lydbokforlaget-feed.isysnet.no/export/export?changesOnly=false&productTypeImportCodes=person&importCodes=99991%2C99992&size=2',
                'https://lydbokforlaget-feed.isysnet.no/export/export?changesOnly=false&productTypeImportCodes=person&importCodes=99993%2C99994&size=2'
            ]
        ),
        (
            'not_found.json',
            [ProductType.PERSON, ProductType.SERIES, ProductType.PERSON],
            ['99991'],
            [
                'https://lydbokforlaget-feed.isysnet.no/export/export?changesOnly=false&productTypeImportCodes=person%2Cserie&importCodes=99991&size=2'
            ]
        )
    ])
def test_get_products_by_import_code(
        data_file_name: str,
        product_types: List[ProductType],
        search_parameters: List[str],
        expected_endpoints: List[str],
        mocker
) -> None:

    test_data: Dict = read_json_data(f'{TEST_DATA_DIRECTORY}/{data_file_name}')

    mocked_send_request_call = mocker.patch.object(
        FeedExport,
        attribute='_FeedExport__send_product_export_request',
        side_effect=test_data['response_data']
    )

    feed_export: FeedExport = FeedExport('fake_client_id', 'fake_client_secret')
    products_found: List[Dict] = feed_export.get_products_by_attribute(
        export_by_attribute=ExportAttribute.IMPORT_CODES,
        attribute_values=search_parameters,
        product_types=product_types,
        batch_size=2)

    actual_endpoints: List[str] = [call.args[0] for call in mocked_send_request_call.call_args_list]

    assert actual_endpoints == expected_endpoints
    assert products_found == test_data['expected']
