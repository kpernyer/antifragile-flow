#!/usr/bin/env python3
"""
Document processing workflow starter.

This script demonstrates the complete document processing pipeline:
1. Upload document to storage
2. Analyze with OpenAI using prompt templates
3. Generate summary
"""

import asyncio
from datetime import timedelta
import os

from temporalio.client import Client

from shared import shared
from workflow.document_processing import DocumentProcessingRequest, DocumentProcessingWorkflow


async def main():
    """Start a document processing workflow with sample data."""

    # Connect to Temporal server
    target_host = os.environ.get("TEMPORAL_ADDRESS", "localhost:7233")
    client = await Client.connect(target_host)

    # Sample document content for testing
    sample_documents = [
        {
            "content": """
            EXECUTIVE SUMMARY

            Q3 2024 Financial Report
            Company: TechCorp Inc.

            Key Financial Metrics:
            - Revenue: $2.5M (up 15% from Q2)
            - Operating Expenses: $1.8M
            - Net Profit: $700K
            - Cash Flow: Positive $500K

            Strategic Initiatives:
            1. Launch of new AI product line
            2. Expansion into European markets
            3. Partnership with GlobalTech Solutions

            Risk Factors:
            - Increased competition in AI space
            - Supply chain uncertainties
            - Regulatory changes in data privacy

            Recommendations:
            - Accelerate product development
            - Increase marketing spend by 20%
            - Establish European office by Q1 2025

            Next Steps:
            - Board review scheduled for November 15
            - Investor presentation on November 30
            - Strategic planning session in December
            """,
            "filename": "Q3_2024_Financial_Report.txt",
            "type": "financial_report",
        },
        {
            "content": """
            SOFTWARE LICENSE AGREEMENT

            This Software License Agreement ("Agreement") is entered into between
            TechCorp Inc. ("Licensor") and Enterprise Client Corp. ("Licensee").

            1. LICENSE GRANT
            Subject to the terms and conditions of this Agreement, Licensor hereby
            grants to Licensee a non-exclusive, non-transferable license to use
            the Software.

            2. TERM
            This Agreement shall commence on January 1, 2025 and shall continue
            for a period of three (3) years, unless earlier terminated.

            3. FEES
            Licensee shall pay Licensor an annual license fee of $50,000, payable
            in advance on January 1 of each year.

            4. SUPPORT AND MAINTENANCE
            Licensor will provide technical support and software updates during
            business hours (9 AM - 5 PM, Monday through Friday).

            5. TERMINATION
            Either party may terminate this Agreement upon 90 days written notice
            to the other party.

            6. CONFIDENTIALITY
            Both parties agree to maintain confidentiality of proprietary
            information shared under this Agreement.
            """,
            "filename": "Software_License_Agreement.txt",
            "type": "contract",
        },
    ]

    print("🚀 Starting document processing workflows...")
    print("=" * 60)

    for i, doc in enumerate(sample_documents, 1):
        print(f"\n📄 Processing Document {i}: {doc['filename']}")
        print(f"   Type: {doc['type']}")
        print(f"   Size: {len(doc['content'])} characters")

        # Create processing request
        request = DocumentProcessingRequest(
            document_data=doc["content"].encode("utf-8"),
            filename=doc["filename"],
            document_type=doc["type"],
        )

        # Start workflow
        workflow_id = f"document-processing-{i}-{doc['filename'].replace('.', '-')}"

        try:
            result = await client.execute_workflow(
                DocumentProcessingWorkflow.run,
                request,
                id=workflow_id,
                task_queue=shared.TASK_QUEUE_NAME,
                execution_timeout=timedelta(minutes=10),
            )

            print(f"✅ Processing completed for {doc['filename']}")

            if result.success:
                print("\n📊 PROCESSING SUMMARY:")
                summary = result.summary
                print(f"   📁 File: {summary['document_info']['filename']}")
                print(f"   📈 Size: {summary['document_info']['size']} bytes")
                print(f"   🎯 Confidence: {summary['analysis_summary']['confidence']}/10")
                print(f"   💡 Key Insight: {summary['analysis_summary']['key_insights']}")

                print("\n🎯 ACTION ITEMS:")
                for action in summary["analysis_summary"]["action_items"]:
                    print(f"   • {action}")

                print("\n🔍 Analysis Overview:")
                print(f"   {summary['analysis_summary']['overview']}")

            else:
                print(f"❌ Processing failed: {result.error}")

        except Exception as e:
            print(f"❌ Workflow execution failed: {e!s}")

        print("-" * 60)

    print("\n🎉 Document processing demonstration completed!")
    print("\nThis demonstrates:")
    print("✅ Document upload and storage simulation")
    print("✅ AI analysis using prompt templates")
    print("✅ Structured summary generation")
    print("✅ End-to-end Temporal workflow orchestration")


if __name__ == "__main__":
    asyncio.run(main())
