from typing import List
from datetime import datetime, timedelta
from lxml.etree import _Element
from fabelcommon.xmls.xml import xml_to_etree
from fabelcommon.xmls.onix_x_path_reader import OnixXPathReader
from fabelcommon.http.verbs import HttpVerb
from fabelcommon.bokbasen.bokbasen_api_service import BokbasenApiService
from fabelcommon.bokbasen.export_type import ExportType
from fabelcommon.bokbasen.export_response import BokbasenExportResponse
from fabelcommon.bokbasen.export_result import ExportResult

EXPORT_CUTOFF_DAYS: int = 180


class BokbasenExport:
    bokbasen_api_service: BokbasenApiService

    def __init__(self, bokbasen_api_service: BokbasenApiService) -> None:
        self.bokbasen_api_service = bokbasen_api_service

    def get_product_by_isbn(self, isbn: str) -> _Element:
        url: str = f'/metadata/export/onix/{isbn}'
        xml: str = self.bokbasen_api_service.send_request(HttpVerb.GET, url)
        return xml_to_etree(xml)

    def get_by_cursor(self, cursor: str, batch_size: int) -> ExportResult:
        url: str = self.__build_url(ExportType.CURSOR, cursor, batch_size)
        return self.__get(url)

    def get_after_date(self, timestamp: str, batch_size: int) -> ExportResult:
        self.__validate_timestamp(timestamp)
        url: str = self.__build_url(ExportType.DATE, timestamp, batch_size)
        return self.__get(url)

    def __get(self, url: str) -> ExportResult:
        response: BokbasenExportResponse = self.bokbasen_api_service.send_export_request(url)
        return ExportResult(
            books=self.__parse_exported_books(response.content),
            cursor=response.cursor
        )

    @staticmethod
    def __validate_timestamp(timestamp: str) -> None:
        # additional check due to issue with datetime.strptime - strings like '20100111211' incorrectly parsed as valid dates
        if len(timestamp) != len('yyyyMMddHHmmss'):
            raise Exception(f"time data '{timestamp}' does not match format '%Y%m%d%H%M%S'")

        converted_date: datetime = datetime.strptime(timestamp, '%Y%m%d%H%M%S')
        current_date: datetime = datetime.now()

        if converted_date < current_date - timedelta(days=EXPORT_CUTOFF_DAYS):
            raise Exception(f'Items updated more than {EXPORT_CUTOFF_DAYS} days ago cannot be exported; please contact Bokbasen if this is needed')

        if converted_date > current_date:
            raise Exception("Provided timestamp is in the future")

    @staticmethod
    def __build_url(export_type: ExportType, parameter: str, batch_size: int) -> str:
        return f'/metadata/export/onix?{export_type.value}={parameter}&subscription=extended&pagesize={batch_size}'

    @classmethod
    def __parse_exported_books(cls, export: str) -> List[_Element]:
        tree: _Element = xml_to_etree(export)
        return OnixXPathReader.get_elements(tree, '/o:ONIXMessage/o:Product')
