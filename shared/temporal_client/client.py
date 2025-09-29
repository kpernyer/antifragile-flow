"""
Temporal client management with connection pooling and health checking.

Provides centralized client creation and management with automatic
reconnection, health monitoring, and graceful shutdown handling.
"""

import asyncio
import logging

from temporalio.client import Client
from temporalio.service import RPCError, RPCStatusCode

from .config import TemporalConfig

logger = logging.getLogger(__name__)


class TemporalClientManager:
    """
    Manages Temporal client connections with health checking and reconnection.

    Provides a singleton pattern for client access with automatic
    health monitoring and connection recovery.
    """

    def __init__(self, config: TemporalConfig):
        self.config = config
        self._client: Client | None = None
        self._health_check_task: asyncio.Task | None = None
        self._shutdown_requested = False

    async def get_client(self) -> Client:
        """Get or create a Temporal client connection."""
        if self._client is None or self._shutdown_requested:
            await self._create_client()

        return self._client

    async def _create_client(self) -> None:
        """Create a new Temporal client with configured settings."""
        try:
            logger.info(f"Connecting to Temporal at {self.config.target_host}")

            connect_kwargs = {
                "target_host": self.config.target_host,
                "namespace": self.config.namespace,
            }

            # Add TLS configuration if provided
            if self.config.tls_config:
                connect_kwargs["tls"] = self.config.tls_config

            # Add API key for Temporal Cloud
            if self.config.api_key:
                connect_kwargs["api_key"] = self.config.api_key

            # Add telemetry configuration
            if self.config.telemetry_config:
                connect_kwargs["runtime_config"] = {"telemetry": self.config.telemetry_config}

            self._client = await Client.connect(**connect_kwargs)

            logger.info(f"Successfully connected to Temporal namespace '{self.config.namespace}'")

            # Start health checking if metrics are enabled
            if self.config.enable_metrics and not self._health_check_task:
                self._health_check_task = asyncio.create_task(self._health_check_loop())

        except Exception as e:
            logger.error(f"Failed to connect to Temporal: {e!s}")
            raise

    async def _health_check_loop(self) -> None:
        """Continuously monitor client health and reconnect if needed."""
        while not self._shutdown_requested:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds

                if self._client:
                    # Perform a simple health check by listing workflows
                    try:
                        async for _ in self._client.list_workflows():
                            break  # Just check if we can list workflows

                        logger.debug("Temporal client health check passed")

                    except RPCError as e:
                        if e.status == RPCStatusCode.UNAVAILABLE:
                            logger.warning("Temporal server unavailable, attempting reconnection")
                            await self._recreate_client()
                        else:
                            logger.error(f"Temporal health check failed: {e!s}")

                    except Exception as e:
                        logger.error(f"Unexpected error during health check: {e!s}")
                        await self._recreate_client()

            except asyncio.CancelledError:
                logger.info("Health check loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in health check loop: {e!s}")

    async def _recreate_client(self) -> None:
        """Recreate the client connection after a failure."""
        try:
            if self._client:
                # Close the existing client if possible
                try:
                    # Note: Temporal Python SDK doesn't have an explicit close method
                    # The connection will be cleaned up when the object is garbage collected
                    pass
                except Exception as e:
                    logger.warning(f"Error closing existing client: {e!s}")

            self._client = None
            await self._create_client()
            logger.info("Successfully recreated Temporal client connection")

        except Exception as e:
            logger.error(f"Failed to recreate Temporal client: {e!s}")

    async def shutdown(self) -> None:
        """Gracefully shutdown the client manager."""
        logger.info("Shutting down Temporal client manager")
        self._shutdown_requested = True

        # Cancel health check task
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

        # Close client connection
        if self._client:
            # Note: Temporal Python SDK doesn't have an explicit close method
            # The connection will be cleaned up when the object is garbage collected
            self._client = None

        logger.info("Temporal client manager shutdown complete")

    async def __aenter__(self):
        """Async context manager entry."""
        return await self.get_client()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.shutdown()


# Global client manager instance
_client_manager: TemporalClientManager | None = None


async def get_temporal_client(
    config: TemporalConfig | None = None, environment: str = "local"
) -> Client:
    """
    Get a Temporal client instance with automatic configuration.

    Args:
        config: Optional explicit configuration. If not provided,
                configuration will be loaded from environment.
        environment: Environment name for configuration loading.

    Returns:
        Configured Temporal client instance.
    """
    global _client_manager

    # Create configuration if not provided
    if config is None:
        config = TemporalConfig.from_environment(environment)

    # Create or reuse client manager
    if _client_manager is None:
        _client_manager = TemporalClientManager(config)

    return await _client_manager.get_client()


async def shutdown_temporal_client() -> None:
    """Shutdown the global client manager."""
    global _client_manager

    if _client_manager:
        await _client_manager.shutdown()
        _client_manager = None


# Context manager for easy client lifecycle management
class TemporalClientContext:
    """Context manager for Temporal client lifecycle management."""

    def __init__(self, config: TemporalConfig | None = None, environment: str = "local"):
        self.config = config
        self.environment = environment
        self.client: Client | None = None

    async def __aenter__(self) -> Client:
        """Get client on context entry."""
        self.client = await get_temporal_client(self.config, self.environment)
        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Cleanup on context exit."""
        # Note: We don't shutdown the global client manager here
        # as it may be used by other parts of the application
        pass


# Utility functions for common patterns
async def with_temporal_client(
    func, config: TemporalConfig | None = None, environment: str = "local"
):
    """
    Execute a function with a Temporal client.

    Usage:
        result = await with_temporal_client(
            lambda client: client.start_workflow(...)
        )
    """
    async with TemporalClientContext(config, environment) as client:
        return await func(client)


def get_default_retry_policy():
    """Get the default retry policy for activities."""
    from datetime import timedelta

    from temporalio.common import RetryPolicy

    return RetryPolicy(
        initial_interval=timedelta(seconds=1),
        maximum_interval=timedelta(seconds=60),
        maximum_attempts=3,
        backoff_coefficient=2.0,
        non_retryable_error_types=["ValidationError"],
    )
