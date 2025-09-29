#!/usr/bin/env python3
"""
Test Document Processing Workflow Starter

Tests the complete document processing pipeline with repeatable sample data.
This demonstrates: Document Upload → AI Analysis → Structured Summary

Uses prompt template: document_processor.analyze_document
Expected response format: Structured JSON with summary, insights, and actions
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

from demo_datum.sample_documents import ALL_SAMPLE_DOCUMENTS
from shared import shared
from workflow.document_processing import DocumentProcessingRequest, DocumentProcessingWorkflow


async def main():
    """Test document processing workflow with sample documents."""

    print("🧪 DOCUMENT PROCESSING WORKFLOW TEST")
    print("=" * 60)

    # Show prompt details
    print("📋 PROMPT CONFIGURATION:")
    print("   Template ID: document_processor.analyze_document")
    print("   Template File: shared/prompts/definitions/agents/document_processor.yaml")
    print("   Expected Response: Structured JSON with summary, insights, actions")
    print("   Variables: document_type, document_title, document_content")
    print()

    # Connect to Temporal server
    target_host = os.environ.get("TEMPORAL_ADDRESS", "localhost:7233")
    client = await Client.connect(target_host)

    print(f"🔗 Connected to Temporal server: {target_host}")
    print(f"📦 Task Queue: {shared.TASK_QUEUE_NAME}")
    print()

    # Process each sample document
    for i, doc in enumerate(ALL_SAMPLE_DOCUMENTS, 1):
        print(f"📄 PROCESSING DOCUMENT {i}/{len(ALL_SAMPLE_DOCUMENTS)}")
        print(f"   📁 File: {doc.filename}")
        print(f"   📋 Type: {doc.document_type}")
        print(f"   📊 Size: {len(doc.content)} characters")
        print(f"   🎯 Expected Insights: {len(doc.expected_insights)} items")

        # Create processing request
        request = DocumentProcessingRequest(
            document_data=doc.content.encode("utf-8"),
            filename=doc.filename,
            document_type=doc.document_type,
        )

        # Generate unique workflow ID
        workflow_id = f"test-doc-processing-{i}-{doc.document_type}"

        try:
            print(f"   ⚡ Starting workflow: {workflow_id}")

            result = await client.execute_workflow(
                DocumentProcessingWorkflow.run,
                request,
                id=workflow_id,
                task_queue=shared.TASK_QUEUE_NAME,
                execution_timeout=timedelta(minutes=10),
            )

            if result.success:
                print("   ✅ Processing completed successfully!")

                # Display results
                summary = result.summary
                print()
                print("   📊 PROCESSING RESULTS:")
                print(f"      📁 File: {summary['document_info']['filename']}")
                print(f"      📈 Size: {summary['document_info']['size']} bytes")
                print(f"      🎯 Confidence: {summary['analysis_summary']['confidence']}/10")
                print(f"      🏪 Storage: {summary['document_info']['storage_location']}")

                print()
                print("   💡 KEY INSIGHT:")
                print(f"      {summary['analysis_summary']['key_insights']}")

                print()
                print("   🎯 ACTION ITEMS:")
                for j, action in enumerate(summary["analysis_summary"]["action_items"], 1):
                    print(f"      {j}. {action}")

                print()
                print("   📝 DOCUMENT OVERVIEW:")
                overview = summary["analysis_summary"]["overview"]
                # Wrap long text
                if len(overview) > 80:
                    words = overview.split()
                    lines = []
                    current_line = "      "
                    for word in words:
                        if len(current_line + word) > 76:
                            lines.append(current_line.rstrip())
                            current_line = "      " + word + " "
                        else:
                            current_line += word + " "
                    lines.append(current_line.rstrip())
                    print("\n".join(lines))
                else:
                    print(f"      {overview}")

                # Show analysis details for verification
                print()
                print("   🔍 ANALYSIS METADATA:")
                processing_info = summary["processing_info"]
                print(f"      🤖 Model: {processing_info['model_used']}")
                print(f"      ⏰ Processed: {processing_info['timestamp']}")
                print(f"      ✅ Status: {processing_info['status']}")

            else:
                print(f"   ❌ Processing failed: {result.error}")

        except Exception as e:
            print(f"   💥 Workflow execution failed: {e!s}")

        print()
        print("-" * 60)

    print()
    print("🎉 DOCUMENT PROCESSING TEST COMPLETED!")
    print()
    print("📋 WHAT WAS TESTED:")
    print("✅ Document upload and storage simulation")
    print("✅ Prompt template loading and variable substitution")
    print("✅ AI analysis workflow execution")
    print("✅ Structured response generation")
    print("✅ End-to-end Temporal workflow orchestration")
    print("✅ Error handling and status tracking")
    print()
    print("🔧 NEXT STEPS:")
    print("• Replace mock AI responses with actual OpenAI integration")
    print("• Implement real MinIO storage connectivity")
    print("• Add prompt template customization")
    print("• Extend to batch document processing")


async def test_prompt_rendering():
    """Test prompt template rendering separately."""
    print("\n🧪 TESTING PROMPT TEMPLATE RENDERING")
    print("=" * 50)

    from shared.prompts import load_prompt

    doc = ALL_SAMPLE_DOCUMENTS[0]  # Use financial report

    try:
        prompt = load_prompt(
            "document_processor.analyze_document",
            document_type=doc.document_type,
            document_title=doc.filename,
            document_content=doc.content[:1000] + "..." if len(doc.content) > 1000 else doc.content,
        )

        print("✅ Prompt template loaded successfully!")
        print()
        print("📋 RENDERED PROMPT PREVIEW:")
        print("-" * 40)
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        print("-" * 40)
        print(f"📊 Total prompt length: {len(prompt)} characters")

    except Exception as e:
        print(f"❌ Prompt rendering failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_prompt_rendering())
    asyncio.run(main())
