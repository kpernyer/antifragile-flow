"""
Shared data models and types for the Antifragile Flow system.

This module provides strongly-typed data models that ensure consistency
across agents, workflows, and services while maintaining Temporal compatibility.
"""

# Import only enum types to avoid Temporal sandbox issues with base.py
from .types import *  # Enum types for type safety

# Note: base.py contains Pydantic models that use datetime.utcnow
# which is restricted in Temporal workflows. Only import base when needed
# outside of workflows.

__all__ = [
    # Enum types (from types.py)
    "Priority",
    "ModelPreference",
    "OnboardingStage",
    "InteractionMode",
    "ScanType",
    "NotificationType",
    "DataType",
    "TaskType",
]
