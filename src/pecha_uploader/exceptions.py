class APIError(Exception):
    """Base class for API-related errors."""

    def __init__(self, message="An API error occurred"):
        self.message = message
        super().__init__(self.message)
