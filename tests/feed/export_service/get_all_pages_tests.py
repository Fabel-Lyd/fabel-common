from typing import Dict, List
from fabelcommon.feed.export_service.get_all_pages import get_all_pages


def export_function(page_count: int) -> List[Dict]:
    return [{'page': page_count + 1}] if page_count < 3 else []


def test_get_all_pages() -> None:
    expected_result: List[Dict] = [
        {'page': 1},
        {'page': 2},
        {'page': 3}
    ]

    assert get_all_pages(export_function) == expected_result
