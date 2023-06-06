from typing import Dict, Optional, Any
from fabelcommon.access_token_key import AccessTokenKey
from fabelcommon.api_service import ApiService


class FeedApiService(ApiService):
    @property
    def _access_token_key(self) -> AccessTokenKey:
        return AccessTokenKey.ACCESS_TOKEN

    @property
    def _token_request_data(self) -> Dict:
        return {'grant_type': 'client_credentials'}

    @property
    def _token_request_auth(self) -> Optional[Any]:
        return self._client_id, self._client_secret

    def _create_authorization_header(self, access_token: str) -> Dict:
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

    BASE_URL: str = 'https://lydbokforlaget-feed.isysnet.no'

    def __init__(self, client_id: str, client_secret: str) -> None:
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            base_url=self.BASE_URL,
            auth_path='/token-server/oauth/token'
        )
