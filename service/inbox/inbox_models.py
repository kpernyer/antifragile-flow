"""
User Inbox and Task Management Data Models
For the full system: PostgreSQL tables + Neo4j relationships + Redis caching
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class MessageType(Enum):
    NUDGE = "nudge"  # Gentle reminder or suggestion
    RECOMMENDATION = "recommendation"  # Data-driven suggestion with reasoning
    DIRECT_ORDER = "direct_order"  # Clear instruction from authority
    INFORMATION = "information"  # FYI, no action required
    REQUEST = "request"  # Asking for input/decision
    ESCALATION = "escalation"  # Issue requires immediate attention


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


class Mood(Enum):
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    CONCERNED = "concerned"
    FRUSTRATED = "frustrated"
    EXCITED = "excited"
    CONFIDENT = "confident"
    WORRIED = "worried"


class TaskStatus(Enum):
    UNREAD = "unread"
    READ = "read"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELEGATED = "delegated"
    DEFERRED = "deferred"
    CANCELLED = "cancelled"


@dataclass
class InboxMessage:
    """
    Rich message model for user inbox
    In full system: stored in PostgreSQL with foreign keys to Neo4j entities
    """

    # Core identification
    message_id: str
    workflow_id: str | None = None
    thread_id: str | None = None  # For message threading

    # Communication metadata
    from_user_id: str = ""
    to_user_id: str = ""
    cc_user_ids: list[str] = field(default_factory=list)

    # Message classification
    message_type: MessageType = MessageType.INFORMATION
    priority: Priority = Priority.MEDIUM
    urgency: int = 3  # 1-5 scale
    mood: Mood = Mood.NEUTRAL

    # Content
    original_message: str = ""
    processed_message: str = ""  # AI-enhanced/personalized version
    intention: str = ""  # Extracted intent (e.g., "approve budget", "review contract")
    context: dict[str, Any] = field(default_factory=dict)  # Additional context

    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    due_date: datetime | None = None
    escalation_date: datetime | None = None

    # Status tracking
    status: TaskStatus = TaskStatus.UNREAD
    read_at: datetime | None = None
    completed_at: datetime | None = None

    # Relationship context (would be rich Neo4j queries in full system)
    related_entities: list[str] = field(default_factory=list)  # Projects, customers, etc.
    decision_factors: list[str] = field(default_factory=list)  # What should influence decision

    # AI enhancements
    sentiment_score: float = 0.0  # -1 to 1
    complexity_score: int = 3  # 1-5, affects response time expectations
    stakeholder_impact: list[str] = field(default_factory=list)  # Who else is affected

    # Attachments and references
    attachment_ids: list[str] = field(default_factory=list)  # Blob storage references
    reference_urls: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON storage/API"""
        return {
            "message_id": self.message_id,
            "workflow_id": self.workflow_id,
            "thread_id": self.thread_id,
            "from_user_id": self.from_user_id,
            "to_user_id": self.to_user_id,
            "cc_user_ids": self.cc_user_ids,
            "message_type": self.message_type.value,
            "priority": self.priority.value,
            "urgency": self.urgency,
            "mood": self.mood.value,
            "original_message": self.original_message,
            "processed_message": self.processed_message,
            "intention": self.intention,
            "context": self.context,
            "created_at": self.created_at.isoformat(),
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "escalation_date": self.escalation_date.isoformat() if self.escalation_date else None,
            "status": self.status.value,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "related_entities": self.related_entities,
            "decision_factors": self.decision_factors,
            "sentiment_score": self.sentiment_score,
            "complexity_score": self.complexity_score,
            "stakeholder_impact": self.stakeholder_impact,
            "attachment_ids": self.attachment_ids,
            "reference_urls": self.reference_urls,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InboxMessage":
        """Create from dictionary"""
        msg = cls(
            message_id=data["message_id"],
            workflow_id=data.get("workflow_id"),
            thread_id=data.get("thread_id"),
            from_user_id=data.get("from_user_id", ""),
            to_user_id=data.get("to_user_id", ""),
            cc_user_ids=data.get("cc_user_ids", []),
            message_type=MessageType(data.get("message_type", "information")),
            priority=Priority(data.get("priority", 2)),
            urgency=data.get("urgency", 3),
            mood=Mood(data.get("mood", "neutral")),
            original_message=data.get("original_message", ""),
            processed_message=data.get("processed_message", ""),
            intention=data.get("intention", ""),
            context=data.get("context", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None,
            escalation_date=datetime.fromisoformat(data["escalation_date"])
            if data.get("escalation_date")
            else None,
            status=TaskStatus(data.get("status", "unread")),
            read_at=datetime.fromisoformat(data["read_at"]) if data.get("read_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"])
            if data.get("completed_at")
            else None,
            related_entities=data.get("related_entities", []),
            decision_factors=data.get("decision_factors", []),
            sentiment_score=data.get("sentiment_score", 0.0),
            complexity_score=data.get("complexity_score", 3),
            stakeholder_impact=data.get("stakeholder_impact", []),
            attachment_ids=data.get("attachment_ids", []),
            reference_urls=data.get("reference_urls", []),
        )
        return msg


@dataclass
class UserInbox:
    """User's personal inbox with filtering and prioritization"""

    user_id: str
    messages: list[InboxMessage] = field(default_factory=list)
    last_checked: datetime | None = None

    def add_message(self, message: InboxMessage):
        """Add message to inbox"""
        self.messages.append(message)
        self.messages.sort(key=lambda m: (m.priority.value, m.urgency, m.created_at), reverse=True)

    def get_unread_count(self) -> int:
        """Get count of unread messages"""
        return len([m for m in self.messages if m.status == TaskStatus.UNREAD])

    def get_urgent_tasks(self) -> list[InboxMessage]:
        """Get urgent unread tasks"""
        return [
            m
            for m in self.messages
            if m.status in [TaskStatus.UNREAD, TaskStatus.IN_PROGRESS] and m.urgency >= 4
        ]

    def get_messages_by_type(self, msg_type: MessageType) -> list[InboxMessage]:
        """Filter messages by type"""
        return [m for m in self.messages if m.message_type == msg_type]

    def get_pending_decisions(self) -> list[InboxMessage]:
        """Get messages requiring decisions"""
        return [
            m
            for m in self.messages
            if m.status in [TaskStatus.UNREAD, TaskStatus.IN_PROGRESS]
            and m.message_type in [MessageType.REQUEST, MessageType.DIRECT_ORDER]
        ]


# PostgreSQL Table Schemas (for full system)
INBOX_SCHEMA = """
CREATE TABLE user_inbox_messages (
    message_id UUID PRIMARY KEY,
    workflow_id UUID,
    thread_id UUID,
    from_user_id VARCHAR(100) NOT NULL,
    to_user_id VARCHAR(100) NOT NULL,
    cc_user_ids TEXT[], -- Array of user IDs

    message_type VARCHAR(50) NOT NULL,
    priority INTEGER NOT NULL,
    urgency INTEGER NOT NULL,
    mood VARCHAR(50),

    original_message TEXT NOT NULL,
    processed_message TEXT,
    intention TEXT,
    context JSONB,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    due_date TIMESTAMP WITH TIME ZONE,
    escalation_date TIMESTAMP WITH TIME ZONE,

    status VARCHAR(50) NOT NULL DEFAULT 'unread',
    read_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    related_entities TEXT[], -- Neo4j entity IDs
    decision_factors TEXT[],

    sentiment_score REAL DEFAULT 0.0,
    complexity_score INTEGER DEFAULT 3,
    stakeholder_impact TEXT[],

    attachment_ids TEXT[], -- Blob storage references
    reference_urls TEXT[],

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_inbox_user_status ON user_inbox_messages(to_user_id, status);
CREATE INDEX idx_inbox_priority ON user_inbox_messages(priority DESC, urgency DESC);
CREATE INDEX idx_inbox_workflow ON user_inbox_messages(workflow_id);
CREATE INDEX idx_inbox_created ON user_inbox_messages(created_at DESC);
"""

# Neo4j Relationships (for full system)
NEO4J_RELATIONSHIPS = """
# User relationships
(:User)-[:REPORTS_TO]->(:User)
(:User)-[:COLLABORATES_WITH]->(:User)
(:User)-[:MANAGES]->(:Department)

# Message relationships
(:Message)-[:SENT_BY]->(:User)
(:Message)-[:SENT_TO]->(:User)
(:Message)-[:PART_OF]->(:Workflow)
(:Message)-[:REFERENCES]->(:Entity)
(:Message)-[:IMPACTS]->(:Stakeholder)

# Context relationships
(:Message)-[:RELATES_TO]->(:Project)
(:Message)-[:CONCERNS]->(:Customer)
(:Message)-[:AFFECTS]->(:Budget)
"""
