#!/usr/bin/env python3
"""
Simple Document Processing Test

Tests just the document processing workflow without organizational twin dependencies.
This demonstrates: Document Upload → AI Analysis → Summary (mock mode)
"""

import asyncio
from datetime import timedelta
import os
from pathlib import Path
import sys

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from temporalio.client import Client
from workflow.document_summary_workflow import DocumentSummaryWorkflow

from demo.sample_documents import FINANCIAL_REPORT
from shared import shared


async def test_prompt_rendering():
    """Test prompt template rendering first."""
    print("🧪 TESTING PROMPT TEMPLATE RENDERING")
    print("=" * 50)

    from shared.prompts import load_prompt

    try:
        prompt = load_prompt(
            "document_processor.analyze_document",
            document_type=FINANCIAL_REPORT.document_type,
            document_title=FINANCIAL_REPORT.filename,
            document_content=FINANCIAL_REPORT.content[:1000] + "...",
        )

        print("✅ Prompt template loaded successfully!")
        print()
        print("📋 RENDERED PROMPT PREVIEW:")
        print("-" * 40)
        print(prompt[:600] + "..." if len(prompt) > 600 else prompt)
        print("-" * 40)
        print(f"📊 Total prompt length: {len(prompt)} characters")
        print()

    except Exception as e:
        print(f"❌ Prompt rendering failed: {e}")
        return False

    return True


async def test_document_processing():
    """Test document processing workflow."""
    print("🚀 TESTING DOCUMENT PROCESSING WORKFLOW")
    print("=" * 50)

    # Connect to Temporal server
    target_host = os.environ.get("TEMPORAL_ADDRESS", "localhost:7233")

    try:
        client = await Client.connect(target_host)
        print(f"✅ Connected to Temporal server: {target_host}")
    except Exception as e:
        print(f"❌ Failed to connect to Temporal: {e}")
        print("   Make sure Temporal server is running: make temporal")
        return False

    # Test with financial report
    doc = FINANCIAL_REPORT
    print(f"📄 Processing: {doc.filename}")
    print(f"   Type: {doc.document_type}")
    print(f"   Size: {len(doc.content)} characters")

    # Create a temporary file for the document
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(doc.content)
        temp_file_path = f.name

    import uuid

    workflow_id = f"simple-test-{doc.document_type}-{uuid.uuid4().hex[:8]}"

    try:
        print(f"⚡ Starting workflow: {workflow_id}")

        result = await client.execute_workflow(
            DocumentSummaryWorkflow.run,
            temp_file_path,
            id=workflow_id,
            task_queue=shared.TASK_QUEUE_NAME,
            execution_timeout=timedelta(minutes=5),
        )

        if result:
            print("✅ Processing completed successfully!")

            print()
            print("📊 PROCESSING RESULTS:")
            print(f"   📁 File: {result.file_name}")
            print(f"   🎯 Confidence: {result.confidence_score}")

            print()
            print("💡 SHORT SUMMARY:")
            print(f"   {result.short_summary}")

            print()
            print("🎯 KEY TAKEAWAYS:")
            for i, takeaway in enumerate(result.key_takeaways, 1):
                print(f"   {i}. {takeaway}")

            print()
            print("📝 MAIN TOPICS:")
            for i, topic in enumerate(result.main_topics, 1):
                print(f"   {i}. {topic}")

            print()
            print("📋 DETAILED REPORT:")
            print(
                result.markdown_report[:500] + "..."
                if len(result.markdown_report) > 500
                else result.markdown_report
            )

        else:
            print("❌ Processing failed: No result returned")
            return False

    except Exception as e:
        print(f"💥 Workflow execution failed: {e!s}")
        return False
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_file_path)
        except:
            pass

    return True


async def main():
    """Run the complete test."""
    print("🧪 SIMPLE DOCUMENT PROCESSING TEST")
    print("=" * 60)
    print()

    # Test 1: Prompt rendering
    if not await test_prompt_rendering():
        return

    print()

    # Test 2: Document processing workflow
    if not await test_document_processing():
        return

    print()
    print("🎉 ALL TESTS PASSED!")
    print()
    print("✅ Prompt template system working")
    print("✅ Document processing workflow operational")
    print("✅ Mock AI analysis generating structured responses")
    print("✅ End-to-end pipeline functional")


if __name__ == "__main__":
    asyncio.run(main())
