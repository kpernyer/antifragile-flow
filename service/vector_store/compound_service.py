"""Compound vector store service combining Neo4j and Weaviate strategies."""

from dataclasses import dataclass
from enum import Enum
import logging
from typing import Any

from .ports import IHybridVectorStore, IVectorStore

logger = logging.getLogger(__name__)


class SearchStrategy(Enum):
    """Available search strategies for compound store."""

    NEO4J_ONLY = "neo4j_only"
    WEAVIATE_ONLY = "weaviate_only"
    SEMANTIC_FIRST = "semantic_first"  # Weaviate then Neo4j
    GRAPH_FIRST = "graph_first"  # Neo4j then Weaviate
    PARALLEL_FUSION = "parallel_fusion"  # Both in parallel, fuse results
    ADAPTIVE = "adaptive"  # Choose strategy based on query


@dataclass
class SearchResult:
    """Enhanced search result with metadata."""

    id: str
    text: str
    source: str
    score: float
    created_at: str = ""
    store_origin: str = ""  # "neo4j", "weaviate", "fused"
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class CompoundVectorStore(IHybridVectorStore):
    """
    Compound vector store that intelligently routes queries between
    Neo4j (graph relationships) and Weaviate (semantic search) based on configurable strategies.

    Perfect for organizational twin systems where you need both:
    - Fast semantic search (Weaviate)
    - Rich relationship context (Neo4j)
    """

    def __init__(
        self,
        neo4j_store: IVectorStore | None = None,
        weaviate_store: IHybridVectorStore | None = None,
        default_strategy: SearchStrategy = SearchStrategy.PARALLEL_FUSION,
        fusion_weights: dict[str, float] | None = None,
    ):
        self.neo4j_store = neo4j_store
        self.weaviate_store = weaviate_store
        self.default_strategy = default_strategy
        self.fusion_weights = fusion_weights or {"neo4j": 0.6, "weaviate": 0.4}

        # Validate at least one store is provided
        if not neo4j_store and not weaviate_store:
            raise ValueError("At least one vector store must be provided")

        logger.info(f"CompoundVectorStore initialized with strategy: {default_strategy}")

    def search(
        self,
        tenant_id: str,
        query_vector: list[float],
        k: int = 5,
        strategy: SearchStrategy | None = None,
        **kwargs,
    ) -> list[dict[str, Any]]:
        """
        Search using specified strategy.

        Args:
            tenant_id: Tenant identifier
            query_vector: Query vector
            k: Number of results to return
            strategy: Override default search strategy
            **kwargs: Additional parameters (query text for hybrid search, etc.)
        """
        active_strategy = strategy or self.default_strategy

        try:
            if active_strategy == SearchStrategy.NEO4J_ONLY:
                return self._search_neo4j_only(tenant_id, query_vector, k)

            elif active_strategy == SearchStrategy.WEAVIATE_ONLY:
                return self._search_weaviate_only(tenant_id, query_vector, k)

            elif active_strategy == SearchStrategy.SEMANTIC_FIRST:
                return self._search_semantic_first(tenant_id, query_vector, k, **kwargs)

            elif active_strategy == SearchStrategy.GRAPH_FIRST:
                return self._search_graph_first(tenant_id, query_vector, k, **kwargs)

            elif active_strategy == SearchStrategy.PARALLEL_FUSION:
                return self._search_parallel_fusion(tenant_id, query_vector, k, **kwargs)

            elif active_strategy == SearchStrategy.ADAPTIVE:
                return self._search_adaptive(tenant_id, query_vector, k, **kwargs)

            else:
                logger.warning(
                    f"Unknown strategy {active_strategy}, falling back to parallel fusion"
                )
                return self._search_parallel_fusion(tenant_id, query_vector, k, **kwargs)

        except Exception as e:
            logger.error(f"Compound search error: {e}")
            # Fallback to any available store
            return self._fallback_search(tenant_id, query_vector, k)

    def _search_neo4j_only(
        self, tenant_id: str, query_vector: list[float], k: int
    ) -> list[dict[str, Any]]:
        """Search using Neo4j only for graph relationship context."""
        if not self.neo4j_store:
            return []

        results = self.neo4j_store.search(tenant_id, query_vector, k)
        for result in results:
            result["store_origin"] = "neo4j"
        return results

    def _search_weaviate_only(
        self, tenant_id: str, query_vector: list[float], k: int
    ) -> list[dict[str, Any]]:
        """Search using Weaviate only for fast semantic search."""
        if not self.weaviate_store:
            return []

        results = self.weaviate_store.search(tenant_id, query_vector, k)
        for result in results:
            result["store_origin"] = "weaviate"
        return results

    def _search_semantic_first(
        self, tenant_id: str, query_vector: list[float], k: int, **kwargs
    ) -> list[dict[str, Any]]:
        """Search Weaviate first (fast), supplement with Neo4j if needed."""
        results = []

        # First try Weaviate (fast semantic search)
        if self.weaviate_store:
            weaviate_results = self.weaviate_store.search(tenant_id, query_vector, k)
            for result in weaviate_results:
                result["store_origin"] = "weaviate"
            results.extend(weaviate_results)

        # If we don't have enough results, supplement with Neo4j
        if len(results) < k and self.neo4j_store:
            remaining = k - len(results)
            neo4j_results = self.neo4j_store.search(tenant_id, query_vector, remaining)
            for result in neo4j_results:
                result["store_origin"] = "neo4j"
            results.extend(neo4j_results)

        return results[:k]

    def _search_graph_first(
        self, tenant_id: str, query_vector: list[float], k: int, **kwargs
    ) -> list[dict[str, Any]]:
        """Search Neo4j first (graph relationships), supplement with Weaviate if needed."""
        results = []

        # First try Neo4j (graph relationships)
        if self.neo4j_store:
            neo4j_results = self.neo4j_store.search(tenant_id, query_vector, k)
            for result in neo4j_results:
                result["store_origin"] = "neo4j"
            results.extend(neo4j_results)

        # If we don't have enough results, supplement with Weaviate
        if len(results) < k and self.weaviate_store:
            remaining = k - len(results)
            weaviate_results = self.weaviate_store.search(tenant_id, query_vector, remaining)
            for result in weaviate_results:
                result["store_origin"] = "weaviate"
            results.extend(weaviate_results)

        return results[:k]

    def _search_parallel_fusion(
        self, tenant_id: str, query_vector: list[float], k: int, **kwargs
    ) -> list[dict[str, Any]]:
        """Search both stores in parallel and fuse results using reciprocal rank fusion."""
        results = []

        # Get results from both stores
        neo4j_results = []
        weaviate_results = []

        if self.neo4j_store:
            neo4j_results = self.neo4j_store.search(tenant_id, query_vector, k * 2)
            for result in neo4j_results:
                result["store_origin"] = "neo4j"

        if self.weaviate_store:
            weaviate_results = self.weaviate_store.search(tenant_id, query_vector, k * 2)
            for result in weaviate_results:
                result["store_origin"] = "weaviate"

        # Fuse results using reciprocal rank fusion
        fused_results = self._fuse_results(neo4j_results, weaviate_results)

        return fused_results[:k]

    def _search_adaptive(
        self, tenant_id: str, query_vector: list[float], k: int, **kwargs
    ) -> list[dict[str, Any]]:
        """Adaptively choose strategy based on query characteristics."""
        # Simple heuristic: if we have query text, prefer semantic-first
        # Otherwise, use parallel fusion for comprehensive results
        query_text = kwargs.get("query", "")

        if query_text and len(query_text.split()) > 5:
            # Longer queries might benefit from semantic understanding
            logger.debug("Using semantic-first strategy for long query")
            return self._search_semantic_first(tenant_id, query_vector, k, **kwargs)
        else:
            # Short queries or no text - use parallel fusion
            logger.debug("Using parallel fusion strategy")
            return self._search_parallel_fusion(tenant_id, query_vector, k, **kwargs)

    def _fuse_results(
        self, neo4j_results: list[dict], weaviate_results: list[dict]
    ) -> list[dict[str, Any]]:
        """Fuse results from multiple stores using reciprocal rank fusion."""
        # Reciprocal Rank Fusion (RRF) algorithm
        rrf_scores = {}
        k_constant = 60  # RRF constant

        # Score Neo4j results (weighted higher for organizational context)
        for i, result in enumerate(neo4j_results):
            doc_id = result.get("text", "")[:100]  # Use text snippet as key
            rrf_scores[doc_id] = (
                rrf_scores.get(doc_id, 0)
                + (1 / (k_constant + i + 1)) * self.fusion_weights["neo4j"]
            )

        # Score Weaviate results (weighted for semantic relevance)
        for i, result in enumerate(weaviate_results):
            doc_id = result.get("text", "")[:100]
            rrf_scores[doc_id] = (
                rrf_scores.get(doc_id, 0)
                + (1 / (k_constant + i + 1)) * self.fusion_weights["weaviate"]
            )

        # Create lookup for full results
        all_results = {}
        for result in neo4j_results + weaviate_results:
            doc_id = result.get("text", "")[:100]
            if doc_id not in all_results:
                all_results[doc_id] = result
                all_results[doc_id]["store_origin"] = "fused"
                all_results[doc_id]["fusion_score"] = rrf_scores.get(doc_id, 0)

        # Sort by RRF score
        sorted_items = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

        return [all_results[doc_id] for doc_id, _ in sorted_items]

    def _fallback_search(
        self, tenant_id: str, query_vector: list[float], k: int
    ) -> list[dict[str, Any]]:
        """Fallback search when primary strategy fails."""
        if self.neo4j_store:
            try:
                results = self.neo4j_store.search(tenant_id, query_vector, k)
                for result in results:
                    result["store_origin"] = "neo4j_fallback"
                return results
            except Exception:
                pass

        if self.weaviate_store:
            try:
                results = self.weaviate_store.search(tenant_id, query_vector, k)
                for result in results:
                    result["store_origin"] = "weaviate_fallback"
                return results
            except Exception:
                pass

        return []

    def upsert_chunks(
        self, tenant_id: str, title: str, chunks: list[str], embeddings: list[list[float]]
    ) -> str:
        """Upsert chunks to all available stores."""
        source_id = ""

        # Insert to Neo4j if available (for relationship context)
        if self.neo4j_store:
            try:
                source_id = self.neo4j_store.upsert_chunks(tenant_id, title, chunks, embeddings)
                logger.info(f"Inserted to Neo4j: {source_id}")
            except Exception as e:
                logger.error(f"Neo4j upsert failed: {e}")

        # Insert to Weaviate if available (for fast semantic search)
        if self.weaviate_store:
            try:
                weaviate_id = self.weaviate_store.upsert_chunks(
                    tenant_id, title, chunks, embeddings
                )
                if not source_id:  # Use Weaviate ID if Neo4j failed
                    source_id = weaviate_id
                logger.info(f"Inserted to Weaviate: {weaviate_id}")
            except Exception as e:
                logger.error(f"Weaviate upsert failed: {e}")

        return source_id

    def get_recent_sources(self, tenant_id: str, limit: int = 20) -> list[dict[str, Any]]:
        """Get recent sources from primary store (Neo4j preferred for relationship context)."""
        if self.neo4j_store:
            try:
                return self.neo4j_store.get_recent_sources(tenant_id, limit)
            except Exception as e:
                logger.error(f"Neo4j get_recent_sources failed: {e}")

        if self.weaviate_store:
            try:
                return self.weaviate_store.get_recent_sources(tenant_id, limit)
            except Exception as e:
                logger.error(f"Weaviate get_recent_sources failed: {e}")

        return []

    def hybrid_search(
        self,
        tenant_id: str,
        query: str,
        query_vector: list[float],
        k: int = 5,
        alpha: float = 0.7,
        strategy: SearchStrategy | None = None,
    ) -> list[dict[str, Any]]:
        """
        Perform hybrid search with text + vector queries.

        Args:
            tenant_id: Tenant identifier
            query: Text query
            query_vector: Query vector
            k: Number of results
            alpha: Vector vs keyword weight
            strategy: Search strategy override
        """
        # Try Weaviate hybrid search first (if available)
        if self.weaviate_store and hasattr(self.weaviate_store, "hybrid_search"):
            try:
                results = self.weaviate_store.hybrid_search(
                    tenant_id, query, query_vector, k, alpha
                )
                for result in results:
                    result["store_origin"] = "weaviate_hybrid"

                # If we get good results, return them
                if results:
                    return results
            except Exception as e:
                logger.warning(f"Weaviate hybrid search failed: {e}")

        # Fallback to compound search with query text as additional parameter
        return self.search(
            tenant_id=tenant_id,
            query_vector=query_vector,
            k=k,
            strategy=strategy,
            query=query,
            alpha=alpha,
        )


class CompoundStoreConfig:
    """Configuration for compound vector store."""

    def __init__(
        self,
        enable_neo4j: bool = True,
        enable_weaviate: bool = True,
        default_strategy: SearchStrategy = SearchStrategy.PARALLEL_FUSION,
        fusion_weights: dict[str, float] | None = None,
    ):
        self.enable_neo4j = enable_neo4j
        self.enable_weaviate = enable_weaviate
        self.default_strategy = default_strategy
        self.fusion_weights = fusion_weights or {"neo4j": 0.6, "weaviate": 0.4}
