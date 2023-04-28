from typing import Dict, List, Union, Optional
import json
from time import sleep
from requests import Response
from fabelcommon.feed.feed_api_service import FeedApiService
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
            f'/{guid}/status?includeNewProducts=true&includeUpdatedAndDeletedProducts=true&page='

        import_report: Dict = self._send_request(HttpVerb.GET, url + '0').json()

        if import_report['finishedTime'] is None:
            return None

        page_count: int = import_report['report']['totalPages']
        import_reports: List[Dict] = [import_report]

        for page in range(1, page_count):
            import_report = self._send_request(HttpVerb.GET, url + str(page)).json()
            import_reports.append(import_report)

        return ImportResult(import_reports)

    def await_import_finish(
            self,
            guid: str,
            query_interval_seconds: int,
            max_attempts: int
    ) -> ImportResult:

        for i in range(0, max_attempts):
            import_result: Union[ImportResult, None] = self.get_import_result(guid)

            if import_result is None:
                sleep(query_interval_seconds)
                continue

            return import_result

        raise Exception(
            f'Feed product import did not return finished status '
            f'(queried {max_attempts} times with {query_interval_seconds} s interval)'
        )

    def __build_url(self) -> str:
        return f'{self.BASE_URL}{self.PRODUCT_IMPORT}'

    def __send_request(self, url: str, data: str) -> str:
        response: Response = self._send_request(HttpVerb.POST, url, data)
        return response.text
