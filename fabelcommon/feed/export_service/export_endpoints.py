from enum import Enum


class ExportEndpoint(Enum):
    PRODUCT = 'export/export'
    DATA_REGISTER = 'export/basedata/dataRegisters'
    STRUCTURE = 'export/structure/structures'
