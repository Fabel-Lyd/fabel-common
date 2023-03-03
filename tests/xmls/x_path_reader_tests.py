from typing import List, Union
import pytest
from lxml.etree import _Element
from fabelcommon.xmls.onix_x_path_reader import OnixXPathReader
from fabelcommon.xmls.xml import read_xml_etree


TEST_DATA: _Element = read_xml_etree('tests/xmls/data/test_data.xml')


def test_get_values_successful() -> None:
    value: List[str] = OnixXPathReader.get_values(
        TEST_DATA,
        '/o:ONIXMessage/o:Header/o:Subject/o:SubjectCode/text()'
    )
    assert value == ['FBA', 'FXM']


@pytest.mark.parametrize(
    'xpath, expected_value',
    [
        ('/o:ONIXMessage/o:Header/o:Sender/o:SenderIdentifier/o:SenderIDType/text()', '01'),
        ('/o:ONIXMessage/o:Header/o:ContributorDate/o:Date/@dateformat', '05'),
        ('/o:ONIXMessage/o:Missing/text()', None)
    ])
def test_get_value_successful(xpath: str, expected_value: Union[str, None]) -> None:
    value: Union[str, None] = OnixXPathReader.get_value(TEST_DATA, xpath)
    assert value == expected_value


def test_get_elements_successful() -> None:
    elements: List[_Element] = OnixXPathReader.get_elements(TEST_DATA, '/o:ONIXMessage/o:Header/o:Subject/o:SubjectCode')
    values: List[str] = [element.text for element in elements]

    assert values == ['FBA', 'FXM']


def test_get_element_successful() -> None:
    element: _Element = OnixXPathReader.get_element(
        TEST_DATA,
        '/o:ONIXMessage/o:Header/o:ContributorDate/o:ContributorDateRole'
    )
    assert element.text == '50'


@pytest.mark.parametrize(
    'subtree_path, value_path',
    [
        ('/o:ONIXMessage/o:Header', 'o:Subject/o:SubjectCode/text()'),
        ('/o:ONIXMessage/o:Header/o:Subject', 'o:SubjectCode/text()')
    ])
def test_get_values_from_subtree_successful(subtree_path: str, value_path: str) -> None:
    elements: List[_Element] = OnixXPathReader.get_elements(TEST_DATA, subtree_path)

    values: List[str] = []
    for element in elements:
        values += OnixXPathReader.get_values(element, value_path)

    assert values == ['FBA', 'FXM']


def test_get_value_failed_multiple() -> None:
    with pytest.raises(Exception) as exception:
        OnixXPathReader.get_value(TEST_DATA, '/o:ONIXMessage/o:Header/o:Subject/o:SubjectCode/text()')

    assert str(exception.value) == 'Expected single node, found 2'
