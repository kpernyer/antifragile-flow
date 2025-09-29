#!/usr/bin/env python3
"""Clear all data from the database"""

from db_inbox_service import DatabaseInboxService
from db_models import InboxMessage, Workflow, db_manager


def clear_all_data():
    """Clear all inbox messages and workflows from database"""
    db_service = DatabaseInboxService()
    session = db_manager.get_session()
    try:
        # Delete all inbox messages using ORM
        session.query(InboxMessage).delete()
        # Delete all workflows using ORM
        session.query(Workflow).delete()
        session.commit()
        print("✅ All inboxes and workflows cleared from database")
    except Exception as e:
        session.rollback()
        print(f"❌ Error clearing database: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    clear_all_data()
