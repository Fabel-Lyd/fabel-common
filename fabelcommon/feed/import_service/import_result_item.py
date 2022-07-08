from typing import List
from dataclasses import dataclass
from fabelcommon.feed.import_service.import_status import ImportStatus


@dataclass(frozen=True)
class ImportResultItem:
    import_code: str
    product_number: str
    status: ImportStatus
    messages: List[str]
