#!/usr/bin/env python3
"""
Globex Industrial Group - Onboarding Demo

This demo shows the complete organization onboarding workflow using real Globex data:
- 5 leadership team members (Mary, John, Isac, Priya, Bob)
- 4 strategic documents (Profile, Annual Report, Product Brochure, Sustainability)
- Full 5-phase onboarding process
"""

import asyncio
from pathlib import Path

from temporalio.client import Client

from shared.config.defaults import TASK_QUEUE_NAME
from shared.models.types import Priority
from workflow.workflows import OrganizationOnboardingWorkflow, OnboardingRequest


async def main():
    """Run the Globex onboarding demo"""

    print("=" * 70)
    print("🏢 GLOBEX INDUSTRIAL GROUP - ONBOARDING DEMO")
    print("=" * 70)
    print()

    # Connect to Temporal
    print("📡 Connecting to Temporal server...")
    try:
        client = await Client.connect("localhost:7233")
        print("✅ Connected to Temporal at localhost:7233")
    except Exception as e:
        print(f"❌ Failed to connect to Temporal server: {e}")
        print()
        print("Please start Temporal server:")
        print("  make temporal")
        print()
        return

    print()
    print("👥 GLOBEX LEADERSHIP TEAM")
    print("-" * 70)
    print("  1. Mary O'Keefe       - CEO")
    print("  2. John Appelkvist    - VP of Sales")
    print("  3. Isac 'Happy' Ironsmith - VP of Engineering")
    print("  4. Priya Sharma       - VP of Legal")
    print("  5. Bob Greenland      - IT Admin")

    print()
    print("📄 STRATEGIC DOCUMENTS")
    print("-" * 70)

    # Define document paths
    demo_dir = Path(__file__).parent
    doc_dir = demo_dir / "documents" / "globex"

    documents = [
        doc_dir / "Globex_Profile.pdf",
        doc_dir / "Globex_Annual_Report_2025.pdf",
        doc_dir / "Globex_Product_Brochure.pdf",
        doc_dir / "Globex_Sustainability_Report.pdf",
    ]

    # Check if documents exist
    for i, doc_path in enumerate(documents, 1):
        if doc_path.exists():
            size_kb = doc_path.stat().st_size / 1024
            print(f"  {i}. ✅ {doc_path.name} ({size_kb:.1f} KB)")
        else:
            print(f"  {i}. ❌ {doc_path.name} (NOT FOUND)")

    print()
    print("🚀 ONBOARDING WORKFLOW - 5 PHASES")
    print("-" * 70)
    print("  Phase 1: Document Processing (AI analysis of 4 PDFs)")
    print("  Phase 2: AI Training Status (Custom Globex AI model)")
    print("  Phase 3: Interactive Research (Market intelligence)")
    print("  Phase 4: Competitor Monitoring (Ongoing surveillance)")
    print("  Phase 5: Completion (Summary and next steps)")

    print()
    print("🎬 Starting workflow in 3 seconds...")
    await asyncio.sleep(3)
    print()

    # Create onboarding request
    request = OnboardingRequest(
        organization_name="Globex Industrial Group",
        documents=[str(doc) for doc in documents if doc.exists()],
        research_queries=[
            "What is Globex's competitive position in industrial automation?",
            "Analyze Globex's sustainability initiatives vs competitors",
            "Market opportunities for Globex products in emerging markets",
        ],
        competitors=[
            "Acme Manufacturing",
            "Industrial Solutions Inc",
            "TechCorp Industries",
        ],
        admin_emails=[
            "mary.okeefe@globex-industrial-group.com",
            "john.appelkvist@globex-industrial-group.com",
            "isac.ironsmith@globex-industrial-group.com",
            "priya.sharma@globex-industrial-group.com",
            "bob.greenland@globex-industrial-group.com",
        ],
        priority=Priority.HIGH,
        enable_ai_customization=True,
    )

    workflow_id = "demo-globex-onboarding"

    print(f"🎬 Starting workflow: {workflow_id}")
    print(f"   Task Queue: {TASK_QUEUE_NAME}")
    print()

    try:
        # Start the workflow
        handle = await client.start_workflow(
            OrganizationOnboardingWorkflow.run,
            request,
            id=workflow_id,
            task_queue=TASK_QUEUE_NAME,
        )

        print("✅ Workflow started successfully!")
        print()
        print("📊 MONITORING")
        print("-" * 70)
        print(f"  Workflow ID: {workflow_id}")
        print(f"  Temporal Web UI: http://localhost:8233")
        print(f"  Direct Link: http://localhost:8233/namespaces/default/workflows/{workflow_id}")
        print()
        print("⏳ Waiting for workflow to complete...")
        print("   (This will process 4 documents and may take a few minutes)")
        print()

        # Wait for result
        result = await handle.result()

        print()
        print("=" * 70)
        print("🎉 ONBOARDING COMPLETE!")
        print("=" * 70)
        print()
        print(f"✅ Success: {result.success}")
        print(f"📝 Onboarding ID: {result.onboarding_id}")
        print(f"📄 Documents Processed: {result.progress.documents_processed}/{result.progress.total_documents}")
        print(f"🤖 AI Training: {'Initiated' if result.training_job_id else 'Not started'}")
        print()

        if result.document_results:
            print("📊 DOCUMENT PROCESSING RESULTS")
            print("-" * 70)
            for summary in result.document_results.admin_summaries[:3]:
                print(f"  • {summary.document_name}")
                print(f"    {summary.summary_text[:100]}...")
                print()

        print("🎯 NEXT STEPS")
        print("-" * 70)
        if result.next_steps:
            for step in result.next_steps:
                print(f"  • {step}")
        print()

    except Exception as e:
        print()
        print(f"❌ Error running workflow: {e}")
        print()
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
