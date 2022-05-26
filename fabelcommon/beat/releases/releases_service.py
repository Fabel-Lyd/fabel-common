from fabelcommon.beat.beat_service import BeatService
import requests


class ReleasesService(BeatService):

    def search(self, query: str):
        token = self.get_token()
        headers = self.create_headers(token)
        url = f'{BeatService.BASE_URL}/v2/releases?query="{query}"'
        response = requests.get(url, headers=headers, verify=True, allow_redirects=False)
        response.raise_for_status()

        return response.json()['releases']
