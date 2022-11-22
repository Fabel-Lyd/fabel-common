import json
from typing import Dict, Optional
from requests import Response
from fabelcommon.api_service import ApiService
from fabelcommon.http.verbs import HttpVerb

HARDCODED_BASE_URL = 'https://api.fabel.no'


class BeatApiService(ApiService):

    BASE_URL = HARDCODED_BASE_URL

    def __init__(
            self,
            client_id,
            client_secret,
            base_url=HARDCODED_BASE_URL,
            auth_path='/v2/oauth2/token'
    ):
        super().__init__(
            client_id,
            client_secret,
            base_url,
            auth_path

        )

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
