from typing import Dict
from fabelcommon.bokbasen.audiences.audience import BokbasenAudience
from fabelcommon.bokbasen.bokbasen_api_service import BokbasenApiService


class BokbasenBokskyaApiService(BokbasenApiService):

    @property
    def _token_request_data(self) -> Dict:
        return self._create_token_request_data(BokbasenAudience.BOKSKYA)
