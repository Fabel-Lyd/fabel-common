import json
from typing import List, Dict, Union
from urllib.parse import urlencode
from requests import Response
from fabelcommon.feed.export_service.identifier_type import IdentifierType
from fabelcommon.feed.feed_api_service import FeedApiService
from fabelcommon.feed.export_service import ProductType, ExportEndpoint
from fabelcommon.feed.export_service.feed_attribute import FeedAttribute
from fabelcommon.http.verbs import HttpVerb
from fabelcommon.feed.export_service.exceptions import BookNotFoundException, DuplicateBookException
from fabelcommon.batch.batch import chunk_list


class FeedExport(FeedApiService):
    IMPORT_CODE_EXPORT_BATCH_SIZE: int = 300
    NAME_EXPORT_BATCH_SIZE: int = 100

    def __init__(self, client_id: str, client_secret: str) -> None:
        super().__init__(client_id, client_secret)

    def get_all_products(self, page_size: int = 100) -> List[Dict]:
        partial_url: str = self.__build_url(
            ExportEndpoint.PRODUCT,
            f'changesOnly=false&size={page_size}&page='
        )

        all_products: List[Dict] = []
        page_count: int = 0

        while True:
            product_batch: List[Dict] = self.__send_product_export_request(f'{partial_url}{page_count}')
            if len(product_batch) == 0:
                break

            all_products.extend(product_batch)
            page_count += 1

        return all_products

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
                f'size={FeedExport.NAME_EXPORT_BATCH_SIZE}&'
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
        batched_identifier_values: List[List[str]] = chunk_list(identifier_values, batch_size)

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
            page_size: int,
            page: int
    ) -> List[Dict]:

        url: str = self.__build_url(
            ExportEndpoint.PRODUCT,
            f'changesOnly=false&productTypeImportCodes=ERP&size={page_size}&page={page}'
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

        return self.__send_product_export_request(url, json.dumps(payload))

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

    def __build_url(self, export_endpoint: ExportEndpoint, parameters: str) -> str:
        return f'{self.BASE_URL}/{export_endpoint.value}?{parameters}'

    def __send_product_export_request(
            self,
            url: str,
            data: Union[Dict, str, None] = None
    ) -> List[Dict]:

        response: Response = self._send_request(HttpVerb.POST, url, data)
        return response.json()['content']
