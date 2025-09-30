"""
Temporal Workflow Definitions

This module consolidates all business workflows following proper naming conventions.
Workers import from this single module for clean registration.

Architecture:
- Workflows contain only business logic
- No technical implementation details
- Delegate complex work to activities
- Activities collaborate with services
"""

# Import all business workflows for worker registration
from workflow.daily_interaction_workflow import (
    DailyInteractionRequest,
    DailyInteractionResult,
    DailyInteractionWorkflow,
)
from workflow.document_processing_workflow import (
    DocumentProcessingRequest,
    DocumentProcessingResult,
    DocumentProcessingWorkflow,
)
from workflow.organization_onboarding_workflow import (
    OnboardingProgress,
    OnboardingRequest,
    OnboardingResult,
    OrganizationOnboardingWorkflow,
)
from workflow.scheduler_workflow import (
    CompetitorMonitoringWorkflow,
    WeeklyCompetitorReportRequest,
    WeeklyCompetitorReportResult,
)

# Export all workflows for worker registration
__all__ = [
    # Organization Onboarding
    "OrganizationOnboardingWorkflow",
    "OnboardingRequest",
    "OnboardingResult",
    "OnboardingProgress",
    # Document Processing
    "DocumentProcessingWorkflow",
    "DocumentProcessingRequest",
    "DocumentProcessingResult",
    # Daily Interaction (Demo Workflow)
    "DailyInteractionWorkflow",
    "DailyInteractionRequest",
    "DailyInteractionResult",
    # Scheduler/Monitoring
    "CompetitorMonitoringWorkflow",
    "WeeklyCompetitorReportRequest",
    "WeeklyCompetitorReportResult",
]
