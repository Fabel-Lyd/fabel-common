from typing import List
from dataclasses import dataclass


@dataclass(frozen=True)
class MediaImportResult:
    finished: bool
    errors: List[str]

    def was_successful(self) -> bool:
        return self.finished and len(self.errors) == 0
