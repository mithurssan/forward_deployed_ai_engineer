class CustomerNotFound(Exception):
    code = "CUSTOMER_NOT_FOUND"
    http_status = 404

class ComplaintNotFound(Exception):
    code = "COMPLAINT_NOT_FOUND"
    http_status = 404

class InvalidTransition(Exception):
    code = "INVALID_TRANSITION"
    http_status = 409

class ApprovalRequired(Exception):
    code = "APPROVAL_REQUIRED"
    http_status = 409

class ValidationError(Exception):
    code = "VALIDATION_ERROR"
    http_status = 422

class ForbiddenRole(Exception):
    code = "FORBIDDEN_ROLE"
    http_status = 403

class DependencyUnavailable(Exception):
    code = "DEPENDENCY_UNAVAILABLE"
    http_status = 503

class InternalError(Exception):
    code = "INTERNAL_ERROR"
    http_status = 500
    message = (
        "Unexpected error. Quote the correlation ID when reporting it."
    )
