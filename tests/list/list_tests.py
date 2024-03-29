from typing import List, Any
import pytest
from fabelcommon.list.list import get_distinct_list


@pytest.mark.parametrize(
    'input_list, expected_list',
    [
        (
            [],
            []
        ),
        (
            [1],
            [1]
        ),
        (
            [2, 1, 1, 4, 5, 5],
            [2, 1, 4, 5]
        ),
        (
            ['b', 'a', 'a', 'd', 'e', 'e'],
            ['b', 'a', 'd', 'e']
        )
    ]
)
def test_get_distinct_list(input_list: List[Any], expected_list: List[Any]) -> None:
    assert get_distinct_list(input_list) == expected_list
