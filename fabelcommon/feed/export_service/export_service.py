from typing import List, Dict
from requests import Response
from fabelcommon.feed.feed_api_service import FeedApiService
from fabelcommon.feed.export_service import ProductType, ExportEndpoint
from fabelcommon.http.verbs import HttpVerb
from fabelcommon.feed.export_service.exceptions import BookNotFoundException, DuplicateBookException
from fabelcommon.batch.batch import chunk_list


class FeedExport(FeedApiService):
    IMPORT_CODE_EXPORT_BATCH_SIZE: int = 300

    def __init__(self, client_id: str, client_secret: str) -> None:
        super().__init__(client_id, client_secret)

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
                f'changesOnly=false&productTypeImportCodes={product_type.value}&name={name}'
            )

            response: List[Dict] = self.__send_product_export_request(url)
            result.extend(response)
        return result

    def get_products_by_import_code(
            self,
            import_codes: List[str],
            product_types: List[ProductType],
            batch_size: int = IMPORT_CODE_EXPORT_BATCH_SIZE
    ) -> List[Dict]:

        unique_product_types: List[str] = [product_type.value for product_type in set(product_types)]
        concatenated_product_types: str = ','.join(sorted(unique_product_types))
        batched_import_codes: List[List[str]] = chunk_list(import_codes, batch_size)

        result_list: List[Dict] = []
        for batch in batched_import_codes:
            concatenated_import_codes: str = ','.join(batch)

            url: str = self.__build_url(
                ExportEndpoint.PRODUCT,
                f'changesOnly=false&productTypeImportCodes={concatenated_product_types}&importCodes={concatenated_import_codes}&size={batch_size}'
            )

            result_list.extend(self.__send_product_export_request(url))

        return result_list

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

    def __send_product_export_request(self, url: str) -> List[Dict]:
        response: Response = self._send_request(HttpVerb.POST, url)
        return response.json()['content']
