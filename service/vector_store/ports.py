"""Vector store port interfaces for pluggable vector database implementations."""

from abc import ABC, abstractmethod
from typing import Any


class IVectorStore(ABC):
    """
    Abstract interface for vector storage and retrieval systems.

    Supports both Neo4j graph-based vector search and Weaviate
    semantic vector search implementations.
    """

    @abstractmethod
    def search(self, tenant_id: str, query_vector: list[float], k: int = 5) -> list[dict[str, Any]]:
        """
        Search for similar vectors.

        Args:
            tenant_id: Tenant identifier for multi-tenancy
            query_vector: Query vector for similarity search
            k: Number of results to return

        Returns:
            List of search results with metadata
        """
        pass

    @abstractmethod
    def upsert_chunks(
        self, tenant_id: str, title: str, chunks: list[str], embeddings: list[list[float]]
    ) -> str:
        """
        Insert or update document chunks with embeddings.

        Args:
            tenant_id: Tenant identifier
            title: Document title/source
            chunks: Text chunks to store
            embeddings: Corresponding embedding vectors

        Returns:
            Source identifier for the inserted document
        """
        pass

    @abstractmethod
    def get_recent_sources(self, tenant_id: str, limit: int = 20) -> list[dict[str, Any]]:
        """
        Get recently ingested sources for a tenant.

        Args:
            tenant_id: Tenant identifier
            limit: Maximum number of sources to return

        Returns:
            List of recent sources with metadata
        """
        pass


class IHybridVectorStore(IVectorStore):
    """
    Extended interface for hybrid search combining vector and keyword search.
    """

    @abstractmethod
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

        Returns:
            List of hybrid search results
        """
        pass
