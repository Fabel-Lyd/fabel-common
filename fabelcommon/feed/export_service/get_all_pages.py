from typing import Dict, List, Callable


def get_all_pages(export_function: Callable) -> List[Dict]:
    results: List[Dict] = []
    page_count: int = 0

    while True:
        result_page: List[Dict] = export_function(page_count)
        if len(result_page) == 0:
            break

        results.extend(result_page)
        page_count += 1

    return results
