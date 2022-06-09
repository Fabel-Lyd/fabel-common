from typing import Dict, List, Union
import requests
from requests import Response
from fabelcommon.http.verbs import HttpVerb


class FeedApiService:
    BASE_URL: str = 'https://lydbokforlaget-feed.isysnet.no'
    PRODUCT_EXPORT: str = '/export/export'
    PRODUCT_IMPORT: str = '/import/import'

    def __init__(self, client_id: str, client_secret: str) -> None:
        self._client_id: str = client_id
        self._client_secret: str = client_secret

    @staticmethod
    def __create_headers(access_token: str) -> Dict[str, str]:
        headers: Dict[str, str] = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        return headers

    def __get_token(self) -> str:
        url: str = f'{self.BASE_URL}/token-server/oauth/token'
        data: Dict[str, str] = {
            'grant_type': 'client_credentials',
        }

        response: Response = requests.post(
            url,
            data=data,
            verify=True,
            allow_redirects=False,
            auth=(self._client_id, self._client_secret)
        )
        response.raise_for_status()

        return response.json()['access_token']

    @staticmethod
    def build_url(action: str, parameters: str = '') -> str:
        url = f'{FeedApiService.BASE_URL}{action}'

        if action == FeedApiService.PRODUCT_EXPORT:
            url += f'?{parameters}'

        return url

    def send_request(self, verb: HttpVerb, url: str, data: Union[str, None] = None) -> Response:
        token: str = self.__get_token()
        headers: Dict[str, str] = self.__create_headers(token)

        response: Response = requests.request(verb.value, url, headers=headers, data=data)
        response.raise_for_status()

        return response
