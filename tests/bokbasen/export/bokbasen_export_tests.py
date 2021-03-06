from unittest.mock import MagicMock
from fabelcommon.bokbasen.bokbasen_api_service import BokbasenApiService
from fabelcommon.bokbasen.export.export import BokbasenExport
from fabelcommon.http.verbs import HttpVerb
from xmldiff import main
from fabelcommon.xmls.xml import read_xml_etree, read_xml_str

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
