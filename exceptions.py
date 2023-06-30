# custom exceptions

class RequestFailedException(Exception):
    """Raised when the request fails (doesn't return 200)."""
    pass
