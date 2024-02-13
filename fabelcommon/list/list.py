from typing import List, Any


def get_distinct_list(input_list: List[Any]) -> List[Any]:
    return sorted(list(set(input_list)))
