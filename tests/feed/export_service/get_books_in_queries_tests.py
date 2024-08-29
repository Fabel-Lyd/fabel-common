import json
from fabelcommon.feed.export_service import FeedExport
from fabelcommon.json.json_files import read_json_data


def test_get_books_in_queries(requests_mock) -> None:
    test_data: str = read_json_data('tests/feed/export_service/data/get_books_in_queries/9788203367939.json')

    requests_mock.post(
        'https://lydbokforlaget-feed.isysnet.no/token-server/oauth/token',
        text=json.dumps({'access_token': 'fake_access_token'})
    )

    requests_mock.get(
        'https://lydbokforlaget-feed.isysnet.no/export/structure/query/10?exportFrom=2024-08-28T07:00:00.00Z',
        text=json.dumps(test_data)
    )

    feed_export: FeedExport = FeedExport('test_username', 'test_password')

    books_in_queries = feed_export.get_books_from_queries(
        query_url='https://lydbokforlaget-feed.isysnet.no/export/structure/query/10',
        export_from='2024-08-28T07:00:00.00Z')

    assert books_in_queries == test_data
