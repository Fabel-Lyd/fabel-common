import pytest
from fabelcommon.xmls.x_path_reader import XPathReader
from fabelcommon.xmls.xml import read_xml_etree


@pytest.fixture
def x_path_reader_fixture() -> XPathReader:
    return XPathReader(
        read_xml_etree('tests/xmls/data/test_data.xml'),
        {'o': 'http://ns.editeur.org/onix/3.0/reference'})


def test_read_text(x_path_reader_fixture):
    value = x_path_reader_fixture.read_text('/o:ONIXMessage/o:Header/o:Sender/o:SenderIdentifier/o:SenderIDType')
    assert value == '01'


def test_read_attribute_value(x_path_reader_fixture):
    value = x_path_reader_fixture.read_attribute_value('/o:ONIXMessage/o:Header/o:ContributorDate/o:Date/@dateformat')
    assert value == '05'


def test_get_values(x_path_reader_fixture):
    value = x_path_reader_fixture.get_values('/o:ONIXMessage/o:Header/o:Subject/o:SubjectCode')
    assert value == ['FBA', 'FXM']
