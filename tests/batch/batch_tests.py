from typing import List, Any
import pytest
from fabelcommon.batch.batch import chunk_list


@pytest.mark.parametrize(
    'initial_list, expected_list, batch_size',
    [
        (
            [1, 2, 3, 4],
            [[1, 2], [3, 4]],
            2
        ),
        (
            ['a', 'b', 'c', 'd', 'e'],
            [['a', 'b', 'c'], ['d', 'e']],
            3
        ),
        (
            [],
            [],
            4
        ),
        (
            [1],
            [[1]],
            11
        ),
        (
            'string',
            ['str', 'ing'],
            3
        )
    ]
)
def test_chunk_list_success(
        initial_list: List[Any],
        expected_list: List[List[Any]],
        batch_size: int
) -> None:

    actual_list: List[List[Any]] = chunk_list(initial_list, batch_size)
    assert actual_list == expected_list


@pytest.mark.parametrize(
    'batch_size',
    [0, -1]
)
def test_chunk_list_failure(batch_size: int) -> None:
    with pytest.raises(Exception) as exception_info:
        chunk_list([1], batch_size)

    assert str(exception_info.value) == 'Batch size must be greater than 0'
