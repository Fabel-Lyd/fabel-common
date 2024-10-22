from typing import Dict, List, Optional
import json
from time import sleep
from requests import Response
from fabelcommon.feed.feed_api_service import FeedApiService
from fabelcommon.http.verbs import HttpVerb
from fabelcommon.feed.import_service.import_mode import ImportMode
from fabelcommon.feed.import_service.import_type import ImportType
from fabelcommon.feed.import_service.import_result import ImportResult
from fabelcommon.feed.import_service.media_import_result import MediaImportResult
from fabelcommon.feed.import_service.product_identifier import ProductIdentifier
from fabelcommon.feed.import_service.structure_node import StructureNode


class FeedImport(FeedApiService):

    def __init__(self, client_id: str, client_secret: str) -> None:
        super().__init__(client_id, client_secret)

    def import_products(
            self,
            formatted_products: List[Dict],
            import_mode: ImportMode
    ) -> str:

        if len(formatted_products) == 0:
            raise Exception('List of products to be imported is empty')

        url: str = self.__build_url(ImportType.PRODUCT)
        payload: Dict = {
            "importSettings": {
                "importMode": import_mode.value
            },
            "products": formatted_products
        }
        return self.__send_request(url, json.dumps(payload))

    def add_product_to_structure(
            self,
            product_identifier: ProductIdentifier,
            structure_node: StructureNode
    ) -> None:

        url: str = f'{self.BASE_URL}/import/structure/{structure_node.structure_import_code}/node/{structure_node.node_import_code}/product'
        data: List[Dict] = [{
            "productNo": product_identifier.product_number,
            "importCode": product_identifier.import_code
        }]

        self.__send_request(url, json.dumps(data))

    def delete_product_from_structure(
            self,
            product_identifier: List[ProductIdentifier],
            structure_node: StructureNode
    ) -> None:
        url: str = f'{self.BASE_URL}/import/structure/{structure_node.structure_import_code}/node/{structure_node.node_import_code}/product'
        data: List[Dict] = [{"productNo": identifier.product_number} for identifier in product_identifier]

        self._send_request(HttpVerb.DELETE, url, json.dumps(data))

    def import_data_register_items(self, data_register_value: str, data: Dict) -> None:

        url: str = f'{self.BASE_URL}/import/basedata/dataRegisters/{data_register_value}'

        import_items: Response = self._send_request(HttpVerb.PATCH, url, data)
        response: List = json.loads(import_items.text)

        if len(response) >= 1:
            raise Exception(response[0])

        return None

    def import_media(self, data: Dict) -> str:
        url: str = f'{self.BASE_URL}/media/import/upload/url'
        response: Response = self._send_request(HttpVerb.POST, url, json.dumps(data))

        return response.text

    def update_media(
            self,
            media_code: str,
            file_name: str,
            data: Dict
    ) -> None:
        url: str = f'{self.BASE_URL}/media/import/replace/url?importCode={media_code}&fileName={file_name}'
        self._send_request(HttpVerb.PUT, url, json.dumps(data))

    def get_product_import_result(self, guid: str, page_size: int) -> ImportResult:
        url: str = self.__build_url(ImportType.PRODUCT) + \
            f'/{guid}/status?includeNewProducts=true&includeUpdatedAndDeletedProducts=true&size={page_size}&page='

        import_report: Dict = self._send_request(HttpVerb.GET, url + '0').json()

        report_details: Optional[Dict] = import_report.get('report')
        if report_details is None:
            return ImportResult([import_report])

        page_count: int = report_details['totalPages']
        import_reports: List[Dict] = [import_report]

        for page in range(1, page_count):
            import_report = self._send_request(HttpVerb.GET, url + str(page)).json()
            import_reports.append(import_report)

        return ImportResult(import_reports)

    def await_import_finish(
            self,
            guid: str,
            query_interval_seconds: int,
            max_attempts: int,
            report_page_size: int
    ) -> ImportResult:

        for i in range(0, max_attempts):
            import_result: ImportResult = self.get_product_import_result(guid, report_page_size)

            if not import_result.report['finished']:
                sleep(query_interval_seconds)
                continue

            return import_result

        raise Exception(
            f'Feed product import did not return finished status '
            f'(queried {max_attempts} times with {query_interval_seconds} s interval)'
        )

    def get_media_import_result(self, guid: str) -> MediaImportResult:
        url: str = self.__build_url(ImportType.MEDIA) + f'/status?guid={guid}'
        import_result: Dict = self._send_request(HttpVerb.GET, url).json()

        finished: bool = import_result.get('dateFinished') is not None
        errors: List[str] = import_result['messages']

        return MediaImportResult(finished, errors)

    def __build_url(self, import_type: ImportType) -> str:
        return f'{self.BASE_URL}{import_type.value}'

    def __send_request(self, url: str, data: str) -> str:
        response: Response = self._send_request(HttpVerb.POST, url, data)
        return response.text
