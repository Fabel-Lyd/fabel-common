from typing import Dict, Any
from requests import Response
from fabelcommon.bokbasen.audiences.audience import BokbasenAudience
from fabelcommon.bokbasen.bokbasen_api_service import BokbasenApiService
from fabelcommon.bokbasen.export_response.download_response import DownloadResponse
from fabelcommon.bokbasen.export_response.order_response import OrderResponse
from fabelcommon.http.verbs import HttpVerb


class BokbasenDdsApiService(BokbasenApiService):

    @property
    def _token_request_data(self) -> Dict:
        return self._create_token_request_data(BokbasenAudience.DDS)

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
