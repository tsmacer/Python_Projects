import bcrypt

class UserAlreadyExistsError(ValueError):
    """Exception raised when a user tries to register with a username that already exists."""
    pass


class AuthenticationError(Exception):
    """Exception raised for errors in the authentication process."""
    pass


class InsufficientFundsError(ValueError):
    """Exception raised when a withdrawal attempt is made with insufficient funds."""
    pass


class InvalidTransactionError(ValueError):
    """Exception raised for invalid transaction operations."""
    pass


class UnauthorizedError(PermissionError):
    """Exception raised when an unauthorized action is attempted by a user."""
    pass


# Helper function to hash password
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())
