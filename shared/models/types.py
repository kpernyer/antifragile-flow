"""
Shared type definitions using Enum for type safety.

All enums inherit from (str, Enum) to be:
- JSON serializable for Temporal
- String-compatible for comparisons
- Database-friendly for storage
"""

from enum import Enum


class Priority(str, Enum):
    """Priority levels for workflows and tasks"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class ModelPreference(str, Enum):
    """Model training preferences"""
    FAST = "fast"
    BALANCED = "balanced"
    DETAILED = "detailed"


class InteractionMode(str, Enum):
    """Daily interaction workflow modes"""
    CATCHBALL = "catchball"
    WISDOM = "wisdom"


class ScanType(str, Enum):
    """Competitor scan types"""
    NEWS = "news"
    SOCIAL = "social"
    WEB = "web"
    ALL = "all"


class NotificationType(str, Enum):
    """Notification delivery types"""
    EMAIL = "email"
    SLACK = "slack"
    SMS = "sms"


class OnboardingStage(str, Enum):
    """Organization onboarding workflow stages"""
    INITIALIZING = "initializing"
    DOCUMENT_PROCESSING = "document_processing"
    AI_TRAINING_STATUS = "ai_training_status"
    RESEARCH = "research"
    COMPETITOR_SETUP = "competitor_setup"
    COMPLETED = "completed"


class DataType(str, Enum):
    """Data types for cleanup operations"""
    DOCUMENTS = "documents"
    REPORTS = "reports"
    CACHE = "cache"
    LOGS = "logs"


class TaskType(str, Enum):
    """Ad-hoc scheduler task types"""
    COMPETITOR_SCAN = "competitor_scan"
    HEALTH_CHECK = "health_check"
    CLEANUP = "cleanup"
