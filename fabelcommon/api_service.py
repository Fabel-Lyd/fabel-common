from abc import ABC
from typing import Dict, Union, Optional, Any
from urllib.parse import urljoin
import requests
from requests import Response
from fabelcommon.access_token import AccessToken
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
        self.__access_token: Optional[AccessToken] = None

    @property
    def _access_token_key(self) -> AccessTokenKey:
        raise NotImplementedError(
            'Implement which key to use to retrieve the access token from authentication requests.')

    @property
    def _token_request_data(self) -> Dict:
        raise NotImplementedError(
            'Implement generation of the parameter "data" for requests.post() used to get access token.')

    @property
    def _token_request_auth(self) -> Optional[Any]:
        raise NotImplementedError(
            'Implement generation of the parameter "auth" for requests.post() to get access token.')

    def _create_authorization_header(self, access_token: str) -> Dict:
        raise NotImplementedError('Implement creation of header.')

    def _get_token(self) -> AccessToken:
        if self.__access_token is not None and self.__access_token.is_valid:
            return self.__access_token

        return self.__get_token(self._token_request_data)

    def _get_token_non_cached(self, token_request_data: Dict) -> AccessToken:
        return self.__get_token(token_request_data)

    def __get_token(self, token_request_data: Dict) -> AccessToken:
        response = requests.post(
            url=urljoin(self._base_url, self._auth_path),
            data=token_request_data,
            verify=True,
            allow_redirects=False,
            auth=self._token_request_auth
        )
        response.raise_for_status()

        token_data = response.json()

        self.__access_token = AccessToken(
            access_token_value=token_data[self._access_token_key.value],
            expires_in=token_data.get('expires_in', 600),
            user_id=token_data.get('user_id')
        )
        return self.__access_token

    def _send_request(
            self,
            verb: HttpVerb,
            path: str,
            # when data passed as Dict only top level properties are serialized
            data: Union[Dict, str, None] = None,
            files=None,
            headers_to_add: Optional[Dict[str, str]] = None,
            token_value: Optional[str] = None
    ) -> Response:

        if token_value is None:
            token_value = self._get_token().access_token_value

        headers: Dict[str, str] = self._create_authorization_header(token_value)
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
