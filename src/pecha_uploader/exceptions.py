class AlreadyExistsError(Exception):
    """Raised when a resource (e.g., index) already exists."""

    def __init__(self, message="Resource already exists"):
        self.message = message
        super().__init__(self.message)


class APIError(Exception):
    """Base class for API-related errors."""

    def __init__(self, message="An API error occurred"):
        self.message = message
        super().__init__(self.message)
