"""
Temporal client configuration management.

Provides environment-based configuration with validation and defaults
for connecting to Temporal clusters in different environments.
"""

from dataclasses import dataclass, field
import os

from temporalio.client import TLSConfig
from temporalio.runtime import PrometheusConfig, TelemetryConfig


@dataclass
class TemporalConfig:
    """
    Comprehensive Temporal client configuration.

    Supports local development, cloud deployment, and production environments
    with appropriate security and monitoring configurations.
    """

    # Connection settings
    target_host: str = "localhost:7233"
    namespace: str = "default"

    # Authentication and TLS
    tls_config: TLSConfig | None = None
    api_key: str | None = None

    # Client behavior
    default_task_queue: str = "antifragile-flow"
    default_workflow_timeout_seconds: int = 3600  # 1 hour
    default_activity_timeout_seconds: int = 300  # 5 minutes

    # Retry and resilience
    connection_timeout_seconds: int = 30
    keep_alive_ping_interval_seconds: int = 30
    keep_alive_timeout_seconds: int = 5

    # Telemetry and monitoring
    telemetry_config: TelemetryConfig | None = None
    enable_metrics: bool = True
    enable_logging: bool = True

    # Task queue configurations for different workflow types
    task_queues: dict[str, str] = field(
        default_factory=lambda: {
            "onboarding": "onboarding-queue",
            "daily_interaction": "daily-interaction-queue",
            "consensus_building": "consensus-queue",
            "document_processing": "document-processing-queue",
            "knowledge_building": "knowledge-building-queue",
        }
    )

    @classmethod
    def from_environment(cls, env: str = "local") -> "TemporalConfig":
        """Create configuration based on environment."""
        if env == "local":
            return cls._local_config()
        elif env == "cloud":
            return cls._cloud_config()
        elif env == "production":
            return cls._production_config()
        else:
            raise ValueError(f"Unknown environment: {env}")

    @classmethod
    def _local_config(cls) -> "TemporalConfig":
        """Configuration for local development."""
        return cls(
            target_host=os.getenv("TEMPORAL_ADDRESS", "localhost:7233"),
            namespace=os.getenv("TEMPORAL_NAMESPACE", "default"),
            default_task_queue=os.getenv("TEMPORAL_TASK_QUEUE", "antifragile-flow"),
            enable_metrics=False,  # Simplified for local development
            telemetry_config=None,
        )

    @classmethod
    def _cloud_config(cls) -> "TemporalConfig":
        """Configuration for Temporal Cloud."""
        namespace = os.getenv("TEMPORAL_CLOUD_NAMESPACE")
        if not namespace:
            raise ValueError(
                "TEMPORAL_CLOUD_NAMESPACE environment variable is required for cloud config"
            )

        api_key = os.getenv("TEMPORAL_CLOUD_API_KEY")
        if not api_key:
            raise ValueError(
                "TEMPORAL_CLOUD_API_KEY environment variable is required for cloud config"
            )

        cert_path = os.getenv("TEMPORAL_CLOUD_CERT_PATH")
        key_path = os.getenv("TEMPORAL_CLOUD_KEY_PATH")

        tls_config = None
        if cert_path and key_path:
            with open(cert_path, "rb") as cert_file:
                cert_data = cert_file.read()
            with open(key_path, "rb") as key_file:
                key_data = key_file.read()

            tls_config = TLSConfig(client_cert=cert_data, client_private_key=key_data)

        return cls(
            target_host=f"{namespace}.tmprl.cloud:7233",
            namespace=namespace,
            tls_config=tls_config,
            api_key=api_key,
            enable_metrics=True,
            telemetry_config=TelemetryConfig(metrics=PrometheusConfig(bind_address="0.0.0.0:9464")),
        )

    @classmethod
    def _production_config(cls) -> "TemporalConfig":
        """Configuration for production deployment."""
        # This would typically use Kubernetes service discovery
        # or load balancer addresses for production Temporal clusters
        target_host = os.getenv(
            "TEMPORAL_PRODUCTION_HOST", "temporal.production.svc.cluster.local:7233"
        )
        namespace = os.getenv("TEMPORAL_PRODUCTION_NAMESPACE", "production")

        # Production should always use TLS
        cert_path = os.getenv("TEMPORAL_TLS_CERT_PATH")
        key_path = os.getenv("TEMPORAL_TLS_KEY_PATH")
        ca_path = os.getenv("TEMPORAL_TLS_CA_PATH")

        tls_config = None
        if cert_path and key_path:
            with open(cert_path, "rb") as cert_file:
                cert_data = cert_file.read()
            with open(key_path, "rb") as key_file:
                key_data = key_file.read()

            ca_data = None
            if ca_path:
                with open(ca_path, "rb") as ca_file:
                    ca_data = ca_file.read()

            tls_config = TLSConfig(
                client_cert=cert_data, client_private_key=key_data, ca_cert=ca_data
            )

        return cls(
            target_host=target_host,
            namespace=namespace,
            tls_config=tls_config,
            api_key=os.getenv("TEMPORAL_API_KEY"),
            default_workflow_timeout_seconds=7200,  # 2 hours for production
            default_activity_timeout_seconds=600,  # 10 minutes for production
            connection_timeout_seconds=60,  # Longer timeout for production
            enable_metrics=True,
            telemetry_config=TelemetryConfig(metrics=PrometheusConfig(bind_address="0.0.0.0:9464")),
        )

    def get_task_queue(self, workflow_type: str) -> str:
        """Get the appropriate task queue for a workflow type."""
        return self.task_queues.get(workflow_type, self.default_task_queue)

    def validate(self) -> None:
        """Validate the configuration."""
        if not self.target_host:
            raise ValueError("target_host is required")

        if not self.namespace:
            raise ValueError("namespace is required")

        if self.default_workflow_timeout_seconds <= 0:
            raise ValueError("default_workflow_timeout_seconds must be positive")

        if self.default_activity_timeout_seconds <= 0:
            raise ValueError("default_activity_timeout_seconds must be positive")

        if self.connection_timeout_seconds <= 0:
            raise ValueError("connection_timeout_seconds must be positive")

        # Validate TLS configuration if provided
        if self.tls_config and not self.tls_config.client_cert:
            raise ValueError("TLS configuration requires client certificate")

    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate()
