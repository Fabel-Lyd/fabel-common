from typing import List, Dict
from requests import Response
from fabelcommon.feed.api_service import FeedApiService
from fabelcommon.feed.export.product_types import ProductType
from fabelcommon.http.verbs import HttpVerb


class FeedExport(FeedApiService):
    PRODUCT_EXPORT: str = '/export/export'

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
                f'changesOnly=false&productTypeImportCodes={product_type.value}&name={name}'
            )

            response: List[Dict] = self.__send_request(url)

            if product_type == ProductType.PERSON and len(response) > 1:
                raise Exception(f'Multiple persons named "{name}" found in Feed')

            result.extend(response)
        return result

    def get_products_by_import_code(self, import_codes: List[str], product_type: ProductType) -> List[Dict]:
        concatenated_import_codes: str = ','.join(import_codes)

        url: str = self.__build_url(
            f'changesOnly=false&productTypeImportCodes={product_type.value}&importCodes={concatenated_import_codes}&size=500&page=0'
        )

        return self.__send_request(url)

    def get_book(self, isbn: str) -> Dict:
        url: str = self.__build_url(
            f'changesOnly=false&productTypeImportCodes={ProductType.BOOK.value}&productNo={isbn}'
        )
        book_list: List[Dict] = self.__send_request(url)

        if len(book_list) == 0:
            raise Exception(f'Book with ISBN {isbn} not found in Feed')
        if len(book_list) > 1:
            raise Exception(f'Multiple books with ISBN {isbn} found in Feed')

        return book_list[0]

    def __build_url(self, parameters: str) -> str:
        return f'{self.BASE_URL}{self.PRODUCT_EXPORT}?{parameters}'

    def __send_request(self, url: str) -> List[Dict]:
        response: Response = self._send_request(HttpVerb.POST, url)
        return response.json()['content']
