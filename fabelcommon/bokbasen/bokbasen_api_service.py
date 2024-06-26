from abc import abstractmethod
from typing import Dict, Optional, Tuple, Any
import requests
from requests import Response
from fabelcommon.access_token import AccessToken
from fabelcommon.access_token_key import AccessTokenKey
from fabelcommon.api_service import ApiService
from fabelcommon.bokbasen.audiences.audience import BokbasenAudience
from fabelcommon.datetime.time_formats import TimeFormats
from fabelcommon.http.verbs import HttpVerb
from fabelcommon.utilities.response_extension import ResponseExtension


class BokbasenApiService(ApiService):

    @property
    def _access_token_key(self) -> AccessTokenKey:
        return AccessTokenKey.ACCESS_TOKEN

    @property
    def _token_request_auth(self) -> Optional[Tuple]:
        return None

    @property
    @abstractmethod
    def _token_request_data(self) -> Dict:
        pass

    def _create_token_request_data(self, audience: BokbasenAudience):
        return {
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'audience': f'{self._base_url}/{audience.value}/',
            'grant_type': 'client_credentials'
        }

    def __init__(
            self,
            client_id: str,
            client_secret: str,
            base_url: str,
            auth_path: str,

    ) -> None:
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            base_url=base_url,
            auth_path=auth_path
        )

    def _create_authorization_header(self, access_token: str) -> Dict:
        return {
            'Authorization': f'Bearer {access_token}',
            'Date': TimeFormats.get_date_time()
        }

    def send_request(
            self,
            verb: HttpVerb,
            url: str,
            data: Any = None,
            headers_to_add: Optional[Dict[str, str]] = None
    ) -> str:
        access_token: AccessToken = self._get_token()

        response: Response = self._send_request(
            verb=verb,
            path=url,
            data=data,
            token_value=access_token.access_token_value,
            headers_to_add=headers_to_add
        )
        return response.text

    def __create_token(self, token_request_data: Dict) -> AccessToken:
        response: Response = requests.post(
            url=self._auth_path,
            data=token_request_data,
            verify=True,
            allow_redirects=False
        )
        ResponseExtension.raise_for_error(response=response)

        token_data: Dict = response.json()

        access_token: AccessToken = AccessToken(
            access_token_value=token_data[self._access_token_key.value],
            expires_in=token_data.get('expires_in', token_data['expires_in']),
            user_id=None,
            refresh_token_value=None
        )
        return access_token
