from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError

class errors:
    NOT_FOUND_ERROR = "Resource not found"
    CONFLICT_ERROR = "Conflict"
    UNAUTHORIZED_ERROR = "Unauthorized"
    FORBIDDEN_ERROR = "Forbidden"
    BAD_REQUEST_ERROR = "Bad request"
    INTERNAL_SERVER_ERROR = "Internal server error"
    VALIDATION_ERROR = "Validation failed"
    RATE_LIMIT_EXCEEDED = "Rate limit exceeded"
    SERVICE_UNAVAILABLE = "Service unavailable"
    NOT_IMPLEMENTED = "Not implemented"
    UNSUPPORTED_MEDIA_TYPE = "Unsupported media type"
    REQUEST_TIMEOUT = "Request timeout"
    PRECONDITION_FAILED = "Precondition failed"
    PAYLOAD_TOO_LARGE = "Payload too large"
    UNPROCESSABLE_ENTITY = "Unprocessable entity"
    TOO_MANY_REQUESTS = "Too many requests"
    GONE = "Resource gone"
    METHOD_NOT_ALLOWED = "Method not allowed"
    BAD_GATEWAY = "Bad gateway"
    GATEWAY_TIMEOUT = "Gateway timeout"
    LENGTH_REQUIRED = "Length required"
    NOT_ACCEPTABLE = "Not acceptable"
    UNSUPPORTED_HTTP_VERSION = "HTTP version not supported"
    INSUFFICIENT_STORAGE = "Insufficient storage"
    NETWORK_AUTH_REQUIRED = "Network authentication required"
    LOCKED = "Resource locked"
    FAILED_DEPENDENCY = "Failed dependency"
    UPGRADE_REQUIRED = "Upgrade required"
    REQUEST_HEADER_FIELDS_TOO_LARGE = "Request header fields too large"
    UNAVAILABLE_FOR_LEGAL_REASONS = "Unavailable for legal reasons"
    INTEGRITY_ERROR = "Database integrity error"
    OPERATIONAL_ERROR = "Database operational error"
    GENERIC_DATABASE_ERROR = "Database error"


class NotFoundError(HTTPException):
    def __init__(self, detail=errors.NOT_FOUND_ERROR):
        super().__init__(status_code=404, detail=detail)

class ConflictError(HTTPException):
    def __init__(self, detail=errors.CONFLICT_ERROR):
        super().__init__(status_code=409, detail=detail)

class UnauthorizedError(HTTPException):
    def __init__(self, detail=errors.UNAUTHORIZED_ERROR):
        super().__init__(status_code=401, detail=detail)

class ForbiddenError(HTTPException):
    def __init__(self, detail=errors.FORBIDDEN_ERROR):
        super().__init__(status_code=403, detail=detail)

class BadRequestError(HTTPException):
    def __init__(self, detail=errors.BAD_REQUEST_ERROR):
        super().__init__(status_code=400, detail=detail)

class InternalServerError(HTTPException):
    def __init__(self, detail=errors.INTERNAL_SERVER_ERROR):
        super().__init__(status_code=500, detail=detail)

class ValidationError(HTTPException):
    def __init__(self, detail=errors.VALIDATION_ERROR):
        super().__init__(status_code=422, detail=detail)

class RateLimitExceededError(HTTPException):
    def __init__(self, detail=errors.RATE_LIMIT_EXCEEDED):
        super().__init__(status_code=429, detail=detail)

class ServiceUnavailableError(HTTPException):
    def __init__(self, detail=errors.SERVICE_UNAVAILABLE):
        super().__init__(status_code=503, detail=detail)

class NotImplementedError(HTTPException):
    def __init__(self, detail=errors.NOT_IMPLEMENTED):
        super().__init__(status_code=501, detail=detail)

class UnsupportedMediaTypeError(HTTPException):
    def __init__(self, detail=errors.UNSUPPORTED_MEDIA_TYPE):
        super().__init__(status_code=415, detail=detail)

class RequestTimeoutError(HTTPException):
    def __init__(self, detail=errors.REQUEST_TIMEOUT):
        super().__init__(status_code=408, detail=detail)

class PreconditionFailedError(HTTPException):
    def __init__(self, detail=errors.PRECONDITION_FAILED):
        super().__init__(status_code=412, detail=detail)

class PayloadTooLargeError(HTTPException):
    def __init__(self, detail=errors.PAYLOAD_TOO_LARGE):
        super().__init__(status_code=413, detail=detail)

class UnprocessableEntityError(HTTPException):
    def __init__(self, detail=errors.UNPROCESSABLE_ENTITY):
        super().__init__(status_code=422, detail=detail)

class TooManyRequestsError(HTTPException):
    def __init__(self, detail=errors.TOO_MANY_REQUESTS):
        super().__init__(status_code=429, detail=detail)

class GoneError(HTTPException):
    def __init__(self, detail=errors.GONE):
        super().__init__(status_code=410, detail=detail)

class MethodNotAllowedError(HTTPException):
    def __init__(self, detail=errors.METHOD_NOT_ALLOWED):
        super().__init__(status_code=405, detail=detail)

class BadGatewayError(HTTPException):
    def __init__(self, detail=errors.BAD_GATEWAY):
        super().__init__(status_code=502, detail=detail)

class GatewayTimeoutError(HTTPException):
    def __init__(self, detail=errors.GATEWAY_TIMEOUT):
        super().__init__(status_code=504, detail=detail)

class LengthRequiredError(HTTPException):
    def __init__(self, detail=errors.LENGTH_REQUIRED):
        super().__init__(status_code=411, detail=detail)

class NotAcceptableError(HTTPException):
    def __init__(self, detail=errors.NOT_ACCEPTABLE):
        super().__init__(status_code=406, detail=detail)

class UnsupportedHTTPVersionError(HTTPException):
    def __init__(self, detail=errors.UNSUPPORTED_HTTP_VERSION):
        super().__init__(status_code=505, detail=detail)

class InsufficientStorageError(HTTPException):
    def __init__(self, detail=errors.INSUFFICIENT_STORAGE):
        super().__init__(status_code=507, detail=detail)

class NetworkAuthRequiredError(HTTPException):
    def __init__(self, detail=errors.NETWORK_AUTH_REQUIRED):
        super().__init__(status_code=511, detail=detail)

class LockedError(HTTPException):
    def __init__(self, detail=errors.LOCKED):
        super().__init__(status_code=423, detail=detail)

class FailedDependencyError(HTTPException):
    def __init__(self, detail=errors.FAILED_DEPENDENCY):
        super().__init__(status_code=424, detail=detail)

class UpgradeRequiredError(HTTPException):
    def __init__(self, detail=errors.UPGRADE_REQUIRED):
        super().__init__(status_code=426, detail=detail)

class RequestHeaderFieldsTooLargeError(HTTPException):
    def __init__(self, detail=errors.REQUEST_HEADER_FIELDS_TOO_LARGE):
        super().__init__(status_code=431, detail=detail)

class UnavailableForLegalReasonsError(HTTPException):
    def __init__(self, detail=errors.UNAVAILABLE_FOR_LEGAL_REASONS):
        super().__init__(status_code=451, detail=detail)

class DatabaseIntegrityError(HTTPException):
    def __init__(self, detail=errors.INTEGRITY_ERROR):
        super().__init__(status_code=409, detail=detail)

class DatabaseOperationalError(HTTPException):
    def __init__(self, detail=errors.OPERATIONAL_ERROR):
        super().__init__(status_code=500, detail=detail)

class DatabaseError(HTTPException):
    def __init__(self, detail=errors.GENERIC_DATABASE_ERROR):
        super().__init__(status_code=500, detail=detail)
