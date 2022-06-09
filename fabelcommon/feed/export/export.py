from typing import List, Dict
from fabelcommon.feed.api_service import FeedApiService
from fabelcommon.feed.export.product_types import ProductType
from fabelcommon.http.verbs import HttpVerb
from fabelcommon.feed.products.relations import Relation


class FeedExport:
    feed_api_service: FeedApiService

    def __init__(self, feed_api_service: FeedApiService) -> None:
        self.feed_api_service: FeedApiService = feed_api_service

    def products_by_name(
            self,
            # case-insensitive, redundant spaces removed and trimmed, exact match
            names: List[str],
            product_type: ProductType
    ) -> List[Dict]:

        result: List[Dict] = []

        for name in names:
            url: str = FeedApiService.build_url(
                FeedApiService.PRODUCT_EXPORT,
                f'changesOnly=false&productTypeImportCodes={product_type.value}&name={name}')

            response: List[Dict] = self.feed_api_service.send_request(HttpVerb.POST, url)
            if product_type == ProductType.PERSON and len(response) > 1:
                raise Exception(f'Multiple persons named "{name}" found in Feed')

            result.extend(response)
        return result

    def products_by_import_code(self, import_codes: List[str], product_type: ProductType) -> List[Dict]:
        concatenated_import_codes: str = ','.join(import_codes)

        url: str = FeedApiService.build_url(
            FeedApiService.PRODUCT_EXPORT,
            f'changesOnly=false&productTypeImportCodes={product_type.value}&importCodes={concatenated_import_codes}&size=500&page=0')

        response: List[Dict] = self.feed_api_service.send_request(HttpVerb.POST, url)
        return response
