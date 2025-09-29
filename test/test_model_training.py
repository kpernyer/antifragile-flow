#!/usr/bin/env python3
"""
Test script for LoRA model training with both Mistral-7B and Qwen-3B

This script demonstrates:
1. Training with Mistral-7B-Instruct-v0.2 (larger, more capable)
2. Training with Qwen-3B-Instruct (smaller, faster)
3. Comparing results and performance
4. Testing Ollama deployment
"""

import asyncio
import logging
import sys

from temporalio import activity

from activity.model_training_activities import (
    ModelTrainingRequest,
    test_qwen_model,
    train_organizational_model,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample organizational documents for testing
SAMPLE_DOCUMENTS = [
    {
        "text": """
        Our company values excellence in everything we do. We believe in innovation-driven growth
        and maintaining the highest standards of integrity in all our business practices.

        Our strategic priorities focus on:
        1. Customer-centric product development
        2. Sustainable business practices
        3. Technological innovation and digital transformation
        4. Building strong partnerships and collaborative relationships

        We communicate with clarity, transparency, and professionalism. Our organizational culture
        emphasizes continuous learning, adaptability, and results-oriented thinking.
        """,
        "title": "Organizational Values and Strategy",
        "type": "strategic_document",
    },
    {
        "text": """
        Communication Guidelines for Our Organization:

        - Use clear, concise language that reflects our professional standards
        - Always consider our strategic context when providing recommendations
        - Maintain consistency with our core values of excellence, innovation, and integrity
        - Focus on actionable insights that drive organizational success
        - Ensure all communications align with our customer-centric approach

        When responding to stakeholders, remember that we are committed to transparency
        while maintaining competitive confidentiality. Our responses should demonstrate
        our expertise while remaining accessible to diverse audiences.
        """,
        "title": "Communication Standards",
        "type": "communication_guide",
    },
    {
        "text": """
        Market Position and Competitive Advantages:

        We operate in a dynamic market environment where innovation and customer satisfaction
        are key differentiators. Our competitive advantages include:

        - Deep domain expertise and technical capabilities
        - Strong customer relationships built on trust and reliability
        - Agile development processes that enable rapid adaptation
        - Commitment to sustainable and responsible business practices

        Our market strategy emphasizes building long-term value through strategic partnerships,
        continuous innovation, and maintaining our position as a trusted industry leader.
        We prioritize quality over volume and focus on markets where we can deliver
        exceptional value to our customers.
        """,
        "title": "Market Strategy Document",
        "type": "strategic_analysis",
    },
]


async def test_mistral_training():
    """Test training with Mistral-7B model"""
    logger.info("🚀 Testing Mistral-7B-Instruct-v0.2 Training")

    request = ModelTrainingRequest(
        organization_name="Test Organization",
        organization_id="test-org",
        documents=SAMPLE_DOCUMENTS,
        base_model="mistralai/Mistral-7B-Instruct-v0.2",
        training_examples=10,  # Reduced for testing
        epochs=1,  # Quick training for demo
        organizational_values=["excellence", "innovation", "customer-centricity"],
        communication_style="professional and strategic",
        deploy_to_ollama=True,
    )

    # Mock activity context for testing
    class MockActivity:
        logger = logger

    # Temporarily set activity context
    original_activity = activity.logger if hasattr(activity, "logger") else None
    activity.logger = MockActivity.logger

    try:
        result = await train_organizational_model(request)

        logger.info("=== MISTRAL-7B TRAINING RESULTS ===")
        logger.info(f"Success: {result.success}")
        logger.info(f"Training Duration: {result.training_duration_minutes:.1f} minutes")
        logger.info(f"Training Examples: {result.training_examples_generated}")
        logger.info(f"Model Path: {result.model_path}")
        logger.info(f"Ollama Model: {result.ollama_model_name}")

        if result.error_message:
            logger.error(f"Error: {result.error_message}")

        return result

    finally:
        # Restore original activity context
        if original_activity:
            activity.logger = original_activity


async def test_qwen_training():
    """Test training with Qwen-3B model"""
    logger.info("🚀 Testing Qwen-3B-Instruct Training")

    request = ModelTrainingRequest(
        organization_name="Test Organization",
        organization_id="test-org-qwen",
        documents=SAMPLE_DOCUMENTS,
        base_model="Qwen/Qwen2.5-3B-Instruct",  # Smaller model
        training_examples=10,  # Reduced for testing
        epochs=1,  # Quick training for demo
        organizational_values=["excellence", "innovation", "customer-centricity"],
        communication_style="professional and strategic",
        deploy_to_ollama=True,
    )

    # Mock activity context for testing
    class MockActivity:
        logger = logger

    # Temporarily set activity context
    original_activity = activity.logger if hasattr(activity, "logger") else None
    activity.logger = MockActivity.logger

    try:
        result = await train_organizational_model(request)

        logger.info("=== QWEN-3B TRAINING RESULTS ===")
        logger.info(f"Success: {result.success}")
        logger.info(f"Training Duration: {result.training_duration_minutes:.1f} minutes")
        logger.info(f"Training Examples: {result.training_examples_generated}")
        logger.info(f"Model Path: {result.model_path}")
        logger.info(f"Ollama Model: {result.ollama_model_name}")

        if result.error_message:
            logger.error(f"Error: {result.error_message}")

        return result

    finally:
        # Restore original activity context
        if original_activity:
            activity.logger = original_activity


async def test_qwen_base_model():
    """Test Qwen base model functionality"""
    logger.info("🧪 Testing Qwen-3B Base Model")

    # Mock activity context for testing
    class MockActivity:
        logger = logger

    original_activity = activity.logger if hasattr(activity, "logger") else None
    activity.logger = MockActivity.logger

    try:
        result = await test_qwen_model(
            organization_name="Test Organization",
            test_prompt="What are the key principles for organizational communication?",
        )

        logger.info("=== QWEN-3B BASE MODEL TEST ===")
        logger.info(f"Success: {result['success']}")
        if result["success"]:
            logger.info(f"Model: {result['model_name']}")
            logger.info(f"Model Size: {result['model_size_gb']}")
            logger.info(f"Test Response: {result['response'][:200]}...")
        else:
            logger.error(f"Error: {result['error']}")

        return result

    finally:
        if original_activity:
            activity.logger = original_activity


def compare_results(mistral_result, qwen_result):
    """Compare training results between models"""
    logger.info("\n" + "=" * 60)
    logger.info("📊 COMPARISON: MISTRAL-7B vs QWEN-3B")
    logger.info("=" * 60)

    comparison = {
        "Model": ["Mistral-7B-Instruct-v0.2", "Qwen-3B-Instruct"],
        "Success": [mistral_result.success, qwen_result.success],
        "Training Time (min)": [
            f"{mistral_result.training_duration_minutes:.1f}",
            f"{qwen_result.training_duration_minutes:.1f}",
        ],
        "Training Examples": [
            mistral_result.training_examples_generated,
            qwen_result.training_examples_generated,
        ],
        "Ollama Deployed": [
            "✅" if mistral_result.ollama_model_name else "❌",
            "✅" if qwen_result.ollama_model_name else "❌",
        ],
    }

    # Print comparison table
    for key, values in comparison.items():
        logger.info(f"{key:20} | {values[0]!s:25} | {values[1]!s:25}")

    logger.info("\n💡 RECOMMENDATIONS:")
    if mistral_result.success and qwen_result.success:
        logger.info("✅ Both models trained successfully!")
        logger.info("📝 Mistral-7B: Better for complex reasoning and detailed responses")
        logger.info("⚡ Qwen-3B: Faster training and inference, good for quick responses")
        logger.info("🎯 Choose based on your use case: accuracy vs speed")
    elif mistral_result.success:
        logger.info("✅ Mistral-7B trained successfully")
        logger.info("❌ Qwen-3B training failed - check dependencies and system resources")
    elif qwen_result.success:
        logger.info("❌ Mistral-7B training failed - may need more memory/time")
        logger.info("✅ Qwen-3B trained successfully - good for resource-constrained environments")
    else:
        logger.info("❌ Both models failed to train - check system setup and dependencies")


def print_ollama_usage(mistral_result, qwen_result):
    """Print Ollama usage instructions"""
    logger.info("\n" + "=" * 60)
    logger.info("🔧 OLLAMA USAGE INSTRUCTIONS")
    logger.info("=" * 60)

    if mistral_result.ollama_model_name:
        logger.info(f"🎯 Mistral-7B Model: {mistral_result.ollama_model_name}")
        logger.info(f"   Usage: ollama run {mistral_result.ollama_model_name}")
        logger.info("   Best for: Complex analysis and detailed organizational insights")
        logger.info("")

    if qwen_result.ollama_model_name:
        logger.info(f"⚡ Qwen-3B Model: {qwen_result.ollama_model_name}")
        logger.info(f"   Usage: ollama run {qwen_result.ollama_model_name}")
        logger.info("   Best for: Quick responses and lightweight organizational Q&A")
        logger.info("")

    if mistral_result.ollama_model_name or qwen_result.ollama_model_name:
        logger.info("💬 Example conversation:")
        logger.info("   User: What are our core organizational values?")
        logger.info("   AI: Based on our organizational principles, our core values are...")
        logger.info("")
        logger.info("📖 Learn more: https://ollama.ai/docs")


async def main():
    """Main test function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--qwen-only":
        logger.info("Testing Qwen models only")
        qwen_base_result = await test_qwen_base_model()
        qwen_result = await test_qwen_training()
        return

    if len(sys.argv) > 1 and sys.argv[1] == "--mistral-only":
        logger.info("Testing Mistral model only")
        mistral_result = await test_mistral_training()
        return

    # Test both models
    logger.info("🔬 COMPREHENSIVE MODEL TRAINING TEST")
    logger.info("Testing both Mistral-7B and Qwen-3B models")
    logger.info("This will take several minutes depending on your hardware...\n")

    # Test Qwen base model first (quick test)
    logger.info("Step 1: Testing Qwen base model functionality")
    qwen_base_result = await test_qwen_base_model()

    if not qwen_base_result["success"]:
        logger.warning("Qwen base model test failed, skipping Qwen training")
        logger.info("Step 2: Testing Mistral-7B training only")
        mistral_result = await test_mistral_training()
        return

    # Run both training processes
    logger.info("Step 2: Training both models")
    mistral_task = asyncio.create_task(test_mistral_training())
    qwen_task = asyncio.create_task(test_qwen_training())

    # Wait for both to complete
    mistral_result, qwen_result = await asyncio.gather(mistral_task, qwen_task)

    # Compare results
    compare_results(mistral_result, qwen_result)
    print_ollama_usage(mistral_result, qwen_result)

    logger.info("\n🎉 Model training test completed!")


if __name__ == "__main__":
    # Handle missing dependencies gracefully
    try:
        asyncio.run(main())
    except ImportError as e:
        logger.error(f"Missing dependencies: {e}")
        logger.error(
            "Please install: pip install torch transformers peft trl datasets bitsandbytes"
        )
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test failed: {e}")
        sys.exit(1)
