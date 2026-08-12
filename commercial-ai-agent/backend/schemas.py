"""
Pydantic request/response models for API validation.
Ensures all inputs are validated against defined schemas.
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any, List
from enum import Enum


class LoginRequest(BaseModel):
    """User login request model."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, max_length=256, description="User password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "password123"
            }
        }


class ProcessRequest(BaseModel):
    """Process request model for workflow submission."""
    user_input: str = Field(
        ...,
        min_length=5,
        max_length=5000,
        description="User request or instruction"
    )
    auto_approve: bool = Field(
        default=False,
        description="Automatically approve all steps (dangerous, use with caution)"
    )
    
    @validator("user_input")
    def validate_user_input(cls, v):
        """Ensure user input is not just whitespace."""
        if not v.strip():
            raise ValueError("User input cannot be empty or whitespace only")
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_input": "I need a quote for John Doe for an e-commerce website",
                "auto_approve": False
            }
        }


class ApproveRequest(BaseModel):
    """Step approval request model."""
    execution_id: str = Field(
        ...,
        min_length=10,
        description="Execution ID from process request"
    )
    step_id: int = Field(
        ...,
        ge=1,
        description="Step ID to approve"
    )
    approved: bool = Field(
        ...,
        description="Approval decision (true to approve, false to reject)"
    )
    rejection_reason: Optional[str] = Field(
        None,
        max_length=500,
        description="Reason for rejection (if approved=false)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "execution_id": "exec-550e8400-e29b-41d4-a716-446655440000",
                "step_id": 1,
                "approved": True
            }
        }


class ExecutionStatusRequest(BaseModel):
    """Get execution status request model."""
    execution_id: str = Field(
        ...,
        min_length=10,
        description="Execution ID to check"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "execution_id": "exec-550e8400-e29b-41d4-a716-446655440000"
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    context: Optional[Dict[str, Any]] = Field(None, description="Error context")
    request_id: Optional[str] = Field(None, description="Request correlation ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "INVALID_INPUT",
                "message": "Email is required",
                "context": {"field": "email"},
                "request_id": "req-550e8400-e29b-41d4-a716-446655440000"
            }
        }


class ProcessResponse(BaseModel):
    """Process request response model."""
    execution_id: str = Field(..., description="Execution ID")
    status: str = Field(
        ...,
        description="Execution status (executing, waiting_approval, completed, failed)"
    )
    message: Optional[str] = Field(None, description="Status message")
    step: Optional[int] = Field(None, description="Current step ID if waiting approval")
    tool: Optional[str] = Field(None, description="Tool name if waiting approval")
    arguments: Optional[Dict[str, Any]] = Field(None, description="Tool arguments if waiting approval")
    results: Optional[Dict[str, Any]] = Field(None, description="Results if completed")
    error: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "execution_id": "exec-550e8400-e29b-41d4-a716-446655440000",
                "status": "waiting_approval",
                "message": "Approval required for step 1",
                "step": 1,
                "tool": "db.find_or_create_client",
                "arguments": {"name": "John Doe"}
            }
        }


class ApproveResponse(BaseModel):
    """Approval response model."""
    status: str = Field(..., description="Updated execution status")
    message: str = Field(..., description="Status message")
    execution_id: str = Field(..., description="Execution ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "executing",
                "message": "Step approved, continuing execution",
                "execution_id": "exec-550e8400-e29b-41d4-a716-446655440000"
            }
        }


class HealthCheckResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service status (ok, degraded, down)")
    service: str = Field(..., description="Service name")
    timestamp: str = Field(..., description="Check timestamp")
    database: str = Field(..., description="Database status")
    llm: str = Field(..., description="LLM provider status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok",
                "service": "commercial-ai-agent",
                "timestamp": "2024-08-12T12:20:36Z",
                "database": "connected",
                "llm": "ready"
            }
        }


class LoginResponse(BaseModel):
    """Login response model."""
    token: str = Field(..., description="JWT authentication token")
    user_id: int = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "user_id": 1,
                "email": "user@example.com"
            }
        }


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of items per page"
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of items to skip"
    )


class SearchParams(BaseModel):
    """Search parameters for query endpoints."""
    query: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Search query"
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum results"
    )
