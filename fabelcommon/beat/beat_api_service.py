from abc import ABC
from typing import Any, Dict
from requests import Response
import requests

from fabelcommon.http.verbs import HttpVerb


class BeatApiService:

    BASE_URL = 'https://api.fabel.no'

    def __init__(self, client_id, client_secret):
        self._client_id = client_id
        self._client_secret = client_secret

    @staticmethod
    def create_headers(access_token):
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        return headers

    def get_token(self) -> str:

        url = f'{BeatApiService.BASE_URL}/v2/oauth2/token'
        data = {
            'grant_type': 'client_credentials',
            'client_id': self._client_id,
            'client_secret': self._client_secret,
        }

        response = requests.post(url, data=data, verify=True, allow_redirects=False)
        response.raise_for_status()

        response_data = response.json()
        return response_data['access_token']

    def send_request(self, verb: HttpVerb, url: str, data: Any) -> str:
        token: str = self.get_token()
        headers: Dict[str, str] = self.create_headers(token)

        response: Response = requests.request(verb.value, url, headers=headers, data=data)
        response.raise_for_status()

        return response.text
