from typing import Optional
import pytest
import json
from rest_framework import status
from fabelcommon.json.json_files import read_json_data
from fabelcommon.feed.export_service import FeedExport, ProductType


TEST_DATA_DIRECTORY: str = 'tests/feed/export_service/data/get_import_code_by_product_number'


@pytest.mark.parametrize(
    'export_result_filename, expected_return_value',
    [
        ('exported_book.json', '32781'),
        ('empty.json', None)
    ]
)
def test_get_import_code_by_product_number_success(
        export_result_filename: str,
        expected_return_value: Optional[str],
        requests_mock
) -> None:

    requests_mock.post(
        'https://lydbokforlaget-feed.isysnet.no/token-server/oauth/token',
        text=json.dumps({'access_token': 'test_access_token'})
    )

    requests_mock.post(
        url='https://lydbokforlaget-feed.isysnet.no/export/export?'
            'changesOnly=false&productTypeImportCodes=ERP&productNo=9788234001635&productHeadOnly=true',
        status_code=status.HTTP_200_OK,
        text=json.dumps(read_json_data(f'{TEST_DATA_DIRECTORY}/{export_result_filename}'))
    )

    feed_export: FeedExport = FeedExport('test_username', 'test_password')
    actual_import_code: Optional[str] = feed_export.get_import_code_by_product_number(ProductType.BOOK, '9788234001635')

    assert actual_import_code == expected_return_value


def test_get_import_code_by_product_number_failure(requests_mock) -> None:
    requests_mock.post(
        'https://lydbokforlaget-feed.isysnet.no/token-server/oauth/token',
        text=json.dumps({'access_token': 'test_access_token'})
    )

    requests_mock.post(
        url='https://lydbokforlaget-feed.isysnet.no/export/export?'
            'changesOnly=false&productTypeImportCodes=ERP&productNo=9788234001635&productHeadOnly=true',
        status_code=status.HTTP_200_OK,
        text=json.dumps(read_json_data(f'{TEST_DATA_DIRECTORY}/exported_books.json'))
    )

    feed_export: FeedExport = FeedExport('test_username', 'test_password')

    with pytest.raises(Exception) as exception:
        feed_export.get_import_code_by_product_number(ProductType.BOOK, '9788234001635')

    assert str(exception.value) == 'Provided product number belongs to more than one product'
