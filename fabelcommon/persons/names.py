from typing import List


def fix_inverted_name(name: str) -> str:
    if ',' not in name:
        return name

    name_parts: List[str] = name.split(sep=', ', maxsplit=1)
    name_parts.reverse()

    return ' '.join(name_parts)
