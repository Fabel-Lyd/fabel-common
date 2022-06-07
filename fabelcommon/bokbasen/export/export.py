from lxml import etree
from fabelcommon.http.verbs import HttpVerb
from fabelcommon.bokbasen.bokbasen_api_service import BokbasenApiService
from fabelcommon.xml.xml import xml_to_etree


class BokbasenExport:

    bokbasen_api_service: BokbasenApiService

    def __init__(self, bokbasen_api_service: BokbasenApiService):

        self.bokbasen_api_service = bokbasen_api_service

    def get_product_by_isbn(self, isbn: str) -> etree:

        url: str = f'{BokbasenApiService.BASE_URL}/metadata/export/onix/{isbn}'
        xml: str = self.bokbasen_api_service.send_request(HttpVerb.GET, url)
        return xml_to_etree(xml)
