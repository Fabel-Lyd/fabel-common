from dataclasses import dataclass


@dataclass
class ProductIdentifier:
    import_code: int
    product_number: str
