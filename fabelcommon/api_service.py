from abc import ABC
from typing import Dict, Union, Optional
from urllib.parse import urljoin
import requests
from requests import Response
from fabelcommon.http.verbs import HttpVerb


class ApiService(ABC):

    def __init__(
            self,
            client_id: str,
            client_secret: str,
            base_url: str,
            auth_path: str

    ) -> None:
        self._client_id: str = client_id
        self._client_secret: str = client_secret
        self._base_url: str = base_url
        self._auth_path: str = auth_path

    @staticmethod
    def __create_headers(access_token: str) -> Dict[str, str]:
        headers: Dict[str, str] = {
            'Authorization': f'Bearer {access_token}'
        }
        return headers

    def __get_token(self) -> str:
        data: Dict[str, str] = {
            'grant_type': 'client_credentials',
        }

        response = requests.post(
            url=urljoin(self._base_url, self._auth_path),
            data=data,
            verify=True,
            allow_redirects=False,
            auth=(self._client_id, self._client_secret))

        response.raise_for_status()

        return response.json()['access_token']

    def _send_request(
            self,
            verb: HttpVerb,
            path: str,
            # when data passed as Dict only top level properties are serialized
            data: Union[Dict, str, None] = None,
            files=None,
            headers_to_add: Optional[Dict[str, str]] = None
    ) -> Response:
        token: str = self.__get_token()
        headers: Dict[str, str] = self.__create_headers(token)
        if headers_to_add is not None:
            headers.update(headers_to_add)
        response: Response = requests.request(
            verb.value,
            url=urljoin(self._base_url, path),
            headers=headers,
            data=data,
            files=files)

        response.raise_for_status()

        return response
