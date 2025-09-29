"""
GraphQL server configuration for Knowledge Base.

Provides comprehensive configuration for GraphQL server setup,
including schema management, middleware, and performance settings.
"""

from dataclasses import dataclass, field
import os
from typing import Any

from .defaults import HOSTS, PORTS


@dataclass
class GraphQLServerConfig:
    """
    Comprehensive GraphQL server configuration.

    Optimized for Knowledge Base server with schema introspection,
    playground, subscriptions, and performance settings.
    """

    # Server settings
    host: str = HOSTS.LOCAL
    port: int = PORTS.GRAPHQL_SERVER
    debug: bool = True

    # GraphQL features
    enable_playground: bool = True
    enable_introspection: bool = True
    enable_subscriptions: bool = True
    enable_uploads: bool = True  # For file uploads in Knowledge Base

    # Performance and security
    max_query_depth: int = 15  # Prevent deep query attacks
    max_query_complexity: int = 1000  # Query complexity limit
    query_cache_size: int = 100  # Cache frequently used queries
    enable_query_caching: bool = True
    enable_tracing: bool = True  # Apollo tracing

    # CORS settings
    cors_origins: list[str] = field(
        default_factory=lambda: [
            "http://localhost:3000",  # React frontend
            "http://localhost:8080",  # API server
            "http://localhost:4000",  # GraphQL playground
        ]
    )
    cors_credentials: bool = True

    # WebSocket settings (for subscriptions)
    websocket_path: str = "/graphql"
    websocket_origins: list[str] = field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:4000",
        ]
    )

    # Schema and middleware
    schema_file: str = "knowledge_base_schema.graphql"
    enable_federation: bool = False  # Apollo Federation support

    # Rate limiting
    enable_rate_limiting: bool = True
    rate_limit_max: int = 1000  # Requests per window
    rate_limit_window: int = 900  # 15 minutes in seconds

    # Logging and monitoring
    log_level: str = "INFO"
    enable_metrics: bool = True
    metrics_path: str = "/metrics"

    @classmethod
    def from_environment(cls, env: str = "local") -> "GraphQLServerConfig":
        """Create configuration based on environment."""
        if env == "local":
            return cls._local_config()
        elif env == "development":
            return cls._development_config()
        elif env == "production":
            return cls._production_config()
        else:
            return cls()

    @classmethod
    def _local_config(cls) -> "GraphQLServerConfig":
        """Configuration for local development."""
        return cls(
            host=os.getenv("GRAPHQL_HOST", HOSTS.LOCAL),
            port=int(os.getenv("GRAPHQL_PORT", PORTS.GRAPHQL_SERVER)),
            debug=True,
            enable_playground=True,
            enable_introspection=True,
            max_query_depth=50,  # More lenient for development
            enable_rate_limiting=False,  # Disabled for local dev
            log_level="DEBUG",
        )

    @classmethod
    def _development_config(cls) -> "GraphQLServerConfig":
        """Configuration for development environment."""
        return cls(
            host=os.getenv("GRAPHQL_HOST", "0.0.0.0"),
            port=int(os.getenv("GRAPHQL_PORT", PORTS.GRAPHQL_SERVER)),
            debug=True,
            enable_playground=True,
            enable_introspection=True,
            cors_origins=os.getenv("GRAPHQL_CORS_ORIGINS", "").split(",") or cls().cors_origins,
            enable_rate_limiting=True,
            rate_limit_max=5000,  # Higher limit for development
            log_level="DEBUG",
        )

    @classmethod
    def _production_config(cls) -> "GraphQLServerConfig":
        """Configuration for production environment."""
        return cls(
            host=os.getenv("GRAPHQL_HOST", "0.0.0.0"),
            port=int(os.getenv("GRAPHQL_PORT", PORTS.GRAPHQL_SERVER)),
            debug=False,
            enable_playground=False,  # Disabled in production
            enable_introspection=False,  # Disabled in production
            max_query_depth=10,  # Stricter limits
            max_query_complexity=500,
            cors_origins=os.getenv("GRAPHQL_CORS_ORIGINS", "").split(",") or [],
            enable_rate_limiting=True,
            rate_limit_max=1000,
            log_level="INFO",
            enable_tracing=False,  # Disable for performance
        )

    def get_server_url(self) -> str:
        """Get the full server URL."""
        return f"http://{self.host}:{self.port}"

    def get_graphql_endpoint(self) -> str:
        """Get the GraphQL endpoint URL."""
        return f"{self.get_server_url()}/graphql"

    def get_playground_url(self) -> str:
        """Get the GraphQL Playground URL."""
        return f"{self.get_server_url()}/playground"

    def get_subscriptions_url(self) -> str:
        """Get the WebSocket subscriptions URL."""
        return f"ws://{self.host}:{self.port}{self.websocket_path}"

    def validate(self) -> None:
        """Validate the configuration."""
        if self.port < 1 or self.port > 65535:
            raise ValueError(f"Invalid port number: {self.port}")

        if self.max_query_depth <= 0:
            raise ValueError("max_query_depth must be positive")

        if self.max_query_complexity <= 0:
            raise ValueError("max_query_complexity must be positive")

        if self.enable_rate_limiting and self.rate_limit_max <= 0:
            raise ValueError("rate_limit_max must be positive when rate limiting is enabled")


@dataclass
class KnowledgeBaseConfig:
    """
    Knowledge Base specific GraphQL configuration.

    Defines schema, resolvers, and business logic configuration
    for the Knowledge Base GraphQL server.
    """

    # Schema configuration
    enable_auto_schema_generation: bool = True
    schema_output_path: str = "knowledge_base/schema.graphql"

    # Knowledge Base features
    enable_full_text_search: bool = True
    enable_semantic_search: bool = True
    enable_document_indexing: bool = True
    enable_real_time_updates: bool = True

    # Search configuration
    search_results_limit: int = 50
    semantic_search_threshold: float = 0.7
    full_text_search_boost: float = 1.2

    # Document processing
    max_document_size: int = 10 * 1024 * 1024  # 10MB
    supported_file_types: list[str] = field(
        default_factory=lambda: ["pdf", "docx", "txt", "md", "html", "csv", "json"]
    )

    # Real-time features
    enable_live_queries: bool = True
    subscription_timeout: int = 3600  # 1 hour

    # Integration settings
    temporal_integration: bool = True  # Integrate with Temporal workflows
    database_backend: str = "postgresql"  # postgresql, mongodb, neo4j
    vector_database: str = "pinecone"  # pinecone, weaviate, qdrant

    def get_search_config(self) -> dict[str, Any]:
        """Get search configuration for resolvers."""
        return {
            "full_text_enabled": self.enable_full_text_search,
            "semantic_enabled": self.enable_semantic_search,
            "results_limit": self.search_results_limit,
            "semantic_threshold": self.semantic_search_threshold,
            "full_text_boost": self.full_text_search_boost,
        }

    def get_document_config(self) -> dict[str, Any]:
        """Get document processing configuration."""
        return {
            "max_size": self.max_document_size,
            "supported_types": self.supported_file_types,
            "indexing_enabled": self.enable_document_indexing,
        }


def get_graphql_server_config(env: str = None) -> GraphQLServerConfig:
    """Get GraphQL server configuration for the specified environment."""
    env = env or os.getenv("ENVIRONMENT", "local")
    return GraphQLServerConfig.from_environment(env)


def get_knowledge_base_config() -> KnowledgeBaseConfig:
    """Get Knowledge Base configuration with environment overrides."""
    return KnowledgeBaseConfig(
        enable_full_text_search=os.getenv("KB_FULL_TEXT_SEARCH", "true").lower() == "true",
        enable_semantic_search=os.getenv("KB_SEMANTIC_SEARCH", "true").lower() == "true",
        search_results_limit=int(os.getenv("KB_SEARCH_LIMIT", "50")),
        semantic_search_threshold=float(os.getenv("KB_SEMANTIC_THRESHOLD", "0.7")),
        database_backend=os.getenv("KB_DATABASE_BACKEND", "postgresql"),
        vector_database=os.getenv("KB_VECTOR_DATABASE", "pinecone"),
    )


# Default instances for easy import
DEFAULT_GRAPHQL_CONFIG = get_graphql_server_config()
DEFAULT_KB_CONFIG = get_knowledge_base_config()
