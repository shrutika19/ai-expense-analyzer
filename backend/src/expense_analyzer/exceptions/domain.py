class DomainException(Exception):
    """Base exception for domain-level errors."""


class InvalidExpenseException(DomainException):
    """Raised when an expense violates domain rules."""