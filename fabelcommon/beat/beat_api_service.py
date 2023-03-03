import json
from typing import Dict, Optional, Tuple
from requests import Response
from fabelcommon.access_token import AccessToken
from fabelcommon.access_token_key import AccessTokenKey
from fabelcommon.api_service import ApiService
from fabelcommon.http.verbs import HttpVerb


class BeatApiService(ApiService):

    @property
    def _access_token_key(self) -> AccessTokenKey:
        return AccessTokenKey.ACCESS_TOKEN

    @property
    def _token_request_auth(self) -> Optional[Tuple]:
        return None

    @property
    def _token_request_data(self) -> Dict:
        return {
            'grant_type': 'client_credentials',
            'client_id': self._client_id,
            'client_secret': self._client_secret,
        }

    def __init__(
            self,
            client_id,
            client_secret,
            base_url,
            auth_path='/v2/oauth2/token'
    ):
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            base_url=base_url,
            auth_path=auth_path,
        )

    def _create_authorization_header(self, access_token: str):
        return {'Authorization': f'Bearer {access_token}'}

    def send_request(
            self,
            verb: HttpVerb,
            url: str,
            data: Optional[Dict] = None,
            headers_to_add: Optional[Dict[str, str]] = None
    ) -> str:
        headers = {} if headers_to_add is None else headers_to_add
        headers.update({'Content-Type': 'application/json'})

        response: Response = self._send_request(
            verb,
            path=url,
            headers_to_add=headers,
            data=json.dumps(data)
        )

        response.raise_for_status()

        return response.text

    def send_request_with_token(
            self,
            verb: HttpVerb,
            url: str,
            token_value: str,
            data: Optional[Dict] = None
    ) -> str:
        response: Response = self._send_request(
            verb,
            path=url,
            headers_to_add=None,
            data=json.dumps(data),
            token_value=token_value
        )

        return response.text

    def get_password_flow_token(self, user_name: str, password: str) -> AccessToken:
        token_request_data = {
            'grant_type': 'password',
            'username': user_name,
            'password': password,
            'client_id': self._client_id,
            'client_secret': self._client_secret
        }
        return self._get_token_non_cached(token_request_data)
