from typing import List
from dataclasses import dataclass
from fabelcommon.feed.import_service.import_status import ImportStatus
from fabelcommon.feed.import_service.import_result_item import ImportResultItem


@dataclass(frozen=True)
class ImportResult:
    status: ImportStatus
    created_items: List[ImportResultItem]
