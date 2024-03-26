from typing import Dict, Optional, Tuple, Any
import requests
from requests import Response
from fabelcommon.access_token import AccessToken
from fabelcommon.access_token_key import AccessTokenKey
from fabelcommon.api_service import ApiService
from fabelcommon.bokbasen.audiences.audience import BokbasenAudience
from fabelcommon.bokbasen.export_response import BokbasenExportResponse
from fabelcommon.bokbasen.export_response.download_response import DownloadResponse
from fabelcommon.bokbasen.export_response.order_response import OrderResponse
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
    def _token_request_data(self) -> Dict:
        return {
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'audience': f'{self._base_url}/{self._audience}/',
            'grant_type': 'client_credentials'
        }

    def __init__(
            self,
            client_id: str,
            client_secret: str,
            base_url: str,
            auth_path: str,
            audience: BokbasenAudience
    ) -> None:
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            base_url=base_url,
            auth_path=auth_path,
            audience=audience.value
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
            headers_to_add: Optional[Dict[str, str]] = None
    ) -> str:
        access_token: AccessToken = self._get_token()

        response: Response = self._send_request(
            verb=verb,
            path=url,
            token_value=access_token.access_token_value,
            headers_to_add=headers_to_add
        )
        return response.text

    def send_order_request(self, verb: HttpVerb, url: str, data: Any = None) -> OrderResponse:
        response: Response = self._send_request(
            verb=verb,
            path=url,
            data=data,
            headers_to_add={
                "Accept": "application/json",
                "Content-type": "application/json"
            }
        )
        return OrderResponse(location=response.headers['Location'])

    def send_download_url_request(self, url: str) -> DownloadResponse:
        params: Dict[str, str] = {
            "type": "audio/vnd.bokbasen.complete-public",
            "bitrate": "64"
        }
        response: Response = self._send_request(
            verb=HttpVerb.GET,
            path=url,
            data=None,
            params=params,
            headers_to_add={"Accept": "application/json"},
            allow_redirects=False)

        return DownloadResponse(response.headers['Location'])

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
            user_id=None
        )
        return access_token

    def send_export_request(self, url: str) -> BokbasenExportResponse:
        response: Response = self._send_request(HttpVerb.GET, url, None)
        return BokbasenExportResponse(content=response.text, cursor=response.headers['next'])
