#!/usr/bin/env python3
"""
Temporal Worker - Main Entry Point

This is the primary worker that registers all workflows and activities.
Follows proper naming conventions with clean imports from consolidated modules.

Architecture Principles:
- Worker knows about workflows and activities
- Worker lifecycle managed by Temporal/Docker
- Services have independent lifecycle (Docker/K8s)
- Clean separation of concerns maintained
"""

import asyncio
import logging

from temporalio.client import Client
from temporalio.worker import Worker

from activity.activities import (
    analyze_document_content,
    cancel_training_job,
    check_training_job_status,
    # System activities
    cleanup_old_data,
    collect_model_feedback,
    generate_document_summary,
    get_organization_training_history,
    health_check_external_services,
    # Document processing activities
    process_document_upload,
    schedule_competitor_scan,
    send_scheduled_notification,
    start_model_improvement,
    # Organizational learning activities (business interface to services)
    submit_model_training_job,
    validate_training_readiness,
)

# Import shared configuration
from shared.config.defaults import TASK_QUEUE_NAME, get_temporal_address

# Import consolidated modules (proper naming convention)
from workflow.workflows import (
    CompetitorMonitoringWorkflow,
    DocumentProcessingWorkflow,
    OrganizationOnboardingWorkflow,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """
    Main worker function

    Registers all workflows and activities with proper separation:
    - Workflows: Business orchestration
    - Activities: Business operations (delegate to services)
    - Services: Technical implementation (independent lifecycle)
    """
    logger.info("Starting Organizational Twin Worker")

    # Connect to Temporal
    temporal_address = get_temporal_address()
    client = await Client.connect(temporal_address)
    logger.info(f"Connected to Temporal at {temporal_address}")

    # Create worker with all workflows and activities
    worker = Worker(
        client,
        task_queue=TASK_QUEUE_NAME,
        workflows=[
            # Business workflows (thin orchestration)
            OrganizationOnboardingWorkflow,
            DocumentProcessingWorkflow,
            CompetitorMonitoringWorkflow,
        ],
        activities=[
            # Document processing activities
            process_document_upload,
            analyze_document_content,
            generate_document_summary,
            # System activities
            cleanup_old_data,
            health_check_external_services,
            schedule_competitor_scan,
            send_scheduled_notification,
            # Organizational learning activities
            # These delegate to model_training_service (independent lifecycle)
            submit_model_training_job,
            check_training_job_status,
            get_organization_training_history,
            cancel_training_job,
            collect_model_feedback,
            start_model_improvement,
            validate_training_readiness,
        ],
    )

    logger.info(f"Worker configured for task queue: {TASK_QUEUE_NAME}")
    logger.info("Registered workflows:")
    for workflow in worker._workflows:
        logger.info(f"  - {workflow.__name__}")

    logger.info("Registered activities:")
    for activity_name in worker._activities.keys():
        logger.info(f"  - {activity_name}")

    logger.info("Worker ready - services run independently via Docker/K8s")
    logger.info("Architecture: Worker (Temporal) <-> Activities <-> Services (Independent)")

    # Start worker
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
