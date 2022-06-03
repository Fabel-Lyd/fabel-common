from typing import Dict, List
from fabelcommon.json.json_files import read_json_data
import pytest
from fabelcommon.feed.export.export import FeedExport
from fabelcommon.feed.api_service import FeedApiService


def test_persons_by_name_successful(mocker) -> None:
    test_data: Dict = read_json_data('tests/feed/export/data/persons_by_name_two.json')

    mocker.patch.object(
        FeedApiService,
        attribute='send_request',
        side_effect=test_data['response_data']
    )

    feed_api_service: FeedApiService = FeedApiService('fake_client_id', 'fake_client_secret')

    feed_export = FeedExport(feed_api_service)
    persons_found: List[Dict] = feed_export.persons_by_name(['a', 'b'])
    assert persons_found == test_data['expected']


def test_persons_by_name_duplicate_person(mocker) -> None:
    test_data: Dict = read_json_data('tests/feed/export/data/persons_by_name_duplicate.json')

    mocker.patch.object(
        FeedApiService,
        attribute='send_request',
        side_effect=test_data['response_data']
    )

    feed_api_service: FeedApiService = FeedApiService('fake_client_id', 'fake_client_secret')

    feed_export: FeedExport = FeedExport(feed_api_service)

    with pytest.raises(Exception) as exception_info:
        feed_export.persons_by_name(['a'])

    assert str(exception_info.value) == 'Multiple persons named "a" found in Feed'


def test_persons_by_name_not_found(mocker) -> None:
    test_data: Dict = read_json_data('tests/feed/export/data/persons_not_found.json')

    mocker.patch.object(
        FeedApiService,
        attribute='send_request',
        side_effect=test_data['response_data']
    )

    feed_api_service: FeedApiService = FeedApiService('fake_client_id', 'fake_client_secret')

    feed_export = FeedExport(feed_api_service)
    persons_found: List = feed_export.persons_by_name(['a'])
    assert persons_found == test_data['expected']
