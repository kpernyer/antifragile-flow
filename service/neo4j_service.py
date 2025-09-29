"""
Neo4j service for organizational graph data
Handles organizational structure, relationships, and graph queries
"""

from datetime import datetime
import json
import logging
from typing import Any

from neo4j import GraphDatabase


class Neo4jService:
    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "neo4j_password",
    ):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.logger = logging.getLogger(__name__)

    def close(self):
        self.driver.close()

    def create_person(self, person_data: dict[str, Any]) -> dict[str, Any]:
        """Create a person node in the organizational graph"""
        with self.driver.session() as session:
            # Convert personality traits to string for Neo4j storage
            personality = person_data.get("personality_traits", {})
            personality_str = json.dumps(personality) if personality else ""

            result = session.run(
                """
                MERGE (p:Person {id: $id})
                SET p.email = $email,
                    p.name = $name,
                    p.title = $title,
                    p.personality_traits = $personality_traits,
                    p.updated_at = datetime($updated_at)
                RETURN p
            """,
                id=person_data["id"],
                email=person_data["email"],
                name=person_data["name"],
                title=person_data.get("title", ""),
                personality_traits=personality_str,
                updated_at=datetime.now().isoformat(),
            )
            return result.single()["p"]

    def get_person(self, person_id: str) -> dict[str, Any] | None:
        """Get person by ID"""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:Person {id: $id})
                RETURN p
            """,
                id=person_id,
            )

            record = result.single()
            return dict(record["p"]) if record else None

    def get_person_with_relationships(self, person_id: str) -> dict[str, Any]:
        """Get person with all their organizational relationships"""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:Person {id: $id})
                OPTIONAL MATCH (p)-[:HAS_ROLE]->(r:Role)
                OPTIONAL MATCH (p)-[:BELONGS_TO]->(d:Department)
                OPTIONAL MATCH (p)-[:REPORTS_TO]->(manager:Person)
                OPTIONAL MATCH (direct_report:Person)-[:REPORTS_TO]->(p)
                OPTIONAL MATCH (p)-[:COLLABORATES_WITH]->(colleague:Person)
                RETURN p, r, d, manager,
                       collect(DISTINCT direct_report) as direct_reports,
                       collect(DISTINCT colleague) as colleagues
            """,
                id=person_id,
            )

            record = result.single()
            if not record:
                return None

            return {
                "person": dict(record["p"]),
                "role": dict(record["r"]) if record["r"] else None,
                "department": dict(record["d"]) if record["d"] else None,
                "manager": dict(record["manager"]) if record["manager"] else None,
                "direct_reports": [dict(dr) for dr in record["direct_reports"] if dr],
                "colleagues": [dict(c) for c in record["colleagues"] if c],
            }

    def get_organizational_hierarchy(self) -> list[dict[str, Any]]:
        """Get the complete organizational hierarchy"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Person)-[:HAS_ROLE]->(r:Role)-[:IN_DEPARTMENT]->(d:Department)
                OPTIONAL MATCH (p)-[:REPORTS_TO]->(manager:Person)
                RETURN p, r, d, manager
                ORDER BY d.name, r.title, p.name
            """)

            hierarchy = []
            for record in result:
                hierarchy.append(
                    {
                        "person": dict(record["p"]),
                        "role": dict(record["r"]),
                        "department": dict(record["d"]),
                        "manager": dict(record["manager"]) if record["manager"] else None,
                    }
                )

            return hierarchy

    def find_people_by_department(self, department_name: str) -> list[dict[str, Any]]:
        """Find all people in a specific department"""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:Person)-[:BELONGS_TO]->(d:Department {name: $dept_name})
                OPTIONAL MATCH (p)-[:HAS_ROLE]->(r:Role)
                RETURN p, r
                ORDER BY p.name
            """,
                dept_name=department_name,
            )

            people = []
            for record in result:
                people.append(
                    {
                        "person": dict(record["p"]),
                        "role": dict(record["r"]) if record["r"] else None,
                    }
                )

            return people

    def find_collaboration_paths(
        self, from_person_id: str, to_person_id: str, max_hops: int = 3
    ) -> list[list[dict[str, Any]]]:
        """Find collaboration paths between two people"""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH path = shortestPath((from:Person {id: $from_id})-[:REPORTS_TO|:COLLABORATES_WITH|:BELONGS_TO*1..$max_hops]-(to:Person {id: $to_id}))
                RETURN nodes(path) as path_nodes, relationships(path) as path_relationships
                LIMIT 5
            """,
                from_id=from_person_id,
                to_id=to_person_id,
                max_hops=max_hops,
            )

            paths = []
            for record in result:
                path = []
                nodes = record["path_nodes"]
                relationships = record["path_relationships"]

                for i, node in enumerate(nodes):
                    path_node = {
                        "node": dict(node),
                        "relationship": dict(relationships[i]) if i < len(relationships) else None,
                    }
                    path.append(path_node)

                paths.append(path)

            return paths

    def create_collaboration_relationship(
        self, person1_id: str, person2_id: str, project_context: str = None
    ):
        """Create a collaboration relationship between two people"""
        with self.driver.session() as session:
            session.run(
                """
                MATCH (p1:Person {id: $person1_id})
                MATCH (p2:Person {id: $person2_id})
                MERGE (p1)-[c:COLLABORATES_WITH]->(p2)
                SET c.created_at = datetime($created_at),
                    c.project_context = $project_context
                MERGE (p2)-[c2:COLLABORATES_WITH]->(p1)
                SET c2.created_at = datetime($created_at),
                    c2.project_context = $project_context
            """,
                person1_id=person1_id,
                person2_id=person2_id,
                project_context=project_context,
                created_at=datetime.now().isoformat(),
            )

    def get_team_dynamics(self, department_name: str) -> dict[str, Any]:
        """Analyze team dynamics within a department"""
        with self.driver.session() as session:
            # Get collaboration network
            result = session.run(
                """
                MATCH (p1:Person)-[:BELONGS_TO]->(:Department {name: $dept_name})
                MATCH (p2:Person)-[:BELONGS_TO]->(:Department {name: $dept_name})
                WHERE p1 <> p2
                OPTIONAL MATCH (p1)-[c:COLLABORATES_WITH]->(p2)
                RETURN p1.name as person1, p2.name as person2,
                       c.project_context as collaboration_context,
                       c.created_at as collaboration_date
            """,
                dept_name=department_name,
            )

            collaborations = []
            for record in result:
                if record["collaboration_context"]:
                    collaborations.append(
                        {
                            "person1": record["person1"],
                            "person2": record["person2"],
                            "context": record["collaboration_context"],
                            "date": record["collaboration_date"],
                        }
                    )

            # Get department size and roles
            result = session.run(
                """
                MATCH (p:Person)-[:BELONGS_TO]->(:Department {name: $dept_name})
                OPTIONAL MATCH (p)-[:HAS_ROLE]->(r:Role)
                RETURN count(p) as team_size, collect(DISTINCT r.title) as roles
            """,
                dept_name=department_name,
            )

            stats = result.single()

            return {
                "department": department_name,
                "team_size": stats["team_size"],
                "roles": [role for role in stats["roles"] if role],
                "collaborations": collaborations,
                "collaboration_density": len(collaborations)
                / max(1, stats["team_size"] * (stats["team_size"] - 1)),
            }

    def search_people(self, search_term: str) -> list[dict[str, Any]]:
        """Search for people by name, title, or bio"""
        with self.driver.session() as session:
            result = session.run(
                """
                CALL db.index.fulltext.queryNodes('person_search_index', $search_term)
                YIELD node, score
                MATCH (node)-[:HAS_ROLE]->(r:Role)
                MATCH (node)-[:BELONGS_TO]->(d:Department)
                RETURN node, r, d, score
                ORDER BY score DESC
                LIMIT 10
            """,
                search_term=search_term,
            )

            people = []
            for record in result:
                people.append(
                    {
                        "person": dict(record["node"]),
                        "role": dict(record["r"]),
                        "department": dict(record["d"]),
                        "relevance_score": record["score"],
                    }
                )

            return people

    def update_person_status(self, person_id: str, status_update: dict[str, Any]):
        """Update person's current status or context"""
        with self.driver.session() as session:
            session.run(
                """
                MATCH (p:Person {id: $id})
                SET p.current_status = $status,
                    p.status_updated_at = datetime($updated_at),
                    p += $additional_props
            """,
                id=person_id,
                status=status_update.get("status", ""),
                updated_at=datetime.now().isoformat(),
                additional_props=status_update,
            )

    def get_connection_strength(self, person1_id: str, person2_id: str) -> dict[str, Any]:
        """Calculate connection strength between two people"""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p1:Person {id: $person1_id})
                MATCH (p2:Person {id: $person2_id})

                // Direct collaboration
                OPTIONAL MATCH (p1)-[c:COLLABORATES_WITH]->(p2)

                // Shared department
                OPTIONAL MATCH (p1)-[:BELONGS_TO]->(shared_dept:Department)<-[:BELONGS_TO]-(p2)

                // Shared manager
                OPTIONAL MATCH (p1)-[:REPORTS_TO]->(shared_manager:Person)<-[:REPORTS_TO]-(p2)

                // Mutual connections
                OPTIONAL MATCH (p1)-[:COLLABORATES_WITH]->(mutual:Person)<-[:COLLABORATES_WITH]-(p2)

                RETURN
                    c IS NOT NULL as direct_collaboration,
                    shared_dept.name as shared_department,
                    shared_manager.name as shared_manager,
                    count(DISTINCT mutual) as mutual_connections
            """,
                person1_id=person1_id,
                person2_id=person2_id,
            )

            record = result.single()
            if not record:
                return {"strength": 0, "factors": []}

            strength = 0
            factors = []

            if record["direct_collaboration"]:
                strength += 50
                factors.append("Direct collaboration")

            if record["shared_department"]:
                strength += 30
                factors.append(f"Same department: {record['shared_department']}")

            if record["shared_manager"]:
                strength += 20
                factors.append(f"Shared manager: {record['shared_manager']}")

            mutual_count = record["mutual_connections"]
            if mutual_count > 0:
                strength += min(mutual_count * 10, 30)
                factors.append(f"{mutual_count} mutual connections")

            return {
                "strength": min(strength, 100),
                "factors": factors,
                "direct_collaboration": record["direct_collaboration"],
                "shared_department": record["shared_department"],
                "shared_manager": record["shared_manager"],
                "mutual_connections": mutual_count,
            }


# Global Neo4j service instance
neo4j_service = Neo4jService()
