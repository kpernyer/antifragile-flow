"""Neo4j vector store service for graph-based document retrieval with relationships."""

from datetime import datetime
import logging
from typing import Any
import uuid

try:
    from neo4j import GraphDatabase

    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    GraphDatabase = None

from .ports import IVectorStore

logger = logging.getLogger(__name__)


class Neo4jStore(IVectorStore):
    """
    Neo4j implementation of vector store with graph relationship capabilities.
    Provides semantic search with organizational relationship context.
    """

    def __init__(self, config):
        if not NEO4J_AVAILABLE:
            raise ImportError("Neo4j driver is not installed. Install with: pip install neo4j")

        self.driver = GraphDatabase.driver(config.uri, auth=(config.user, config.password))
        self.database = config.database
        self.vector_index = config.vector_index
        self.node_label = getattr(config, "node_label", "Document")
        self.embedding_property = getattr(config, "embedding_property", "embedding")

        logger.info(f"Connected to Neo4j at {config.uri}")
        self._ensure_constraints_and_indexes()

    def _ensure_constraints_and_indexes(self):
        """Ensure necessary constraints and indexes exist."""
        try:
            with self.driver.session(database=self.database) as session:
                # Create unique constraints
                session.run(
                    f"CREATE CONSTRAINT IF NOT EXISTS FOR (d:{self.node_label}) REQUIRE d.id IS UNIQUE"
                )
                session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (s:Source) REQUIRE s.id IS UNIQUE")

                # Create indexes for better performance
                session.run(f"CREATE INDEX IF NOT EXISTS FOR (d:{self.node_label}) ON (d.tenantId)")
                session.run(f"CREATE INDEX IF NOT EXISTS FOR (d:{self.node_label}) ON (d.source)")
                session.run("CREATE INDEX IF NOT EXISTS FOR (s:Source) ON (s.tenantId)")

                logger.info("Neo4j constraints and indexes ensured")
        except Exception as e:
            logger.warning(f"Error ensuring constraints/indexes: {e}")

    def search(self, tenant_id: str, query_vector: list[float], k: int = 5) -> list[dict[str, Any]]:
        """Search for similar vectors using Neo4j vector index."""
        query = """
        CALL db.index.vector.queryNodes($index, $k, $vec) YIELD node, score
        WHERE coalesce(node.tenantId, 'demo') = $tenant
        RETURN node as n, score
        ORDER BY score DESC
        """

        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(
                    query, index=self.vector_index, k=k, vec=query_vector, tenant=tenant_id
                )

                results = []
                for record in result:
                    node = record["n"]
                    results.append(
                        {
                            "id": node.element_id,
                            "text": node.get("text", ""),
                            "source": node.get("source", ""),
                            "score": record["score"],
                            "created_at": node.get("createdAt", ""),
                            "chunk_index": node.get("chunkIndex", 0),
                            "tenant_id": node.get("tenantId", ""),
                        }
                    )

                return results

        except Exception as e:
            logger.error(f"Neo4j search error: {e}")
            return []

    def upsert_chunks(
        self, tenant_id: str, title: str, chunks: list[str], embeddings: list[list[float]]
    ) -> str:
        """Insert document chunks with embeddings into Neo4j graph."""
        source_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat() + "Z"

        def _transaction(tx):
            # Create or update source node
            tx.run(
                """
                MERGE (s:Source {id: $sid})
                SET s.title = $title,
                    s.tenantId = $tenantId,
                    s.createdAt = $now,
                    s.chunkCount = $chunkCount
            """,
                sid=source_id,
                title=title,
                tenantId=tenant_id,
                now=now,
                chunkCount=len(chunks),
            )

            # Create document chunks with relationships
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings, strict=False)):
                chunk_id = str(uuid.uuid4())
                tx.run(
                    f"""
                    MERGE (d:{self.node_label} {{id: $id}})
                    SET d.text = $text,
                        d.source = $title,
                        d.{self.embedding_property} = $emb,
                        d.tenantId = $tenantId,
                        d.createdAt = $now,
                        d.chunkIndex = $chunkIndex
                    WITH d
                    MATCH (s:Source {{id: $sid}})
                    MERGE (s)-[:HAS_CHUNK]->(d)
                """,
                    id=chunk_id,
                    text=chunk,
                    emb=embedding,
                    tenantId=tenant_id,
                    now=now,
                    title=title,
                    sid=source_id,
                    chunkIndex=i,
                )

        try:
            with self.driver.session(database=self.database) as session:
                session.execute_write(_transaction)
            logger.info(f"Inserted {len(chunks)} chunks for source {title}")
            return source_id

        except Exception as e:
            logger.error(f"Neo4j upsert error: {e}")
            return ""

    def ensure_vector_index(
        self,
        dimensions: int = 1536,
        similarity: str = "cosine",
    ) -> None:
        """Ensure the vector index exists with the expected dimensions and similarity function."""
        try:
            cypher = f"""
            CREATE VECTOR INDEX {self.vector_index} IF NOT EXISTS
            FOR (n:{self.node_label}) ON (n.{self.embedding_property})
            OPTIONS {{
                indexConfig: {{
                    `vector.dimensions`: {dimensions},
                    `vector.similarity_function`: '{similarity}'
                }}
            }}
            """

            with self.driver.session(database=self.database) as session:
                session.run(cypher)
            logger.info(f"Vector index {self.vector_index} ensured")

        except Exception as e:
            logger.error(f"Error ensuring vector index: {e}")

    def get_recent_sources(self, tenant_id: str, limit: int = 20) -> list[dict[str, Any]]:
        """Get recently ingested sources for a tenant."""
        query = """
        MATCH (s:Source)
        WHERE coalesce(s.tenantId, 'demo') = $tenant
        OPTIONAL MATCH (s)-[:HAS_CHUNK]->(d:Document)
        WITH s, count(d) as chunk_count
        RETURN s.id as id, s.title as title, s.createdAt as created_at,
               chunk_count, 'document' as type
        ORDER BY s.createdAt DESC
        LIMIT $limit
        """

        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, tenant=tenant_id, limit=limit)
                sources = []
                for record in result:
                    sources.append(
                        {
                            "id": record["id"],
                            "title": record["title"],
                            "created_at": record["created_at"],
                            "chunk_count": record["chunk_count"],
                            "type": record["type"],
                        }
                    )
                return sources

        except Exception as e:
            logger.error(f"Neo4j get_recent_sources error: {e}")
            return []

    def get_document_relationships(self, tenant_id: str, document_id: str) -> list[dict[str, Any]]:
        """Get relationships for a specific document (Neo4j specific functionality)."""
        query = """
        MATCH (d:Document {id: $doc_id, tenantId: $tenant})
        OPTIONAL MATCH (d)-[r]-(related)
        RETURN type(r) as relationship_type,
               labels(related) as related_labels,
               related.id as related_id,
               related.title as related_title
        """

        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, doc_id=document_id, tenant=tenant_id)
                relationships = []
                for record in result:
                    if record["relationship_type"]:
                        relationships.append(
                            {
                                "type": record["relationship_type"],
                                "related_labels": record["related_labels"],
                                "related_id": record["related_id"],
                                "related_title": record["related_title"],
                            }
                        )
                return relationships

        except Exception as e:
            logger.error(f"Neo4j get_document_relationships error: {e}")
            return []

    def create_organizational_relationships(
        self, tenant_id: str, document_id: str, organization_data: dict[str, Any]
    ) -> bool:
        """Create organizational relationships for document context (Neo4j specific)."""
        query = """
        MATCH (d:Document {id: $doc_id, tenantId: $tenant})
        MERGE (org:Organization {name: $org_name, tenantId: $tenant})
        SET org.type = $org_type,
            org.industry = $industry,
            org.size = $size
        MERGE (d)-[:BELONGS_TO]->(org)
        """

        try:
            with self.driver.session(database=self.database) as session:
                session.run(
                    query,
                    doc_id=document_id,
                    tenant=tenant_id,
                    org_name=organization_data.get("name", "Unknown"),
                    org_type=organization_data.get("type", ""),
                    industry=organization_data.get("industry", ""),
                    size=organization_data.get("size", 0),
                )
            logger.info(f"Created organizational relationships for document {document_id}")
            return True

        except Exception as e:
            logger.error(f"Error creating organizational relationships: {e}")
            return False

    def close(self):
        """Close the Neo4j connection."""
        if hasattr(self, "driver"):
            self.driver.close()


class Neo4jConfig:
    """Configuration for Neo4j store."""

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "password",
        database: str = "neo4j",
        vector_index: str = "document_embeddings",
        node_label: str = "Document",
        embedding_property: str = "embedding",
    ):
        self.uri = uri
        self.user = user
        self.password = password
        self.database = database
        self.vector_index = vector_index
        self.node_label = node_label
        self.embedding_property = embedding_property
