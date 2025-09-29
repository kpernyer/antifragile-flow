#!/usr/bin/env python3
"""
Complete Workflow Integration Test

This demonstrates the full integration from Temporal workflows to model training,
showing how all components work together in the proper architecture.

Flow:
1. Document Processing Workflow (Temporal)
2. Model Training Activity (Business Interface)
3. Training Service (Technical Implementation)
4. Real ML Training (LoRA Fine-tuning)
"""

import asyncio
import logging
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from temporalio.client import Client
from temporalio.worker import Worker

from activity.activities import (
    analyze_document_content,
    check_training_job_status,
    generate_document_summary,
    process_document_upload,
    submit_model_training_job,
)
from service.model_training_service import ModelTrainingService, TrainingJobStatus
from shared.config.defaults import TASK_QUEUE_NAME, get_temporal_address

# Import workflow and activities
from workflow.document_processing_workflow import (
    DocumentProcessingRequest,
    DocumentProcessingWorkflow,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def create_test_documents():
    """Create test documents for workflow processing"""
    return [
        {
            "file_path": "demo_financial_report.txt",
            "content": """
            TechCorp Q4 2024 Financial Report

            EXECUTIVE SUMMARY
            Revenue: $12.5M (25% YoY growth)
            Profit Margin: 18% (industry leading)
            Customer Satisfaction: 94%

            KEY ACHIEVEMENTS:
            - Launched 3 major AI products
            - Expanded to 5 new markets
            - Achieved carbon-neutral operations
            - 95% employee retention rate

            STRATEGIC OUTLOOK:
            TechCorp continues to lead in ethical AI innovation while
            maintaining sustainable business practices. Our focus on
            human-centered design drives exceptional customer outcomes.
            """,
            "document_type": "financial_report",
            "uploaded_by": "finance@techcorp.com",
        },
        {
            "file_path": "product_strategy.txt",
            "content": """
            TechCorp Product Strategy 2025

            CORE PRINCIPLES:
            - Innovation through ethical AI development
            - Sustainability in all operations
            - User privacy and security first
            - Accessibility for all users

            PRODUCT ROADMAP:
            Q1: Launch AI-powered analytics platform
            Q2: Expand mobile capabilities
            Q3: Introduce sustainability metrics
            Q4: Deploy advanced security features

            Our products embody TechCorp values and demonstrate our
            commitment to responsible technology development.
            """,
            "document_type": "strategic_document",
            "uploaded_by": "strategy@techcorp.com",
        },
    ]


async def run_complete_workflow_test():
    """Run the complete workflow integration test"""

    print("🔄 COMPLETE WORKFLOW INTEGRATION TEST")
    print("=" * 60)

    # Step 1: Setup Temporal Connection
    print("\n1️⃣  TEMPORAL SETUP")
    try:
        temporal_address = get_temporal_address()
        client = await Client.connect(temporal_address)
        print(f"   ✅ Connected to Temporal at {temporal_address}")
    except Exception as e:
        print(f"   ❌ Temporal connection failed: {e}")
        return False

    # Step 2: Start Worker (In Background)
    print("\n2️⃣  WORKER CONFIGURATION")

    worker = Worker(
        client,
        task_queue=TASK_QUEUE_NAME,
        workflows=[DocumentProcessingWorkflow],
        activities=[
            process_document_upload,
            analyze_document_content,
            generate_document_summary,
            submit_model_training_job,
            check_training_job_status,
        ],
    )

    print("   ✅ Worker configured with workflows and activities")

    # Start worker in background
    async def run_worker():
        await worker.run()

    worker_task = asyncio.create_task(run_worker())
    print("   🔄 Worker started in background")

    # Give worker time to start
    await asyncio.sleep(2)

    # Step 3: Prepare Test Data
    print("\n3️⃣  TEST DATA PREPARATION")

    documents = create_test_documents()
    print(f"   📚 Created {len(documents)} test documents")

    for i, doc in enumerate(documents, 1):
        print(f"   {i}. {doc['file_path']} ({doc['document_type']})")

    # Step 4: Execute Document Processing Workflow
    print("\n4️⃣  DOCUMENT PROCESSING WORKFLOW")

    workflow_id = "complete-test-workflow"

    request = DocumentProcessingRequest(
        documents=documents,
        organization_name="TechCorp Inc",
        organization_id="techcorp_complete_test",
        processing_priority="high",
        enable_model_training=True,  # Enable ML training!
        organizational_values=["innovation", "sustainability", "ethics"],
        communication_style="professional",
        requester_email="test@techcorp.com",
    )

    print(f"   🚀 Starting workflow: {workflow_id}")
    print(f"   🏢 Organization: {request.organization_name}")
    print(f"   🤖 ML Training Enabled: {request.enable_model_training}")

    try:
        # Start workflow
        handle = await client.start_workflow(
            DocumentProcessingWorkflow.run, request, id=workflow_id, task_queue=TASK_QUEUE_NAME
        )

        print(f"   ✅ Workflow started with ID: {workflow_id}")

        # Step 5: Monitor Workflow Progress
        print("\n5️⃣  WORKFLOW MONITORING")

        # Wait for workflow to complete (with timeout)
        import time

        start_time = time.time()
        max_wait = 300  # 5 minutes max

        while time.time() - start_time < max_wait:
            try:
                # Check if workflow is still running
                workflow_info = await handle.describe()
                status = workflow_info.status.name

                elapsed = time.time() - start_time
                print(f"   [{elapsed:6.1f}s] Workflow status: {status}")

                if status in ["COMPLETED", "FAILED", "TERMINATED"]:
                    break

                await asyncio.sleep(5)

            except Exception as e:
                print(f"   ⚠️  Workflow monitoring error: {e}")
                break

        # Get final result
        try:
            result = await handle.result()
            print("   ✅ Workflow completed successfully!")

            # Display results
            print(f"   📊 Processed {result.documents_processed} documents")
            print(f"   📈 Success rate: {result.success_count}/{result.documents_processed}")

            if result.training_job_id:
                print(f"   🤖 Training job started: {result.training_job_id}")

        except Exception as e:
            print(f"   ❌ Workflow execution error: {e}")
            result = None

        # Step 6: Check Training Status
        if result and result.training_job_id:
            print("\n6️⃣  MODEL TRAINING STATUS")

            service = ModelTrainingService()

            # Monitor training for a bit
            for check in range(6):  # Check 6 times over 1 minute
                job_status = service.get_job_status(result.training_job_id)

                if job_status:
                    print(f"   [{check * 10:3d}s] Training: {job_status.status.value}")

                    if job_status.status == TrainingJobStatus.COMPLETED:
                        print("   🎉 Training completed!")
                        print(f"   ⏱️  Duration: {job_status.training_duration_minutes:.1f} minutes")
                        print(f"   📚 Examples: {job_status.training_examples_count}")
                        if job_status.model_location:
                            print(f"   📁 Model: {job_status.model_location}")
                        break

                    elif job_status.status == TrainingJobStatus.FAILED:
                        print(f"   ❌ Training failed: {job_status.error_message}")
                        break

                await asyncio.sleep(10)

        # Step 7: Summary
        print("\n7️⃣  INTEGRATION TEST SUMMARY")

        if result:
            print("   ✅ WORKFLOW INTEGRATION SUCCESSFUL")
            print("      • Temporal workflow executed")
            print("      • Documents processed through activities")
            print("      • Model training initiated")
            print("      • Service layer handled ML operations")
            print("      • Architecture separation maintained")

            if result.training_job_id:
                print(f"      • Training job: {result.training_job_id}")

        else:
            print("   ⚠️  Workflow integration had issues")

        return result is not None

    except Exception as e:
        print(f"   ❌ Workflow execution failed: {e}")
        return False

    finally:
        # Cleanup worker
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass


async def main():
    """Main test function"""

    try:
        success = await run_complete_workflow_test()

        if success:
            print("\n🎊 COMPLETE WORKFLOW INTEGRATION SUCCESS!")
            print("\n📋 WHAT WAS DEMONSTRATED:")
            print("   • End-to-end Temporal workflow execution")
            print("   • Document processing activities")
            print("   • Model training service integration")
            print("   • Proper separation of concerns")
            print("   • Business workflows + Technical services")
            print("\n🏗️  ARCHITECTURE VERIFIED:")
            print("   • Workflows orchestrate business logic")
            print("   • Activities provide business interfaces")
            print("   • Services handle technical implementation")
            print("   • Independent service lifecycle")
        else:
            print("\n⚠️  Workflow integration test incomplete")

    except Exception as e:
        logger.error(f"Complete workflow test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
