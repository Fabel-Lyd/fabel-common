from xml.etree.ElementTree import XMLParser
from lxml import etree


def read_xml_str(xml_file_name: str) -> str:
    with open(xml_file_name, 'r', encoding='utf-8') as xml_file:
        return xml_file.read()


def read_xml_etree(xml_file_name: str) -> etree:
    tree = etree.parse(xml_file_name)
    return tree


def xml_to_etree(xml_str: str) -> etree:
    utf8_parser: XMLParser = etree.XMLParser(encoding='utf-8')
    xml_str_as_utf8: bytes = xml_str.encode('utf-8')
    tree: etree = etree.fromstring(xml_str_as_utf8, parser=utf8_parser)
    return tree
