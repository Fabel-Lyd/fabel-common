from xml.etree.ElementTree import XMLParser
from lxml import etree
from lxml.etree import _Element, _ElementTree


def read_xml_str(xml_file_name: str) -> str:
    with open(xml_file_name, 'r', encoding='utf-8') as xml_file:
        return xml_file.read()


def read_xml_etree(xml_file_name: str) -> _Element:
    tree: _ElementTree = etree.parse(xml_file_name)
    return tree.getroot()


def xml_to_etree(xml_str: str) -> _Element:
    utf8_parser: XMLParser = etree.XMLParser(encoding='utf-8')
    xml_str_as_utf8: bytes = xml_str.encode('utf-8')
    tree_root: _Element = etree.fromstring(xml_str_as_utf8, parser=utf8_parser)
    return tree_root
