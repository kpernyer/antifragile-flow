"""
Database-backed inbox service for OrganizationalTwin
Production-ready with proper transaction handling and relationship management
"""

from datetime import datetime, timedelta
from typing import Any
import uuid

from db_models import DatabaseManager, InboxMessage, Workflow, db_manager
from inbox_models import MessageType, Mood, Priority
from sqlalchemy import and_, desc


class DatabaseInboxService:
    """
    Pure database persistence layer for inbox messages
    Used by OrganizationalTwin for data storage - contains no business logic
    """

    def __init__(self, db_manager_instance: DatabaseManager = None):
        self.db_manager = db_manager_instance or db_manager
        # Initialize demo users on startup
        self.db_manager.init_demo_users()

    def create_workflow_record(
        self, workflow_id: str, workflow_type: str, initiator_id: str, context: dict = None
    ):
        """Create workflow record in database"""
        with self.db_manager.get_session() as session:
            workflow = Workflow(
                id=workflow_id,
                workflow_type=workflow_type,
                initiator_user_id=initiator_id,
                context_data=context or {},
            )
            session.add(workflow)
            session.commit()

    def add_message_to_workflow(
        self,
        workflow_id: str,
        from_user_id: str,
        to_user_id: str,
        message_type: MessageType,
        priority: Priority,
        urgency: int,
        original_message: str,
        processed_message: str = None,
        intention: str = None,
        context: dict = None,
        due_hours: int = 24,
    ) -> str:
        """Add message to user's inbox linked to workflow"""

        with self.db_manager.get_session() as session:
            message_id = str(uuid.uuid4())

            # Calculate due date based on urgency
            due_date = datetime.utcnow() + timedelta(hours=due_hours)

            message = InboxMessage(
                message_id=message_id,
                workflow_id=workflow_id,
                from_user_id=from_user_id,
                to_user_id=to_user_id,
                message_type=message_type.value
                if isinstance(message_type, MessageType)
                else message_type,
                priority=priority.value if isinstance(priority, Priority) else priority,
                urgency=urgency,
                mood=Mood.CONCERNED.value if urgency >= 4 else Mood.NEUTRAL.value,
                original_message=original_message,
                processed_message=processed_message or original_message,
                intention=intention or "workflow_participation",
                context_data=context or {},
                due_date=due_date,
                related_entities=context.get("related_entities", []) if context else [],
                decision_factors=context.get("decision_factors", []) if context else [],
            )

            session.add(message)
            session.commit()
            return message_id

    def get_user_inbox_summary(self, user_id: str) -> dict[str, Any]:
        """Get inbox summary for dashboard"""
        with self.db_manager.get_session() as session:
            # Get all messages for user
            messages = session.query(InboxMessage).filter(InboxMessage.to_user_id == user_id).all()

            unread = [m for m in messages if m.status == "unread"]
            urgent = [
                m for m in messages if m.urgency >= 4 and m.status in ["unread", "in_progress"]
            ]
            decisions = [
                m
                for m in messages
                if m.message_type in ["request", "direct_order"]
                and m.status in ["unread", "in_progress"]
            ]

            return {
                "total_messages": len(messages),
                "unread_count": len(unread),
                "urgent_count": len(urgent),
                "pending_decisions": len(decisions),
                "recent_messages": [m.to_dict() for m in messages[:5]],
            }

    def get_urgent_tasks(self, user_id: str) -> list[dict]:
        """Get urgent tasks for user"""
        with self.db_manager.get_session() as session:
            messages = (
                session.query(InboxMessage)
                .filter(
                    and_(
                        InboxMessage.to_user_id == user_id,
                        InboxMessage.urgency >= 4,
                        InboxMessage.status.in_(["unread", "in_progress"]),
                    )
                )
                .order_by(desc(InboxMessage.urgency), desc(InboxMessage.priority))
                .all()
            )

            return [m.to_dict() for m in messages]

    def get_pending_decisions(self, user_id: str) -> list[dict]:
        """Get pending decisions for user"""
        with self.db_manager.get_session() as session:
            messages = (
                session.query(InboxMessage)
                .filter(
                    and_(
                        InboxMessage.to_user_id == user_id,
                        InboxMessage.message_type.in_(["request", "direct_order"]),
                        InboxMessage.status.in_(["unread", "in_progress"]),
                    )
                )
                .order_by(desc(InboxMessage.priority), InboxMessage.due_date)
                .all()
            )

            return [m.to_dict() for m in messages]

    def get_unread_messages(self, user_id: str, limit: int = 10) -> list[dict]:
        """Get unread messages for user"""
        with self.db_manager.get_session() as session:
            messages = (
                session.query(InboxMessage)
                .filter(and_(InboxMessage.to_user_id == user_id, InboxMessage.status == "unread"))
                .order_by(desc(InboxMessage.created_at))
                .limit(limit)
                .all()
            )

            return [m.to_dict() for m in messages]

    def mark_message_read(self, message_id: str, user_id: str) -> bool:
        """Mark message as read"""
        with self.db_manager.get_session() as session:
            message = (
                session.query(InboxMessage)
                .filter(
                    and_(InboxMessage.message_id == message_id, InboxMessage.to_user_id == user_id)
                )
                .first()
            )

            if message:
                message.status = "read"
                message.read_at = datetime.utcnow()
                session.commit()
                return True
            return False

    def mark_message_completed(self, message_id: str, user_id: str) -> bool:
        """Mark message as completed"""
        with self.db_manager.get_session() as session:
            message = (
                session.query(InboxMessage)
                .filter(
                    and_(InboxMessage.message_id == message_id, InboxMessage.to_user_id == user_id)
                )
                .first()
            )

            if message:
                message.status = "completed"
                message.completed_at = datetime.utcnow()
                session.commit()
                return True
            return False

    def update_workflow_status(self, workflow_id: str, status: str):
        """Update workflow status"""
        with self.db_manager.get_session() as session:
            workflow = session.query(Workflow).filter(Workflow.id == workflow_id).first()
            if workflow:
                workflow.status = status
                workflow.updated_at = datetime.utcnow()
                session.commit()


# Global database inbox service instance
db_inbox_service = DatabaseInboxService()
