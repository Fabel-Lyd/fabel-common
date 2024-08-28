from typing import Dict, List, Union, Optional
import json
from requests import Response
from urllib.parse import urlencode
from datetime import datetime
from fabelcommon.feed.feed_api_service import FeedApiService
from fabelcommon.feed.export_service import ExportEndpoint
from fabelcommon.feed.export_service.product_types import ProductType
from fabelcommon.feed.export_service.identifier_type import IdentifierType
from fabelcommon.feed.export_service.feed_attribute import FeedAttribute
from fabelcommon.feed.export_service.exceptions import BookNotFoundException, DuplicateBookException
from fabelcommon.feed.export_service.get_all_pages import get_all_pages
from fabelcommon.http.verbs import HttpVerb
from fabelcommon.list.list import get_distinct_list
from fabelcommon.batch.batch import chunk_list
from fabelcommon.datetime.time_formats import TimeFormats


class FeedExport(FeedApiService):
    IMPORT_CODE_EXPORT_BATCH_SIZE: int = 100
    DEFAULT_EXPORT_BATCH_SIZE: int = 100

    def __init__(self, client_id: str, client_secret: str) -> None:
        super().__init__(client_id, client_secret)

    def get_all_products(
            self,
            product_type: ProductType,
            export_from: Optional[datetime] = None,
            page_size: int = DEFAULT_EXPORT_BATCH_SIZE
    ) -> List[Dict]:

        partial_url: str = self.__build_url(
            ExportEndpoint.PRODUCT,
            f'changesOnly=false'
            f'&productTypeImportCodes={product_type.value}'
            f'&size={page_size}'
            f'{"&exportFrom=" + TimeFormats.get_date_time_string_utc(export_from) if export_from else ""}'
            f'&page='
        )

        def callback(page_count: int) -> List[Dict]:
            return self.__send_product_export_request(f'{partial_url}{page_count}')

        return get_all_pages(callback)

    def get_products_by_name(
            self,
            # case-insensitive, redundant spaces removed and trimmed, exact match
            names: List[str],
            product_type: ProductType
    ) -> List[Dict]:

        result: List[Dict] = []

        for name in names:
            url: str = self.__build_url(
                ExportEndpoint.PRODUCT,
                'changesOnly=false&'
                f'size={FeedExport.DEFAULT_EXPORT_BATCH_SIZE}&'
                f'productTypeImportCodes={product_type.value}&'
                f'name={name}'
            )

            response: List[Dict] = self.__send_product_export_request(url)
            result.extend(response)
        return result

    def get_products_by_identifier(
            self,
            identifier_type: IdentifierType,
            identifier_values: List[str],
            product_types: List[ProductType],
            batch_size: int = IMPORT_CODE_EXPORT_BATCH_SIZE,
            product_head_only: bool = False
    ) -> List[Dict]:

        unique_product_types: List[str] = [product_type.value for product_type in set(product_types)]
        concatenated_product_types: str = ','.join(sorted(unique_product_types))
        unique_identifier_values: List[str] = get_distinct_list(identifier_values)
        batched_identifier_values: List[List[str]] = chunk_list(unique_identifier_values, batch_size)

        result_list: List[Dict] = []
        for batch in batched_identifier_values:
            concatenated_identifier_values: str = ','.join(batch)

            url: str = self.__build_url(
                export_endpoint=ExportEndpoint.PRODUCT,
                parameters=urlencode({
                    'changesOnly': str(False).lower(),
                    'productTypeImportCodes': concatenated_product_types,
                    identifier_type.value: concatenated_identifier_values,
                    'size': batch_size,
                    'productHeadOnly': str(product_head_only).lower()
                })
            )

            result_list.extend(self.__send_product_export_request(url))

        return result_list

    def get_books_by_attributes(
            self,
            attributes: List[FeedAttribute],
            page_size: int
    ) -> List[Dict]:

        partial_url: str = self.__build_url(
            ExportEndpoint.PRODUCT,
            f'changesOnly=false&productTypeImportCodes=ERP&size={page_size}&page='
        )

        payload_attributes: List[Dict] = [
            {
                "importCode": attribute.import_code,
                "value": attribute.value
            }
            for attribute
            in attributes
        ]
        payload: Dict = {'attributes': payload_attributes}

        def callback(page_count: int):
            return self.__send_product_export_request(f'{partial_url}{page_count}', json.dumps(payload))

        return get_all_pages(callback)

    def get_book(self, isbn: str) -> Dict:
        url: str = self.__build_url(
            ExportEndpoint.PRODUCT,
            f'changesOnly=false&productTypeImportCodes={ProductType.BOOK.value}&productNo={isbn}'
        )
        book_list: List[Dict] = self.__send_product_export_request(url)

        if len(book_list) == 0:
            raise BookNotFoundException(isbn)
        if len(book_list) > 1:
            raise DuplicateBookException(isbn)

        return book_list[0]

    def get_data_register(self, import_code: str) -> Dict:
        url: str = self.__build_url(ExportEndpoint.DATA_REGISTER, f'importCode={import_code}')
        data_register_list: List[Dict] = self._send_request(HttpVerb.GET, url).json()

        if len(data_register_list) == 0:
            raise Exception(f'Data register with import code {import_code} does not exist in Feed')

        return data_register_list[0]

    def get_structure(self, import_code: str) -> List[Dict]:
        url: str = f'{self.BASE_URL}/{ExportEndpoint.STRUCTURE.value}/{import_code}'
        structure_list: List[Dict] = self._send_request(HttpVerb.GET, url).json()
        return structure_list

    def get_import_code_by_product_number(self, product_type: ProductType, product_number: str) -> Optional[str]:
        found_products: List[Dict] = self.get_products_by_identifier(
            IdentifierType.PRODUCT_NUMBER,
            [product_number],
            [product_type],
            2,
            True
        )

        if len(found_products) == 0:
            return None

        if len(found_products) > 1:
            raise Exception('Provided product number belongs to more than one product')

        return found_products[0]['identifier']['importCode']

    def __build_url(self, export_endpoint: ExportEndpoint, parameters: str) -> str:
        return f'{self.BASE_URL}/{export_endpoint.value}?{parameters}'

    def __send_product_export_request(
            self,
            url: str,
            data: Union[Dict, str, None] = None
    ) -> List[Dict]:

        response: Response = self._send_request(HttpVerb.POST, url, data)
        return response.json()['content']
