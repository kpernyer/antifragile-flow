"""
Base persona class providing standardized patterns for human actor simulation.

Enforces best practices for actor personas including:
- Consistent personality modeling and behavior patterns
- Realistic decision-making simulation
- Interaction history and learning patterns
- Communication style generation
- Workflow integration and triggering
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import random
from typing import Any, TypeVar

from temporalio.client import Client

from ...shared.models.base import BaseModel, Priority


class CommunicationStyle(str, Enum):
    """Communication style preferences."""

    DIRECT = "direct"
    COLLABORATIVE = "collaborative"
    ANALYTICAL = "analytical"
    PERSUASIVE = "persuasive"
    DIPLOMATIC = "diplomatic"
    CONCISE = "concise"


class DecisionStyle(str, Enum):
    """Decision-making style patterns."""

    QUICK_DECISIVE = "quick_decisive"
    ANALYTICAL_THOROUGH = "analytical_thorough"
    CONSENSUS_SEEKING = "consensus_seeking"
    RISK_AVERSE = "risk_averse"
    INNOVATIVE_BOLD = "innovative_bold"
    DATA_DRIVEN = "data_driven"


class RiskTolerance(str, Enum):
    """Risk tolerance levels."""

    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class PersonaProfile(BaseModel):
    """Comprehensive persona profile with behavioral characteristics."""

    # Basic information
    name: str
    role: str
    department: str
    seniority_level: str  # "junior", "senior", "executive", "c_suite"

    # Behavioral characteristics
    decision_style: DecisionStyle
    communication_style: CommunicationStyle
    risk_tolerance: RiskTolerance

    # Preferences and patterns
    priorities: list[str] = field(default_factory=list)
    expertise_areas: list[str] = field(default_factory=list)
    preferred_meeting_times: list[str] = field(default_factory=list)
    response_time_hours: float = 2.0

    # Personality traits (0.0 to 1.0)
    assertiveness: float = 0.5
    openness_to_change: float = 0.5
    detail_orientation: float = 0.5
    team_orientation: float = 0.5
    strategic_thinking: float = 0.5

    # Working patterns
    availability_hours: dict[str, list[str]] = field(default_factory=dict)
    timezone: str = "UTC"

    # Learning and adaptation
    experience_level: float = 0.5  # 0.0 = novice, 1.0 = expert
    adaptability: float = 0.5  # How quickly they adapt to new information

    class Config:
        use_enum_values = True


@dataclass
class InteractionContext:
    """Context for persona interactions and decision-making."""

    topic: str
    urgency: Priority
    stakeholders: list[str]
    available_data: dict[str, Any]
    constraints: list[str] = field(default_factory=list)
    deadline: datetime | None = None
    budget_implications: float | None = None
    strategic_importance: float = 0.5  # 0.0 to 1.0


@dataclass
class PersonaResponse:
    """Structured response from a persona."""

    decision: str | None = None
    reasoning: str = ""
    confidence: float = 0.5  # 0.0 to 1.0
    additional_questions: list[str] = field(default_factory=list)
    suggested_next_steps: list[str] = field(default_factory=list)
    escalation_needed: bool = False
    response_time_minutes: int | None = None
    communication_style_used: CommunicationStyle | None = None


@dataclass
class InteractionHistory:
    """Track persona interaction history for learning."""

    timestamp: datetime
    context: InteractionContext
    response: PersonaResponse
    outcome: str | None = None
    feedback_received: str | None = None
    lessons_learned: list[str] = field(default_factory=list)


TPersonaProfile = TypeVar("TPersonaProfile", bound=PersonaProfile)


class BasePersona(ABC, Generic[TPersonaProfile]):
    """
    Base class for all actor personas in the system.

    Provides:
    - Consistent personality modeling
    - Realistic decision-making patterns
    - Communication style generation
    - Interaction history tracking
    - Workflow integration capabilities
    """

    def __init__(self, profile: TPersonaProfile, temporal_client: Client | None = None):
        self.profile = profile
        self.temporal_client = temporal_client
        self.interaction_history: list[InteractionHistory] = []
        self._current_workload: list[dict[str, Any]] = []

    @property
    @abstractmethod
    def persona_type(self) -> str:
        """Return the persona type identifier."""
        pass

    @property
    def name(self) -> str:
        """Get the persona's name."""
        return self.profile.name

    @property
    def role(self) -> str:
        """Get the persona's role."""
        return self.profile.role

    @property
    def is_available(self) -> bool:
        """Check if the persona is currently available."""
        current_hour = datetime.now().hour
        day_of_week = datetime.now().strftime("%A").lower()

        if day_of_week in self.profile.availability_hours:
            available_hours = self.profile.availability_hours[day_of_week]
            return any(
                int(hour_range.split("-")[0]) <= current_hour <= int(hour_range.split("-")[1])
                for hour_range in available_hours
            )

        # Default availability (9 AM to 6 PM)
        return 9 <= current_hour <= 18

    def generate_response(
        self, context: InteractionContext, additional_context: dict[str, Any] | None = None
    ) -> PersonaResponse:
        """Generate a response based on persona characteristics and context."""

        # Calculate response characteristics based on persona traits
        confidence = self._calculate_confidence(context)
        reasoning = self._generate_reasoning(context)
        decision = self._make_decision(context, confidence)

        # Determine response time based on urgency and persona characteristics
        response_time = self._calculate_response_time(context)

        # Generate questions and next steps based on decision style
        questions = self._generate_questions(context)
        next_steps = self._generate_next_steps(context, decision)

        # Check if escalation is needed
        escalation_needed = self._should_escalate(context, confidence)

        response = PersonaResponse(
            decision=decision,
            reasoning=reasoning,
            confidence=confidence,
            additional_questions=questions,
            suggested_next_steps=next_steps,
            escalation_needed=escalation_needed,
            response_time_minutes=response_time,
            communication_style_used=self.profile.communication_style,
        )

        # Record interaction
        self._record_interaction(context, response)

        return response

    def format_communication(
        self, message: str, recipient: str | None = None, context: InteractionContext | None = None
    ) -> str:
        """Format communication based on persona's communication style."""

        style = self.profile.communication_style

        if style == CommunicationStyle.DIRECT:
            return self._format_direct_communication(message)
        elif style == CommunicationStyle.COLLABORATIVE:
            return self._format_collaborative_communication(message, recipient)
        elif style == CommunicationStyle.ANALYTICAL:
            return self._format_analytical_communication(message, context)
        elif style == CommunicationStyle.PERSUASIVE:
            return self._format_persuasive_communication(message)
        elif style == CommunicationStyle.DIPLOMATIC:
            return self._format_diplomatic_communication(message, recipient)
        elif style == CommunicationStyle.CONCISE:
            return self._format_concise_communication(message)
        else:
            return message

    def get_priorities_for_context(self, context: InteractionContext) -> list[str]:
        """Get relevant priorities for the given context."""
        return [
            priority
            for priority in self.profile.priorities
            if any(keyword in context.topic.lower() for keyword in priority.lower().split())
        ]

    def assess_expertise_relevance(self, context: InteractionContext) -> float:
        """Assess how relevant the persona's expertise is to the context."""
        relevant_areas = [
            area
            for area in self.profile.expertise_areas
            if any(keyword in context.topic.lower() for keyword in area.lower().split())
        ]

        if not self.profile.expertise_areas:
            return 0.5  # Default relevance if no expertise defined

        return len(relevant_areas) / len(self.profile.expertise_areas)

    async def start_workflow(
        self, workflow_name: str, workflow_input: dict[str, Any], task_queue: str = "default"
    ) -> str:
        """Start a Temporal workflow from this persona."""
        if not self.temporal_client:
            raise ValueError("Temporal client not configured for this persona")

        workflow_id = f"{workflow_name}_{self.name}_{datetime.now().timestamp()}"

        handle = await self.temporal_client.start_workflow(
            workflow_name, workflow_input, id=workflow_id, task_queue=task_queue
        )

        self._current_workload.append(
            {
                "workflow_id": workflow_id,
                "workflow_name": workflow_name,
                "started_at": datetime.now(),
                "handle": handle,
            }
        )

        return workflow_id

    def _calculate_confidence(self, context: InteractionContext) -> float:
        """Calculate confidence level based on expertise and context."""
        base_confidence = 0.5

        # Adjust based on expertise relevance
        expertise_relevance = self.assess_expertise_relevance(context)
        base_confidence += (expertise_relevance - 0.5) * 0.3

        # Adjust based on experience level
        base_confidence += (self.profile.experience_level - 0.5) * 0.2

        # Adjust based on available data
        if context.available_data:
            data_quality = len(context.available_data) / 10  # Assume 10 is "complete" data
            base_confidence += min(data_quality, 0.2)

        # Adjust based on urgency (high urgency may reduce confidence)
        if context.urgency == Priority.URGENT:
            base_confidence -= 0.1
        elif context.urgency == Priority.LOW:
            base_confidence += 0.1

        return max(0.1, min(0.9, base_confidence))

    def _generate_reasoning(self, context: InteractionContext) -> str:
        """Generate reasoning based on persona characteristics."""
        style = self.profile.decision_style

        if style == DecisionStyle.ANALYTICAL_THOROUGH:
            return self._analytical_reasoning(context)
        elif style == DecisionStyle.DATA_DRIVEN:
            return self._data_driven_reasoning(context)
        elif style == DecisionStyle.RISK_AVERSE:
            return self._risk_averse_reasoning(context)
        elif style == DecisionStyle.INNOVATIVE_BOLD:
            return self._innovative_reasoning(context)
        else:
            return self._general_reasoning(context)

    def _make_decision(self, context: InteractionContext, confidence: float) -> str | None:
        """Make a decision based on context and persona characteristics."""
        # This is a simplified decision-making process
        # Real implementations would be much more sophisticated

        if confidence < 0.3:
            return None  # Not confident enough to decide

        if context.urgency == Priority.URGENT and confidence > 0.5:
            return "approve"  # Quick decision for urgent matters

        if self.profile.risk_tolerance == RiskTolerance.VERY_LOW and confidence < 0.7:
            return "defer"  # Defer if not very confident and risk-averse

        return "approve" if confidence > 0.6 else "needs_review"

    def _calculate_response_time(self, context: InteractionContext) -> int:
        """Calculate realistic response time in minutes."""
        base_time = self.profile.response_time_hours * 60

        # Adjust for urgency
        if context.urgency == Priority.URGENT:
            base_time *= 0.1  # Very quick response
        elif context.urgency == Priority.HIGH:
            base_time *= 0.3
        elif context.urgency == Priority.LOW:
            base_time *= 2.0

        # Add some randomness for realism
        variation = random.uniform(0.7, 1.3)
        return int(base_time * variation)

    def _generate_questions(self, context: InteractionContext) -> list[str]:
        """Generate questions based on persona's decision style."""
        questions = []

        if self.profile.decision_style == DecisionStyle.ANALYTICAL_THOROUGH:
            questions.extend(
                [
                    "What are the potential risks and mitigation strategies?",
                    "Do we have sufficient data to support this decision?",
                    "What are the long-term implications?",
                ]
            )

        if self.profile.decision_style == DecisionStyle.DATA_DRIVEN:
            questions.extend(
                [
                    "What metrics should we track to measure success?",
                    "Can we validate this with historical data?",
                    "What evidence supports this approach?",
                ]
            )

        return questions[:2]  # Limit to 2 questions for brevity

    def _generate_next_steps(self, context: InteractionContext, decision: str | None) -> list[str]:
        """Generate suggested next steps based on decision and persona."""
        if not decision:
            return ["Gather more information before proceeding"]

        if decision == "approve":
            return [
                "Proceed with implementation",
                "Set up monitoring and tracking",
                "Schedule follow-up review",
            ]
        elif decision == "needs_review":
            return [
                "Schedule stakeholder review meeting",
                "Prepare additional analysis",
                "Seek expert consultation",
            ]

        return []

    def _should_escalate(self, context: InteractionContext, confidence: float) -> bool:
        """Determine if the decision should be escalated."""
        if confidence < 0.3:
            return True

        if context.urgency == Priority.URGENT and confidence < 0.6:
            return True

        if context.budget_implications and context.budget_implications > 100000:  # $100k+
            return True

        return False

    def _record_interaction(self, context: InteractionContext, response: PersonaResponse) -> None:
        """Record the interaction for learning and history."""
        interaction = InteractionHistory(
            timestamp=datetime.now(), context=context, response=response
        )

        self.interaction_history.append(interaction)

        # Keep only recent history (last 100 interactions)
        if len(self.interaction_history) > 100:
            self.interaction_history = self.interaction_history[-100:]

    # Communication formatting methods
    def _format_direct_communication(self, message: str) -> str:
        return f"Bottom line: {message}"

    def _format_collaborative_communication(self, message: str, recipient: str | None) -> str:
        greeting = f"Hi {recipient}, " if recipient else "Team, "
        return f"{greeting}I'd like to share my thoughts on this: {message} What do you think?"

    def _format_analytical_communication(
        self, message: str, context: InteractionContext | None
    ) -> str:
        return f"Based on my analysis: {message}"

    def _format_persuasive_communication(self, message: str) -> str:
        return f"I strongly believe that {message}. Here's why this makes sense..."

    def _format_diplomatic_communication(self, message: str, recipient: str | None) -> str:
        return f"I appreciate the complexity of this situation. {message} Perhaps we could explore this further?"

    def _format_concise_communication(self, message: str) -> str:
        # Keep only the essential points
        sentences = message.split(". ")
        return ". ".join(sentences[:2]) + "." if len(sentences) > 1 else message

    # Reasoning generation methods
    def _analytical_reasoning(self, context: InteractionContext) -> str:
        return f"After careful analysis of {context.topic}, considering the available data and potential outcomes..."

    def _data_driven_reasoning(self, context: InteractionContext) -> str:
        data_points = len(context.available_data) if context.available_data else 0
        return f"Based on {data_points} data points and historical trends in {context.topic}..."

    def _risk_averse_reasoning(self, context: InteractionContext) -> str:
        return f"Given the potential risks associated with {context.topic}, we should proceed cautiously..."

    def _innovative_reasoning(self, context: InteractionContext) -> str:
        return f"This presents an exciting opportunity to innovate in {context.topic}. While there are risks..."

    def _general_reasoning(self, context: InteractionContext) -> str:
        return f"Considering the context of {context.topic} and our current priorities..."
