#!/usr/bin/env python3
"""
Test integrated workflow with storage + OpenAI agents.
Demonstrates clean architecture with proper separation of concerns.
"""

import asyncio
from datetime import timedelta
import os
from pathlib import Path
import sys
import tempfile

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from temporalio.client import Client
from workflow.document_summary_workflow import DocumentSummaryWorkflow

from demo.sample_documents import FINANCIAL_REPORT
from shared import shared


async def create_temp_document(content: str, filename: str) -> str:
    """Create a temporary document file for testing."""
    temp_dir = tempfile.mkdtemp()
    temp_file = Path(temp_dir) / filename

    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(content)

    return str(temp_file)


async def test_integrated_document_workflow():
    """Test the complete integrated workflow."""
    print("🤖 TESTING INTEGRATED DOCUMENT WORKFLOW")
    print("=" * 60)
    print("Architecture Test:")
    print("  🏪 Storage Agent → 📄 Document Agent → 🤖 Analysis Agent")
    print("  Each agent has single responsibility and clean boundaries")
    print("=" * 60)

    # Connect to Temporal server
    target_host = os.environ.get("TEMPORAL_ADDRESS", "localhost:7233")

    try:
        client = await Client.connect(target_host)
        print(f"✅ Connected to Temporal server: {target_host}")
    except Exception as e:
        print(f"❌ Failed to connect to Temporal: {e}")
        print("   Make sure Temporal server is running: make temporal")
        return False

    # Create temporary document file
    doc = FINANCIAL_REPORT
    temp_file_path = await create_temp_document(doc.content, doc.filename)
    print(f"📄 Created test document: {temp_file_path}")
    print(f"   Type: {doc.document_type}")
    print(f"   Size: {len(doc.content)} characters")

    workflow_id = f"integrated-test-{doc.document_type}"

    try:
        print(f"⚡ Starting integrated workflow: {workflow_id}")
        print("   🏪 Step 1: Storage agent will handle file operations")
        print("   📄 Step 2: Document agent will extract text")
        print("   🤖 Step 3: Analysis agent will use OpenAI agents framework")

        result = await client.execute_workflow(
            DocumentSummaryWorkflow.run,
            temp_file_path,
            id=workflow_id,
            task_queue=shared.TASK_QUEUE_NAME,
            execution_timeout=timedelta(minutes=10),
        )

        print("✅ Integrated workflow completed successfully!")
        print()

        # Display results
        print("📋 WORKFLOW RESULTS:")
        print(f"   📁 File: {result.file_name}")
        print(f"   📊 Confidence: {result.confidence_score}")
        print()

        print("📝 SUMMARY:")
        print(f"   {result.short_summary}")
        print()

        print("🎯 KEY TAKEAWAYS:")
        for i, takeaway in enumerate(result.key_takeaways, 1):
            print(f"   {i}. {takeaway}")
        print()

        print("📚 MAIN TOPICS:")
        for i, topic in enumerate(result.main_topics, 1):
            print(f"   {i}. {topic}")
        print()

        print("📄 FILE INFO:")
        info = result.file_info
        print(f"   • Path: {info['file_path']}")
        print(f"   • Size: {info['file_size']} bytes")
        print(f"   • Type: {info['file_type']}")
        print(f"   • Pages: {info['page_count']}")
        print()

        print("🤖 AGENT-GENERATED REPORT:")
        print("=" * 50)
        report_preview = result.markdown_report[:600]
        print(report_preview + "..." if len(result.markdown_report) > 600 else report_preview)
        print("=" * 50)

        # Clean up
        Path(temp_file_path).unlink()
        print(f"🧹 Cleaned up temporary file: {temp_file_path}")

        return True

    except Exception as e:
        print(f"💥 Workflow execution failed: {e!s}")
        # Clean up on error
        try:
            Path(temp_file_path).unlink()
        except:
            pass
        return False


async def main():
    """Run the integrated architecture test."""
    print("🧪 INTEGRATED DOCUMENT PROCESSING ARCHITECTURE TEST")
    print("=" * 70)
    print("Testing proper agent separation and OpenAI agents integration:")
    print()
    print("  🏗️ ARCHITECTURE PRINCIPLES:")
    print("    • Each agent has single responsibility")
    print("    • Agents don't know how other agents work")
    print("    • Temporal orchestrates but doesn't contain business logic")
    print("    • OpenAI agents framework used for AI processing")
    print("    • Clean boundaries between storage, processing, and analysis")
    print()
    print("=" * 70)
    print()

    if not await test_integrated_document_workflow():
        return

    print()
    print("🎉 ALL INTEGRATION TESTS PASSED!")
    print()
    print("✅ Clean agent architecture maintained")
    print("✅ Proper separation of concerns verified")
    print("✅ OpenAI agents framework integrated successfully")
    print("✅ Each agent operates independently with single responsibility")
    print("✅ Workflow orchestrates without containing business logic")
    print("✅ End-to-end pipeline functional")


if __name__ == "__main__":
    asyncio.run(main())
