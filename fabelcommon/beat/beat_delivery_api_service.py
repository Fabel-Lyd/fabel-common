from typing import Optional, Dict
from requests import Response
from fabelcommon.api_service import ApiService
from fabelcommon.http.verbs import HttpVerb


class BeatDeliveryApiService(ApiService):

    def __init__(self, username, password, base_url: str, auth_path: str):
        super().__init__(username, password, base_url, auth_path)

    def send_request(
            self,
            verb: HttpVerb,
            path: str,
            files=None,
            data: Optional[Dict] = None
    ) -> str:
        response: Response = self._send_request(
            verb,
            path=path,
            data=data,
            files=files)

        return response.text
