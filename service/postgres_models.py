"""
PostgreSQL models for the inbox system
Production-ready with SQLAlchemy ORM and proper PostgreSQL features
"""

from typing import Any
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker
from sqlalchemy.sql import func

Base = declarative_base()


class Workflow(Base):
    """Workflow tracking table for PostgreSQL"""

    __tablename__ = "workflows"

    id = Column(String(100), primary_key=True)
    workflow_type = Column(String(100), nullable=False)
    status = Column(String(50), default="running")
    initiator_user_id = Column(String(50), nullable=True)  # References Neo4j person
    context_data = Column(JSONB, default=dict)

    # Relationships
    messages = relationship("InboxMessage", back_populates="workflow")

    # Timestamps with timezone support
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "workflow_type": self.workflow_type,
            "status": self.status,
            "initiator_user_id": self.initiator_user_id,
            "context_data": self.context_data or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class InboxMessage(Base):
    """Enhanced inbox message table for PostgreSQL"""

    __tablename__ = "inbox_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(String(100), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String(100), ForeignKey("workflows.id"), nullable=True)
    thread_id = Column(String(100), nullable=True)

    # User references (these reference Neo4j person IDs)
    from_user_id = Column(String(50), nullable=False)
    to_user_id = Column(String(50), nullable=False)

    # Message classification
    message_type = Column(String(50), nullable=False)  # nudge, recommendation, direct_order, etc.
    priority = Column(Integer, default=3)  # 1=LOW to 5=CRITICAL
    urgency = Column(Integer, default=3)  # 1-5 scale
    mood = Column(String(50), default="neutral")

    # Content
    original_message = Column(Text, nullable=False)
    processed_message = Column(Text)
    intention = Column(String(200))
    context_data = Column(JSONB, default=dict)

    # Timing
    due_date = Column(DateTime(timezone=True), nullable=True)
    escalation_date = Column(DateTime(timezone=True), nullable=True)

    # Status tracking
    status = Column(String(50), default="unread")
    read_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # AI enhancements
    sentiment_score = Column(Float, default=0.0)  # -1 to 1
    complexity_score = Column(Integer, default=3)  # 1-5

    # PostgreSQL-specific enhancements
    tags = Column(ARRAY(String), default=list)  # Message tags for categorization
    attachments = Column(JSONB, default=list)  # File attachments metadata
    mentions = Column(ARRAY(String), default=list)  # @mentions in message

    # Rich relationships (stored as JSONB for flexibility)
    related_entities = Column(JSONB, default=list)
    decision_factors = Column(JSONB, default=list)
    stakeholder_impact = Column(JSONB, default=list)

    # Search and indexing
    search_vector = Column(Text)  # For full-text search

    # Audit fields
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    version = Column(Integer, default=1)

    # Relationships
    workflow = relationship("Workflow", back_populates="messages")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "message_id": self.message_id,
            "workflow_id": self.workflow_id,
            "thread_id": self.thread_id,
            "from_user_id": self.from_user_id,
            "to_user_id": self.to_user_id,
            "message_type": self.message_type,
            "priority": self.priority,
            "urgency": self.urgency,
            "mood": self.mood,
            "original_message": self.original_message,
            "processed_message": self.processed_message,
            "intention": self.intention,
            "context_data": self.context_data or {},
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "escalation_date": self.escalation_date.isoformat() if self.escalation_date else None,
            "status": self.status,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "sentiment_score": self.sentiment_score,
            "complexity_score": self.complexity_score,
            "tags": self.tags or [],
            "attachments": self.attachments or [],
            "mentions": self.mentions or [],
            "related_entities": self.related_entities or [],
            "decision_factors": self.decision_factors or [],
            "stakeholder_impact": self.stakeholder_impact or [],
            "is_deleted": self.is_deleted,
            "version": self.version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def soft_delete(self):
        """Soft delete the message"""
        self.is_deleted = True
        self.deleted_at = func.now()

    def mark_as_read(self):
        """Mark message as read"""
        if self.status == "unread":
            self.status = "read"
            self.read_at = func.now()

    def mark_as_completed(self):
        """Mark message as completed"""
        self.status = "completed"
        self.completed_at = func.now()


class MessageThread(Base):
    """Message thread tracking for conversation grouping"""

    __tablename__ = "message_threads"

    id = Column(String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    subject = Column(String(200), nullable=False)
    participants = Column(ARRAY(String), nullable=False)  # Array of user IDs
    thread_type = Column(String(50), default="conversation")  # conversation, notification, workflow
    is_active = Column(Boolean, default=True)

    # Thread metadata
    message_count = Column(Integer, default=0)
    last_message_at = Column(DateTime(timezone=True))
    created_by = Column(String(50), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class PostgresInboxService:
    """Service for managing inbox data in PostgreSQL"""

    def __init__(self, database_url: str = None):
        if database_url is None:
            database_url = "postgresql://app_user:app_password@localhost:5433/antifragile"

        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        # Create tables
        Base.metadata.create_all(bind=self.engine)

    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()

    def create_message(self, message_data: dict[str, Any]) -> InboxMessage:
        """Create a new inbox message"""
        with self.get_session() as session:
            message = InboxMessage(**message_data)
            session.add(message)
            session.commit()
            session.refresh(message)
            return message

    def get_messages_for_user(
        self, user_id: str, status: str | None = None, limit: int = 50
    ) -> list[InboxMessage]:
        """Get messages for a specific user"""
        with self.get_session() as session:
            query = session.query(InboxMessage).filter(
                InboxMessage.to_user_id == user_id, InboxMessage.is_deleted == False
            )

            if status:
                query = query.filter(InboxMessage.status == status)

            return query.order_by(InboxMessage.created_at.desc()).limit(limit).all()

    def get_message_by_id(self, message_id: str) -> InboxMessage | None:
        """Get message by ID"""
        with self.get_session() as session:
            return (
                session.query(InboxMessage)
                .filter(InboxMessage.message_id == message_id, InboxMessage.is_deleted == False)
                .first()
            )

    def update_message_status(self, message_id: str, status: str) -> bool:
        """Update message status"""
        with self.get_session() as session:
            message = (
                session.query(InboxMessage).filter(InboxMessage.message_id == message_id).first()
            )

            if message:
                message.status = status
                if status == "read" and not message.read_at:
                    message.read_at = func.now()
                elif status == "completed" and not message.completed_at:
                    message.completed_at = func.now()

                session.commit()
                return True
            return False

    def search_messages(
        self, user_id: str, search_term: str, limit: int = 20
    ) -> list[InboxMessage]:
        """Search messages by content"""
        with self.get_session() as session:
            return (
                session.query(InboxMessage)
                .filter(
                    InboxMessage.to_user_id == user_id,
                    InboxMessage.is_deleted == False,
                    InboxMessage.original_message.ilike(f"%{search_term}%"),
                )
                .order_by(InboxMessage.created_at.desc())
                .limit(limit)
                .all()
            )

    def get_messages_by_workflow(self, workflow_id: str) -> list[InboxMessage]:
        """Get all messages for a specific workflow"""
        with self.get_session() as session:
            return (
                session.query(InboxMessage)
                .filter(InboxMessage.workflow_id == workflow_id, InboxMessage.is_deleted == False)
                .order_by(InboxMessage.created_at.asc())
                .all()
            )

    def get_user_message_stats(self, user_id: str) -> dict[str, Any]:
        """Get message statistics for a user"""
        with self.get_session() as session:
            total = (
                session.query(InboxMessage)
                .filter(InboxMessage.to_user_id == user_id, InboxMessage.is_deleted == False)
                .count()
            )

            unread = (
                session.query(InboxMessage)
                .filter(
                    InboxMessage.to_user_id == user_id,
                    InboxMessage.status == "unread",
                    InboxMessage.is_deleted == False,
                )
                .count()
            )

            overdue = (
                session.query(InboxMessage)
                .filter(
                    InboxMessage.to_user_id == user_id,
                    InboxMessage.due_date < func.now(),
                    InboxMessage.status.notin_(["completed", "cancelled"]),
                    InboxMessage.is_deleted == False,
                )
                .count()
            )

            return {
                "total_messages": total,
                "unread_messages": unread,
                "overdue_messages": overdue,
                "read_messages": total - unread,
            }

    def create_workflow(self, workflow_data: dict[str, Any]) -> Workflow:
        """Create a new workflow"""
        with self.get_session() as session:
            workflow = Workflow(**workflow_data)
            session.add(workflow)
            session.commit()
            session.refresh(workflow)
            return workflow

    def get_workflow(self, workflow_id: str) -> Workflow | None:
        """Get workflow by ID"""
        with self.get_session() as session:
            return session.query(Workflow).filter(Workflow.id == workflow_id).first()

    def update_workflow_status(self, workflow_id: str, status: str) -> bool:
        """Update workflow status"""
        with self.get_session() as session:
            workflow = session.query(Workflow).filter(Workflow.id == workflow_id).first()
            if workflow:
                workflow.status = status
                session.commit()
                return True
            return False


# Global PostgreSQL service instance
postgres_inbox_service = PostgresInboxService()
