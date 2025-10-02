#!/usr/bin/env python3
"""
Temporal ML Worker - Machine Learning Activities

This worker handles ML training and model-related activities that require
specialized compute resources and ML libraries.

Responsibilities:
- LoRA fine-tuning of local models (Mistral, Qwen)
- Model training job management
- ML model testing and evaluation

Architecture:
Worker (ml-queue) -> ML Activities -> Local ML Training

Note: This worker requires ML dependencies (torch, transformers, peft, trl)
"""

import asyncio
import logging

from temporalio.client import Client
from temporalio.worker import Worker

from activity.model_training_activities import (
    train_organizational_model,
    test_qwen_model,
)

# Import shared configuration
from shared.config.defaults import ML_QUEUE, get_temporal_address

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """
    ML worker function

    Registers ML-specific activities that require specialized compute resources.
    """
    logger.info("Starting ML Worker")

    # Connect to Temporal
    temporal_address = get_temporal_address()
    client = await Client.connect(temporal_address)
    logger.info(f"Connected to Temporal at {temporal_address}")

    # Create worker with ML activities
    worker = Worker(
        client,
        task_queue=ML_QUEUE,
        workflows=[],  # No workflows, only activities
        activities=[
            # ML training activities
            train_organizational_model,
            test_qwen_model,
        ],
    )

    logger.info(f"ML Worker configured for task queue: {ML_QUEUE}")
    logger.info("Registered ML activities:")
    logger.info("  - train_organizational_model (LoRA fine-tuning)")
    logger.info("  - test_qwen_model (Model testing)")

    logger.info("Architecture: ML Worker <-> Local ML Training")
    logger.info("Compute Resources: GPU/MPS/CPU (auto-detected)")
    logger.info("Supported Models: Mistral-7B, Qwen-3B variants")

    # Start worker
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
