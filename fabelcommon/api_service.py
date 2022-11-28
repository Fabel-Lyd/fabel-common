from abc import ABC
from typing import Dict, Union, Optional, Any
from urllib.parse import urljoin
import requests
from requests import Response
from fabelcommon.access_token_key import AccessTokenKey
from fabelcommon.http.verbs import HttpVerb


class ApiService(ABC):

    def __init__(
            self,
            client_id: str,
            client_secret: str,
            base_url: str,
            auth_path: str,

    ) -> None:
        self._client_id: str = client_id
        self._client_secret: str = client_secret
        self._base_url: str = base_url
        self._auth_path: str = auth_path

    @property
    def _access_token_key(self) -> AccessTokenKey:
        raise NotImplementedError('Implement by which key to retrieve access token.')

    @property
    def _token_request_data(self) -> Dict:
        raise NotImplementedError(
            'Implement generation of the parameter "data" for requests.post() used to get access token.')

    @property
    def _token_request_auth(self) -> Optional[Any]:
        raise NotImplementedError(
            'Implement generation of the parameter "auth" for requests.post() to get access token.')

    def create_header(self, access_token: str) -> Dict:
        raise NotImplementedError('Implement creation of header.')

    def __get_token(self) -> str:

        response = requests.post(
            url=urljoin(self._base_url, self._auth_path),
            data=self._token_request_data,
            verify=True,
            allow_redirects=False,
            auth=self._token_request_auth
        )

        response.raise_for_status()

        return response.json()[self._access_token_key.value]

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

        headers: Dict[str, str] = self.create_header(token)
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
