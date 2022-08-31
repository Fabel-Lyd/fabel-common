from typing import List
from unittest.mock import MagicMock
import pytest
from freezegun import freeze_time
from xmldiff import main
from lxml.etree import _Element
from rest_framework import status
from fabelcommon.http.verbs import HttpVerb
from fabelcommon.xmls.xml import read_xml_etree, read_xml_str, xml_to_etree
from fabelcommon.bokbasen.bokbasen_api_service import BokbasenApiService
from fabelcommon.bokbasen.export.export import BokbasenExport
from fabelcommon.bokbasen.export_result import ExportResult

BOKBASEN_XML_DATA: str = 'tests/bokbasen/export/data/bokbasen-9788234001635.xml'


def test_export_product_by_isbn(mocker) -> None:
    send_request_mock: MagicMock = mocker.patch.object(
        BokbasenApiService,
        attribute='send_request',
        return_value=read_xml_str(BOKBASEN_XML_DATA)
    )

    bokbasen_api_service = BokbasenApiService('fake_username', 'fake-password')
    bokbasen_export = BokbasenExport(bokbasen_api_service)

    book = bokbasen_export.get_product_by_isbn('9788234001635')

    send_request_expected_args = (HttpVerb.GET, 'https://api.boknett.no/metadata/export/onix/9788234001635')
    assert send_request_mock.call_args.args == send_request_expected_args

    expected_book = read_xml_etree(BOKBASEN_XML_DATA)
    differences = main.diff_trees(book, expected_book)
    assert len(differences) == 0, differences


@freeze_time('2020-01-02')
def test_get_after_date(requests_mock, mocker) -> None:
    export_text: str = read_xml_str('tests/bokbasen/export/data/bokbasen_export_two_books.xml')
    export_tree: _Element = xml_to_etree(export_text)
    timestamp: str = '20200101120000'

    mocker.patch.object(
        target=BokbasenApiService,
        attribute=BokbasenApiService.get_ticket.__name__,
        return_value='ticket'
    )
    requests_mock.get(
        f'https://api.boknett.no/metadata/export/onix?after={timestamp}&subscription=basic&pagesize=2',
        headers={'next': 'cursor'},
        status_code=status.HTTP_200_OK,
        text=export_text
    )

    bokbasen_api_service: BokbasenApiService = BokbasenApiService('test_username', 'test_password')
    bokbasen_export: BokbasenExport = BokbasenExport(bokbasen_api_service)

    actual_result: ExportResult = bokbasen_export.get_after_date(timestamp, 2)

    differences: List = main.diff_trees(actual_result.books[0].getroottree(), export_tree)

    assert len(differences) == 0
    assert len(actual_result.books) == 2
    assert actual_result.cursor == 'cursor'


def test_get_by_cursor(requests_mock, mocker) -> None:
    export_text: str = read_xml_str('tests/bokbasen/export/data/bokbasen_export_two_books.xml')
    export_tree: _Element = xml_to_etree(export_text)

    mocker.patch.object(
        target=BokbasenApiService,
        attribute=BokbasenApiService.get_ticket.__name__,
        return_value='ticket'
    )
    requests_mock.get(
        'https://api.boknett.no/metadata/export/onix?next=cursor&subscription=basic&pagesize=2',
        headers={'next': 'cursor'},
        status_code=status.HTTP_200_OK,
        text=export_text
    )

    bokbasen_api_service: BokbasenApiService = BokbasenApiService('test_username', 'test_password')
    bokbasen_export: BokbasenExport = BokbasenExport(bokbasen_api_service)

    actual_result: ExportResult = bokbasen_export.get_by_cursor('cursor', 2)

    differences: List = main.diff_trees(actual_result.books[0].getroottree(), export_tree)

    assert len(differences) == 0
    assert len(actual_result.books) == 2
    assert actual_result.cursor == 'cursor'


@freeze_time('2020-01-02')
def test_validate_timestamp_successful(requests_mock, mocker):
    timestamp: str = '20200101120000'

    mocker.patch.object(
        target=BokbasenApiService,
        attribute=BokbasenApiService.get_ticket.__name__,
        return_value='ticket'
    )
    requests_mock.get(
        f'https://api.boknett.no/metadata/export/onix?after={timestamp}&subscription=basic&pagesize=2',
        headers={'next': 'cursor'},
        status_code=status.HTTP_200_OK,
        text='<ONIXMessage/>'
    )

    bokbasen_api_service: BokbasenApiService = BokbasenApiService('test_username', 'test_password')
    bokbasen_export: BokbasenExport = BokbasenExport(bokbasen_api_service)

    bokbasen_export.get_after_date(timestamp, 2)


@freeze_time('2020-01-02')
@pytest.mark.parametrize(
    'timestamp, exception_message',
    [
        ('20200103120000', 'Provided timestamp is in the future'),
        ('20100101120000', 'Items updated more than 180 days ago cannot be exported; please contact Bokbasen if this is needed'),
        ('', "time data '' does not match format '%Y%m%d%H%M%S'"),
        ('abc', "time data 'abc' does not match format '%Y%m%d%H%M%S'"),
        ('20100111211', "time data '20100111211' does not match format '%Y%m%d%H%M%S'"),
        ('MTI2NDA2ZWI3NWZkIzE4MmM1MjQxZmY2IzhmNjM1ZWE=', "time data 'MTI2NDA2ZWI3NWZkIzE4MmM1MjQxZmY2IzhmNjM1ZWE=' does not match format '%Y%m%d%H%M%S'")
    ]
)
def test_validate_timestamp_failed(timestamp: str, exception_message: str, requests_mock, mocker):
    mocker.patch.object(
        target=BokbasenApiService,
        attribute=BokbasenApiService.get_ticket.__name__,
        return_value='ticket'
    )
    requests_mock.get(
        f'https://api.boknett.no/metadata/export/onix?after={timestamp}&subscription=basic&pagesize=2',
        headers={'next': 'cursor'},
        status_code=status.HTTP_200_OK,
        text="<ONIXMessage/>"
    )

    bokbasen_api_service: BokbasenApiService = BokbasenApiService('test_username', 'test_password')
    bokbasen_export: BokbasenExport = BokbasenExport(bokbasen_api_service)

    with pytest.raises(Exception) as exception_info:
        bokbasen_export.get_after_date(timestamp, 2)

    assert str(exception_info.value) == exception_message
