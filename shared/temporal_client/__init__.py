"""
Temporal client configuration and management for Antifragile Flow.

Provides centralized client configuration with:
- Environment-based configuration
- Connection pooling and retry logic
- TLS and authentication support
- Health checking and monitoring
- Graceful shutdown handling
"""

from .client import TemporalClientManager, get_temporal_client
from .config import TemporalConfig

__all__ = ["TemporalClientManager", "TemporalConfig", "get_temporal_client"]
