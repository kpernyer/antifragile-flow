#!/usr/bin/env python3
"""
Migration script to move inbox data from SQLite to PostgreSQL
This script preserves all inbox messages and workflow data
"""

import json
import logging
import sqlite3
from typing import Any

import psycopg2
from psycopg2.extras import Json, RealDictCursor


class PostgreSQLMigrator:
    def __init__(self, sqlite_path: str, postgres_config: dict[str, str]):
        self.sqlite_path = sqlite_path
        self.postgres_config = postgres_config
        self.logger = logging.getLogger(__name__)

    def extract_sqlite_data(self) -> dict[str, list[dict[str, Any]]]:
        """Extract inbox and workflow data from SQLite"""
        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = sqlite3.Row

        # Extract workflows
        workflows_query = """
        SELECT id, workflow_type, status, initiator_user_id, context_data, created_at, updated_at
        FROM workflows
        """
        workflows = [dict(row) for row in conn.execute(workflows_query).fetchall()]

        # Extract inbox messages
        messages_query = """
        SELECT id, message_id, workflow_id, thread_id, from_user_id, to_user_id,
               message_type, priority, urgency, mood, original_message, processed_message,
               intention, context_data, due_date, escalation_date, status, read_at,
               completed_at, sentiment_score, complexity_score, related_entities,
               decision_factors, stakeholder_impact, created_at, updated_at
        FROM inbox_messages
        """
        messages = [dict(row) for row in conn.execute(messages_query).fetchall()]

        conn.close()

        return {"workflows": workflows, "messages": messages}

    def create_postgres_tables(self, conn):
        """Create PostgreSQL tables with proper schema"""
        cursor = conn.cursor()

        # Create workflows table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflows (
                id VARCHAR(100) PRIMARY KEY,
                workflow_type VARCHAR(100) NOT NULL,
                status VARCHAR(50) DEFAULT 'running',
                initiator_user_id VARCHAR(50),
                context_data JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create inbox_messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inbox_messages (
                id SERIAL PRIMARY KEY,
                message_id VARCHAR(100) UNIQUE NOT NULL,
                workflow_id VARCHAR(100) REFERENCES workflows(id),
                thread_id VARCHAR(100),
                from_user_id VARCHAR(50) NOT NULL,
                to_user_id VARCHAR(50) NOT NULL,
                message_type VARCHAR(50) NOT NULL,
                priority INTEGER DEFAULT 3,
                urgency INTEGER DEFAULT 3,
                mood VARCHAR(50) DEFAULT 'neutral',
                original_message TEXT NOT NULL,
                processed_message TEXT,
                intention VARCHAR(200),
                context_data JSONB,
                due_date TIMESTAMP WITH TIME ZONE,
                escalation_date TIMESTAMP WITH TIME ZONE,
                status VARCHAR(50) DEFAULT 'unread',
                read_at TIMESTAMP WITH TIME ZONE,
                completed_at TIMESTAMP WITH TIME ZONE,
                sentiment_score FLOAT DEFAULT 0.0,
                complexity_score INTEGER DEFAULT 3,
                related_entities JSONB,
                decision_factors JSONB,
                stakeholder_impact JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_from_user ON inbox_messages(from_user_id);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_to_user ON inbox_messages(to_user_id);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_workflow ON inbox_messages(workflow_id);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_status ON inbox_messages(status);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_created_at ON inbox_messages(created_at);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_workflows_initiator ON workflows(initiator_user_id);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_workflows_type ON workflows(workflow_type);
        """)

        # Create trigger for updated_at
        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql';
        """)

        cursor.execute("""
            DROP TRIGGER IF EXISTS update_workflows_updated_at ON workflows;
            CREATE TRIGGER update_workflows_updated_at
                BEFORE UPDATE ON workflows
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """)

        cursor.execute("""
            DROP TRIGGER IF EXISTS update_messages_updated_at ON inbox_messages;
            CREATE TRIGGER update_messages_updated_at
                BEFORE UPDATE ON inbox_messages
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """)

        conn.commit()

    def migrate_data_to_postgres(self, data: dict[str, list[dict[str, Any]]]):
        """Migrate data to PostgreSQL"""
        conn = psycopg2.connect(**self.postgres_config)

        try:
            self.create_postgres_tables(conn)
            cursor = conn.cursor()

            # Clear existing data (be careful in production!)
            cursor.execute("DELETE FROM inbox_messages")
            cursor.execute("DELETE FROM workflows")

            # Migrate workflows
            for workflow in data["workflows"]:
                context_data = workflow["context_data"]
                if isinstance(context_data, str):
                    try:
                        context_data = json.loads(context_data)
                    except json.JSONDecodeError:
                        context_data = {}

                cursor.execute(
                    """
                    INSERT INTO workflows (id, workflow_type, status, initiator_user_id, context_data, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        workflow["id"],
                        workflow["workflow_type"],
                        workflow["status"],
                        workflow["initiator_user_id"],
                        Json(context_data),
                        workflow["created_at"],
                        workflow["updated_at"],
                    ),
                )

            # Migrate inbox messages
            for message in data["messages"]:
                # Parse JSON fields
                context_data = self._parse_json_field(message["context_data"])
                related_entities = self._parse_json_field(message["related_entities"])
                decision_factors = self._parse_json_field(message["decision_factors"])
                stakeholder_impact = self._parse_json_field(message["stakeholder_impact"])

                cursor.execute(
                    """
                    INSERT INTO inbox_messages (
                        message_id, workflow_id, thread_id, from_user_id, to_user_id,
                        message_type, priority, urgency, mood, original_message, processed_message,
                        intention, context_data, due_date, escalation_date, status, read_at,
                        completed_at, sentiment_score, complexity_score, related_entities,
                        decision_factors, stakeholder_impact, created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """,
                    (
                        message["message_id"],
                        message["workflow_id"],
                        message["thread_id"],
                        message["from_user_id"],
                        message["to_user_id"],
                        message["message_type"],
                        message["priority"],
                        message["urgency"],
                        message["mood"],
                        message["original_message"],
                        message["processed_message"],
                        message["intention"],
                        Json(context_data),
                        message["due_date"],
                        message["escalation_date"],
                        message["status"],
                        message["read_at"],
                        message["completed_at"],
                        message["sentiment_score"],
                        message["complexity_score"],
                        Json(related_entities),
                        Json(decision_factors),
                        Json(stakeholder_impact),
                        message["created_at"],
                        message["updated_at"],
                    ),
                )

            conn.commit()

        finally:
            conn.close()

    def _parse_json_field(self, field_value):
        """Helper to parse JSON fields that might be strings"""
        if field_value is None:
            return {}
        if isinstance(field_value, str):
            try:
                return json.loads(field_value)
            except json.JSONDecodeError:
                return {}
        return field_value

    def verify_migration(self):
        """Verify the migration was successful"""
        conn = psycopg2.connect(**self.postgres_config, cursor_factory=RealDictCursor)

        try:
            cursor = conn.cursor()

            # Count records
            cursor.execute("SELECT COUNT(*) as count FROM workflows")
            workflow_count = cursor.fetchone()["count"]

            cursor.execute("SELECT COUNT(*) as count FROM inbox_messages")
            message_count = cursor.fetchone()["count"]

            self.logger.info(f"Workflows migrated: {workflow_count}")
            self.logger.info(f"Messages migrated: {message_count}")

            # Show sample data
            cursor.execute("""
                SELECT m.message_id, m.from_user_id, m.to_user_id, m.message_type, w.workflow_type
                FROM inbox_messages m
                LEFT JOIN workflows w ON m.workflow_id = w.id
                LIMIT 5
            """)

            self.logger.info("Sample migrated messages:")
            for record in cursor.fetchall():
                self.logger.info(
                    f"Message {record['message_id']}: {record['from_user_id']} -> {record['to_user_id']} ({record['message_type']}) [{record['workflow_type']}]"
                )

        finally:
            conn.close()


def main():
    logging.basicConfig(level=logging.INFO)

    # Configuration
    sqlite_path = "organizational_twin.db"
    postgres_config = {
        "host": "localhost",
        "port": 5433,
        "database": "antifragile",
        "user": "app_user",
        "password": "app_password",
    }

    migrator = PostgreSQLMigrator(sqlite_path, postgres_config)

    try:
        print("🔄 Extracting data from SQLite...")
        data = migrator.extract_sqlite_data()
        print(
            f"✅ Extracted {len(data['workflows'])} workflows and {len(data['messages'])} messages"
        )

        print("🔄 Migrating to PostgreSQL...")
        migrator.migrate_data_to_postgres(data)
        print("✅ Migration completed")

        print("🔄 Verifying migration...")
        migrator.verify_migration()
        print("✅ Verification completed")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise


if __name__ == "__main__":
    main()
