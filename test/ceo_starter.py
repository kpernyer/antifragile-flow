#!/usr/bin/env python3
"""
CEO Strategic Priority Starter
Static list of 5 strategic priorities that can be initiated by number
"""

import asyncio
from datetime import datetime

from temporalio.client import Client

import shared
from workflows import StrategicDecisionWorkflow


class CEOPriorityStarter:
    def __init__(self):
        self.client = None
        self.strategic_priorities = [
            {
                "title": "AI Capability Expansion",
                "proposal": "Acquire TechCorp for $50M to rapidly expand our AI and machine learning capabilities",
                "workflow_type": "strategic",
                "urgency": "high",
            },
            {
                "title": "Market Penetration Strategy",
                "proposal": "Launch aggressive pricing strategy to capture 25% market share in Q1",
                "workflow_type": "strategic",
                "urgency": "medium",
            },
            {
                "title": "Talent Acquisition Initiative",
                "proposal": "Establish new R&D center in Austin with 100 engineers, budget $15M annually",
                "workflow_type": "strategic",
                "urgency": "high",
            },
            {
                "title": "Partnership & Alliances",
                "proposal": "Form strategic partnership with CloudTech to integrate our platforms",
                "workflow_type": "strategic",
                "urgency": "medium",
            },
            {
                "title": "Product Line Expansion",
                "proposal": "Develop enterprise security suite, invest $8M in new product development",
                "workflow_type": "strategic",
                "urgency": "low",
            },
        ]

    async def connect(self):
        """Connect to Temporal server"""
        self.client = await Client.connect("localhost:7233")
        print("✅ Connected to Temporal server")

    def display_priorities(self):
        """Display the static priority list"""
        print("\n" + "=" * 80)
        print("🎯 CEO STRATEGIC PRIORITIES DASHBOARD")
        print("=" * 80)
        print("Select a priority to initiate the strategic decision workflow:\n")

        for i, priority in enumerate(self.strategic_priorities, 1):
            urgency_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                priority["urgency"], "⚪"
            )
            print(f"{i}. {urgency_icon} {priority['title']}")
            print(f"   {priority['proposal']}")
            print(f"   Urgency: {priority['urgency'].upper()}")
            print()

        print("0. 🚪 Exit")
        print("=" * 80)

    async def start_strategic_workflow(self, priority_index: int):
        """Start a strategic decision workflow for the selected priority"""
        if priority_index < 1 or priority_index > len(self.strategic_priorities):
            print("❌ Invalid priority selection")
            return

        priority = self.strategic_priorities[priority_index - 1]
        proposal = priority["proposal"]

        # Generate unique workflow ID
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        workflow_id = f"strategic-{priority_index}-{timestamp}"

        try:
            print("\n🚀 Initiating Strategic Decision Workflow")
            print(f"Priority: {priority['title']}")
            print(f"Proposal: {proposal}")
            print(f"Workflow ID: {workflow_id}")
            print(f"Urgency: {priority['urgency'].upper()}")

            await self.client.start_workflow(
                StrategicDecisionWorkflow.run,
                args=(proposal, "mary"),  # CEO Mary is the initiator
                id=workflow_id,
                task_queue=shared.TASK_QUEUE_NAME,
            )

            print("\n✅ Strategic decision workflow started successfully!")
            print("📧 VP notifications sent via OrganizationalTwin")
            print(
                f"🌐 Monitor at: http://localhost:8233/namespaces/default/workflows/{workflow_id}"
            )

        except Exception as e:
            print(f"❌ Error starting workflow: {e}")

    async def run(self):
        """Main interactive loop"""
        await self.connect()

        while True:
            self.display_priorities()

            try:
                choice = input("\nSelect priority (0-5): ").strip()

                if choice == "0":
                    print("👋 Goodbye!")
                    break
                elif choice.isdigit():
                    priority_num = int(choice)
                    if 1 <= priority_num <= 5:
                        await self.start_strategic_workflow(priority_num)
                        input("\nPress Enter to continue...")
                    else:
                        print("❌ Please select a number between 1-5")
                        input("\nPress Enter to continue...")
                else:
                    print("❌ Please enter a valid number")
                    input("\nPress Enter to continue...")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                input("\nPress Enter to continue...")


async def main():
    """Main entry point"""
    ceo_starter = CEOPriorityStarter()
    await ceo_starter.run()


if __name__ == "__main__":
    asyncio.run(main())
