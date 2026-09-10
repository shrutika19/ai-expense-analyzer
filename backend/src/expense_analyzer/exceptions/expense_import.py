class UnsupportedFileTypeException(ValueError):
    """Raised when an unsupported file type is uploaded."""

    def __init__(self, file_type: str) -> None:
        self.file_type = file_type

        super().__init__(
            f"Unsupported file type: {file_type}"
        )


class ExpenseImportException(Exception):
    """Raised when expense import fails."""