from typing import List, Any


def get_distinct_list(input_list: List[Any]) -> List[Any]:
    distinct_items: List[Any] = []

    for item in input_list:
        if item not in distinct_items:
            distinct_items.append(item)

    return distinct_items
