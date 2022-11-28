from typing import Dict, List, Optional
import json
from requests import Response
from fabelcommon.feed.api_service import FeedApiService
from fabelcommon.http.verbs import HttpVerb
from fabelcommon.feed.import_service.import_mode import ImportMode
from fabelcommon.feed.import_service.import_result import ImportResult


class FeedImport(FeedApiService):
    PRODUCT_IMPORT: str = '/import/import'

    def __init__(self, client_id: str, client_secret: str) -> None:
        super().__init__(client_id, client_secret)

    def import_products(
            self,
            formatted_products: List[Dict],
            import_mode: ImportMode
    ) -> str:

        if len(formatted_products) == 0:
            raise Exception('List of products to be imported is empty')

        url: str = self.__build_url()
        payload: Dict = {
            "importSettings": {
                "importMode": import_mode.value
            },
            "products": formatted_products
        }
        return self.__send_request(url, json.dumps(payload))

    def get_import_result(self, guid: str) -> Optional[ImportResult]:
        url: str = self.__build_url() + \
            f'/{guid}/status?includeNewProducts=true&includeUpdatedAndDeletedProducts=true'

        import_report: Dict = self._send_request(HttpVerb.GET, url).json()

        if import_report['finishedTime'] is None:
            return None
        return ImportResult(import_report)

    def __build_url(self) -> str:
        return f'{self.BASE_URL}{self.PRODUCT_IMPORT}'

    def __send_request(self, url: str, data: str) -> str:
        response: Response = self._send_request(HttpVerb.POST, url, data)
        return response.text
