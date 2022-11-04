import json
from typing import Dict, Optional
import requests
from requests import Response
from rest_framework import status

from fabelcommon.http.verbs import HttpVerb


class BeatDeliveryService:

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def get_beat_access_token(self) -> Dict:
        data: Dict[str, str] = {
            'username': self.username,
            'password': self.password
        }

        response = requests.post(
            url='https://ds.test.beat.delivery/v1/auth',
            data=data)

        if response.status_code == status.HTTP_200_OK:
            response = json.loads(response.text)
            return response['access_token']

        raise Exception(f'Failed to retrieve token: status code {response.status_code}')

    @staticmethod
    def create_header(access_token) -> Dict:
        headers: Dict[str, str] = {
            'Authorization': f'Bearer {access_token}'
        }

        return headers

    def send_request(
            self,
            verb: HttpVerb,
            url: str,
            files=None,
            data: Optional[Dict] = None, ):
        access_token = self.get_beat_access_token()
        headers = self.create_header(access_token)

        response: Response = requests.request(
            verb.value,
            url=url,
            headers=headers,
            data=data,
            files=files)
        response.raise_for_status()

        return response.content
