"""
Demo Inbox Service - Simulates full architecture
In production: PostgreSQL + Neo4j + Redis + Blob Storage
For demo: In-memory with JSON persistence
"""

from datetime import datetime, timedelta
import json
from pathlib import Path
import uuid

from inbox_models import InboxMessage, MessageType, Mood, Priority, TaskStatus, UserInbox


class DemoInboxService:
    """
    Demo implementation of user inbox service
    Simulates full architecture with local JSON storage
    """

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            # Always use the same inbox directory regardless of working directory
            project_root = Path(__file__).parent.parent  # go up from src/ to python/
            data_dir = project_root / "demo-data" / "inbox"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.user_inboxes: dict[str, UserInbox] = {}
        self._load_all_inboxes()

    def _get_inbox_file(self, user_id: str) -> Path:
        """Get inbox file path for user"""
        return self.data_dir / f"{user_id}_inbox.json"

    def _load_inbox(self, user_id: str) -> UserInbox:
        """Load user inbox from JSON file"""
        inbox_file = self._get_inbox_file(user_id)
        inbox = UserInbox(user_id=user_id)

        if inbox_file.exists():
            try:
                with open(inbox_file) as f:
                    data = json.load(f)
                    inbox.last_checked = (
                        datetime.fromisoformat(data["last_checked"])
                        if data.get("last_checked")
                        else None
                    )
                    inbox.messages = [
                        InboxMessage.from_dict(msg_data) for msg_data in data.get("messages", [])
                    ]
            except Exception as e:
                print(f"Error loading inbox for {user_id}: {e}")

        return inbox

    def _save_inbox(self, user_id: str):
        """Save user inbox to JSON file"""
        if user_id not in self.user_inboxes:
            return

        inbox = self.user_inboxes[user_id]
        inbox_file = self._get_inbox_file(user_id)

        data = {
            "user_id": user_id,
            "last_checked": inbox.last_checked.isoformat() if inbox.last_checked else None,
            "messages": [msg.to_dict() for msg in inbox.messages],
        }

        try:
            with open(inbox_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving inbox for {user_id}: {e}")

    def _load_all_inboxes(self):
        """Load all existing inboxes"""
        if not self.data_dir.exists():
            return

        for inbox_file in self.data_dir.glob("*_inbox.json"):
            user_id = inbox_file.stem.replace("_inbox", "")
            self.user_inboxes[user_id] = self._load_inbox(user_id)

    def get_inbox(self, user_id: str) -> UserInbox:
        """Get user inbox, creating if doesn't exist"""
        if user_id not in self.user_inboxes:
            self.user_inboxes[user_id] = self._load_inbox(user_id)
        return self.user_inboxes[user_id]

    def add_message(self, message: InboxMessage):
        """Add message to user's inbox"""
        inbox = self.get_inbox(message.to_user_id)
        inbox.add_message(message)
        self._save_inbox(message.to_user_id)

        # Also add to CC users
        for cc_user in message.cc_user_ids:
            cc_inbox = self.get_inbox(cc_user)
            cc_message = InboxMessage(
                message_id=f"{message.message_id}_cc_{cc_user}",
                workflow_id=message.workflow_id,
                thread_id=message.thread_id,
                from_user_id=message.from_user_id,
                to_user_id=cc_user,
                message_type=MessageType.INFORMATION,  # CC messages are informational
                priority=message.priority,
                urgency=max(1, message.urgency - 1),  # Lower urgency for CC
                mood=message.mood,
                original_message=f"[CC] {message.original_message}",
                processed_message=f"[CC] {message.processed_message}",
                intention=message.intention,
                context=message.context.copy(),
                created_at=message.created_at,
                due_date=message.due_date,
                related_entities=message.related_entities.copy(),
                decision_factors=message.decision_factors.copy(),
            )
            cc_inbox.add_message(cc_message)
            self._save_inbox(cc_user)

    def create_workflow_message(
        self, workflow_id: str, workflow_type: str, from_user: str, to_user: str, content: dict
    ) -> InboxMessage:
        """Create a message from workflow context"""
        message_id = str(uuid.uuid4())

        # Extract message details based on workflow type
        if workflow_type == "StrategicDecisionWorkflow":
            return InboxMessage(
                message_id=message_id,
                workflow_id=workflow_id,
                from_user_id=from_user,
                to_user_id=to_user,
                message_type=MessageType.REQUEST,
                priority=Priority.HIGH,
                urgency=4,
                mood=Mood.CONFIDENT,
                original_message=f"Strategic Decision Required: {content.get('proposal', 'Unknown proposal')}",
                processed_message=self._personalize_message(
                    to_user,
                    f"Please review and provide your input on: {content.get('proposal', 'Unknown proposal')}",
                ),
                intention="provide_strategic_input",
                context={
                    "workflow_type": workflow_type,
                    "proposal": content.get("proposal", ""),
                    "deadline": "end_of_day",
                },
                due_date=datetime.now() + timedelta(hours=8),
                escalation_date=datetime.now() + timedelta(hours=24),
                related_entities=["strategic_planning", "executive_team"],
                decision_factors=[
                    "strategic_alignment",
                    "resource_requirements",
                    "risk_assessment",
                ],
            )

        elif workflow_type == "CompetitorAnalysisWorkflow":
            threat = content.get("threat", {})
            return InboxMessage(
                message_id=message_id,
                workflow_id=workflow_id,
                from_user_id=from_user,
                to_user_id=to_user,
                message_type=MessageType.DIRECT_ORDER
                if content.get("urgency") == "high"
                else MessageType.REQUEST,
                priority=Priority.URGENT if content.get("urgency") == "high" else Priority.HIGH,
                urgency=5 if content.get("urgency") == "high" else 3,
                mood=Mood.CONCERNED,
                original_message=f"Competitor Analysis Required: {threat.get('competitor_name', 'Unknown competitor')}",
                processed_message=self._personalize_message(
                    to_user,
                    f"Urgent analysis needed for competitive threat from {threat.get('competitor_name', 'Unknown competitor')}. Threat: {threat.get('threat_description', '')}",
                ),
                intention="analyze_competitive_threat",
                context={
                    "workflow_type": workflow_type,
                    "competitor": threat.get("competitor_name", ""),
                    "threat_description": threat.get("threat_description", ""),
                    "market_segment": threat.get("market_segment", ""),
                    "urgency": content.get("urgency", "medium"),
                },
                due_date=datetime.now()
                + timedelta(hours=4 if content.get("urgency") == "high" else 24),
                related_entities=["competitive_intelligence", "market_analysis"],
                decision_factors=[
                    "technical_feasibility",
                    "legal_implications",
                    "competitive_response",
                ],
            )

        else:
            # Generic workflow message
            return InboxMessage(
                message_id=message_id,
                workflow_id=workflow_id,
                from_user_id=from_user,
                to_user_id=to_user,
                message_type=MessageType.INFORMATION,
                original_message=f"Workflow Update: {workflow_type}",
                processed_message=f"You have a pending task in workflow {workflow_id}",
                intention="workflow_participation",
            )

    def _personalize_message(self, user_id: str, base_message: str) -> str:
        """
        Personalize message based on user profile
        In full system: Use AI with user personality from Neo4j
        """
        # Simple demo personalization
        personalizations = {
            "mary": f"Mary, as CEO your strategic input is needed: {base_message}",
            "john": f"John, from a sales perspective: {base_message}",
            "isac": f"Isac, we need your technical analysis: {base_message}",
            "priya": f"Priya, please review the legal implications: {base_message}",
            "bob": f"Bob, IT infrastructure considerations needed: {base_message}",
        }
        return personalizations.get(user_id, base_message)

    def mark_as_read(self, user_id: str, message_id: str):
        """Mark message as read"""
        inbox = self.get_inbox(user_id)
        for message in inbox.messages:
            if message.message_id == message_id:
                message.status = TaskStatus.READ
                message.read_at = datetime.now()
                break
        self._save_inbox(user_id)

    def mark_as_completed(self, user_id: str, message_id: str):
        """Mark message as completed"""
        inbox = self.get_inbox(user_id)
        for message in inbox.messages:
            if message.message_id == message_id:
                message.status = TaskStatus.COMPLETED
                message.completed_at = datetime.now()
                break
        self._save_inbox(user_id)

    def get_dashboard_summary(self, user_id: str) -> dict:
        """Get dashboard summary for user"""
        inbox = self.get_inbox(user_id)

        return {
            "total_messages": len(inbox.messages),
            "unread_count": inbox.get_unread_count(),
            "urgent_count": len(inbox.get_urgent_tasks()),
            "pending_decisions": len(inbox.get_pending_decisions()),
            "last_checked": inbox.last_checked.isoformat() if inbox.last_checked else None,
            "recent_messages": [msg.to_dict() for msg in inbox.messages[:5]],  # Latest 5
        }


# Demo data seeder
def seed_demo_inbox_data():
    """Create demo inbox messages for testing"""
    service = DemoInboxService()

    # Strategic decision example
    strategic_msg = InboxMessage(
        message_id=str(uuid.uuid4()),
        workflow_id="demo-strategic-20250926-123456",
        from_user_id="mary",
        to_user_id="john",
        message_type=MessageType.REQUEST,
        priority=Priority.HIGH,
        urgency=4,
        mood=Mood.CONFIDENT,
        original_message="Strategic Decision Required: Acquire TechCorp for $50M to expand our AI capabilities",
        processed_message="John, from a sales perspective: Please review and provide your input on acquiring TechCorp for $50M to expand our AI capabilities. Consider customer impact and market opportunity.",
        intention="provide_strategic_input",
        context={
            "proposal": "Acquire TechCorp for $50M to expand our AI capabilities",
            "acquisition_target": "TechCorp",
            "amount": "$50M",
            "strategic_goal": "AI capabilities expansion",
        },
        due_date=datetime.now() + timedelta(hours=8),
        related_entities=["strategic_planning", "ai_initiative", "techcorp"],
        decision_factors=["customer_impact", "market_opportunity", "competitive_advantage"],
    )
    service.add_message(strategic_msg)

    # Add similar messages for other VPs
    for user, context in [
        ("isac", "technical feasibility and integration challenges"),
        ("priya", "legal implications and regulatory compliance"),
    ]:
        msg = InboxMessage(
            message_id=str(uuid.uuid4()),
            workflow_id="demo-strategic-20250926-123456",
            from_user_id="mary",
            to_user_id=user,
            message_type=MessageType.REQUEST,
            priority=Priority.HIGH,
            urgency=4,
            mood=Mood.CONFIDENT,
            original_message="Strategic Decision Required: Acquire TechCorp for $50M to expand our AI capabilities",
            processed_message=f"Please analyze the {context} for acquiring TechCorp for $50M to expand our AI capabilities.",
            intention="provide_strategic_input",
            context=strategic_msg.context.copy(),
            due_date=datetime.now() + timedelta(hours=8),
            related_entities=strategic_msg.related_entities.copy(),
            decision_factors=["risk_assessment", "compliance_requirements", "due_diligence"],
        )
        service.add_message(msg)

    print("✅ Demo inbox data seeded successfully!")
    return service
