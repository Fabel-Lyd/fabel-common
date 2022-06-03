from fabelcommon.json.json_files import read_json_data
import pytest
from fabelcommon.feed.export.export import FeedExport
from fabelcommon.feed.api_service import FeedApiService


def test_person_by_name_successful(mocker):
    test_data = read_json_data('tests/feed/export/data/person_by_name_two.json')

    mocker.patch.object(
        FeedApiService,
        attribute='send_request',
        side_effect=test_data['response_data']
    )

    feed_api_service = FeedApiService('fake_client_id', 'fake_client_secret')

    feed_export = FeedExport(feed_api_service)
    persons_found = feed_export.person_by_name(['a', 'b'])
    assert persons_found == test_data['expected']


def test_person_by_name_duplicate_person(mocker):
    test_data = read_json_data('tests/feed/export/data/person_by_name_duplicate.json')

    mocker.patch.object(
        FeedApiService,
        attribute='send_request',
        side_effect=test_data['response_data']
    )

    feed_api_service = FeedApiService('fake_client_id', 'fake_client_secret')

    feed_export = FeedExport(feed_api_service)

    with pytest.raises(Exception) as exception_info:
        feed_export.person_by_name(['a'])

    assert str(exception_info.value) == 'Multiple persons named "a" found in Feed'


def test_person_by_name_not_found(mocker):
    test_data = read_json_data('tests/feed/export/data/person_not_found.json')

    mocker.patch.object(
        FeedApiService,
        attribute='send_request',
        side_effect=test_data['response_data']
    )

    feed_api_service = FeedApiService('fake_client_id', 'fake_client_secret')

    feed_export = FeedExport(feed_api_service)
    person_found = feed_export.person_by_name(['a'])
    assert person_found == test_data['expected']
