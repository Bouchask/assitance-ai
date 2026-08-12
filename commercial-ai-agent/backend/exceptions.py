"""
Custom exception hierarchy for the Commercial AI Agent.
Provides structured error handling with context preservation and categorization.
"""
import logging
from typing import Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorCode(Enum):
    """Standard error codes for API responses and logging."""
    # Validation errors
    INVALID_INPUT = "INVALID_INPUT"
    SCHEMA_VALIDATION = "SCHEMA_VALIDATION"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    
    # Authentication/Authorization
    AUTHENTICATION_REQUIRED = "AUTHENTICATION_REQUIRED"
    INVALID_TOKEN = "INVALID_TOKEN"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    
    # LLM errors
    LLM_TIMEOUT = "LLM_TIMEOUT"
    LLM_UNAVAILABLE = "LLM_UNAVAILABLE"
    LLM_INVALID_RESPONSE = "LLM_INVALID_RESPONSE"
    LLM_RATE_LIMIT = "LLM_RATE_LIMIT"
    
    # Execution errors
    EXECUTION_TIMEOUT = "EXECUTION_TIMEOUT"
    STEP_TIMEOUT = "STEP_TIMEOUT"
    STEP_FAILED = "STEP_FAILED"
    DEPENDENCY_FAILED = "DEPENDENCY_FAILED"
    TOOL_NOT_FOUND = "TOOL_NOT_FOUND"
    TOOL_INVOCATION_FAILED = "TOOL_INVOCATION_FAILED"
    
    # Database errors
    DATABASE_ERROR = "DATABASE_ERROR"
    DATABASE_UNAVAILABLE = "DATABASE_UNAVAILABLE"
    RECORD_NOT_FOUND = "RECORD_NOT_FOUND"
    DUPLICATE_RECORD = "DUPLICATE_RECORD"
    
    # Planning errors
    PLAN_INVALID = "PLAN_INVALID"
    PLAN_GENERATION_FAILED = "PLAN_GENERATION_FAILED"
    
    # Approval errors
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    APPROVAL_DENIED = "APPROVAL_DENIED"
    APPROVAL_TIMEOUT = "APPROVAL_TIMEOUT"
    
    # Generic errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"


class AgentException(Exception):
    """Base exception for all agent-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.INTERNAL_ERROR,
        status_code: int = 500,
        context: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        """
        Initialize AgentException with structured error information.
        
        Args:
            message: Human-readable error message
            error_code: Standardized error code
            status_code: HTTP status code
            context: Additional context data
            original_error: Original exception if wrapped
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.context = context or {}
        self.original_error = original_error
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error": self.error_code.value,
            "message": self.message,
            "context": self.context
        }
    
    def log(self, logger_instance: logging.Logger = logger) -> None:
        """Log exception with full context."""
        logger_instance.error(
            f"{self.error_code.value}: {self.message}",
            extra={
                "error_code": self.error_code.value,
                "context": self.context,
                "status_code": self.status_code
            },
            exc_info=self.original_error
        )


class ValidationError(AgentException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        context = kwargs.pop("context", {})
        if field:
            context["field"] = field
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_INPUT,
            status_code=400,
            context=context,
            **kwargs
        )


class SchemaValidationError(AgentException):
    """Raised when schema validation fails."""
    
    def __init__(self, message: str, schema_error: Optional[str] = None, **kwargs):
        context = kwargs.pop("context", {})
        if schema_error:
            context["schema_error"] = schema_error
        super().__init__(
            message=message,
            error_code=ErrorCode.SCHEMA_VALIDATION,
            status_code=400,
            context=context,
            **kwargs
        )


class AuthenticationError(AgentException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication required", **kwargs):
        super().__init__(
            message=message,
            error_code=ErrorCode.AUTHENTICATION_REQUIRED,
            status_code=401,
            context=kwargs.pop("context", {}),
            **kwargs
        )


class PermissionError(AgentException):
    """Raised when user lacks required permissions."""
    
    def __init__(self, message: str = "Permission denied", **kwargs):
        super().__init__(
            message=message,
            error_code=ErrorCode.PERMISSION_DENIED,
            status_code=403,
            context=kwargs.pop("context", {}),
            **kwargs
        )


class TimeoutError(AgentException):
    """Raised when an operation exceeds timeout."""
    
    def __init__(self, message: str, operation: Optional[str] = None, timeout_sec: Optional[float] = None, **kwargs):
        context = kwargs.pop("context", {})
        if operation:
            context["operation"] = operation
        if timeout_sec:
            context["timeout_seconds"] = timeout_sec
        super().__init__(
            message=message,
            error_code=ErrorCode.EXECUTION_TIMEOUT,
            status_code=504,
            context=context,
            **kwargs
        )


class LLMError(AgentException):
    """Raised when LLM operations fail."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.LLM_UNAVAILABLE,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.pop("context", {})
        if model:
            context["model"] = model
        if provider:
            context["provider"] = provider
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=503,
            context=context,
            **kwargs
        )


class RetryableError(AgentException):
    """Raised for errors that can be safely retried."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.INTERNAL_ERROR,
        retry_after_sec: Optional[float] = None,
        max_retries: int = 3,
        **kwargs
    ):
        context = kwargs.pop("context", {})
        context["max_retries"] = max_retries
        if retry_after_sec:
            context["retry_after_seconds"] = retry_after_sec
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=429,
            context=context,
            **kwargs
        )


class ExecutionError(AgentException):
    """Raised when workflow execution fails."""
    
    def __init__(
        self,
        message: str,
        step_id: Optional[int] = None,
        execution_id: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.pop("context", {})
        if step_id is not None:
            context["step_id"] = step_id
        if execution_id:
            context["execution_id"] = execution_id
        super().__init__(
            message=message,
            error_code=ErrorCode.STEP_FAILED,
            status_code=422,
            context=context,
            **kwargs
        )


class ToolError(AgentException):
    """Raised when tool invocation fails."""
    
    def __init__(
        self,
        message: str,
        tool_name: Optional[str] = None,
        tool_error: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.pop("context", {})
        if tool_name:
            context["tool"] = tool_name
        if tool_error:
            context["tool_error"] = tool_error
        super().__init__(
            message=message,
            error_code=ErrorCode.TOOL_INVOCATION_FAILED,
            status_code=422,
            context=context,
            **kwargs
        )


class DatabaseError(AgentException):
    """Raised when database operations fail."""
    
    def __init__(self, message: str, operation: Optional[str] = None, **kwargs):
        context = kwargs.pop("context", {})
        if operation:
            context["operation"] = operation
        super().__init__(
            message=message,
            error_code=ErrorCode.DATABASE_ERROR,
            status_code=500,
            context=context,
            **kwargs
        )


def create_error_response(exc: Exception, request_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Create standardized error response from any exception.
    
    Args:
        exc: Exception to convert
        request_id: Optional request ID for correlation
    
    Returns:
        Dictionary suitable for JSON response
    """
    if isinstance(exc, AgentException):
        response = exc.to_dict()
    else:
        response = {
            "error": ErrorCode.INTERNAL_ERROR.value,
            "message": str(exc) or "An unexpected error occurred"
        }
    
    if request_id:
        response["request_id"] = request_id
    
    return response
