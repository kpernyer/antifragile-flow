#!/usr/bin/env python3
"""
Real Model Training Test with LoRA

This script tests actual ML training with the smaller Qwen-3B model
to demonstrate the complete LoRA fine-tuning flow.
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


def create_focused_documents():
    """Create focused documents for real training"""
    return [
        {
            "text": """
            TechCorp Innovation Philosophy

            At TechCorp, we believe that innovation is not just about technology—it's about
            solving real-world problems with ethical solutions. Our approach combines:

            • Human-centered design thinking
            • Sustainable technology development
            • Collaborative problem solving
            • Continuous learning and adaptation

            We value integrity above profit, sustainability over short-term gains,
            and meaningful impact over technological complexity.

            Our mission is to create technology that enhances human potential
            while protecting our shared environment.
            """,
            "title": "Innovation Philosophy",
            "type": "strategic_document",
        },
        {
            "text": """
            Product Development Standards

            Every TechCorp product must meet our excellence criteria:

            Quality Standards:
            - 99.9% reliability requirement
            - User-friendly interface design
            - Comprehensive security testing
            - Environmental impact assessment

            Development Process:
            - Agile methodologies with customer feedback loops
            - Peer code review requirements
            - Automated testing at every stage
            - Documentation-first approach

            Our products reflect our organizational values and commitment
            to responsible innovation.
            """,
            "title": "Development Standards",
            "type": "operational_document",
        },
    ]


async def test_real_lora_training():
    """Test real LoRA training with Qwen-3B"""

    print("🤖 REAL LORA TRAINING TEST WITH QWEN-3B")
    print("=" * 60)

    # Check ML availability
    print("\n🔧 CHECKING ML ENVIRONMENT")
    try:
        import torch
        from transformers import AutoTokenizer

        device = (
            "mps"
            if torch.backends.mps.is_available()
            else "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )
        print(f"   ✅ PyTorch available (device: {device})")
        print(
            f"   🧠 Memory available: {torch.mps.current_allocated_memory() / 1024**2:.1f} MB"
            if device == "mps"
            else ""
        )

        # Test small model loading
        model_name = "Qwen/Qwen2.5-3B-Instruct"
        print(f"   🔄 Testing model access: {model_name}")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        print(f"   ✅ Model accessible (vocab size: {tokenizer.vocab_size})")

    except Exception as e:
        print(f"   ❌ ML environment issue: {e}")
        return False

    # Initialize service
    print("\n🏗️  INITIALIZING TRAINING SERVICE")
    config = {
        "models_dir": "./models_test",
        "training_data_dir": "./training_data_test",
        "jobs_dir": "./jobs_test",
    }
    service = ModelTrainingService(config)

    # Create training request with smaller model
    print("\n📋 CREATING TRAINING REQUEST")
    documents = create_focused_documents()
    request = TrainingJobRequest(
        organization_name="TechCorp Inc",
        organization_id="techcorp_test",
        documents=documents,
        model_type=ModelType.QWEN_3B,  # Use smaller model
        organizational_values=["innovation", "integrity", "sustainability"],
        communication_style="professional",
        priority="high",
        deploy_to_ollama=False,  # Skip Ollama for this test
        requester_email="test@techcorp.com",
    )

    print(f"   🤖 Model: {request.model_type.value}")
    print(f"   📚 Documents: {len(request.documents)}")
    print(f"   🎯 Values: {request.organizational_values}")

    # Submit training job
    print("\n🚀 SUBMITTING TRAINING JOB")
    job_id = await service.submit_training_job(request)
    print(f"   ✅ Job ID: {job_id}")

    # Monitor progress with longer timeout for real training
    print("\n📊 MONITORING TRAINING PROGRESS")
    import time

    max_wait_time = 1800  # 30 minutes max for real training
    check_interval = 10  # Check every 10 seconds
    start_time = time.time()

    while time.time() - start_time < max_wait_time:
        job_status = service.get_job_status(job_id)

        if job_status:
            elapsed = time.time() - start_time
            print(f"   [{elapsed:6.1f}s] Status: {job_status.status.value}")

            if job_status.status == TrainingJobStatus.COMPLETED:
                print("   🎉 Real LoRA training completed!")
                break
            elif job_status.status == TrainingJobStatus.FAILED:
                print(f"   ❌ Training failed: {job_status.error_message}")
                break
            elif job_status.status == TrainingJobStatus.TRAINING:
                print("   🔄 LoRA fine-tuning in progress...")

        await asyncio.sleep(check_interval)
    else:
        print("   ⏰ Training timeout reached")

    # Show results
    print("\n📈 TRAINING RESULTS")
    final_status = service.get_job_status(job_id)

    if final_status:
        print(f"   📊 Final Status: {final_status.status.value}")
        print(f"   ⏱️  Duration: {final_status.training_duration_minutes:.1f} minutes")
        print(f"   📚 Training Examples: {final_status.training_examples_count}")

        if final_status.model_location:
            model_path = Path(final_status.model_location)
            print(f"   📁 Model Location: {model_path}")

            # Check if model files exist
            if model_path.exists():
                files = list(model_path.glob("*"))
                print(f"   📄 Model Files: {len(files)} files created")
                for file in files[:5]:  # Show first 5 files
                    print(f"      - {file.name}")

        if final_status.error_message:
            print(f"   ❌ Error: {final_status.error_message}")

    print("\n✅ REAL TRAINING TEST COMPLETE")
    return final_status and final_status.status == TrainingJobStatus.COMPLETED


async def main():
    """Main test function"""
    try:
        success = await test_real_lora_training()

        if success:
            print("\n🎊 SUCCESS: Real LoRA training completed!")
            print("\n💡 What happened:")
            print("   1. Loaded Qwen-3B-Instruct model")
            print("   2. Generated training examples from documents")
            print("   3. Applied LoRA (Low-Rank Adaptation)")
            print("   4. Fine-tuned with organizational data")
            print("   5. Saved adapted model weights")
        else:
            print("\n⚠️  Training test did not complete successfully")

    except Exception as e:
        logger.error(f"Real training test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
