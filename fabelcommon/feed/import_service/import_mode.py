from enum import Enum


class ImportMode(Enum):
    CREATE = 'CREATE'
    UPDATE = 'UPDATE'
    CREATE_OR_UPDATE = 'CREATE_OR_UPDATE'
