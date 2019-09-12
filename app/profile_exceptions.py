__all__ = (
          'APIError',
          'ProfileNotFoundError',
)

class APIError(Exception):
    """Generic error"""
    pass

class ProfileNotFoundError(APIError):
    """Could not find requested profile in the provider API"""
    pass
