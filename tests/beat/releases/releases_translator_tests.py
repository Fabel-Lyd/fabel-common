from fabelcommon.beat.releases.releases_translator import ReleasesTranslator
from fabelcommon.json.json_files import read_json_data


def test_releases_translator():
    release_translator = ReleasesTranslator()
    beat_releases = read_json_data('tests/beat/releases/data/9788203368110.json')

    result = release_translator.translate_releases(beat_releases['releases'])
    assert result[0]['isbn'] == '9788203368110'
    assert result[0]['title'] == 'Sjalusimannen og andre fortellinger'
