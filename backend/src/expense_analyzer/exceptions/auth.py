class AuthException(Exception):
    """Base authentication exception."""


class UserAlreadyExistsException(AuthException):
    """Raised when attempting to register an existing email."""


class InvalidCredentialsException(AuthException):
    """Raised when credentials are invalid."""


class UserNotFoundException(AuthException):
    """Raised when a user cannot be found."""


class InactiveUserException(AuthException):
    """Raised when an inactive user attempts authentication."""


class InvalidTokenException(AuthException):
    """Reserved for JWT authentication."""