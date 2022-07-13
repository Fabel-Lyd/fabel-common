from dataclasses import dataclass


@dataclass(frozen=True)
class ImportResultItem:
    import_code: str
    product_number: str
