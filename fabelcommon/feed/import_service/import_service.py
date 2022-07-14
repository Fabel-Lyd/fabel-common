from typing import Dict, List, Union
import json
from time import sleep
from requests import Response
from fabelcommon.feed.api_service import FeedApiService
from fabelcommon.http.verbs import HttpVerb
from fabelcommon.feed.import_service.import_result import ImportResult
from fabelcommon.feed.import_service.import_status import ImportStatus


class FeedImport(FeedApiService):
    PRODUCT_IMPORT: str = '/import/import'

    def __init__(self, client_id: str, client_secret: str) -> None:
        super().__init__(client_id, client_secret)

    def create_or_update_products(
            self,
            formatted_products: List[Dict],
            query_interval_seconds: int,
            max_attempts: int
    ) -> ImportResult:

        if len(formatted_products) == 0:
            raise Exception('List of products to be imported is empty')

        status_guid: str = self.__send_payload(formatted_products)
        return self.__await_import_finish(
            guid=status_guid,
            query_interval_seconds=query_interval_seconds,
            max_attempts=max_attempts
        )

    def __send_payload(self, formatted_products: List[Dict]) -> str:
        url: str = self.__build_url()
        payload: Dict = {
            "importSettings": {
                "importMode": "CREATE_OR_UPDATE"
            },
            "products": formatted_products
        }
        return self.__send_request(url, json.dumps(payload))

    def __await_import_finish(
            self,
            guid: str,
            query_interval_seconds: int,
            max_attempts: int
    ) -> ImportResult:

        for i in range(0, max_attempts):
            import_result: Union[ImportResult, None] = self.__get_import_report(guid)

            if import_result is None:
                sleep(query_interval_seconds)
                continue

            if import_result.status != ImportStatus.OK:
                raise Exception('Feed product import unsuccessful. Report: ' + json.dumps(import_result.report))
            return import_result

        raise Exception(
            f'Feed product import did not return finished status '
            f'(queried {max_attempts} times with {query_interval_seconds} s interval)'
        )

    def __get_import_report(self, guid: str) -> Union[ImportResult, None]:
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
