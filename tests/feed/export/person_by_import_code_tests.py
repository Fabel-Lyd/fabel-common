from fabelcommon.feed.api_service import FeedApiService
from fabelcommon.feed.export.export import FeedExport
from fabelcommon.json.json_files import read_json_data


def test_persons_by_import_code_successful(mocker):
    test_data = read_json_data('tests/feed/export/data/persons_by_import_code_two.json')

    mocker.patch.object(
        FeedApiService,
        attribute='send_request',
        side_effect=test_data['response_data']
    )

    feed_api_service = FeedApiService('fake_client_id', 'fake_client_secret')

    feed_export = FeedExport(feed_api_service)
    persons_found = feed_export.persons_by_import_code(['99991', '99992'])

    assert persons_found == test_data['expected']


def test_persons_by_import_code_not_found(mocker):
    test_data = read_json_data('tests/feed/export/data/persons_not_found.json')

    mocker.patch.object(
        FeedApiService,
        attribute='send_request',
        side_effect=test_data['response_data']
    )

    feed_api_service = FeedApiService('fake_client_id', 'fake_client_secret')

    feed_export = FeedExport(feed_api_service)
    persons_found = feed_export.persons_by_import_code(['99991'])

    assert persons_found == test_data['expected']
