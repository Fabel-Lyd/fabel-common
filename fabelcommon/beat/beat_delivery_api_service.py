from typing import Optional, Dict, Any
from requests import Response
from fabelcommon.access_token_key import AccessTokenKey
from fabelcommon.api_service import ApiService
from fabelcommon.http.verbs import HttpVerb

HARDCODED_DELIVERY_BASE_URL = 'https://beat-delivery'


class BeatDeliveryApiService(ApiService):

    def __init__(
            self,
            username: str,
            password: str,
            base_url: str = HARDCODED_DELIVERY_BASE_URL,
            auth_path: str = '/oauth'
    ):
        super().__init__(
            client_id=username,
            client_secret=password,
            base_url=base_url,
            auth_path=auth_path,
        )

    @property
    def _access_token_key(self) -> AccessTokenKey:
        return AccessTokenKey.ACCESS_TOKEN

    @property
    def _token_request_data(self) -> Dict:
        return {}

    @property
    def _token_request_auth(self) -> Optional[Any]:
        return None

    def create_header(self, access_token: str) -> Dict:
        return {'Authorization': f'Bearer {access_token}'}

    def send_request(
            self,
            verb: HttpVerb,
            path: str,
            files=None,
            data: Optional[Dict] = None
    ) -> str:
        response: Response = self._send_request(
            verb=verb,
            path=path,
            data=data,
            files=files)

        return response.text
