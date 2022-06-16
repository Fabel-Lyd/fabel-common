import pytest
from typing import List
from fabelcommon.persons.names import fix_inverted_names


@pytest.mark.parametrize(
    'inverted_names, expected',
    [
        (['Nesbø, Jo', 'Jo Nesbø', 'Homer', ''], ['Jo Nesbø', 'Jo Nesbø', 'Homer', '']),
        (['Nesbø, Jo'], ['Jo Nesbø'])
    ])
def test_fix_inverted_names(inverted_names: List[str], expected: List[str]) -> None:
    assert fix_inverted_names(inverted_names) == expected
