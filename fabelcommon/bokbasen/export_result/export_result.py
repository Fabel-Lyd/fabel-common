from typing import List
from dataclasses import dataclass
from lxml.etree import _Element


@dataclass(frozen=True)
class ExportResult:
    books: List[_Element]
    cursor: str
