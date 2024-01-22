from typing import Dict
import requests
from fabelcommon.access_token import AccessToken
from fabelcommon.access_token_key import AccessTokenKey
from fabelcommon.api_service import ApiService
from fabelcommon.datetime.time_formats import TimeFormats
from fabelcommon.utilities.response_extension import ResponseExtension


class BokbasenMetadataApiService(ApiService):

    @property
    def _access_token_key(self) -> AccessTokenKey:
        return AccessTokenKey.ACCESS_TOKEN

    @property
    def _token_request_data(self) -> Dict:
        return {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "audience": "https://api.bokbasen.io/metadata/",
            "grant_type": "client_credentials"
        }

    def __init__(
            self,
            client_id: str,
            client_secret: str,
            base_url: str,
            auth_path: str
    ):
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

    def _get_token_non_cached(self, token_request_data: Dict) -> AccessToken:
        return self.__create_token(token_request_data)

    def __create_token(self, token_request_data: Dict) -> AccessToken:
        response = requests.post(
            url=self._auth_path,
            data=token_request_data,
            verify=True,
            allow_redirects=False
        )
        ResponseExtension.raise_for_error(response=response)

        token_data = response.json()

        access_token: AccessToken = AccessToken(
            access_token_value=token_data[self._access_token_key.value],
            expires_in=token_data.get('expires_in', token_data['expires_in']),
            user_id=None
        )
        return access_token
