import pytest
import json
from datetime import datetime
import pytz
from fabelcommon.feed.export_service import FeedExport
from fabelcommon.json.json_files import read_json_data, read_json_as_text


TEST_DATA_DIRECTORY: str = 'tests/feed/export_service/data/get_books_in_queries'


@pytest.mark.parametrize(
    'export_from_string',
    [
        '2024-08-28T07:00:00.000Z',
        ''
    ]
)
def test_get_books_in_queries(
        export_from_string: str,
        requests_mock
) -> None:

    expected_result = read_json_data(f'{TEST_DATA_DIRECTORY}/expected.json')

    requests_mock.post(
        'https://lydbokforlaget-feed.isysnet.no/token-server/oauth/token',
        text=json.dumps({'access_token': 'fake_access_token'})
    )

    for page in range(3):
        requests_mock.get(
            f'https://lydbokforlaget-feed.isysnet.no/export/structure/query/10'
            f'?exportFrom={export_from_string}'
            f'&page={page}',
            text=read_json_as_text(f'{TEST_DATA_DIRECTORY}/exported_product_{page + 1}.json')
        )
    feed_export: FeedExport = FeedExport('test_username', 'test_password')

    books_in_queries = feed_export.get_books_from_queries(
        query_url='https://lydbokforlaget-feed.isysnet.no/export/structure/query/10',
        export_from=datetime(year=2024, month=8, day=28, hour=7, minute=0, second=0, tzinfo=pytz.UTC) if export_from_string else None
    )

    assert books_in_queries == expected_result
