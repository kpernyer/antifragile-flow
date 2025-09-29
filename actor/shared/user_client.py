#!/usr/bin/env python3
"""
Interactive terminal client for users to participate in workflows
Each user can run this in their own terminal window
"""

import asyncio
from datetime import datetime
import json
import sys

from db_inbox_service import DatabaseInboxService
from inbox_models import MessageType, Priority
from organizational_twin import OrganizationalTwin
from temporalio.client import Client
from user_profiles import get_user_display_info
from users import get_all_users, get_user

import shared

# from temporalio.exceptions import WorkflowFailureError
from workflows import CompetitorAnalysisWorkflow, StrategicDecisionWorkflow


class UserClient:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.user = get_user(user_id)
        self.client = None

        # OrganizationalTwin - the intelligent system
        self.org_twin = OrganizationalTwin()

        # Direct database access for reading user's own data
        self.inbox_service = DatabaseInboxService()

        if not self.user:
            print(f"❌ User '{user_id}' not found!")
            print("Available users:", list(get_all_users().keys()))
            sys.exit(1)

    async def connect(self):
        self.client = await Client.connect("localhost:7233")
        print(f"✅ Connected as {self.user.name} ({self.user.role})")

        # Display user profile information
        line1, line2, line3 = get_user_display_info(self.user_id)
        print("\n" + "=" * 60)
        print(line1)
        print(line2)
        print(line3)
        print("=" * 60)

    def display_menu(self):
        print("\n" + "=" * 60)
        print(f"🏢 {self.user.name} - {self.user.role} Dashboard")
        print("=" * 60)
        print("1. 📬 List Priorities")

        # Role-specific menu items
        if self.user.role == "CEO":
            print("2. 🎯 Strategic Priorities Dashboard")
            print("3. 🚀 Start a strategic decision workflow")

        if "Sales" in self.user.role:
            print("4. 🎯 Start a competitor analysis workflow")

        print("5. 📊 Query workflow status")
        print("6. 🔄 Refresh dashboard")
        print("0. 👋 Exit")
        print("=" * 60)

    async def list_priorities(self):
        """List user's priority tasks from rich inbox"""
        print(f"\n📬 Priority Tasks for {self.user.name}...")

        try:
            # Get inbox summary from database
            summary = self.inbox_service.get_user_inbox_summary(self.user_id)

            print("\n📊 Inbox Summary:")
            print(f"   📧 Total messages: {summary['total_messages']}")
            print(f"   🔥 Unread: {summary['unread_count']}")
            print(f"   ⚡ Urgent: {summary['urgent_count']}")
            print(f"   🎯 Decisions needed: {summary['pending_decisions']}")

            # Show urgent tasks first
            urgent_tasks = self.inbox_service.get_urgent_tasks(self.user_id)
            if urgent_tasks:
                print(f"\n🚨 URGENT TASKS ({len(urgent_tasks)}):")
                for msg in urgent_tasks[:3]:  # Show top 3 urgent
                    self._display_db_message_summary(msg)

            # Show pending decisions
            pending_decisions = self.inbox_service.get_pending_decisions(self.user_id)
            if pending_decisions:
                print(f"\n🎯 DECISIONS NEEDED ({len(pending_decisions)}):")
                for msg in pending_decisions[:3]:  # Show top 3 decisions
                    self._display_db_message_summary(msg)

            # Show recent unread messages
            unread_messages = self.inbox_service.get_unread_messages(self.user_id, limit=5)
            shown_ids = {msg["message_id"] for msg in urgent_tasks + pending_decisions}
            remaining_unread = [
                msg for msg in unread_messages if msg["message_id"] not in shown_ids
            ]

            if remaining_unread:
                print("\n📋 RECENT MESSAGES:")
                for msg in remaining_unread[:3]:  # Show up to 3 more
                    self._display_db_message_summary(msg)

            if summary["total_messages"] == 0:
                print("✅ No messages in inbox")
            elif summary["unread_count"] == 0:
                print("✅ No unread messages")

        except Exception as e:
            print(f"❌ Error checking inbox: {e}")

    def _display_db_message_summary(self, msg: dict):
        """Display a summary of a database message"""
        # Priority and urgency indicators
        priority_icons = {5: "🔴", 4: "🟡", 3: "🟠", 2: "🔵", 1: "⚪"}
        priority_icon = priority_icons.get(msg.get("priority", 3), "🔵")

        # Message type indicators
        type_icons = {
            "direct_order": "⚡",
            "request": "❓",
            "recommendation": "💡",
            "nudge": "👋",
            "information": "ℹ️",
            "escalation": "🚨",
        }
        type_icon = type_icons.get(msg.get("message_type", "information"), "📄")

        # Time info
        created_at = (
            datetime.fromisoformat(msg["created_at"].replace("Z", "+00:00"))
            if msg.get("created_at")
            else datetime.utcnow()
        )
        time_ago = self._format_time_ago(created_at)

        due_info = ""
        if msg.get("due_date"):
            due_date = datetime.fromisoformat(msg["due_date"].replace("Z", "+00:00"))
            due_in = due_date - datetime.utcnow()
            if due_in.total_seconds() > 0:
                due_info = f" | Due in {self._format_duration(due_in)}"
            else:
                due_info = " | ⚠️ OVERDUE"

        processed_msg = msg.get("processed_message", msg.get("original_message", ""))
        print(
            f"   {priority_icon}{type_icon} {processed_msg[:80]}{'...' if len(processed_msg) > 80 else ''}"
        )
        print(f"      From: {msg.get('from_user_id')} | {time_ago}{due_info}")
        if msg.get("workflow_id"):
            print(f"      Workflow: {msg['workflow_id']}")
        print()

    def _display_message_summary(self, msg):
        """Display a summary of an inbox message"""
        # Priority and urgency indicators
        priority_icon = {
            Priority.CRITICAL: "🔴",
            Priority.URGENT: "🟡",
            Priority.HIGH: "🟠",
            Priority.MEDIUM: "🔵",
            Priority.LOW: "⚪",
        }.get(msg.priority, "🔵")

        # Message type indicators
        type_icon = {
            MessageType.DIRECT_ORDER: "⚡",
            MessageType.REQUEST: "❓",
            MessageType.RECOMMENDATION: "💡",
            MessageType.NUDGE: "👋",
            MessageType.INFORMATION: "ℹ️",
            MessageType.ESCALATION: "🚨",
        }.get(msg.message_type, "📄")

        # Time info
        time_ago = self._format_time_ago(msg.created_at)
        due_info = ""
        if msg.due_date:
            due_in = msg.due_date - datetime.now()
            if due_in.total_seconds() > 0:
                due_info = f" | Due in {self._format_duration(due_in)}"
            else:
                due_info = " | ⚠️ OVERDUE"

        print(
            f"   {priority_icon}{type_icon} {msg.processed_message[:80]}{'...' if len(msg.processed_message) > 80 else ''}"
        )
        print(f"      From: {msg.from_user_id} | {time_ago}{due_info}")
        if msg.workflow_id:
            print(f"      Workflow: {msg.workflow_id}")
        print()

    def _format_time_ago(self, dt: datetime) -> str:
        """Format time ago in human readable format"""
        diff = datetime.now() - dt
        if diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600}h ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60}m ago"
        else:
            return "just now"

    def _format_duration(self, duration) -> str:
        """Format duration in human readable format"""
        if duration.days > 0:
            return f"{duration.days}d"
        elif duration.seconds > 3600:
            return f"{duration.seconds // 3600}h"
        elif duration.seconds > 60:
            return f"{duration.seconds // 60}m"
        else:
            return "now"

    async def start_strategic_decision(self):
        if self.user.role != "CEO":
            print("❌ Only CEO can start strategic decision workflows")
            return

        proposal = input("Enter your strategic proposal: ").strip()
        if not proposal:
            print("❌ Proposal cannot be empty")
            return

        workflow_id = f"strategic-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        try:
            await self.client.start_workflow(
                StrategicDecisionWorkflow.run,
                args=(proposal, self.user_id),
                id=workflow_id,
                task_queue=shared.TASK_QUEUE_NAME,
            )
            print(f"✅ Strategic decision workflow started: {workflow_id}")
            print("📧 Notifications will be sent to VPs via workflow activities")
        except Exception as e:
            print(f"❌ Error starting workflow: {e}")

    async def start_competitor_analysis(self):
        if "Sales" not in self.user.role:
            print("❌ Only VP of Sales can start competitor analysis workflows")
            return

        print("🎯 New Competitor Threat Analysis")
        competitor = input("Competitor name: ").strip()
        threat = input("Threat description: ").strip()
        market = input("Market segment: ").strip()
        urgency = input("Urgency (low/medium/high): ").strip().lower()

        if not all([competitor, threat, market, urgency]):
            print("❌ All fields are required")
            return

        if urgency not in ["low", "medium", "high"]:
            print("❌ Urgency must be low, medium, or high")
            return

        workflow_id = f"competitor-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        try:
            await self.client.start_workflow(
                CompetitorAnalysisWorkflow.run,
                args=(competitor, threat, market, urgency, self.user_id),
                id=workflow_id,
                task_queue=shared.TASK_QUEUE_NAME,
            )
            print(f"✅ Competitor analysis workflow started: {workflow_id}")
            print("📧 Engineering and Legal teams will be notified via workflow activities")
        except Exception as e:
            print(f"❌ Error starting workflow: {e}")

    async def query_workflow(self):
        workflow_id = input("Enter workflow ID: ").strip()
        if not workflow_id:
            print("❌ Workflow ID cannot be empty")
            return

        try:
            handle = self.client.get_workflow_handle(workflow_id)
            status = await handle.query("get_status")
            print("\n📊 Workflow Status:")
            print(json.dumps(status, indent=2, default=str))
        except Exception as e:
            print(f"❌ Error querying workflow: {e}")

    async def respond_to_workflow(self):
        """Handle responses based on user role and pending workflows"""
        workflow_id = input("Enter workflow ID to respond to: ").strip()
        if not workflow_id:
            print("❌ Workflow ID cannot be empty")
            return

        try:
            handle = self.client.get_workflow_handle(workflow_id)

            # Get workflow info to determine type
            description = await handle.describe()
            workflow_type = description.workflow_type

            if workflow_type == "StrategicDecisionWorkflow":
                await self._handle_strategic_response(handle)
            elif workflow_type == "CompetitorAnalysisWorkflow":
                await self._handle_competitor_response(handle)
            else:
                print(f"❌ Unknown workflow type: {workflow_type}")

        except Exception as e:
            print(f"❌ Error responding to workflow: {e}")

    async def _handle_strategic_response(self, handle):
        status = await handle.query("get_status")

        if self.user_id in status.get("pending_vps", []):
            # VP response
            print(f"\n📋 Strategic Proposal: {status['proposal']}")
            decision = input("Your decision (approve/reject/modify): ").strip().lower()
            reason = input("Your reasoning: ").strip()

            if decision in ["approve", "reject", "modify"] and reason:
                await handle.signal("vp_response", self.user_id, decision, reason)
                print("✅ Response submitted successfully")
            else:
                print("❌ Invalid decision or empty reason")

        elif status.get("awaiting_ceo_decision") and self.user.role == "CEO":
            # CEO final decision
            print(f"\n👑 Final Decision Required: {status['proposal']}")
            print("\nVP Responses:")
            for vp_id, response in status.get("vp_responses", {}).items():
                print(f"  {vp_id}: {response['decision']} - {response['reason']}")

            final_decision = input("\nYour final decision: ").strip()
            if final_decision:
                await handle.signal("ceo_final_decision", final_decision)
                print("✅ Final decision submitted successfully")
            else:
                print("❌ Final decision cannot be empty")
        else:
            print("❌ No pending action for you on this workflow")

    async def _handle_competitor_response(self, handle):
        status = await handle.query("get_status")
        threat = status.get("threat", {})

        if status.get("awaiting_engineering") and "Engineering" in self.user.role:
            print("\n🔧 Engineering Analysis Required")
            print(f"Competitor: {threat.get('competitor_name')}")
            print(f"Threat: {threat.get('threat_description')}")
            print(f"Market: {threat.get('market_segment')}")

            analysis = input("Your technical analysis: ").strip()
            if analysis:
                await handle.signal("engineering_analysis", analysis)
                print("✅ Engineering analysis submitted successfully")
            else:
                print("❌ Analysis cannot be empty")

        elif status.get("awaiting_legal") and "Legal" in self.user.role:
            print("\n⚖️  Legal Analysis Required")
            print(f"Competitor: {threat.get('competitor_name')}")
            print(f"Threat: {threat.get('threat_description')}")

            analysis = input("Your legal analysis: ").strip()
            if analysis:
                await handle.signal("legal_analysis", analysis)
                print("✅ Legal analysis submitted successfully")
            else:
                print("❌ Analysis cannot be empty")

        elif status.get("awaiting_ceo_strategy") and self.user.role == "CEO":
            print("\n👑 Strategy Decision Required")
            print(f"Competitor: {threat.get('competitor_name')}")
            print(f"Engineering Analysis: {status.get('engineering_analysis')}")
            print(f"Legal Analysis: {status.get('legal_analysis')}")

            strategy = input("Your strategic response: ").strip()
            if strategy:
                await handle.signal("ceo_strategy", strategy)
                print("✅ Strategy decision submitted successfully")
            else:
                print("❌ Strategy cannot be empty")
        else:
            print("❌ No pending action for you on this workflow")

    async def run(self):
        await self.connect()

        while True:
            self.display_menu()

            try:
                choice = input("\nSelect option: ").strip()

                if choice == "0":
                    print("👋 Goodbye!")
                    break
                elif choice == "1":
                    await self.list_priorities()
                    input("\nPress Enter to continue...")
                elif choice == "2":
                    await self.start_strategic_decision()
                    input("\nPress Enter to continue...")
                elif choice == "3":
                    await self.start_competitor_analysis()
                    input("\nPress Enter to continue...")
                elif choice == "4":
                    await self.query_workflow()
                    input("\nPress Enter to continue...")
                elif choice == "5":
                    continue  # Refresh - just loop back to menu
                elif choice == "r" or choice == "respond":
                    await self.respond_to_workflow()
                    input("\nPress Enter to continue...")
                else:
                    print("❌ Invalid option")
                    input("\nPress Enter to continue...")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                input("\nPress Enter to continue...")


async def main():
    if len(sys.argv) != 2:
        print("Usage: python user_client.py <user_id>")
        print("Available users:", list(get_all_users().keys()))
        sys.exit(1)

    user_id = sys.argv[1].lower()
    client = UserClient(user_id)
    await client.run()


if __name__ == "__main__":
    asyncio.run(main())
