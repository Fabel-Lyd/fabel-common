from dataclasses import dataclass


@dataclass(frozen=True)
class BokbasenExportResponse:
    content: str
    cursor: str
