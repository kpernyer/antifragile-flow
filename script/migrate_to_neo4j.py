#!/usr/bin/env python3
"""
Migration script to move organizational data from SQLite to Neo4j
This script extracts user and organizational data and creates a graph structure
"""

from datetime import datetime
import json
import logging
import sqlite3
from typing import Any

from neo4j import GraphDatabase


class Neo4jMigrator:
    def __init__(self, sqlite_path: str, neo4j_uri: str, neo4j_user: str, neo4j_password: str):
        self.sqlite_path = sqlite_path
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self.logger = logging.getLogger(__name__)

    def close(self):
        self.driver.close()

    def extract_sqlite_data(self) -> dict[str, list[dict[str, Any]]]:
        """Extract organizational data from SQLite"""
        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = sqlite3.Row

        # Extract users (these become Person nodes)
        users_query = """
        SELECT id, email, name, role, department, personality_traits, created_at, updated_at
        FROM users
        """
        users = [dict(row) for row in conn.execute(users_query).fetchall()]

        # Extract workflows (for relationship context)
        workflows_query = """
        SELECT id, workflow_type, status, initiator_user_id, context_data, created_at, updated_at
        FROM workflows
        """
        workflows = [dict(row) for row in conn.execute(workflows_query).fetchall()]

        conn.close()

        return {"users": users, "workflows": workflows}

    def migrate_organizational_structure(self, data: dict[str, list[dict[str, Any]]]):
        """Create organizational graph structure in Neo4j"""

        # Helper function for datetime parsing
        def parse_datetime(dt_str):
            if not dt_str:
                return datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

            try:
                # Try different datetime formats
                if " " in dt_str:
                    # SQLite format: "2025-09-26 15:50:39.851479"
                    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S.%f")
                else:
                    # ISO format
                    dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))

                return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            except:
                return datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        with self.driver.session() as session:
            # Clear existing data (be careful in production!)
            session.run("MATCH (n) DETACH DELETE n")

            # Create departments first
            departments = set()
            roles = set()

            for user in data["users"]:
                departments.add(user["department"])
                roles.add((user["role"], user["department"]))

            # Create department nodes
            for dept_name in departments:
                session.run(
                    """
                    MERGE (d:Department {id: $dept_id})
                    SET d.name = $name,
                        d.created_at = datetime($created_at)
                """,
                    dept_id=f"dept-{dept_name.lower().replace(' ', '-')}",
                    name=dept_name,
                    created_at=datetime.now().isoformat(),
                )

            # Create role nodes
            for role_title, dept_name in roles:
                session.run(
                    """
                    MERGE (r:Role {id: $role_id})
                    SET r.title = $title,
                        r.department = $department,
                        r.created_at = datetime($created_at)
                """,
                    role_id=f"role-{role_title.lower().replace(' ', '-')}",
                    title=role_title,
                    department=dept_name,
                    created_at=datetime.now().isoformat(),
                )

            # Create person nodes and relationships
            for user in data["users"]:
                # Parse personality traits if it's a JSON string
                personality = user["personality_traits"]
                if isinstance(personality, str):
                    try:
                        personality = json.loads(personality)
                    except json.JSONDecodeError:
                        personality = {}

                # Create person node
                # Convert personality traits to JSON string for Neo4j
                personality_str = json.dumps(personality) if personality else ""

                # Convert datetime strings to proper ISO format for Neo4j
                created_at = parse_datetime(user["created_at"])
                updated_at = parse_datetime(user["updated_at"])

                session.run(
                    """
                    MERGE (p:Person {id: $id})
                    SET p.email = $email,
                        p.name = $name,
                        p.title = $role,
                        p.personality_traits = $personality,
                        p.created_at = $created_at,
                        p.updated_at = $updated_at
                """,
                    id=user["id"],
                    email=user["email"],
                    name=user["name"],
                    role=user["role"],
                    personality=personality_str,
                    created_at=created_at,
                    updated_at=updated_at,
                )

                # Create relationships
                dept_id = f"dept-{user['department'].lower().replace(' ', '-')}"
                role_id = f"role-{user['role'].lower().replace(' ', '-')}"

                # Person -> Department relationship
                session.run(
                    """
                    MATCH (p:Person {id: $person_id})
                    MATCH (d:Department {id: $dept_id})
                    MERGE (p)-[:BELONGS_TO]->(d)
                """,
                    person_id=user["id"],
                    dept_id=dept_id,
                )

                # Person -> Role relationship
                session.run(
                    """
                    MATCH (p:Person {id: $person_id})
                    MATCH (r:Role {id: $role_id})
                    MERGE (p)-[:HAS_ROLE]->(r)
                """,
                    person_id=user["id"],
                    role_id=role_id,
                )

                # Role -> Department relationship
                session.run(
                    """
                    MATCH (r:Role {id: $role_id})
                    MATCH (d:Department {id: $dept_id})
                    MERGE (r)-[:IN_DEPARTMENT]->(d)
                """,
                    role_id=role_id,
                    dept_id=dept_id,
                )

            # Create organizational hierarchy relationships
            # This is a simplified hierarchy - you might want to make this more sophisticated
            session.run("""
                MATCH (ceo:Person)-[:HAS_ROLE]->(:Role {title: "CEO"})
                MATCH (vp:Person)-[:HAS_ROLE]->(:Role) WHERE vp.title STARTS WITH "VP"
                MERGE (vp)-[:REPORTS_TO]->(ceo)
            """)

            # Create workflow relationships
            for workflow in data["workflows"]:
                if workflow["initiator_user_id"]:
                    created_at = parse_datetime(workflow["created_at"])

                    session.run(
                        """
                        MATCH (p:Person {id: $person_id})
                        MERGE (w:Workflow {id: $workflow_id})
                        SET w.type = $workflow_type,
                            w.status = $status,
                            w.created_at = $created_at
                        MERGE (p)-[:INITIATED]->(w)
                    """,
                        person_id=workflow["initiator_user_id"],
                        workflow_id=workflow["id"],
                        workflow_type=workflow["workflow_type"],
                        status=workflow["status"],
                        created_at=created_at,
                    )

    def verify_migration(self):
        """Verify the migration was successful"""
        with self.driver.session() as session:
            # Count nodes
            result = session.run("MATCH (n) RETURN labels(n) as labels, count(n) as count")
            for record in result:
                self.logger.info(f"{record['labels']}: {record['count']} nodes")

            # Show sample relationships
            result = session.run("""
                MATCH (p:Person)-[r]->(other)
                RETURN p.name, type(r), labels(other), other.name
                LIMIT 10
            """)

            self.logger.info("Sample relationships:")
            for record in result:
                self.logger.info(
                    f"{record['p.name']} -{record['type(r)']}-> {record['labels(other)']} {record.get('other.name', '')}"
                )


def main():
    logging.basicConfig(level=logging.INFO)

    # Configuration
    sqlite_path = "organizational_twin.db"
    neo4j_uri = "bolt://localhost:7687"
    neo4j_user = "neo4j"
    neo4j_password = "neo4j_password"

    migrator = Neo4jMigrator(sqlite_path, neo4j_uri, neo4j_user, neo4j_password)

    try:
        print("🔄 Extracting data from SQLite...")
        data = migrator.extract_sqlite_data()
        print(f"✅ Extracted {len(data['users'])} users and {len(data['workflows'])} workflows")

        print("🔄 Migrating to Neo4j...")
        migrator.migrate_organizational_structure(data)
        print("✅ Migration completed")

        print("🔄 Verifying migration...")
        migrator.verify_migration()
        print("✅ Verification completed")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        migrator.close()


if __name__ == "__main__":
    main()
