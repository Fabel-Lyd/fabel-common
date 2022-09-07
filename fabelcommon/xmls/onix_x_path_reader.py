from typing import Dict, List, Union, Optional
from lxml.etree import _Element


class OnixXPathReader:
    __name_spaces: Dict[str, str] = {'o': 'http://ns.editeur.org/onix/3.0/reference'}

    @staticmethod
    def get_values(element: _Element, xpath: str) -> List[str]:
        return OnixXPathReader.__get_node_list(element, xpath)

    @staticmethod
    def get_value(element: _Element, xpath: str) -> Optional[str]:
        return OnixXPathReader.__get_single_node(element, xpath)

    @staticmethod
    def get_elements(element: _Element, xpath: str) -> List[_Element]:
        return OnixXPathReader.__get_node_list(element, xpath)

    @staticmethod
    def get_element(element: _Element, xpath: str) -> Optional[_Element]:
        return OnixXPathReader.__get_single_node(element, xpath)

    @staticmethod
    def __get_node_list(
            element: _Element,
            xpath: str
    ) -> Union[List[str], List[_Element]]:

        return element.xpath(
            xpath,
            namespaces=OnixXPathReader.__name_spaces,
            smart_strings=False
        )

    @staticmethod
    def __get_single_node(
            element: _Element,
            xpath: str
    ) -> Union[str, _Element, None]:

        result: Union[List[str], List[_Element]] = OnixXPathReader.__get_node_list(element, xpath)

        if len(result) > 1:
            raise Exception(f'Expected single node, found {len(result)}')

        return result[0] if result else None
