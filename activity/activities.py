"""
Temporal Activity Definitions

This module consolidates all business activities following proper naming conventions.
Workers import from this single module for clean registration.

Architecture:
- Activities handle business operations only
- Delegate technical work to services
- Return quickly, no blocking operations
- Use business terminology, not technical jargon
"""

# Technical document activities (pure file operations)
from activity.document_activities import (
    process_document_upload,
)

# Organizational learning activities (business operations with service delegation)
from activity.organizational_learning_activities import (
    TrainingJobStatus,
    TrainingJobSubmission,
    cancel_training_job,
    check_training_job_status,
    collect_model_feedback,
    get_organization_training_history,
    start_model_improvement,
    submit_model_training_job,
    validate_training_readiness,
)

# Scheduler activities (system operations)
from activity.scheduler_activities import (
    cleanup_old_data,
    health_check_external_services,
    schedule_competitor_scan,
    send_scheduled_notification,
)

# AI-powered activities (delegate to AI agents)
from agent_activity.ai_activities import (
    analyze_document_content,
    generate_document_summary,
)

# Export all activities for worker registration
__all__ = [
    "TrainingJobStatus",
    "TrainingJobSubmission",
    "analyze_document_content",
    "cancel_training_job",
    "check_training_job_status",
    "cleanup_old_data",
    "collect_model_feedback",
    "generate_document_summary",
    "get_organization_training_history",
    "health_check_external_services",
    "process_document_upload",
    "schedule_competitor_scan",
    "send_scheduled_notification",
    "start_model_improvement",
    "submit_model_training_job",
    "validate_training_readiness",
]
