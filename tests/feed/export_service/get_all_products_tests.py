from typing import Dict, List, Optional, Generator
import pytest
import json
from datetime import datetime
import pytz
from fabelcommon.json.json_files import read_json_data, read_json_as_text
from fabelcommon.feed.export_service import FeedExport, ProductType


TEST_DATA_DIRECTORY: str = 'tests/feed/export_service/data/get_all_products'
PAGE_SIZE: int = 100


@pytest.mark.parametrize(
    'export_from',
    (
        '2024-01-12T20:00:00.000Z',
        None
    )
)
def test_get_all_products(export_from: Optional[str], requests_mock) -> None:
    expected_result: List[Dict] = read_json_data(f'{TEST_DATA_DIRECTORY}/expected.json')

    requests_mock.post(
        'https://lydbokforlaget-feed.isysnet.no/token-server/oauth/token',
        text=json.dumps({'access_token': 'test_token'})
    )

    for page in range(3):
        requests_mock.post(
            f'https://lydbokforlaget-feed.isysnet.no/export/export?'
            f'changesOnly=false&'
            f'productTypeImportCodes=person'
            f'&size={PAGE_SIZE}'
            f'{"&exportFrom=" + export_from if export_from else ""}'
            f'&page={page}',
            text=read_json_as_text(f'{TEST_DATA_DIRECTORY}/exported_product_{page + 1}.json')
        )

    feed_export: FeedExport = FeedExport('test_username', 'test_password')
    actual_result: List[Dict] = feed_export.get_all_products(ProductType.PERSON, datetime(year=2024, month=1, day=12, hour=20, minute=0, second=0, tzinfo=pytz.UTC) if export_from else None)

    assert expected_result == actual_result


def test_get_all_products_pageable(requests_mock) -> None:

    requests_mock.post(
        'https://lydbokforlaget-feed.isysnet.no/token-server/oauth/token',
        text=json.dumps({'access_token': 'test_token'})
    )

    for page in range(3):
        requests_mock.post(
            f'https://lydbokforlaget-feed.isysnet.no/export/export?'
            f'changesOnly=false&'
            f'productTypeImportCodes=person'
            f'&size={PAGE_SIZE}'
            f'&page={page}',
            text=read_json_as_text(f'{TEST_DATA_DIRECTORY}/exported_product_{page + 1}.json')
        )

    feed_export: FeedExport = FeedExport('test_username', 'test_password')

    generator: Generator[List[Dict], None, None] = feed_export.get_all_products_pageable(
        product_type=ProductType.PERSON
    )

    result: List[Dict] = []
    for items in generator:
        result.extend(items)

    assert len(result) == 2
