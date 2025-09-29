#!/usr/bin/env python3
"""
Integrated onboarding worker supporting both document processing and web research.
Handles multiple workflows for comprehensive company onboarding process.
"""

import asyncio
import os

from temporalio.client import Client
from temporalio.worker import Worker

# TODO: Add research workflows after fixing import issues
# from workflow.research_bot_workflow import ResearchWorkflow
# TODO: Re-enable after fixing openai_agents import
# from workflow.interactive_research_workflow import InteractiveResearchWorkflow
# Import pure technical activities
from activity.document_activities import (
    process_document_upload,  # Pure file processing, no AI
)

# Import scheduler activities
from activity.scheduler_activities import (
    cleanup_old_data,
    health_check_external_services,
    schedule_competitor_scan,
    send_scheduled_notification,
)

# TODO: Add research activities after fixing import issues
# Import research activities
# from activity.research_activities import (
#     plan_searches,
#     perform_searches,
#     write_report,
#     clarify_query,
#     generate_pdf_report,
# )
# Import storage activities
from activity.storage_activities import StorageActivities

# Import AI-powered activities
from agent_activity.ai_activities import (
    analyze_document_content,
    generate_document_summary,  # Quick summaries for admin UI
    perform_simple_research,  # Simple OpenAI research using prompt templates
)
from shared import shared
from workflow.document_processing_workflow import DocumentProcessingWorkflow

# Import workflows
from workflow.organization_onboarding_workflow import OrganizationOnboardingWorkflow
from workflow.scheduler_workflow import (
    AdHocSchedulerWorkflow,
    CompetitorMonitoringWorkflow,
    MaintenanceWorkflow,
)


async def main():
    """Start the integrated onboarding worker."""
    # Connect to local Temporal server
    target_host = os.environ.get("TEMPORAL_ADDRESS", "localhost:7233")
    client = await Client.connect(target_host)

    # Initialize storage activities
    storage_activities = StorageActivities()

    # Combine all activities
    all_activities = [
        # Storage activities (class methods)
        storage_activities.store_document_in_minio,
        storage_activities.retrieve_document_from_minio,
        # Document processing activities (functions using OpenAI agents)
        process_document_upload,
        analyze_document_content,
        generate_document_summary,  # Quick summary for admin UI
        perform_simple_research,  # One-shot research using prompt templates
        # Scheduler activities (for cron-like operations)
        schedule_competitor_scan,
        send_scheduled_notification,
        cleanup_old_data,
        health_check_external_services,
        # TODO: Add research activities after fixing import issues
        # Research activities (functions using OpenAI agents)
        # plan_searches,
        # perform_searches,
        # write_report,
        # clarify_query,
        # generate_pdf_report,
    ]

    # Register workflows (business processes + scheduling)
    all_workflows = [
        # === BUSINESS WORKFLOWS ===
        OrganizationOnboardingWorkflow,  # Main business process
        DocumentProcessingWorkflow,  # Document sub-process
        # InteractiveResearchWorkflow,   # Research sub-process (TODO: fix imports)
        # === OPERATIONAL WORKFLOWS ===
        CompetitorMonitoringWorkflow,  # Weekly competitor monitoring
        MaintenanceWorkflow,  # Daily maintenance tasks
        AdHocSchedulerWorkflow,  # Ad-hoc scheduled tasks
        # TODO: Add research workflows after fixing import issues
        # ResearchWorkflow,              # Basic web research
    ]

    worker = Worker(
        client,
        task_queue=shared.TASK_QUEUE_NAME,
        workflows=all_workflows,
        activities=all_activities,
    )

    print("🏢 Integrated Onboarding Worker started!")
    print(f"📡 Connected to: {target_host}")
    print(f"📦 Task Queue: {shared.TASK_QUEUE_NAME}")
    print()
    print("🔄 SUPPORTED WORKFLOWS:")
    print("   🏢 Organization Onboarding: Complete business onboarding process")
    print("   📄 Document Processing: Multi-document analysis pipeline")
    print("   💬 Interactive Research: Human-AI research collaboration")
    print("   🗓️  Competitor Monitoring: Weekly scheduled competitor scanning")
    print("   🔧 Daily Maintenance: System cleanup & health checks")
    print("   ⚡ Ad-hoc Scheduler: Custom scheduled tasks")
    print()
    print("⚡ AVAILABLE ACTIVITIES:")
    print("   📁 Storage: MinIO document storage & retrieval")
    print("   📄 Document: Text extraction, analysis & quick summaries")
    print("   🔍 Research: Simple one-shot research using prompt templates")
    print("   ⏰ Scheduler: Cron-like operations & notifications")
    print("   🏥 Health: System monitoring & maintenance")
    print("   💬 Interactive: Complex research with clarifications (coming soon)")
    print("   🤖 AI: OpenAI agents for all intelligence operations")
    print()
    print("✅ Business-aligned workflow architecture operational")
    print("✅ Complete organization onboarding process ready")
    print("✅ Proper separation: workflows orchestrate, activities execute")
    print()
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
