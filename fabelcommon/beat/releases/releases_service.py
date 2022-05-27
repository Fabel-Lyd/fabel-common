from fabelcommon.beat.beat_service import BeatService
import requests
from fabelcommon.beat.releases.releases_translator import ReleasesTranslator


class ReleasesService(BeatService):

    def search(self, query: str):
        token = self.get_token()
        headers = self.create_headers(token)
        url = f'{BeatService.BASE_URL}/v2/releases?query="{query}"'
        response = requests.get(url, headers=headers, verify=True, allow_redirects=False)
        response.raise_for_status()

        releases = response.json()['releases']
        releases_translated = ReleasesTranslator.translate_releases(releases)

        return releases_translated
