#!/usr/bin/env python3
"""
Temporal OpenAI Worker - Remote API Activities

This worker handles activities that make remote OpenAI API calls.
Separating these allows for better resource management and cost control.

Responsibilities:
- OpenAI API calls via agents framework
- Document analysis using GPT models
- Research and synthesis activities
- Catchball interactions
- Wisdom synthesis

Architecture:
Worker (openai-queue) -> AI Activities -> OpenAI API

Note: This worker requires OpenAI API key and agents dependencies
"""

import asyncio
import logging

from temporalio.client import Client
from temporalio.worker import Worker

from agent_activity.ai_activities import (
    analyze_document_content,
    generate_document_summary,
    perform_simple_research,
    run_catchball,
    synthesize_wisdom,
)

# Import shared configuration
from shared.config.defaults import OPENAI_QUEUE, get_temporal_address

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """
    OpenAI worker function

    Registers activities that require OpenAI API access.
    """
    logger.info("Starting OpenAI Worker")

    # Connect to Temporal
    temporal_address = get_temporal_address()
    client = await Client.connect(temporal_address)
    logger.info(f"Connected to Temporal at {temporal_address}")

    # Create worker with OpenAI activities
    worker = Worker(
        client,
        task_queue=OPENAI_QUEUE,
        workflows=[],  # No workflows, only activities
        activities=[
            # AI-powered document activities
            analyze_document_content,
            generate_document_summary,
            # Research activities
            perform_simple_research,
            # Demo interaction activities
            run_catchball,
            synthesize_wisdom,
        ],
    )

    logger.info(f"OpenAI Worker configured for task queue: {OPENAI_QUEUE}")
    logger.info("Registered OpenAI activities:")
    logger.info("  - analyze_document_content (GPT-4 analysis)")
    logger.info("  - generate_document_summary (Quick summaries)")
    logger.info("  - perform_simple_research (Research queries)")
    logger.info("  - run_catchball (Interactive refinement)")
    logger.info("  - synthesize_wisdom (Crowd synthesis)")

    logger.info("Architecture: OpenAI Worker <-> Agents Framework <-> OpenAI API")
    logger.info("API: OpenAI GPT models (requires API key)")

    # Start worker
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
