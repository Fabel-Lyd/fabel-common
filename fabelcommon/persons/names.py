from typing import List


def fix_inverted_names(names: List[str]) -> List[str]:
    fixed_name_list: List[str] = []
    for name in names:
        if ',' not in name:
            fixed_name_list.append(name)
            continue

        name_parts: List[str] = name.split(sep=', ', maxsplit=1)
        name_parts.reverse()
        fixed_name_list.append(' '.join(name_parts))

    return fixed_name_list
