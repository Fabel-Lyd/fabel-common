from typing import List, Tuple, Type
from enum import Enum


def create_choices_list(choices: Type[Enum]) -> List[Tuple[str, str]]:
    return [(choice.value, choice.value.capitalize().replace('_', ' ')) for choice in list(choices)]
