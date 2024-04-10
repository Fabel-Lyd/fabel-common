from typing import Dict
from requests import Response
from fabelcommon.bokbasen.audiences.audience import BokbasenAudience
from fabelcommon.bokbasen.bokbasen_api_service import BokbasenApiService
from fabelcommon.bokbasen.export_response import BokbasenExportResponse
from fabelcommon.http.verbs import HttpVerb


class BokbasenMetadataApiService(BokbasenApiService):

    @property
    def _token_request_data(self) -> Dict:
        return self._create_token_request_data(BokbasenAudience.METADATA)

    def send_export_request(self, url: str) -> BokbasenExportResponse:
        response: Response = self._send_request(HttpVerb.GET, url, None)
        return BokbasenExportResponse(content=response.text, cursor=response.headers['next'])
