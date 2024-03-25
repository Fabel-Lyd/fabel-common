import enum


class BokbasenAudience(enum.Enum):
    METADATA = 'metadata'
    DDS = 'dds'
    BOKSKYA = 'bokskya'
    ORDERS = 'orders'
