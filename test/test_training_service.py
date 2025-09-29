#!/usr/bin/env python3
"""
Isolated Model Training Service Test

This script tests the model training service directly without Temporal workflows.
It shows the complete flow from document input to model training.
"""

import asyncio
import logging
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from service.model_training_service import (
    ModelTrainingService,
    ModelType,
    TrainingJobRequest,
    TrainingJobStatus,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def create_sample_documents():
    """Create sample documents for training"""
    return [
        {
            "text": """
            TechCorp Inc. Strategic Vision 2024

            Our organization is committed to excellence and innovation in technology solutions.
            We believe in sustainable growth, ethical business practices, and empowering our teams.

            Core Values:
            - Excellence in everything we do
            - Innovation through creative problem solving
            - Integrity and transparency in all relationships
            - Sustainability for future generations

            Strategic Objectives:
            - Develop cutting-edge AI solutions
            - Expand market presence in emerging technologies
            - Foster a culture of continuous learning
            - Build strong partnerships with industry leaders
            """,
            "title": "TechCorp Strategic Vision 2024",
            "type": "strategic_document",
        },
        {
            "text": """
            Q3 Financial Performance Summary

            Revenue Growth: 15% quarter-over-quarter
            Customer Satisfaction: 92% (industry leading)
            Employee Retention: 94% (above industry average)

            Key Achievements:
            - Launched new AI platform with 10,000+ users
            - Signed 3 major enterprise contracts
            - Expanded team by 25% with top talent
            - Achieved carbon neutral operations

            Market Position:
            We continue to lead in innovative technology solutions while maintaining
            our commitment to sustainable and ethical business practices.
            """,
            "title": "Q3 Financial Performance",
            "type": "financial_report",
        },
        {
            "text": """
            Product Development Guidelines

            At TechCorp, we follow rigorous development standards to ensure quality
            and innovation in all our products:

            Development Principles:
            - User-centered design approach
            - Agile development methodologies
            - Continuous testing and iteration
            - Security-first implementation

            Quality Standards:
            - 99.9% uptime requirement
            - Sub-100ms response times
            - Zero-tolerance for security vulnerabilities
            - Comprehensive documentation required

            Our development process reflects our organizational commitment to
            excellence and our responsibility to deliver exceptional value to customers.
            """,
            "title": "Product Development Guidelines",
            "type": "operational_document",
        },
    ]


async def test_model_training_flow():
    """Test the complete model training flow"""

    print("🚀 ISOLATED MODEL TRAINING TEST")
    print("=" * 60)

    # Initialize service
    print("\n📋 1. INITIALIZING TRAINING SERVICE")
    service = ModelTrainingService()
    print(f"   ✅ Service initialized (enabled: {service.enabled})")
    print(f"   📁 Models directory: {service.models_dir}")
    print(f"   📁 Training data directory: {service.training_data_dir}")
    print(f"   📁 Jobs directory: {service.jobs_dir}")

    # Check ML dependencies
    try:
        import torch
        from transformers import AutoTokenizer

        ml_available = True
        device = (
            "mps"
            if torch.backends.mps.is_available()
            else "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )
        print(f"   🔧 ML dependencies available (device: {device})")
    except ImportError:
        ml_available = False
        print("   ⚠️  ML dependencies not available - will use mock training")

    # Create sample training data
    print("\n📄 2. PREPARING TRAINING DATA")
    documents = create_sample_documents()
    print(f"   📚 Created {len(documents)} sample documents")

    for i, doc in enumerate(documents, 1):
        print(f"   {i}. {doc['title']} ({len(doc['text'])} chars)")

    # Create training job request
    print("\n⚙️  3. CREATING TRAINING JOB REQUEST")
    request = TrainingJobRequest(
        organization_name="TechCorp Inc",
        organization_id="techcorp_001",
        documents=documents,
        model_type=ModelType.MISTRAL_7B,  # Start with Mistral
        organizational_values=["excellence", "innovation", "integrity", "sustainability"],
        communication_style="professional",
        priority="high",
        deploy_to_ollama=True,
        requester_email="test@techcorp.com",
    )

    print(f"   🏢 Organization: {request.organization_name}")
    print(f"   🤖 Model type: {request.model_type.value}")
    print(f"   📝 Values: {request.organizational_values}")
    print(f"   💬 Style: {request.communication_style}")
    print(f"   🚀 Deploy to Ollama: {request.deploy_to_ollama}")

    # Submit training job
    print("\n🎯 4. SUBMITTING TRAINING JOB")
    job_id = await service.submit_training_job(request)
    print(f"   ✅ Job submitted with ID: {job_id}")

    # Monitor job progress
    print("\n📊 5. MONITORING JOB PROGRESS")
    import time

    max_wait_time = 300  # 5 minutes max
    check_interval = 2  # Check every 2 seconds
    start_time = time.time()

    while time.time() - start_time < max_wait_time:
        job_status = service.get_job_status(job_id)

        if job_status:
            elapsed = time.time() - start_time
            print(f"   [{elapsed:6.1f}s] Status: {job_status.status.value}")

            if job_status.status == TrainingJobStatus.COMPLETED:
                print("   🎉 Training completed successfully!")
                break
            elif job_status.status == TrainingJobStatus.FAILED:
                print(f"   ❌ Training failed: {job_status.error_message}")
                break
            elif job_status.status == TrainingJobStatus.TRAINING:
                print("   🔄 Training in progress...")

        await asyncio.sleep(check_interval)
    else:
        print("   ⏰ Training taking longer than expected...")

    # Show final results
    print("\n📈 6. FINAL RESULTS")
    final_status = service.get_job_status(job_id)

    if final_status:
        print(f"   📊 Status: {final_status.status.value}")
        print(f"   ⏱️  Duration: {final_status.training_duration_minutes:.1f} minutes")
        print(f"   📚 Training examples: {final_status.training_examples_count}")

        if final_status.model_location:
            print(f"   📁 Model location: {final_status.model_location}")

        if final_status.ollama_model_name:
            print(f"   🤖 Ollama model: {final_status.ollama_model_name}")
            print("   💡 You can now test the model with:")
            print(f"      ollama run {final_status.ollama_model_name}")

        if final_status.error_message:
            print(f"   ❌ Error: {final_status.error_message}")

    # Test organizational jobs listing
    print("\n📋 7. ORGANIZATION JOBS HISTORY")
    org_jobs = service.list_organization_jobs("techcorp_001")
    print(f"   📊 Found {len(org_jobs)} jobs for organization")

    for job in org_jobs:
        print(f"   • {job.job_id}: {job.status.value}")

    print("\n✅ MODEL TRAINING TEST COMPLETE")
    print("=" * 60)

    return final_status


async def main():
    """Main test function"""
    try:
        result = await test_model_training_flow()

        if result and result.status == TrainingJobStatus.COMPLETED:
            print("\n🎊 SUCCESS: Model training completed successfully!")

            if result.ollama_model_name:
                print("\n💡 Next Steps:")
                print(f"   1. Test the model: ollama run {result.ollama_model_name}")
                print("   2. Try a query: 'What are TechCorp's core values?'")
                print("   3. Ask for strategic analysis of business scenarios")

        else:
            print("\n⚠️  Training did not complete as expected")

    except Exception as e:
        logger.error(f"Test failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
