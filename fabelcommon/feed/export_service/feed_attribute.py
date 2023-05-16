from dataclasses import dataclass


@dataclass(frozen=True)
class FeedAttribute:
    import_code: str
    value: str
