import pytest
from fabelcommon.persons.names import fix_inverted_name


@pytest.mark.parametrize(
    'inverted_name, expected',
    [
        ('Nesbø, Jo', 'Jo Nesbø'),
        ('Jo Nesbø', 'Jo Nesbø'),
        ('Homer', 'Homer'),
        ('', '')
    ])
def test_fix_inverted_name(inverted_name: str, expected: str) -> None:
    assert fix_inverted_name(inverted_name) == expected
