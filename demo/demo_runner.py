#!/usr/bin/env python3
"""
Demo runner to help test the multi-user workflows
"""

import asyncio
from datetime import datetime

from src.users import get_all_users
from src.workflows import CompetitorAnalysisWorkflow, StrategicDecisionWorkflow
from temporalio.client import Client


async def main():
    print("🏢 Antifragile Flow Demo - Temporal Multi-User Workflows")
    print("=" * 60)

    # Connect to Temporal
    try:
        client = await Client.connect("localhost:7233")
        print("✅ Connected to Temporal server")
    except Exception as e:
        print(f"❌ Failed to connect to Temporal server: {e}")
        print("Make sure Temporal server is running: make temporal")
        return

    # Show available users
    users = get_all_users()
    print("\n👥 Available Users:")
    for user_id, user in users.items():
        print(f"  {user_id}: {user.name} ({user.role})")

    print("\n🚀 Demo Scenarios:")
    print("1. Strategic Decision Workflow")
    print("   - CEO proposes a decision")
    print("   - VPs provide feedback")
    print("   - CEO makes final decision")
    print()
    print("2. Competitor Analysis Workflow")
    print("   - VP Sales reports threat")
    print("   - Engineering analyzes technical impact")
    print("   - Legal analyzes legal implications")
    print("   - CEO decides strategy")

    choice = input("\nSelect scenario (1 or 2): ").strip()

    if choice == "1":
        await demo_strategic_decision(client)
    elif choice == "2":
        await demo_competitor_analysis(client)
    else:
        print("❌ Invalid choice")


async def demo_strategic_decision(client):
    workflow_id = f"demo-strategic-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    proposal = "Acquire TechCorp for $50M to expand our AI capabilities"

    print("\n🚀 Starting Strategic Decision Workflow")
    print(f"Proposal: {proposal}")
    print(f"Workflow ID: {workflow_id}")

    try:
        # Start the workflow
        await client.start_workflow(
            StrategicDecisionWorkflow.run, proposal, id=workflow_id, task_queue="hackathon"
        )

        print("✅ Workflow started successfully!")
        print("\n📋 Next steps:")
        print("1. Start the worker: cd python && uv run src/worker.py")
        print("2. Open terminal for John (VP Sales): cd python && python -m src.user_client john")
        print(
            "3. Open terminal for Isac (VP Engineering): cd python && python -m src.user_client isac"
        )
        print("4. Open terminal for Priya (VP Legal): cd python && python -m src.user_client priya")
        print("5. Open terminal for Mary (CEO): cd python && python -m src.user_client mary")
        print()
        print("Each user should:")
        print("- Check pending tasks (option 1)")
        print("- Type 'r' or 'respond' to respond to workflows")

    except Exception as e:
        print(f"❌ Error starting workflow: {e}")


async def demo_competitor_analysis(client):
    workflow_id = f"demo-competitor-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    print("\n🎯 Starting Competitor Analysis Workflow")
    print(f"Workflow ID: {workflow_id}")

    try:
        # Start the workflow
        await client.start_workflow(
            CompetitorAnalysisWorkflow.run,
            "RivalTech Corp",
            "Launched AI-powered product competing directly with our flagship offering",
            "Enterprise Software",
            "high",
            id=workflow_id,
            task_queue="hackathon",
        )

        print("✅ Workflow started successfully!")
        print("\n📋 Next steps:")
        print("1. Start the worker: cd python && uv run src/worker.py")
        print(
            "2. Open terminal for Isac (VP Engineering): cd python && python -m src.user_client isac"
        )
        print("3. Open terminal for Priya (VP Legal): cd python && python -m src.user_client priya")
        print("4. Open terminal for Mary (CEO): cd python && python -m src.user_client mary")
        print()
        print("Each user should:")
        print("- Check pending tasks (option 1)")
        print("- Type 'r' or 'respond' to respond to workflows")

    except Exception as e:
        print(f"❌ Error starting workflow: {e}")


if __name__ == "__main__":
    asyncio.run(main())
