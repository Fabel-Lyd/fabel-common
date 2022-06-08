from lxml import etree
from typing import Dict


class XPathReader:
    __tree: etree
    __name_spaces: Dict

    def __init__(self, tree: etree, name_spaces: Dict):
        self.__tree = tree
        self.__name_spaces = name_spaces

    def read_text(self, xpath: str):
        elements = self.__tree.xpath(xpath, namespaces=self.__name_spaces)
        return elements[0].text if elements else None

    def read_attribute_value(self, xpath: str):
        elements = self.__tree.xpath(xpath, namespaces=self.__name_spaces)
        return elements[0]

    def get_values(self, xpath: str):
        elements = self.__tree.xpath(xpath, namespaces=self.__name_spaces)
        value_elements = []
        for element in elements:
            value = element.text
            value_elements.append(value)
        return value_elements
