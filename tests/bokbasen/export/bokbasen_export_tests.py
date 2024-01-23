import json
from typing import Optional
from unittest.mock import MagicMock
import pytest
from freezegun import freeze_time
from xmldiff import main
from lxml.etree import _Element
from rest_framework import status
from fabelcommon.bokbasen.bokbasen_metadata_api_service import BokbasenMetadataApiService
from fabelcommon.http.verbs import HttpVerb
from fabelcommon.xmls.xml import read_xml_etree, read_xml_str
from fabelcommon.bokbasen.export.export import BokbasenExport
from fabelcommon.bokbasen.export_result import ExportResult
from fabelcommon.xmls.onix_x_path_reader import OnixXPathReader

TEST_DATA_DIRECTORY: str = 'tests/bokbasen/export/data'
BOKBASEN_XML_DATA: str = 'tests/bokbasen/export/data/bokbasen-9788234001635.xml'

ISBN_XPATH: str = 'o:ProductIdentifier[o:ProductIDType/text()="15"]/o:IDValue/text()'


def test_export_product_by_isbn(mocker) -> None:
    send_request_mock: MagicMock = mocker.patch.object(
        BokbasenMetadataApiService,
        attribute='send_request',
        return_value=read_xml_str(BOKBASEN_XML_DATA)
    )

    bokbasen_metadata_api_service = BokbasenMetadataApiService('fake_username', 'fake-password')
    bokbasen_export = BokbasenExport(bokbasen_metadata_api_service)

    book = bokbasen_export.get_product_by_isbn('9788234001635')

    send_request_expected_args = (HttpVerb.GET, '/metadata/export/onix/v1/9788234001635')
    assert send_request_mock.call_args.args == send_request_expected_args

    expected_book = read_xml_etree(BOKBASEN_XML_DATA)
    differences = main.diff_trees(book, expected_book)
    assert len(differences) == 0, differences


@freeze_time('2020-01-02')
def test_get_after_date(requests_mock, mocker) -> None:
    export_content: str = read_xml_str(f'{TEST_DATA_DIRECTORY}/bokbasen_export_two_books.xml')
    timestamp: str = '20200101120000'

    expected_tree: _Element = read_xml_etree(f'{TEST_DATA_DIRECTORY}/bokbasen_export_single_book.xml')
    expected_product: _Element = OnixXPathReader.get_element(expected_tree, '/o:ONIXMessage/o:Product')

    requests_mock.post(
        "https://login.bokbasen.io/oauth/token",
        status_code=status.HTTP_200_OK,
        text=json.dumps(
            {
                "access_token": "fake-access-token",
                "scope": "export:onix",
                "expires_in": 86400,
                "token_type": "Bearer"
            }
        )
    )
    requests_mock.get(
        f'https://api.bokbasen.io/metadata/export/onix/v1?after={timestamp}&subscription=extended&pagesize=2',
        headers={'next': 'cursor'},
        status_code=status.HTTP_200_OK,
        text=export_content
    )

    bokbasen_metadata_api_service: BokbasenMetadataApiService = BokbasenMetadataApiService('test_username', 'test_password')
    bokbasen_export: BokbasenExport = BokbasenExport(bokbasen_metadata_api_service)

    actual_result: ExportResult = bokbasen_export.get_after_date(timestamp, 2)

    expected_isbn: Optional[str] = OnixXPathReader.get_value(expected_product, ISBN_XPATH)
    actual_isbn: Optional[str] = OnixXPathReader.get_value(actual_result.books[0], ISBN_XPATH)

    assert actual_isbn is not None
    assert actual_isbn == expected_isbn
    assert len(actual_result.books) == 2
    assert actual_result.cursor == 'cursor'


def test_get_by_cursor(requests_mock) -> None:
    export_content: str = read_xml_str(f'{TEST_DATA_DIRECTORY}/bokbasen_export_two_books.xml')

    expected_tree: _Element = read_xml_etree(f'{TEST_DATA_DIRECTORY}/bokbasen_export_single_book.xml')
    expected_product: _Element = OnixXPathReader.get_element(expected_tree, '/o:ONIXMessage/o:Product')

    requests_mock.post(
        "https://login.bokbasen.io/oauth/token",
        status_code=status.HTTP_200_OK,
        text=json.dumps(
            {
                "access_token": "fake-access-token",
                "scope": "export:onix",
                "expires_in": 86400,
                "token_type": "Bearer"
            }
        )
    )
    requests_mock.get(
        'https://api.bokbasen.io/metadata/export/onix/v1?next=cursor&subscription=extended&pagesize=2',
        headers={'next': 'cursor'},
        status_code=status.HTTP_200_OK,
        text=export_content
    )

    bokbasen_metadata_api_service: BokbasenMetadataApiService = BokbasenMetadataApiService('test_username', 'test_password')
    bokbasen_export: BokbasenExport = BokbasenExport(bokbasen_metadata_api_service)

    actual_result: ExportResult = bokbasen_export.get_by_cursor('cursor', 2)

    expected_isbn: Optional[str] = OnixXPathReader.get_value(expected_product, ISBN_XPATH)
    actual_isbn: Optional[str] = OnixXPathReader.get_value(actual_result.books[0], ISBN_XPATH)

    assert actual_isbn is not None
    assert actual_isbn == expected_isbn
    assert len(actual_result.books) == 2
    assert actual_result.cursor == 'cursor'


@freeze_time('2020-01-02')
def test_validate_timestamp_successful(requests_mock) -> None:
    timestamp: str = '20200101120000'

    requests_mock.post(
        "https://login.bokbasen.io/oauth/token",
        status_code=status.HTTP_200_OK,
        text=json.dumps(
            {
                "access_token": "fake-access-token",
                "scope": "export:onix",
                "expires_in": 86400,
                "token_type": "Bearer"
            }
        )
    )
    requests_mock.get(
        f'https://api.bokbasen.io/metadata/export/onix/v1?after={timestamp}&subscription=extended&pagesize=2',
        headers={'next': 'cursor'},
        status_code=status.HTTP_200_OK,
        text='<ONIXMessage/>'
    )

    bokbasen_metadata_api_service: BokbasenMetadataApiService = BokbasenMetadataApiService('test_username', 'test_password')
    bokbasen_export: BokbasenExport = BokbasenExport(bokbasen_metadata_api_service)

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
def test_validate_timestamp_failed(
        timestamp: str,
        exception_message: str,
        requests_mock
) -> None:
    requests_mock.post(
        "https://login.bokbasen.io/oauth/token",
        status_code=status.HTTP_200_OK,
        text=json.dumps(
            {
                "access_token": "fake-access-token",
                "scope": "export:onix",
                "expires_in": 86400,
                "token_type": "Bearer"
            }
        )
    )
    requests_mock.get(
        f'https://api.bokbasen.io/metadata/export/onix/v1?after={timestamp}&subscription=extended&pagesize=2',
        headers={'next': 'cursor'},
        status_code=status.HTTP_200_OK,
        text="<ONIXMessage/>"
    )

    bokbasen_metadata_api_service: BokbasenMetadataApiService = BokbasenMetadataApiService('test_username', 'test_password')
    bokbasen_export: BokbasenExport = BokbasenExport(bokbasen_metadata_api_service)

    with pytest.raises(Exception) as exception_info:
        bokbasen_export.get_after_date(timestamp, 2)

    assert str(exception_info.value) == exception_message
