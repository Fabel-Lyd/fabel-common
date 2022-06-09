import enum


class RelationType(enum.Enum):
    AUTHOR = 'Forfatter_relasjon'
    READER = 'Innleser_relasjon'
    TRANSLATOR = 'Oversetter_relasjon'
    SERIES = 'serie'
