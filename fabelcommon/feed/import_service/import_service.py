import json
from typing import Dict, List
from requests import Response
from fabelcommon.feed.api_service import FeedApiService
from fabelcommon.http.verbs import HttpVerb


class FeedImport(FeedApiService):
    PRODUCT_IMPORT: str = '/import/import'

    def __init__(self, client_id: str, client_secret: str) -> None:
        super().__init__(client_id, client_secret)

    def create_or_update_products(self, formatted_products: List[Dict]) -> str:
        url: str = self.__build_url()
        payload: Dict = {
            "importSettings": {
                "importMode": "CREATE_OR_UPDATE"
            },
            "products": formatted_products
        }
        return self.__send_request(url, json.dumps(payload))

    def __build_url(self) -> str:
        return f'{self.BASE_URL}{self.PRODUCT_IMPORT}'

    def __send_request(self, url: str, data: str) -> str:
        response: Response = self._send_request(HttpVerb.POST, url, data)
        return response.text
