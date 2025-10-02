"""
Centralized default values for the Antifragile Flow application.

This module provides all default ports, URLs, and configuration values
used across both Python and TypeScript/frontend components.

These values should be consistent across all language implementations
and can be overridden via environment variables.
"""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class DefaultPorts:
    """Standard port assignments for all services."""

    # Temporal
    TEMPORAL_SERVER = 7233
    TEMPORAL_UI = 8233

    # Web services
    FRONTEND = 3000
    API_SERVER = 8080
    GRAPHQL_SERVER = 4000  # Knowledge Base GraphQL server

    # Databases
    POSTGRES = 5432
    REDIS = 6379
    MONGODB = 27017

    # Development services
    DEV_PROXY = 9000
    METRICS = 9464


@dataclass(frozen=True)
class DefaultHosts:
    """Standard hostnames for all services."""

    LOCAL = "localhost"
    TEMPORAL_CLOUD_SUFFIX = ".tmprl.cloud"
    PRODUCTION_CLUSTER = "temporal.production.svc.cluster.local"


@dataclass(frozen=True)
class DefaultURLs:
    """Standard URL patterns."""

    # Local development
    FRONTEND_LOCAL = f"http://{DefaultHosts.LOCAL}:{DefaultPorts.FRONTEND}"
    API_LOCAL = f"http://{DefaultHosts.LOCAL}:{DefaultPorts.API_SERVER}"
    GRAPHQL_LOCAL = f"http://{DefaultHosts.LOCAL}:{DefaultPorts.GRAPHQL_SERVER}"
    TEMPORAL_LOCAL = f"{DefaultHosts.LOCAL}:{DefaultPorts.TEMPORAL_SERVER}"
    TEMPORAL_UI_LOCAL = f"http://{DefaultHosts.LOCAL}:{DefaultPorts.TEMPORAL_UI}"

    # Knowledge Base GraphQL endpoints
    GRAPHQL_ENDPOINT = f"http://{DefaultHosts.LOCAL}:{DefaultPorts.GRAPHQL_SERVER}/graphql"
    GRAPHQL_PLAYGROUND = f"http://{DefaultHosts.LOCAL}:{DefaultPorts.GRAPHQL_SERVER}/playground"
    GRAPHQL_SUBSCRIPTIONS = f"ws://{DefaultHosts.LOCAL}:{DefaultPorts.GRAPHQL_SERVER}/graphql"

    # Database connection strings (without credentials)
    POSTGRES_LOCAL = f"postgresql://{DefaultHosts.LOCAL}:{DefaultPorts.POSTGRES}"
    REDIS_LOCAL = f"redis://{DefaultHosts.LOCAL}:{DefaultPorts.REDIS}"
    MONGODB_LOCAL = f"mongodb://{DefaultHosts.LOCAL}:{DefaultPorts.MONGODB}"


@dataclass(frozen=True)
class DefaultCredentials:
    """Default development credentials (never use in production)."""

    # Database defaults for local development
    POSTGRES_USER = "postgres"
    POSTGRES_PASSWORD = "postgres"
    POSTGRES_DB = "antifragile_flow"

    REDIS_PASSWORD = ""  # No password for local development

    # API keys (to be overridden via environment)
    OPENAI_API_KEY = ""  # Must be set via environment

    # Application secrets
    JWT_SECRET = "development-secret-change-in-production"
    SESSION_SECRET = "development-session-secret-change-in-production"


@dataclass(frozen=True)
class TaskQueues:
    """Temporal task queue names."""

    # Three-worker architecture
    DEFAULT = "default-queue"  # General activities
    ML = "ml-queue"  # ML training and model activities
    OPENAI = "openai-queue"  # OpenAI API calls and AI agents

    # Legacy simplified queue name
    HACKATHON = "hackathon"

    # Future organized queues
    ONBOARDING = "onboarding-queue"
    DOCUMENT_PROCESSING = "document-processing-queue"
    RESEARCH = "research-queue"
    CONSENSUS = "consensus-queue"
    DAILY_INTERACTION = "daily-interaction-queue"
    KNOWLEDGE_BUILDING = "knowledge-building-queue"


def get_temporal_address() -> str:
    """Get Temporal server address with environment override."""
    return os.environ.get("TEMPORAL_ADDRESS", DefaultURLs.TEMPORAL_LOCAL)


def get_temporal_ui_url(workflow_id: str, namespace: str = "default") -> str:
    """Generate Temporal UI monitoring URL for a workflow."""
    base_url = os.environ.get("TEMPORAL_UI_ADDRESS", DefaultURLs.TEMPORAL_UI_LOCAL)
    return f"{base_url}/namespaces/{namespace}/workflows/{workflow_id}"


def get_frontend_url() -> str:
    """Get frontend URL with environment override."""
    return os.environ.get("FRONTEND_URL", DefaultURLs.FRONTEND_LOCAL)


def get_api_url() -> str:
    """Get API server URL with environment override."""
    return os.environ.get("API_URL", DefaultURLs.API_LOCAL)


def get_graphql_url() -> str:
    """Get GraphQL server URL with environment override."""
    return os.environ.get("GRAPHQL_URL", DefaultURLs.GRAPHQL_LOCAL)


def get_graphql_endpoint() -> str:
    """Get GraphQL endpoint URL with environment override."""
    return os.environ.get("GRAPHQL_ENDPOINT", DefaultURLs.GRAPHQL_ENDPOINT)


def get_graphql_playground_url() -> str:
    """Get GraphQL Playground URL with environment override."""
    return os.environ.get("GRAPHQL_PLAYGROUND", DefaultURLs.GRAPHQL_PLAYGROUND)


def get_graphql_subscriptions_url() -> str:
    """Get GraphQL subscriptions WebSocket URL with environment override."""
    return os.environ.get("GRAPHQL_SUBSCRIPTIONS", DefaultURLs.GRAPHQL_SUBSCRIPTIONS)


# Export for easy access
PORTS = DefaultPorts()
HOSTS = DefaultHosts()
URLS = DefaultURLs()
CREDENTIALS = DefaultCredentials()
QUEUES = TaskQueues()

# Backward compatibility - maintain current TASK_QUEUE_NAME
TASK_QUEUE_NAME = QUEUES.DEFAULT

# Export individual queue names for easy access
DEFAULT_QUEUE = QUEUES.DEFAULT
ML_QUEUE = QUEUES.ML
OPENAI_QUEUE = QUEUES.OPENAI
