from typing import Dict, List, Union
from lxml import etree
from lxml.etree import _Element


class XPathReader:
    __tree: etree
    __name_spaces: Dict
    __tree_root: _Element

    def __init__(self, tree: etree, name_spaces: Dict) -> None:
        self.__tree = tree
        self.__name_spaces = name_spaces
        self.__tree_root = self.__tree.getroot()

    def __get_node_list(
            self,
            xpath: str,
            subtree_root: Union[_Element, None] = None
    ) -> Union[List[str], List[_Element]]:

        root: _Element = self.__tree_root if subtree_root is None else subtree_root

        result: Union[List[str], List[_Element]] = root.xpath(xpath, namespaces=self.__name_spaces, smart_strings=False)
        return result

    def __get_single_node(
            self,
            xpath: str,
            subtree_root: Union[_Element, None] = None
    ) -> Union[str, _Element, None]:

        result: Union[List[str], List[_Element]] = self.__get_node_list(xpath, subtree_root)

        if len(result) > 1:
            raise Exception(f'Expected single node, found {len(result)}')

        return result[0] if result else None

    def get_values(self, xpath: str) -> List[str]:
        return self.__get_node_list(xpath)

    def get_value(self, xpath: str) -> Union[str, None]:
        return self.__get_single_node(xpath)

    def get_elements(self, xpath: str) -> List[_Element]:
        return self.__get_node_list(xpath)

    def get_element(self, xpath: str) -> Union[_Element, None]:
        return self.__get_single_node(xpath)

    def get_values_from_subtree(
            self,
            relative_xpath: str,  # without leading slash
            subtree_root: _Element
    ) -> List[str]:

        return self.__get_node_list(relative_xpath, subtree_root)

    def get_value_from_subtree(
            self,
            relative_xpath: str,  # without leading slash
            subtree_root: _Element
    ) -> Union[str, None]:

        return self.__get_single_node(relative_xpath, subtree_root)
