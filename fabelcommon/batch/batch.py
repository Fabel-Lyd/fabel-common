from typing import List, Any


def chunk_list(provided_list: List[Any], chunk_size: int) -> List[List[Any]]:
    if chunk_size < 1:
        raise Exception('Batch size must be greater than 0')

    result_list: List[List[Any]] = []

    for batch in range(0, len(provided_list), chunk_size):
        result_list.append(provided_list[batch:batch + chunk_size])

    return result_list
