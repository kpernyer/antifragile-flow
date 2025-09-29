#!/usr/bin/env python3
"""
Test starter for Organization Onboarding Workflow with LoRA Model Training

This script demonstrates the complete onboarding process including:
1. Document processing
2. LoRA model fine-tuning (Mistral-7B or Qwen-3B)
3. Ollama deployment
4. Research workflows (when available)
5. Competitor monitoring

Usage:
    python test/onboarding_with_training_starter.py
    python test/onboarding_with_training_starter.py --qwen  # Use Qwen-3B instead of Mistral-7B
"""

import asyncio
from datetime import datetime
from pathlib import Path
import sys
import tempfile

from temporalio.client import Client

from shared.config.defaults import get_temporal_address
from workflow.organization_onboarding_workflow import (
    OnboardingRequest,
    OrganizationOnboardingWorkflow,
)

# Sample test documents for onboarding
SAMPLE_DOCUMENTS = [
    {
        "filename": "company_values.txt",
        "content": """
        TechCorp Values and Mission Statement

        Our Mission: To revolutionize business operations through innovative technology solutions
        while maintaining the highest standards of customer service and ethical business practices.

        Core Values:
        1. Excellence - We strive for exceptional quality in everything we deliver
        2. Innovation - We embrace cutting-edge technology and creative problem-solving
        3. Integrity - We operate with transparency, honesty, and ethical standards
        4. Customer-Centricity - Our customers' success drives our strategic decisions
        5. Collaboration - We believe in teamwork and building strong partnerships

        Strategic Priorities (2024-2026):
        - Digital transformation leadership in our industry
        - Sustainable business practices and environmental responsibility
        - Expanding our market presence through strategic partnerships
        - Investing in employee development and organizational culture
        - Maintaining competitive advantage through R&D and innovation

        Communication Style:
        We communicate with clarity, professionalism, and strategic insight. Our messaging
        reflects our expertise while remaining accessible to diverse stakeholders. We
        emphasize data-driven decision making and results-oriented thinking.
        """,
    },
    {
        "filename": "strategic_plan.txt",
        "content": """
        TechCorp Strategic Plan 2024-2026

        Executive Summary:
        TechCorp is positioned to capitalize on emerging market opportunities through
        our differentiated technology platform and strong customer relationships.

        Market Analysis:
        - Growing demand for automated business solutions
        - Increasing focus on data security and privacy
        - Shift toward cloud-native and AI-powered tools
        - Competitive landscape consolidating around platform providers

        Strategic Initiatives:
        1. Product Innovation
           - AI/ML integration across our platform
           - Enhanced security and compliance features
           - Mobile-first user experience improvements

        2. Market Expansion
           - Enter European markets by Q3 2024
           - Develop partnerships with systems integrators
           - Launch industry-specific solution packages

        3. Operational Excellence
           - Implement agile development methodologies
           - Enhance customer success and support capabilities
           - Establish metrics-driven performance culture

        Success Metrics:
        - 40% revenue growth by end of 2025
        - 95% customer satisfaction scores
        - 50% reduction in time-to-market for new features
        - Industry leadership in security and compliance certifications
        """,
    },
    {
        "filename": "customer_feedback.txt",
        "content": """
        Customer Feedback Analysis - Q3 2024

        Overview:
        Comprehensive analysis of customer feedback from surveys, support tickets,
        and account management conversations.

        Key Themes:

        Positive Feedback:
        - "TechCorp's platform reliability is exceptional"
        - "The customer support team is knowledgeable and responsive"
        - "Integration capabilities exceeded our expectations"
        - "Security features give us confidence in our compliance"

        Areas for Improvement:
        - User interface could be more intuitive for new users
        - Documentation needs more practical examples
        - Mobile app functionality should match web platform
        - Reporting features need more customization options

        Customer Success Stories:
        1. Global Manufacturing Corp - 60% efficiency improvement
        2. Healthcare Systems Inc - Achieved HIPAA compliance in 30 days
        3. Financial Services LLC - Reduced processing time by 45%

        Recommendations:
        - Prioritize UI/UX improvements in Q4 roadmap
        - Expand documentation with video tutorials and use cases
        - Accelerate mobile app development timeline
        - Enhance reporting engine with advanced analytics

        Customer Retention: 94% (industry average: 78%)
        Net Promoter Score: 67 (industry average: 42)
        """,
    },
]


def create_test_document_files() -> list[str]:
    """Create temporary files for testing"""
    temp_dir = Path(tempfile.mkdtemp(prefix="onboarding_test_"))
    file_paths = []

    for doc in SAMPLE_DOCUMENTS:
        file_path = temp_dir / doc["filename"]
        with open(file_path, "w") as f:
            f.write(doc["content"])
        file_paths.append(str(file_path))

    print(f"📁 Created test documents in: {temp_dir}")
    return file_paths


async def run_onboarding_test(use_qwen: bool = False):
    """Run the complete onboarding test"""
    # Connect to Temporal
    client = await Client.connect(get_temporal_address())

    # Create test documents
    document_paths = create_test_document_files()

    # Determine base model
    base_model = "Qwen/Qwen2.5-3B-Instruct" if use_qwen else "mistralai/Mistral-7B-Instruct-v0.2"
    model_type = "Qwen-3B" if use_qwen else "Mistral-7B"

    print(f"🚀 Starting Onboarding Test with {model_type}")
    print(f"📄 Documents: {len(document_paths)} files")
    print(f"🤖 Base Model: {base_model}")
    print("")

    # Create onboarding request
    request = OnboardingRequest(
        organization_name="TechCorp",
        documents=document_paths,
        research_queries=[
            "What is TechCorp's competitive positioning?",
            "How does TechCorp differentiate from competitors?",
            "What are TechCorp's key growth opportunities?",
        ],
        competitors=["CompetitorA", "CompetitorB", "IndustryLeader"],
        admin_emails=["admin@techcorp.com"],
        priority="high",
        # Model training configuration
        enable_model_training=True,
        base_model=base_model,
        organizational_values=[
            "excellence",
            "innovation",
            "integrity",
            "customer-centricity",
            "collaboration",
        ],
        communication_style="professional, strategic, and data-driven",
        deploy_to_ollama=True,
    )

    # Generate unique workflow ID
    workflow_id = (
        f"onboarding-techcorp-{model_type.lower()}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    )

    try:
        # Execute the onboarding workflow
        result = await client.execute_workflow(
            OrganizationOnboardingWorkflow.run,
            request,
            id=workflow_id,
            task_queue="onboarding-task-queue",
        )

        print("\n" + "=" * 80)
        print(f"🎉 ONBOARDING COMPLETED FOR {request.organization_name}")
        print("=" * 80)
        print(f"Success: {result.success}")
        print(f"Duration: {(result.end_time - result.start_time).total_seconds() / 60:.1f} minutes")
        print(f"Workflow ID: {workflow_id}")
        print("")

        # Document processing results
        if result.document_results:
            print(
                f"📄 Documents Processed: {result.document_results.successful_documents}/{result.document_results.total_documents}"
            )
            print("")

        # Model training results
        if result.model_training_results:
            print("🤖 Model Training Results:")
            print(f"   Success: {result.model_training_results.success}")
            if result.model_training_results.success:
                print(
                    f"   Training Examples: {result.model_training_results.training_examples_generated}"
                )
                print(
                    f"   Training Duration: {result.model_training_results.training_duration_minutes:.1f} minutes"
                )
                print(f"   Model Path: {result.model_training_results.model_path}")
                if result.model_training_results.ollama_model_name:
                    print(f"   Ollama Model: {result.model_training_results.ollama_model_name}")
                    print(
                        f"   🚀 Test your model: ollama run {result.model_training_results.ollama_model_name}"
                    )
            else:
                print(f"   Error: {result.model_training_results.error_message}")
            print("")

        # Next steps
        if result.next_steps:
            print("📋 Recommended Next Steps:")
            for i, step in enumerate(result.next_steps, 1):
                print(f"   {i}. {step}")
            print("")

        print("✅ Test completed successfully!")

    except Exception as e:
        print(f"❌ Onboarding test failed: {e}")
        raise

    finally:
        # Cleanup temporary files
        import shutil

        temp_dir = Path(document_paths[0]).parent
        shutil.rmtree(temp_dir)
        print(f"🧹 Cleaned up test files: {temp_dir}")


if __name__ == "__main__":
    use_qwen = "--qwen" in sys.argv
    print("🧪 ONBOARDING WORKFLOW TEST")
    print(f"Model: {'Qwen-3B' if use_qwen else 'Mistral-7B'}")
    print("=" * 60)

    asyncio.run(run_onboarding_test(use_qwen))
