"""Weaviate vector store service for semantic search and hybrid retrieval."""

from datetime import datetime
import logging
from typing import Any
import uuid

try:
    import weaviate
    from weaviate.classes.config import Configure, DataType, Property, VectorDistances
    from weaviate.classes.query import Filter, MetadataQuery

    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False
    weaviate = None

from .ports import IHybridVectorStore

logger = logging.getLogger(__name__)


class WeaviateStore(IHybridVectorStore):
    """
    Weaviate implementation of vector store.
    Provides fast semantic search with HNSW indexing and hybrid search capabilities.
    """

    def __init__(self, config):
        if not WEAVIATE_AVAILABLE:
            raise ImportError(
                "Weaviate is not installed. Install with: pip install weaviate-client"
            )

        self.url = config.url
        self.api_key = getattr(config, "api_key", None)
        self.collection_name = getattr(config, "collection_name", "AntifragileDoc")
        self.embedding_dimensions = config.embedding_dimensions

        # Connect to Weaviate
        if self.api_key:
            self.client = weaviate.connect_to_wcs(
                cluster_url=self.url, auth_credentials=weaviate.auth.AuthApiKey(self.api_key)
            )
        else:
            # Local connection - extract host and port properly
            import re

            # Extract host and port from URL like http://localhost:8081
            url_match = re.match(r"https?://([^:]+):?(\d+)?", self.url)
            if url_match:
                host = url_match.group(1)
                port = int(url_match.group(2)) if url_match.group(2) else 8080
                self.client = weaviate.connect_to_local(host=host, port=port)
            else:
                # Fallback to simple parsing
                host = self.url.replace("http://", "").replace("https://", "").split(":")[0]
                self.client = weaviate.connect_to_local(host=host)

        logger.info(f"Connected to Weaviate at {self.url}")
        self._ensure_schema()

    def _ensure_schema(self):
        """Ensure the collection schema exists."""
        try:
            # Check if collection exists
            if not self.client.collections.exists(self.collection_name):
                logger.info(f"Creating Weaviate collection: {self.collection_name}")

                # Create collection with vector configuration
                collection = self.client.collections.create(
                    name=self.collection_name,
                    properties=[
                        Property(name="text", data_type=DataType.TEXT),
                        Property(name="source", data_type=DataType.TEXT),
                        Property(name="tenantId", data_type=DataType.TEXT),
                        Property(name="createdAt", data_type=DataType.TEXT),
                        Property(
                            name="chunkIndex", data_type=DataType.INT, skip_vectorization=True
                        ),
                        Property(name="documentType", data_type=DataType.TEXT),
                        Property(name="metadata", data_type=DataType.TEXT),
                    ],
                    vectorizer_config=Configure.Vectorizer.none(),  # Use custom embeddings
                    vector_index_config=Configure.VectorIndex.hnsw(
                        distance_metric=VectorDistances.COSINE,
                        ef_construction=128,
                        ef=64,
                        max_connections=16,
                        dynamic_ef_min=100,
                        dynamic_ef_max=500,
                        dynamic_ef_factor=4,
                    ),
                )
                logger.info(f"Created collection {self.collection_name}")
        except Exception as e:
            logger.warning(f"Error ensuring schema: {e}")

    def search(self, tenant_id: str, query_vector: list[float], k: int = 5) -> list[dict[str, Any]]:
        """Search for similar vectors in Weaviate."""
        try:
            collection = self.client.collections.get(self.collection_name)

            # Perform vector search (tenant filtering disabled for demo)
            # TODO: Re-enable tenant filtering for multi-tenant production
            response = collection.query.near_vector(near_vector=query_vector, limit=k)

            results = []
            for obj in response.objects:
                results.append(
                    {
                        "id": str(obj.uuid),
                        "text": obj.properties.get("text", ""),
                        "source": obj.properties.get("source", ""),
                        "score": getattr(obj.metadata, "distance", 0.0) if obj.metadata else 0.0,
                        "created_at": obj.properties.get("createdAt", ""),
                        "document_type": obj.properties.get("documentType", ""),
                        "chunk_index": obj.properties.get("chunkIndex", 0),
                    }
                )

            return results

        except Exception as e:
            logger.error(f"Weaviate search error: {e}")
            return []

    def upsert_chunks(
        self, tenant_id: str, title: str, chunks: list[str], embeddings: list[list[float]]
    ) -> str:
        """Insert document chunks with embeddings into Weaviate."""
        try:
            collection = self.client.collections.get(self.collection_name)
            source_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat() + "Z"

            # Batch insert chunks using proper DataObject format
            from weaviate.classes.data import DataObject

            objects = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings, strict=False)):
                obj = DataObject(
                    properties={
                        "text": chunk,
                        "source": title,
                        "tenantId": tenant_id,
                        "createdAt": now,
                        "chunkIndex": i,
                        "documentType": "organizational_document",
                        "metadata": f'{{"source_id": "{source_id}", "total_chunks": {len(chunks)}}}',
                    },
                    vector=embedding,
                )
                objects.append(obj)

            # Insert batch
            collection.data.insert_many(objects)
            logger.info(f"Inserted {len(chunks)} chunks for source {title}")

            return source_id

        except Exception as e:
            logger.error(f"Weaviate upsert error: {e}")
            return ""

    def get_recent_sources(self, tenant_id: str, limit: int = 20) -> list[dict[str, Any]]:
        """Get recently ingested sources for a tenant."""
        try:
            collection = self.client.collections.get(self.collection_name)

            # Query for recent sources
            response = collection.query.fetch_objects(
                where=Filter.by_property("tenantId").equal(tenant_id),
                limit=limit * 10,  # Get more to group by source
            )

            # Group by source and get recent ones
            sources_map = {}
            for obj in response.objects:
                source = obj.properties.get("source", "Unknown")
                created_at = obj.properties.get("createdAt", "")

                if source not in sources_map:
                    sources_map[source] = {
                        "title": source,
                        "created_at": created_at,
                        "chunk_count": 1,
                        "type": "document",
                        "document_type": obj.properties.get("documentType", ""),
                    }
                else:
                    sources_map[source]["chunk_count"] += 1

            # Convert to list and sort by creation time
            sources = list(sources_map.values())
            sources.sort(key=lambda x: x["created_at"], reverse=True)

            return sources[:limit]

        except Exception as e:
            logger.error(f"Weaviate get_recent_sources error: {e}")
            return []

    def hybrid_search(
        self, tenant_id: str, query: str, query_vector: list[float], k: int = 5, alpha: float = 0.7
    ) -> list[dict[str, Any]]:
        """
        Perform hybrid search combining vector similarity and keyword matching.

        Args:
            tenant_id: Tenant identifier
            query: Text query for keyword search
            query_vector: Vector for semantic search
            k: Number of results to return
            alpha: Weight for vector vs keyword search (0.0 = keyword only, 1.0 = vector only)
        """
        try:
            collection = self.client.collections.get(self.collection_name)

            # Perform hybrid search (tenant filtering disabled for demo)
            # TODO: Re-enable tenant filtering for multi-tenant production
            response = collection.query.hybrid(
                query=query, vector=query_vector, alpha=alpha, limit=k
            )

            results = []
            for obj in response.objects:
                results.append(
                    {
                        "id": str(obj.uuid),
                        "text": obj.properties.get("text", ""),
                        "source": obj.properties.get("source", ""),
                        "score": getattr(obj.metadata, "score", 0.0) if obj.metadata else 0.0,
                        "created_at": obj.properties.get("createdAt", ""),
                        "document_type": obj.properties.get("documentType", ""),
                        "chunk_index": obj.properties.get("chunkIndex", 0),
                    }
                )

            return results

        except Exception as e:
            logger.error(f"Weaviate hybrid search error: {e}")
            # Fallback to vector search
            return self.search(tenant_id, query_vector, k)

    def close(self):
        """Close the Weaviate connection."""
        if hasattr(self, "client"):
            self.client.close()


class WeaviateConfig:
    """Configuration for Weaviate store."""

    def __init__(
        self,
        url: str = "http://localhost:8080",
        api_key: str | None = None,
        collection_name: str = "AntifragileDoc",
        embedding_dimensions: int = 1536,
    ):
        self.url = url
        self.api_key = api_key
        self.collection_name = collection_name
        self.embedding_dimensions = embedding_dimensions
