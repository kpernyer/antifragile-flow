"""
Main application settings with environment-based configuration.

Provides centralized settings management with validation, type safety,
and environment-specific overrides for the entire system.
"""

from dataclasses import dataclass, field
from functools import lru_cache
import os
from pathlib import Path

from ..temporal_client.config import TemporalConfig
from .ai_config import AIConfig
from .database_config import DatabaseConfig


@dataclass
class Settings:
    """
    Comprehensive application settings.

    Provides environment-based configuration for all system components
    with validation and type safety.
    """

    # Environment and deployment
    environment: str = "local"  # local, development, staging, production
    debug: bool = True
    log_level: str = "INFO"

    # Service configurations
    temporal: TemporalConfig = field(
        default_factory=lambda: TemporalConfig.from_environment("local")
    )
    ai: AIConfig = field(default_factory=AIConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)

    # Application-specific settings
    app_name: str = "antifragile-flow"
    app_version: str = "1.0.0"
    base_url: str = "http://localhost:3000"

    # Security settings
    secret_key: str = "development-secret-key-change-in-production"
    allowed_hosts: list[str] = field(default_factory=lambda: ["localhost", "127.0.0.1"])
    cors_origins: list[str] = field(default_factory=lambda: ["http://localhost:3000"])

    # Feature flags
    enable_ai_research: bool = True
    enable_consensus_building: bool = True
    enable_document_processing: bool = True
    enable_knowledge_graph: bool = True

    # Performance settings
    max_concurrent_workflows: int = 10
    max_concurrent_activities: int = 20
    activity_timeout_seconds: int = 300
    workflow_timeout_seconds: int = 3600

    # File storage settings
    upload_directory: str = "./uploads"
    max_file_size_mb: int = 100
    allowed_file_types: list[str] = field(
        default_factory=lambda: [".pdf", ".docx", ".txt", ".md", ".csv", ".json"]
    )

    # Monitoring and observability
    enable_metrics: bool = True
    enable_tracing: bool = False
    metrics_port: int = 9090
    health_check_interval_seconds: int = 30

    # Development settings
    reload_on_change: bool = False
    enable_debug_endpoints: bool = False

    @classmethod
    def from_environment(cls, env: str | None = None) -> "Settings":
        """Create settings based on environment variables and environment name."""
        if env is None:
            env = os.getenv("ENVIRONMENT", "local")

        # Base configuration
        settings = cls(environment=env)

        # Load environment-specific configurations
        if env == "local":
            settings = cls._configure_local(settings)
        elif env == "development":
            settings = cls._configure_development(settings)
        elif env == "staging":
            settings = cls._configure_staging(settings)
        elif env == "production":
            settings = cls._configure_production(settings)

        # Apply environment variable overrides
        settings = cls._apply_env_overrides(settings)

        # Validate configuration
        settings.validate()

        return settings

    @classmethod
    def _configure_local(cls, settings: "Settings") -> "Settings":
        """Configure settings for local development."""
        settings.debug = True
        settings.log_level = "DEBUG"
        settings.reload_on_change = True
        settings.enable_debug_endpoints = True
        settings.enable_tracing = False
        settings.enable_metrics = False

        # Local service configurations
        settings.temporal = TemporalConfig.from_environment("local")
        settings.ai.environment = "local"
        settings.database.environment = "local"

        return settings

    @classmethod
    def _configure_development(cls, settings: "Settings") -> "Settings":
        """Configure settings for development environment."""
        settings.debug = True
        settings.log_level = "DEBUG"
        settings.enable_metrics = True
        settings.enable_tracing = True
        settings.base_url = os.getenv("BASE_URL", "https://dev.antifragile-flow.com")

        settings.temporal = TemporalConfig.from_environment("cloud")
        settings.ai.environment = "development"
        settings.database.environment = "development"

        return settings

    @classmethod
    def _configure_staging(cls, settings: "Settings") -> "Settings":
        """Configure settings for staging environment."""
        settings.debug = False
        settings.log_level = "INFO"
        settings.enable_metrics = True
        settings.enable_tracing = True
        settings.base_url = os.getenv("BASE_URL", "https://staging.antifragile-flow.com")

        settings.temporal = TemporalConfig.from_environment("cloud")
        settings.ai.environment = "staging"
        settings.database.environment = "staging"

        return settings

    @classmethod
    def _configure_production(cls, settings: "Settings") -> "Settings":
        """Configure settings for production environment."""
        settings.debug = False
        settings.log_level = "WARNING"
        settings.enable_debug_endpoints = False
        settings.enable_metrics = True
        settings.enable_tracing = True
        settings.base_url = os.getenv("BASE_URL", "https://antifragile-flow.com")

        # Production should use secure configurations
        settings.temporal = TemporalConfig.from_environment("production")
        settings.ai.environment = "production"
        settings.database.environment = "production"

        # Enhanced security for production
        settings.max_file_size_mb = 50  # Stricter limits
        settings.activity_timeout_seconds = 600  # Longer timeouts
        settings.workflow_timeout_seconds = 7200

        return settings

    @classmethod
    def _apply_env_overrides(cls, settings: "Settings") -> "Settings":
        """Apply environment variable overrides."""
        # Core settings
        if log_level := os.getenv("LOG_LEVEL"):
            settings.log_level = log_level

        if debug := os.getenv("DEBUG"):
            settings.debug = debug.lower() in ("true", "1", "yes")

        if base_url := os.getenv("BASE_URL"):
            settings.base_url = base_url

        # Security settings
        if secret_key := os.getenv("SECRET_KEY"):
            settings.secret_key = secret_key

        if allowed_hosts := os.getenv("ALLOWED_HOSTS"):
            settings.allowed_hosts = [host.strip() for host in allowed_hosts.split(",")]

        if cors_origins := os.getenv("CORS_ORIGINS"):
            settings.cors_origins = [origin.strip() for origin in cors_origins.split(",")]

        # Performance settings
        if max_workflows := os.getenv("MAX_CONCURRENT_WORKFLOWS"):
            settings.max_concurrent_workflows = int(max_workflows)

        if max_activities := os.getenv("MAX_CONCURRENT_ACTIVITIES"):
            settings.max_concurrent_activities = int(max_activities)

        # Feature flags
        if enable_ai := os.getenv("ENABLE_AI_RESEARCH"):
            settings.enable_ai_research = enable_ai.lower() in ("true", "1", "yes")

        if enable_consensus := os.getenv("ENABLE_CONSENSUS_BUILDING"):
            settings.enable_consensus_building = enable_consensus.lower() in ("true", "1", "yes")

        # File settings
        if upload_dir := os.getenv("UPLOAD_DIRECTORY"):
            settings.upload_directory = upload_dir

        if max_file_size := os.getenv("MAX_FILE_SIZE_MB"):
            settings.max_file_size_mb = int(max_file_size)

        return settings

    def validate(self) -> None:
        """Validate the configuration."""
        # Validate environment
        if self.environment not in ["local", "development", "staging", "production"]:
            raise ValueError(f"Invalid environment: {self.environment}")

        # Validate log level
        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError(f"Invalid log level: {self.log_level}")

        # Validate performance settings
        if self.max_concurrent_workflows <= 0:
            raise ValueError("max_concurrent_workflows must be positive")

        if self.max_concurrent_activities <= 0:
            raise ValueError("max_concurrent_activities must be positive")

        if self.activity_timeout_seconds <= 0:
            raise ValueError("activity_timeout_seconds must be positive")

        if self.workflow_timeout_seconds <= 0:
            raise ValueError("workflow_timeout_seconds must be positive")

        # Validate file settings
        if self.max_file_size_mb <= 0:
            raise ValueError("max_file_size_mb must be positive")

        # Validate security settings in production
        if self.environment == "production":
            if self.secret_key == "development-secret-key-change-in-production":
                raise ValueError("Must set a secure SECRET_KEY for production")

            if self.debug:
                raise ValueError("Debug mode must be disabled in production")

        # Validate upload directory exists or can be created
        upload_path = Path(self.upload_directory)
        upload_path.mkdir(parents=True, exist_ok=True)

        # Validate sub-configurations
        self.temporal.validate()
        self.ai.validate()
        self.database.validate()

    def get_database_url(self, database_name: str = "postgres") -> str:
        """Get database URL for the specified database."""
        return self.database.get_connection_url(database_name)

    def get_temporal_task_queue(self, workflow_type: str) -> str:
        """Get Temporal task queue for the specified workflow type."""
        return self.temporal.get_task_queue(workflow_type)

    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature flag is enabled."""
        feature_flags = {
            "ai_research": self.enable_ai_research,
            "consensus_building": self.enable_consensus_building,
            "document_processing": self.enable_document_processing,
            "knowledge_graph": self.enable_knowledge_graph,
        }
        return feature_flags.get(feature_name, False)

    def to_dict(self) -> dict:
        """Convert settings to dictionary for serialization."""
        # Note: This should exclude sensitive information like secret_key
        return {
            "environment": self.environment,
            "app_name": self.app_name,
            "app_version": self.app_version,
            "debug": self.debug,
            "log_level": self.log_level,
            "base_url": self.base_url,
            "features": {
                "ai_research": self.enable_ai_research,
                "consensus_building": self.enable_consensus_building,
                "document_processing": self.enable_document_processing,
                "knowledge_graph": self.enable_knowledge_graph,
            },
            "limits": {
                "max_concurrent_workflows": self.max_concurrent_workflows,
                "max_concurrent_activities": self.max_concurrent_activities,
                "max_file_size_mb": self.max_file_size_mb,
            },
        }


# Global settings instance
_settings: Settings | None = None


@lru_cache
def get_settings(environment: str | None = None) -> Settings:
    """
    Get application settings with caching.

    Args:
        environment: Optional environment override.

    Returns:
        Configured Settings instance.
    """
    global _settings

    if _settings is None or environment is not None:
        _settings = Settings.from_environment(environment)

    return _settings


def reload_settings(environment: str | None = None) -> Settings:
    """
    Force reload of settings (clears cache).

    Args:
        environment: Optional environment override.

    Returns:
        Newly loaded Settings instance.
    """
    global _settings
    get_settings.cache_clear()
    _settings = None
    return get_settings(environment)
