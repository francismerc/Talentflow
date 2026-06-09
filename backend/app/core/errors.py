class ApplicationError(Exception):
    """Base error for expected application failures."""

    status_code = 400

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(ApplicationError):
    status_code = 404


class ConflictError(ApplicationError):
    status_code = 409


class ConfigurationError(ApplicationError):
    status_code = 503


class IntegrationError(ApplicationError):
    status_code = 502


class ExternalRateLimitError(ApplicationError):
    status_code = 429
