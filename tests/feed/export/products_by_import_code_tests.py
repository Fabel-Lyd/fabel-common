from typing import Dict, List
import pytest
from fabelcommon.feed.api_service import FeedApiService
from fabelcommon.feed.export.export import FeedExport
from fabelcommon.json.json_files import read_json_data
from fabelcommon.feed.export.export import ProductType


@pytest.mark.parametrize(
    'product_type, search_parameters, data_file_name',
    [
        (ProductType.PERSON, ['99991', '99992'], 'tests/feed/export/data/persons_by_import_code.json'),
        (ProductType.PERSON, ['99991'], 'tests/feed/export/data/product_not_found.json'),
    ])
def test_products_by_import_code(
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

    feed_export: FeedExport = FeedExport(feed_api_service)
    persons_found: List[Dict] = feed_export.products_by_import_code(search_parameters, product_type)

    assert persons_found == test_data['expected']
