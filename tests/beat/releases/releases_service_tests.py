import pytest
from fabelcommon.beat.releases.releases_service import ReleasesService
from rest_framework import status
from fabelcommon.json.json_files import read_json_as_text


@pytest.fixture
def patch_get_token(mocker):
    mocker.patch.object(ReleasesService, 'get_token', return_value='dummy_token')


def test_releases_search_success(patch_get_token, requests_mock):

    search_phrase = 'haha'
    requests_mock.get(
        f'https://api.fabel.no/v2/releases?query="{search_phrase}"',
        status_code=status.HTTP_200_OK,
        text=read_json_as_text('tests/beat/releases/data/9788203368110.json'))

    releases = ReleasesService('dummy_client_id', 'dummy_secret')
    result = releases.search(search_phrase)
    assert len(result) == 1, 'Should be found single release'
    assert result[0] == {'isbn': '9788203368110', 'title': 'Sjalusimannen og andre fortellinger'}
