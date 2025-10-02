#!/usr/bin/env python3
"""
Temporal Default Worker - General Activities

This worker handles general-purpose activities that don't require
specialized resources (ML training or OpenAI API calls).

Responsibilities:
- Document processing (extraction, parsing)
- System activities (health checks, cleanup)
- Scheduler activities
- Storage operations

Architecture:
Worker (default-queue) -> General Activities -> Services
"""

import asyncio
import logging

from temporalio.client import Client
from temporalio.worker import Worker

from activity.activities import (
    # Document processing activities (non-AI)
    process_document_upload,
    # System activities
    cleanup_old_data,
    health_check_external_services,
    schedule_competitor_scan,
    send_scheduled_notification,
    # Organizational learning activities (service delegation)
    submit_model_training_job,
    check_training_job_status,
    get_organization_training_history,
    cancel_training_job,
    collect_model_feedback,
    start_model_improvement,
    validate_training_readiness,
)

# Import shared configuration
from shared.config.defaults import DEFAULT_QUEUE, get_temporal_address

# Import consolidated modules (proper naming convention)
from workflow.workflows import (
    CompetitorMonitoringWorkflow,
    DailyInteractionWorkflow,
    DocumentProcessingWorkflow,
    OrganizationOnboardingWorkflow,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """
    Default worker function

    Registers all workflows and general-purpose activities.
    Workflows route tasks to specialized workers as needed.
    """
    logger.info("Starting Default Worker")

    # Connect to Temporal
    temporal_address = get_temporal_address()
    client = await Client.connect(temporal_address)
    logger.info(f"Connected to Temporal at {temporal_address}")

    # Create worker with all workflows and default activities
    worker = Worker(
        client,
        task_queue=DEFAULT_QUEUE,
        workflows=[
            # Business workflows (thin orchestration)
            OrganizationOnboardingWorkflow,
            DocumentProcessingWorkflow,
            DailyInteractionWorkflow,
            CompetitorMonitoringWorkflow,
        ],
        activities=[
            # Document processing activities (non-AI)
            process_document_upload,
            # System activities
            cleanup_old_data,
            health_check_external_services,
            schedule_competitor_scan,
            send_scheduled_notification,
            # Organizational learning activities (delegate to training service)
            submit_model_training_job,
            check_training_job_status,
            get_organization_training_history,
            cancel_training_job,
            collect_model_feedback,
            start_model_improvement,
            validate_training_readiness,
        ],
    )

    logger.info(f"Default Worker configured for task queue: {DEFAULT_QUEUE}")
    logger.info("Registered workflows:")
    logger.info("  - OrganizationOnboardingWorkflow")
    logger.info("  - DocumentProcessingWorkflow")
    logger.info("  - DailyInteractionWorkflow")
    logger.info("  - CompetitorMonitoringWorkflow")

    logger.info("Registered activities:")
    logger.info("  - Document processing (1 activity)")
    logger.info("  - Organizational learning (7 activities)")
    logger.info("  - System activities (4 activities)")

    logger.info("Architecture: Default Worker <-> General Activities <-> Services")
    logger.info("Note: ML and OpenAI activities handled by specialized workers")

    # Start worker
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
