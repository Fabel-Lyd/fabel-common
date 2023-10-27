from typing import List, Tuple
from enum import Enum
from fabelcommon.db.choices import create_choices_list


def test_create_choices_list() -> None:
    class TestEnum(Enum):
        WORD = 'WORD'
        MULTIPLE_WORDS = 'MULTIPLE_WORDS'

    expected_choices_list: List[Tuple[str, str]] = [('WORD', 'Word'), ('MULTIPLE_WORDS', 'Multiple words')]

    assert create_choices_list(TestEnum) == expected_choices_list
