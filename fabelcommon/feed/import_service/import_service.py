from typing import Dict, List, Union
import json
from time import sleep
from requests import Response
from fabelcommon.feed.api_service import FeedApiService
from fabelcommon.http.verbs import HttpVerb
from fabelcommon.feed.import_service.import_result import ImportResult
from fabelcommon.feed.import_service.import_result_item import ImportResultItem
from fabelcommon.feed.import_service.import_status import ImportStatus


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

    def await_import_finish(
            self,
            guid: str,
            query_interval_seconds: int,
            max_attempts: int
    ) -> ImportResult:

        for i in range(0, max_attempts):
            import_report: Dict = self.__get_import_report(guid)
            import_result: Union[ImportResult, None] = self.__parse_import_report(import_report)

            if import_result is None:
                sleep(query_interval_seconds)
                continue

            if import_result.status != ImportStatus.OK:
                raise Exception('Feed product import unsuccessful. Report: ' + json.dumps(import_report))
            return import_result

        raise Exception(
            f'Feed product import did not return finished status '
            f'(queried {max_attempts} times with {query_interval_seconds} s interval)'
        )

    def __get_import_report(self, guid: str) -> Dict:
        url: str = self.__build_url() + \
            f'/{guid}/status?includeNewProducts=true&includeUpdatedAndDeletedProducts=true'
        response: Response = self._send_request(HttpVerb.GET, url)
        return response.json()

    def __parse_import_report(self, import_report: Dict) -> Union[ImportResult, None]:
        if import_report['finishedTime'] is None:
            return None

        return ImportResult(
            status=self.__get_import_status(import_report['sumOfStatuses']),
            created_items=self.__get_created_items(import_report['report']['content'])
        )

    @staticmethod
    def __get_import_status(status_summary: Dict) -> ImportStatus:
        if status_summary['ERROR'] != 0:
            return ImportStatus.ERROR
        elif status_summary['WARNING'] != 0:
            return ImportStatus.WARNING

        return ImportStatus.OK

    @staticmethod
    def __get_created_items(content: Dict) -> List[ImportResultItem]:
        created_items: List[ImportResultItem] = []

        for item in content:
            created_items.append(
                ImportResultItem(
                    import_code=item['importCode'],
                    product_number=item['productNo'],
                    status=ImportStatus[item['status']],
                    messages=item['messages']
                )
            )
        return created_items

    def __build_url(self) -> str:
        return f'{self.BASE_URL}{self.PRODUCT_IMPORT}'

    def __send_request(self, url: str, data: str) -> str:
        response: Response = self._send_request(HttpVerb.POST, url, data)
        return response.text
