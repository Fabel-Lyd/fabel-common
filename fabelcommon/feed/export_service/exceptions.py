

class BookNotFoundException(Exception):

    def __init__(self, isbn: str) -> None:
        msg: str = f'Book with ISBN "{isbn}" not found in Feed'
        super().__init__(msg)


class DuplicateBookException(Exception):

    def __init__(self, isbn: str) -> None:
        msg: str = f'Multiple books with ISBN "{isbn}" found in Feed'
        super().__init__(msg)


class DuplicatePersonException(Exception):

    def __init__(self, name: str) -> None:
        msg: str = f'Multiple persons named "{name}" found in Feed'
        super().__init__(msg)
