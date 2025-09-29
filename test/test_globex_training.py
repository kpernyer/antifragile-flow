#!/usr/bin/env python3
"""
Test script for training a LoRA model on Globex Industrial Group documents.
"""

import asyncio
from pathlib import Path
import sys

# Add service to path
sys.path.append(str(Path(__file__).parent.parent))

from service.model_training_service import (
    ModelTrainingService,
    ModelType,
    TrainingJobRequest,
    TrainingJobStatus,
)


async def prepare_globex_training_documents() -> list[dict]:
    """
    Prepare Globex documents for training.
    """
    documents = [
        {
            "text": "Globex Industrial Group is a leading multinational manufacturer of advanced equipment and solutions for heavy industry and infrastructure. Our tagline is 'Innovating Tomorrow's Infrastructure' and we focus on delivering cutting-edge solutions across four main product lines.",
            "title": "Company Overview",
            "type": "corporate_profile",
        },
        {
            "text": "At Globex Industrial Group, we are committed to innovation, sustainability, and infrastructure excellence. We believe in innovating tomorrow's infrastructure through advanced engineering, sustainable manufacturing practices, and delivering reliable solutions that power the world's most critical industrial operations.",
            "title": "Core Values",
            "type": "corporate_values",
        },
        {
            "text": "Globex Industrial Group is deeply committed to sustainable manufacturing and environmental responsibility. Our sustainability initiatives focus on reducing environmental impact through efficient power systems, automated processes that minimize waste, and construction equipment designed for longevity and energy efficiency.",
            "title": "Sustainability Approach",
            "type": "sustainability_report",
        },
        {
            "text": "Globex offers advanced power distribution systems, including our flagship GX-PDS-2024 power distribution system. Our power systems are engineered for reliability, efficiency, and scalability in heavy industrial applications.",
            "title": "Power Systems Product Line",
            "type": "technical_specification",
        },
        {
            "text": "Globex provides comprehensive industrial automation control systems, including our GX-ACS-2024 automation control system. Our automation solutions integrate seamlessly with existing industrial infrastructure, offering advanced control capabilities, real-time monitoring, and intelligent process optimization.",
            "title": "Automation & Controls",
            "type": "technical_specification",
        },
    ]

    return documents


async def prepare_globex_training_data() -> list[dict]:
    """
    This would typically be generated from the documents.
    For this test, we'll create sample instruction-response pairs.
    """
    training_data = [
        # Company Overview and Identity
        {
            "instruction": "What is Globex Industrial Group?",
            "response": "Globex Industrial Group is a leading multinational manufacturer of advanced equipment and solutions for heavy industry and infrastructure. Our tagline is 'Innovating Tomorrow's Infrastructure' and we focus on delivering cutting-edge solutions across four main product lines: Power Systems, Automation & Controls, Material Handling, and Construction Equipment.",
        },
        {
            "instruction": "What are Globex's core values?",
            "response": "At Globex Industrial Group, we are committed to innovation, sustainability, and infrastructure excellence. We believe in innovating tomorrow's infrastructure through advanced engineering, sustainable manufacturing practices, and delivering reliable solutions that power the world's most critical industrial operations.",
        },
        {
            "instruction": "Describe Globex's approach to sustainability.",
            "response": "Globex Industrial Group is deeply committed to sustainable manufacturing and environmental responsibility. Our sustainability initiatives focus on reducing environmental impact through efficient power systems, automated processes that minimize waste, and construction equipment designed for longevity and energy efficiency. We believe sustainable practices are essential for innovating tomorrow's infrastructure.",
        },
        # Product Lines
        {
            "instruction": "What power systems does Globex offer?",
            "response": "Globex offers advanced power distribution systems, including our flagship GX-PDS-2024 power distribution system. Our power systems are engineered for reliability, efficiency, and scalability in heavy industrial applications. We focus on delivering robust power infrastructure solutions that meet the demanding requirements of modern industrial facilities.",
        },
        {
            "instruction": "Tell me about Globex's automation and control systems.",
            "response": "Globex provides comprehensive industrial automation control systems, including our GX-ACS-2024 automation control system. Our automation solutions integrate seamlessly with existing industrial infrastructure, offering advanced control capabilities, real-time monitoring, and intelligent process optimization for manufacturing and industrial operations.",
        },
        {
            "instruction": "What material handling solutions does Globex provide?",
            "response": "Globex specializes in advanced material handling solutions including conveyor systems, Automated Storage and Retrieval Systems (AS/RS), and robotic handling equipment. Our material handling systems are designed to optimize workflow efficiency, reduce operational costs, and integrate with existing industrial automation infrastructure.",
        },
        {
            "instruction": "Describe Globex's construction equipment.",
            "response": "Globex manufactures heavy construction equipment designed for infrastructure development projects. Our construction equipment catalog includes machinery engineered for durability, efficiency, and performance in demanding construction environments. We focus on equipment that supports large-scale infrastructure development and industrial construction projects.",
        },
        # Technical Excellence
        {
            "instruction": "How does Globex ensure product quality?",
            "response": "Globex Industrial Group maintains the highest standards of product quality through rigorous engineering processes, comprehensive testing protocols, and continuous innovation. Our products undergo extensive quality assurance testing to ensure reliability and performance in critical industrial applications. We are committed to delivering solutions that exceed industry standards.",
        },
        {
            "instruction": "What makes Globex different from competitors?",
            "response": "Globex Industrial Group differentiates itself through our comprehensive approach to industrial solutions, combining advanced engineering with sustainable practices. Our integrated product portfolio spans power systems, automation, material handling, and construction equipment, allowing us to provide complete infrastructure solutions. Our commitment to innovation and sustainability positions us as a leader in industrial equipment manufacturing.",
        },
        # Customer Focus
        {
            "instruction": "Who are Globex's typical customers?",
            "response": "Globex Industrial Group serves a diverse range of customers including manufacturing facilities, power generation companies, construction contractors, and infrastructure development organizations. Our solutions are designed for enterprises that require reliable, high-performance industrial equipment and systems for mission-critical operations.",
        },
        {
            "instruction": "How does Globex support its customers?",
            "response": "Globex provides comprehensive customer support including technical documentation, user manuals, training programs, and ongoing maintenance services. We believe in building long-term partnerships with our customers by ensuring they have the knowledge and support needed to maximize the value of their Globex equipment and systems.",
        },
    ]

    return training_data


async def test_globex_lora_training():
    """Test LoRA training with Globex Industrial Group data."""
    print("🏭 Starting Globex Industrial Group LoRA Training Test")
    print("=" * 60)

    # Initialize training service
    training_service = ModelTrainingService()

    # Prepare training documents
    print("📋 Preparing Globex training documents...")
    documents = await prepare_globex_training_documents()
    print(f"✅ Prepared {len(documents)} training documents")

    # Create training job request
    training_request = TrainingJobRequest(
        organization_name="Globex Industrial Group",
        organization_id="globex-industrial",
        documents=documents,
        model_type=ModelType.QWEN_3B,
        organizational_values=[
            "Innovation in industrial infrastructure",
            "Sustainability and environmental responsibility",
            "Technical excellence and reliability",
            "Comprehensive industrial solutions",
            "Customer partnership and support",
        ],
        communication_style="professional and technical",
        priority="normal",
        deploy_to_ollama=True,
        requester_email=None,
    )

    print(f"🚀 Submitting training job for organization: {training_request.organization_id}")
    print(f"📊 Model type: {training_request.model_type.value}")
    print(f"📈 Training documents: {len(training_request.documents)}")
    print(
        f"🎯 Organizational values: {len(training_request.organizational_values) if training_request.organizational_values else 0}"
    )

    # Submit training job
    try:
        job_id = await training_service.submit_training_job(training_request)
        print("✅ Training job submitted successfully!")
        print(f"🔍 Job ID: {job_id}")

        # Monitor training progress
        print("\n⏳ Monitoring training progress...")
        max_attempts = 30  # Max 5 minutes at 10-second intervals
        attempt = 0

        while attempt < max_attempts:
            attempt += 1
            status = training_service.get_job_status(job_id)

            print(f"📊 Attempt {attempt}: Status = {status.status.value}")

            if status.status == TrainingJobStatus.COMPLETED:
                print("✅ Training completed successfully!")
                print(f"📁 Model saved to: {status.model_location}")
                print(f"⏱️ Training duration: {status.training_duration_minutes:.2f} minutes")

                # Test the trained model
                await test_trained_model(status.model_location)
                break
            elif status.status == TrainingJobStatus.FAILED:
                print(f"❌ Training failed: {status.error_message}")
                break
            elif status.status in [TrainingJobStatus.QUEUED, TrainingJobStatus.TRAINING]:
                print("⏳ Training in progress...")
                await asyncio.sleep(10)  # Wait 10 seconds
            else:
                print(f"❓ Unknown status: {status.status}")
                await asyncio.sleep(5)

        if attempt >= max_attempts:
            print("⏰ Training monitoring timeout - check job status later")

    except Exception as e:
        print(f"❌ Training failed with error: {e}")
        raise


async def test_trained_model(model_path: str):
    """Test the trained model with Globex-specific prompts."""
    print(f"\n🧪 Testing trained model at: {model_path}")
    print("=" * 60)

    # Test questions to validate organizational training
    test_questions = [
        "What is your company's mission?",
        "How does your organization approach sustainability?",
        "What products does your company offer?",
        "What makes your company unique in the market?",
    ]

    for question in test_questions:
        print(f"❓ Question: {question}")
        # Note: In a real implementation, we would load and query the model here
        # For now, we'll just indicate the test structure
        print("🤖 Response: [Model response would be generated here]")
        print()


if __name__ == "__main__":
    asyncio.run(test_globex_lora_training())
