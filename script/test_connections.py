#!/usr/bin/env python3
"""
Test script to verify database connections and run migrations
"""

import logging
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from neo4j_service import Neo4jService
from postgres_models import PostgresInboxService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_postgres_connection():
    """Test PostgreSQL connection and basic operations"""
    try:
        logger.info("🔄 Testing PostgreSQL connection...")

        # Initialize service
        service = PostgresInboxService()

        # Test basic query
        from sqlalchemy import text

        with service.get_session() as session:
            result = session.execute(text("SELECT 1 as test")).fetchone()
            logger.info(f"✅ PostgreSQL connection successful: {result}")

        # Test creating a workflow (use timestamp to ensure uniqueness)
        import time

        timestamp = int(time.time())
        workflow_data = {
            "id": f"test-workflow-{timestamp}",
            "workflow_type": "organizational_message",
            "status": "running",
            "initiator_user_id": "mary",
        }
        workflow = service.create_workflow(workflow_data)
        logger.info(f"✅ Created test workflow: {workflow.id}")

        # Test creating a message
        message_data = {
            "workflow_id": workflow.id,
            "from_user_id": "mary",
            "to_user_id": "john",
            "message_type": "test",
            "original_message": "Test message for database verification",
            "tags": ["test", "verification"],
            "context_data": {"test": True},
        }
        message = service.create_message(message_data)
        logger.info(f"✅ Created test message: {message.message_id}")

        # Test querying messages
        messages = service.get_messages_for_user("john", limit=5)
        logger.info(f"✅ Retrieved {len(messages)} messages for user john")

        # Test stats
        stats = service.get_user_message_stats("john")
        logger.info(f"✅ User stats: {stats}")

        return True

    except Exception as e:
        logger.error(f"❌ PostgreSQL test failed: {e}")
        return False


def test_neo4j_connection():
    """Test Neo4j connection and basic operations"""
    try:
        logger.info("🔄 Testing Neo4j connection...")

        # Initialize service
        service = Neo4jService()

        # Test basic query
        with service.driver.session() as session:
            result = session.run("RETURN 1 as test")
            record = result.single()
            logger.info(f"✅ Neo4j connection successful: {record}")

        # Test creating a person (use timestamp to ensure uniqueness)
        import time

        timestamp = int(time.time())
        person_data = {
            "id": f"test-person-{timestamp}",
            "email": f"test-{timestamp}@example.com",
            "name": f"Test Person {timestamp}",
            "title": "Test Manager",
        }
        result = service.create_person(person_data)
        logger.info(f"✅ Created test person: {person_data['id']}")

        # Test querying person
        person = service.get_person(person_data["id"])
        if person:
            logger.info(f"✅ Retrieved person: {person['name']}")

        # Test basic query instead of search (fulltext index not set up yet)
        with service.driver.session() as session:
            result = session.run("MATCH (p:Person) WHERE p.name CONTAINS 'Test' RETURN p LIMIT 10")
            search_results = list(result)
            logger.info(f"✅ Basic search returned {len(search_results)} results")

        service.close()
        return True

    except Exception as e:
        logger.error(f"❌ Neo4j test failed: {e}")
        return False


def run_migrations():
    """Run the migration scripts"""
    try:
        logger.info("🔄 Running migrations...")

        # Import and run PostgreSQL migration
        logger.info("📦 Running PostgreSQL migration...")
        from migrate_to_postgres import PostgreSQLMigrator

        postgres_config = {
            "host": "localhost",
            "port": 5433,
            "database": "antifragile",
            "user": "app_user",
            "password": "app_password",
        }

        postgres_migrator = PostgreSQLMigrator("organizational_twin.db", postgres_config)
        data = postgres_migrator.extract_sqlite_data()
        postgres_migrator.migrate_data_to_postgres(data)
        postgres_migrator.verify_migration()
        logger.info("✅ PostgreSQL migration completed")

        # Import and run Neo4j migration
        logger.info("📦 Running Neo4j migration...")
        from migrate_to_neo4j import Neo4jMigrator

        neo4j_migrator = Neo4jMigrator(
            "organizational_twin.db", "bolt://localhost:7687", "neo4j", "neo4j_password"
        )

        data = neo4j_migrator.extract_sqlite_data()
        neo4j_migrator.migrate_organizational_structure(data)
        neo4j_migrator.verify_migration()
        neo4j_migrator.close()
        logger.info("✅ Neo4j migration completed")

        return True

    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False


def main():
    """Main test function"""
    logger.info("🚀 Starting database connection tests...")

    # Test PostgreSQL
    postgres_ok = test_postgres_connection()

    # Test Neo4j (wait a bit more if it just started)
    import time

    time.sleep(5)
    neo4j_ok = test_neo4j_connection()

    # Run migrations if both are working
    if postgres_ok and neo4j_ok:
        logger.info("🔄 Both databases working, running migrations...")
        migration_ok = run_migrations()

        if migration_ok:
            logger.info("🎉 All tests and migrations completed successfully!")
            return True

    if not postgres_ok:
        logger.error("❌ PostgreSQL connection failed")
    if not neo4j_ok:
        logger.error("❌ Neo4j connection failed")

    return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
