from typing import Dict, List
import pytest
from fabelcommon.feed.export_service import FeedExport
from fabelcommon.feed.export_service.expot_attribute import ExportAttribute
from fabelcommon.json.json_files import read_json_data
from fabelcommon.feed.export_service import ProductType

TEST_DATA_DIRECTORY: str = 'tests/feed/export_service/data/get_products_by_attribute'


@pytest.mark.parametrize(
    'data_file_name, product_types, export_by_attribute, search_parameters, batch_size, product_head_only, expected_endpoints',
    [
        (
            'two_batches.json',
            [ProductType.PERSON],
            ExportAttribute.IMPORT_CODES,
            ['99991', '99992', '99993', '99994'],
            2,
            False,
            [
                'https://lydbokforlaget-feed.isysnet.no/export/export?changesOnly=false&productTypeImportCodes=person&importCodes=99991%2C99992&size=2&productHeadOnly=false',
                'https://lydbokforlaget-feed.isysnet.no/export/export?changesOnly=false&productTypeImportCodes=person&importCodes=99993%2C99994&size=2&productHeadOnly=false'
            ]
        ),
        (
            'not_found.json',
            [ProductType.PERSON, ProductType.SERIES, ProductType.PERSON],
            ExportAttribute.IMPORT_CODES,
            ['99991'],
            2,
            False,
            [
                'https://lydbokforlaget-feed.isysnet.no/export/export?changesOnly=false&productTypeImportCodes=person%2Cserie&importCodes=99991&size=2&productHeadOnly=false'
            ]
        ),
        (
            'single_batch.json',
            [ProductType.BOOK],
            ExportAttribute.PRODUCT_NUMBERS,
            ['9788202420826,9788234001635'],
            10,
            True,
            [
                'https://lydbokforlaget-feed.isysnet.no/export/export?changesOnly=false&productTypeImportCodes=ERP&productNo=9788202420826%2C9788234001635&size=10&productHeadOnly=true'
            ]
        )
    ])
def test_get_products_by_attribute(
        data_file_name: str,
        product_types: List[ProductType],
        export_by_attribute: ExportAttribute,
        search_parameters: List[str],
        product_head_only: bool,
        batch_size: int,
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
        export_by_attribute=export_by_attribute,
        attribute_values=search_parameters,
        product_types=product_types,
        batch_size=batch_size,
        product_head_only=product_head_only
    )

    actual_endpoints: List[str] = [call.args[0] for call in mocked_send_request_call.call_args_list]

    assert actual_endpoints == expected_endpoints
    assert products_found == test_data['expected']
