from typing import List, Dict
from fabelcommon.feed.api_service import FeedApiService
from fabelcommon.http.verbs import HttpVerb


class FeedExport:
    feed_api_service: FeedApiService

    def __init__(self, feed_api_service: FeedApiService) -> None:
        self.feed_api_service: FeedApiService = feed_api_service

    def persons_by_name(self, names: List[str]) -> List[Dict]:
        result: List[Dict] = []

        for name in names:
            url: str = FeedApiService.build_url(
                FeedApiService.BASE_URL,
                FeedApiService.PRODUCT_EXPORT,
                f'changesOnly=false&productTypeImportCodes=person&name={name}')

            response: List[Dict] = self.feed_api_service.send_request(HttpVerb.POST, url)
            if len(response) > 1:
                raise Exception(f'Multiple persons named "{name}" found in Feed')

            if len(response) == 1:
                result.append(response[0])

        return result

    def persons_by_import_code(self, import_codes: List[str]) -> List[Dict]:
        concatenated_import_codes: str = ','.join(import_codes)

        url: str = FeedApiService.build_url(
            FeedApiService.BASE_URL,
            FeedApiService.PRODUCT_EXPORT,
            f'importCodes={concatenated_import_codes}&productTypeImportCodes=person&size=500&changesOnly=false&page=0')

        response: List[Dict] = self.feed_api_service.send_request(HttpVerb.POST, url)
        return response
