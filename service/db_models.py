"""
Database models for the OrganizationalTwin inbox system
Production-ready with SQLAlchemy ORM, easily migrated to PostgreSQL + Neo4j + Weaviate
"""

from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker

Base = declarative_base()


class User(Base):
    """User table - basic user information"""

    __tablename__ = "users"

    id = Column(String(50), primary_key=True)  # e.g., "mary", "john"
    email = Column(String(200), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    role = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)

    # Profile attributes (will move to Neo4j in production)
    personality_traits = Column(JSON)  # Store YAML personality data as JSON

    # Relationships
    sent_messages = relationship(
        "InboxMessage", foreign_keys="InboxMessage.from_user_id", back_populates="sender"
    )
    received_messages = relationship(
        "InboxMessage", foreign_keys="InboxMessage.to_user_id", back_populates="recipient"
    )

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Workflow(Base):
    """Workflow tracking table - mirrors Temporal workflow instances"""

    __tablename__ = "workflows"

    id = Column(String(100), primary_key=True)  # Temporal workflow ID
    workflow_type = Column(String(100), nullable=False)
    status = Column(String(50), default="running")  # running, completed, failed, cancelled
    initiator_user_id = Column(String(50), ForeignKey("users.id"))

    # Workflow context
    context_data = Column(JSON)  # Store workflow-specific data

    # Relationships
    initiator = relationship("User", foreign_keys=[initiator_user_id])
    messages = relationship("InboxMessage", back_populates="workflow")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class InboxMessage(Base):
    """Rich inbox message table - production ready"""

    __tablename__ = "inbox_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(String(100), unique=True, nullable=False)  # UUID
    workflow_id = Column(String(100), ForeignKey("workflows.id"), nullable=True)
    thread_id = Column(String(100), nullable=True)

    # Users
    from_user_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    to_user_id = Column(String(50), ForeignKey("users.id"), nullable=False)

    # Message classification
    message_type = Column(String(50), nullable=False)  # nudge, recommendation, direct_order, etc.
    priority = Column(Integer, default=3)  # 1=LOW to 5=CRITICAL
    urgency = Column(Integer, default=3)  # 1-5 scale
    mood = Column(String(50), default="neutral")

    # Content
    original_message = Column(Text, nullable=False)
    processed_message = Column(Text)  # AI-enhanced/personalized version
    intention = Column(String(200))  # Extracted intent
    context_data = Column(JSON)  # Additional context

    # Timing
    due_date = Column(DateTime, nullable=True)
    escalation_date = Column(DateTime, nullable=True)

    # Status tracking
    status = Column(String(50), default="unread")  # unread, read, in_progress, completed, etc.
    read_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # AI enhancements (will move to Weaviate in production)
    sentiment_score = Column(Float, default=0.0)  # -1 to 1
    complexity_score = Column(Integer, default=3)  # 1-5

    # Relationships
    sender = relationship("User", foreign_keys=[from_user_id], back_populates="sent_messages")
    recipient = relationship("User", foreign_keys=[to_user_id], back_populates="received_messages")
    workflow = relationship("Workflow", back_populates="messages")

    # Neo4j will handle these relationships in production:
    related_entities = Column(JSON)  # List of entity IDs
    decision_factors = Column(JSON)  # List of factors
    stakeholder_impact = Column(JSON)  # List of affected stakeholders

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "message_id": self.message_id,
            "workflow_id": self.workflow_id,
            "from_user_id": self.from_user_id,
            "to_user_id": self.to_user_id,
            "message_type": self.message_type,
            "priority": self.priority,
            "urgency": self.urgency,
            "mood": self.mood,
            "original_message": self.original_message,
            "processed_message": self.processed_message,
            "intention": self.intention,
            "context_data": self.context_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "status": self.status,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "sentiment_score": self.sentiment_score,
            "complexity_score": self.complexity_score,
            "related_entities": self.related_entities or [],
            "decision_factors": self.decision_factors or [],
            "stakeholder_impact": self.stakeholder_impact or [],
        }


class DatabaseManager:
    """Database connection and session management"""

    def __init__(self, database_url: str = None):
        if database_url is None:
            # Default to SQLite file in project root
            db_path = Path(__file__).parent.parent / "organizational_twin.db"
            database_url = f"sqlite:///{db_path}"

        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        # Create tables
        Base.metadata.create_all(bind=self.engine)

    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()

    def init_demo_users(self):
        """Initialize demo users in database"""
        with self.get_session() as session:
            # Check if users already exist
            if session.query(User).first():
                return

            demo_users = [
                User(
                    id="mary",
                    email="mary.okeefe@globex-industrial-group.com",
                    name="Mary O'Keefe",
                    role="CEO",
                    department="Executive",
                    personality_traits={
                        "decision_style": "decisive",
                        "response_time": "fast",
                        "agreement_tendency": "moderate",
                    },
                ),
                User(
                    id="john",
                    email="john.appelkvist@globex-industrial-group.com",
                    name="John Appelkvist",
                    role="VP of Sales",
                    department="Sales",
                    personality_traits={
                        "decision_style": "collaborative",
                        "response_time": "moderate",
                        "agreement_tendency": "high",
                    },
                ),
                User(
                    id="isac",
                    email="isac.ironsmith@globex-industrial-group.com",
                    name='Isac "Happy" Ironsmith',
                    role="VP of Engineering",
                    department="Engineering",
                    personality_traits={
                        "decision_style": "analytical",
                        "response_time": "slow",
                        "agreement_tendency": "low",
                    },
                ),
                User(
                    id="priya",
                    email="priya.sharma@globex-industrial-group.com",
                    name="Priya Sharma",
                    role="VP of Legal",
                    department="Legal",
                    personality_traits={
                        "decision_style": "analytical",
                        "response_time": "slow",
                        "agreement_tendency": "low",
                    },
                ),
                User(
                    id="bob",
                    email="bob.greenland@globex-industrial-group.com",
                    name="Bob Greenland",
                    role="IT Admin",
                    department="IT",
                    personality_traits={
                        "decision_style": "analytical",
                        "response_time": "fast",
                        "agreement_tendency": "moderate",
                    },
                ),
            ]

            session.add_all(demo_users)
            session.commit()
            print("✅ Demo users initialized in database")


# Global database instance
db_manager = DatabaseManager()
