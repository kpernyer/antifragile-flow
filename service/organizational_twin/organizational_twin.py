"""
OrganizationalTwin - The intelligent system that understands organizational behavior
and makes decisions about communication, workflow participation, and business logic.

The OrganizationalTwin uses various data sources (database, future: Neo4j, Weaviate)
to make intelligent decisions but doesn't directly persist data - it delegates that
to appropriate storage systems.
"""

from dataclasses import dataclass

from db_inbox_service import DatabaseInboxService
from inbox_models import MessageType, Mood, Priority
from users import get_user


@dataclass
class InboxMessage:
    """Represents a message the OrganizationalTwin wants to send"""

    workflow_id: str
    from_user_id: str
    to_user_id: str
    message_type: MessageType
    priority: Priority
    urgency: int
    mood: Mood
    original_message: str
    processed_message: str
    intention: str
    context_data: dict
    due_hours: int
    related_entities: list[str]
    decision_factors: list[str]


class OrganizationalTwin:
    """
    The intelligent organizational behavior system.

    This system understands:
    - Who should be involved in what decisions
    - How to personalize messages based on user profiles
    - What urgency levels are appropriate
    - How organizational context affects communication
    - Business rules about workflows and processes
    """

    def __init__(self, database_service: DatabaseInboxService = None):
        # The OrganizationalTwin uses storage systems but doesn't own them
        self.db_service = database_service or DatabaseInboxService()

        # Organizational knowledge - in future, this comes from Neo4j
        self.org_structure = {
            "strategic_decision_stakeholders": [
                "john",
                "isac",
                "priya",
            ],  # Sales, Engineering, Legal
            "competitor_analysis_stakeholders": ["isac", "priya"],  # Engineering, Legal
            "escalation_paths": {
                "technical": "isac",
                "legal": "priya",
                "commercial": "john",
                "strategic": "mary",
            },
        }

        # Communication preferences - in future, this comes from Weaviate
        self.communication_styles = {
            "mary": {"tone": "direct", "detail": "strategic", "urgency_modifier": 1.2},
            "john": {"tone": "diplomatic", "detail": "balanced", "urgency_modifier": 0.9},
            "isac": {"tone": "technical", "detail": "deep", "urgency_modifier": 1.0},
            "priya": {"tone": "precise", "detail": "legal", "urgency_modifier": 1.1},
            "bob": {"tone": "practical", "detail": "operational", "urgency_modifier": 0.8},
        }

    def analyze_strategic_decision(
        self, workflow_id: str, from_user_id: str, proposal: str
    ) -> list[InboxMessage]:
        """
        OrganizationalTwin analyzes a strategic decision and determines:
        - Who needs to be involved
        - What level of urgency is appropriate
        - How to personalize messages for each stakeholder
        - What context and decision factors are relevant
        """

        # Organizational intelligence: determine stakeholders
        stakeholders = self.org_structure["strategic_decision_stakeholders"]

        # Analyze proposal content for urgency (future: use Weaviate for semantic analysis)
        base_urgency = self._analyze_proposal_urgency(proposal)

        messages = []
        for stakeholder_id in stakeholders:
            # Skip sending message to the initiator
            if stakeholder_id == from_user_id:
                continue

            # OrganizationalTwin creates personalized message
            message = self._create_strategic_message(
                workflow_id=workflow_id,
                from_user_id=from_user_id,
                to_user_id=stakeholder_id,
                proposal=proposal,
                base_urgency=base_urgency,
            )
            messages.append(message)

        return messages

    def analyze_competitor_threat(
        self,
        workflow_id: str,
        from_user_id: str,
        competitor: str,
        threat: str,
        market: str,
        urgency: str,
    ) -> list[InboxMessage]:
        """
        OrganizationalTwin analyzes competitor threat and determines appropriate response
        """

        # Organizational intelligence: determine who handles competitive threats
        stakeholders = self.org_structure["competitor_analysis_stakeholders"]

        # Map urgency to numeric scale
        urgency_map = {"low": 2, "medium": 3, "high": 5}
        urgency_level = urgency_map.get(urgency, 3)

        messages = []
        for stakeholder_id in stakeholders:
            if stakeholder_id == from_user_id:
                continue

            message = self._create_competitor_message(
                workflow_id=workflow_id,
                from_user_id=from_user_id,
                to_user_id=stakeholder_id,
                competitor=competitor,
                threat=threat,
                market=market,
                urgency_level=urgency_level,
                urgency_text=urgency,
            )
            messages.append(message)

        return messages

    def send_messages(self, messages: list[InboxMessage]):
        """
        OrganizationalTwin delegates message persistence to storage system
        """
        for message in messages:
            self.db_service.add_message_to_workflow(
                workflow_id=message.workflow_id,
                from_user_id=message.from_user_id,
                to_user_id=message.to_user_id,
                message_type=message.message_type,
                priority=message.priority,
                urgency=message.urgency,
                original_message=message.original_message,
                processed_message=message.processed_message,
                intention=message.intention,
                context=message.context_data,
                due_hours=message.due_hours,
            )

    def create_workflow_record(
        self, workflow_id: str, workflow_type: str, initiator_id: str, context: dict = None
    ):
        """OrganizationalTwin delegates workflow record creation to database"""
        self.db_service.create_workflow_record(workflow_id, workflow_type, initiator_id, context)

    def _create_strategic_message(
        self, workflow_id: str, from_user_id: str, to_user_id: str, proposal: str, base_urgency: int
    ) -> InboxMessage:
        """OrganizationalTwin crafts personalized strategic decision message"""

        # Get user context for personalization
        user = get_user(to_user_id)
        comm_style = self.communication_styles.get(to_user_id, {})

        # OrganizationalTwin determines appropriate urgency for this person
        urgency = int(base_urgency * comm_style.get("urgency_modifier", 1.0))
        urgency = max(1, min(5, urgency))  # Clamp to 1-5 range

        # OrganizationalTwin creates personalized message
        original_message = f"Strategic Decision Required: {proposal}"
        processed_message = self._personalize_strategic_message(to_user_id, proposal, user)

        # Determine priority based on urgency
        priority = Priority.URGENT if urgency >= 4 else Priority.HIGH

        # Determine mood based on urgency and user
        mood = Mood.CONCERNED if urgency >= 4 else Mood.NEUTRAL

        return InboxMessage(
            workflow_id=workflow_id,
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            message_type=MessageType.REQUEST,
            priority=priority,
            urgency=urgency,
            mood=mood,
            original_message=original_message,
            processed_message=processed_message,
            intention="provide_strategic_input",
            context_data={
                "proposal": proposal,
                "decision_factors": [
                    "strategic_alignment",
                    "resource_requirements",
                    "risk_assessment",
                ],
                "related_entities": ["strategic_planning", "executive_team"],
            },
            due_hours=8,  # Strategic decisions need quick response
            related_entities=["strategic_planning", "executive_team"],
            decision_factors=["strategic_alignment", "resource_requirements", "risk_assessment"],
        )

    def _create_competitor_message(
        self,
        workflow_id: str,
        from_user_id: str,
        to_user_id: str,
        competitor: str,
        threat: str,
        market: str,
        urgency_level: int,
        urgency_text: str,
    ) -> InboxMessage:
        """OrganizationalTwin crafts personalized competitor analysis message"""

        user = get_user(to_user_id)

        # Determine message type based on urgency
        message_type = MessageType.DIRECT_ORDER if urgency_text == "high" else MessageType.REQUEST
        priority = (
            Priority.URGENT
            if urgency_text == "high"
            else Priority.HIGH
            if urgency_text == "medium"
            else Priority.MEDIUM
        )
        due_hours = 4 if urgency_text == "high" else 24 if urgency_text == "medium" else 48

        # OrganizationalTwin determines analysis type based on user role
        analysis_type = "technical" if to_user_id == "isac" else "legal"
        decision_factors = (
            ["technical_feasibility", "competitive_response"]
            if to_user_id == "isac"
            else ["legal_implications", "regulatory_risk"]
        )

        original_message = f"Competitor Analysis Required: {competitor}"
        processed_message = self._personalize_competitor_message(
            to_user_id, competitor, threat, market, user
        )

        return InboxMessage(
            workflow_id=workflow_id,
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            message_type=message_type,
            priority=priority,
            urgency=urgency_level,
            mood=Mood.CONCERNED if urgency_level >= 4 else Mood.NEUTRAL,
            original_message=original_message,
            processed_message=processed_message,
            intention="analyze_competitive_threat",
            context_data={
                "competitor": competitor,
                "threat_description": threat,
                "market_segment": market,
                "urgency": urgency_text,
                "analysis_type": analysis_type,
                "decision_factors": decision_factors,
                "related_entities": ["competitive_intelligence", analysis_type],
            },
            due_hours=due_hours,
            related_entities=["competitive_intelligence", analysis_type],
            decision_factors=decision_factors,
        )

    def _analyze_proposal_urgency(self, proposal: str) -> int:
        """
        OrganizationalTwin analyzes proposal content to determine urgency
        Future: This will use Weaviate for semantic analysis
        """
        urgent_keywords = ["urgent", "immediate", "crisis", "emergency", "critical"]
        high_keywords = ["important", "significant", "major", "key", "strategic"]

        proposal_lower = proposal.lower()

        if any(keyword in proposal_lower for keyword in urgent_keywords):
            return 5
        elif any(keyword in proposal_lower for keyword in high_keywords):
            return 4
        else:
            return 3

    def _personalize_strategic_message(self, user_id: str, proposal: str, user: dict) -> str:
        """OrganizationalTwin personalizes strategic messages based on user context"""
        personalizations = {
            "mary": f"Mary, as CEO your strategic input is needed: {proposal}",
            "john": f"John, from a sales perspective: Strategic Decision Required: {proposal}",
            "isac": f"Isac, we need your technical analysis: Strategic Decision Required: {proposal}",
            "priya": f"Priya, please review the legal implications: Strategic Decision Required: {proposal}",
            "bob": f"Bob, IT infrastructure considerations needed: Strategic Decision Required: {proposal}",
        }
        return personalizations.get(user_id, f"Strategic Decision Required: {proposal}")

    def _personalize_competitor_message(
        self, user_id: str, competitor: str, threat: str, market: str, user: dict
    ) -> str:
        """OrganizationalTwin personalizes competitor messages based on user role"""
        personalizations = {
            "isac": f"Isac, we need your technical analysis: Competitor Analysis Required: {competitor}",
            "priya": f"Priya, please review the legal implications: Competitor Analysis Required: {competitor}",
        }
        return personalizations.get(user_id, f"Competitor Analysis Required: {competitor}")


# Global OrganizationalTwin instance
organizational_twin = OrganizationalTwin()
