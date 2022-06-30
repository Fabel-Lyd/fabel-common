from typing import List, Union
import pytest
from fabelcommon.xmls.x_path_reader import XPathReader
from fabelcommon.xmls.xml import read_xml_etree
from lxml.etree import _Element


@pytest.fixture
def x_path_reader_fixture() -> XPathReader:
    return XPathReader(
        read_xml_etree('tests/xmls/data/test_data.xml'),
        {'o': 'http://ns.editeur.org/onix/3.0/reference'})


def test_get_values_successful(x_path_reader_fixture: XPathReader) -> None:
    value: List[str] = x_path_reader_fixture.get_values('/o:ONIXMessage/o:Header/o:Subject/o:SubjectCode/text()')
    assert value == ['FBA', 'FXM']


@pytest.mark.parametrize(
    'xpath, expected_value',
    [
        ('/o:ONIXMessage/o:Header/o:Sender/o:SenderIdentifier/o:SenderIDType/text()', '01'),
        ('/o:ONIXMessage/o:Header/o:ContributorDate/o:Date/@dateformat', '05'),
        ('/o:ONIXMessage/o:Missing/text()', None)
    ])
def test_get_value_successful(x_path_reader_fixture: XPathReader, xpath: str, expected_value: Union[str, None]) -> None:
    value: str = x_path_reader_fixture.get_value(xpath)
    assert value == expected_value


def test_get_elements_successful(x_path_reader_fixture: XPathReader) -> None:
    elements: List[_Element] = x_path_reader_fixture.get_elements('/o:ONIXMessage/o:Header/o:Subject/o:SubjectCode')
    values: List[str] = [element.text for element in elements]

    assert values == ['FBA', 'FXM']


@pytest.mark.parametrize(
    'subtree_path, value_path',
    [
        ('/o:ONIXMessage/o:Header', 'o:Subject/o:SubjectCode/text()'),
        ('/o:ONIXMessage/o:Header/o:Subject', 'o:SubjectCode/text()')
    ])
def test_get_values_from_subtree_successful(x_path_reader_fixture: XPathReader, subtree_path: str, value_path: str) -> None:
    elements: List[_Element] = x_path_reader_fixture.get_elements(subtree_path)

    values: List[str] = []
    for element in elements:
        values += x_path_reader_fixture.get_values_from_subtree(value_path, element)

    assert values == ['FBA', 'FXM']


def test_get_value_failed_multiple(x_path_reader_fixture: XPathReader):
    with pytest.raises(Exception) as exception:
        x_path_reader_fixture.get_value('/o:ONIXMessage/o:Header/o:Subject/o:SubjectCode/text()')

    assert str(exception.value) == 'Expected single node, found 2'
