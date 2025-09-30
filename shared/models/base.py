"""
Base data models and fundamental types for the Antifragile Flow system.

Provides strongly-typed base classes that ensure consistency across all components
while maintaining compatibility with Temporal's serialization requirements.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import traceback
from typing import Any, Generic, TypeVar
from uuid import UUID, uuid4

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field
try:
    from pydantic import field_validator  # Pydantic V2
    PYDANTIC_V2 = True
except ImportError:
    from pydantic import validator  # Pydantic V1
    PYDANTIC_V2 = False


class ValidationError(Exception):
    """Raised when input validation fails."""

    pass


class ProcessingError(Exception):
    """Raised when processing operations fail."""

    pass


# Generic type for result data
T = TypeVar("T")


class ResultStatus(str, Enum):
    """Standard result status enumeration."""

    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class Priority(str, Enum):
    """Priority levels for tasks and decisions."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class BaseModel(PydanticBaseModel):
    """
    Base model class with enhanced validation and Temporal compatibility.

    Provides:
    - Strong typing with validation
    - Temporal-compatible serialization
    - Consistent error handling
    - Audit trail support
    """

    class Config:
        # Enable validation on assignment
        validate_assignment = True
        # Use enum values for serialization
        use_enum_values = True
        # Allow extra fields for forward compatibility
        extra = "ignore"
        # Ensure JSON serialization works with complex types
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            timedelta: lambda v: v.total_seconds(),
            UUID: lambda v: str(v),
        }

    # Note: Commented out to avoid Pydantic V1/V2 compatibility issues
    # Pydantic already validates required fields by default
    # @validator("*", pre=True)
    # def validate_not_none_required(cls, v, field):
    #     """Ensure required fields are not None."""
    #     if field.required and v is None:
    #         raise ValueError(f"Field {field.name} is required and cannot be None")
    #     return v


@dataclass
class ActivityResult(Generic[T]):
    """
    Standardized result type for all activities.

    Provides consistent error handling, metrics, and audit trails
    across all AI agents and activities.
    """

    status: ResultStatus
    data: T | None = None
    error_message: str | None = None
    error_details: dict[str, Any] | None = None
    execution_time_ms: int | None = None
    tokens_used: int = 0
    cost_usd: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        """Check if the activity completed successfully."""
        return self.status == ResultStatus.SUCCESS

    @property
    def failed(self) -> bool:
        """Check if the activity failed."""
        return self.status == ResultStatus.FAILURE

    @classmethod
    def success_result(
        cls,
        data: T,
        tokens_used: int = 0,
        cost_usd: float = 0.0,
        execution_time_ms: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ActivityResult[T]:
        """Create a successful result."""
        return cls(
            status=ResultStatus.SUCCESS,
            data=data,
            tokens_used=tokens_used,
            cost_usd=cost_usd,
            execution_time_ms=execution_time_ms,
            metadata=metadata or {},
        )

    @classmethod
    def failure_result(
        cls,
        error_message: str,
        error_details: dict[str, Any] | None = None,
        execution_time_ms: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ActivityResult[T]:
        """Create a failure result."""
        return cls(
            status=ResultStatus.FAILURE,
            error_message=error_message,
            error_details=error_details or {},
            execution_time_ms=execution_time_ms,
            metadata=metadata or {},
        )

    @classmethod
    def from_exception(
        cls,
        exception: Exception,
        execution_time_ms: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ActivityResult[T]:
        """Create a failure result from an exception."""
        return cls(
            status=ResultStatus.FAILURE,
            error_message=str(exception),
            error_details={
                "exception_type": type(exception).__name__,
                "traceback": traceback.format_exc(),
            },
            execution_time_ms=execution_time_ms,
            metadata=metadata or {},
        )


@dataclass
class WorkflowResult(Generic[T]):
    """
    Standardized result type for workflows.

    Captures workflow execution outcomes with comprehensive
    audit information for compliance and monitoring.
    """

    workflow_id: str
    status: ResultStatus
    data: T | None = None
    error_message: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    total_cost_usd: float = 0.0
    total_tokens_used: int = 0
    participants: list[str] = field(default_factory=list)
    decisions_made: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        """Check if the workflow completed successfully."""
        return self.status == ResultStatus.SUCCESS

    @property
    def duration(self) -> timedelta | None:
        """Calculate workflow duration."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


@dataclass
class ServiceResult(Generic[T]):
    """
    Standardized result type for service operations.

    Used by knowledge graph, document store, inbox, and scheduler services.
    """

    operation: str
    status: ResultStatus
    data: T | None = None
    error_message: str | None = None
    affected_records: int = 0
    execution_time_ms: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        """Check if the service operation completed successfully."""
        return self.status == ResultStatus.SUCCESS


class AuditableModel(BaseModel):
    """
    Base model with audit trail capabilities.

    Automatically tracks creation and modification metadata
    for compliance and debugging purposes.
    """

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None
    created_by: str | None = None
    updated_by: str | None = None
    version: int = Field(default=1)

    def update_audit_info(self, updated_by: str | None = None) -> None:
        """Update audit information for modifications."""
        self.updated_at = datetime.utcnow()
        self.updated_by = updated_by
        self.version += 1


class ConfigurableModel(BaseModel):
    """
    Base model for components that need configuration.

    Provides standardized configuration handling with
    validation and environment-based overrides.
    """

    enabled: bool = True
    timeout_seconds: int = Field(default=300, ge=1, le=3600)
    retry_attempts: int = Field(default=3, ge=0, le=10)
    retry_delay_seconds: int = Field(default=1, ge=0, le=60)

    # Note: Validation already handled by Field constraints (ge=1, le=3600)
    # @validator("timeout_seconds")
    # def validate_timeout(cls, v):
    #     """Ensure timeout is reasonable."""
    #     if v < 1 or v > 3600:
    #         raise ValueError("Timeout must be between 1 and 3600 seconds")
    #     return v
