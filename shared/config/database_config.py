"""
Database configuration for PostgreSQL, Neo4j, and Redis connections.

Provides environment-based configuration with connection pooling,
SSL settings, and connection string generation.
"""

from dataclasses import dataclass
import os


@dataclass
class DatabaseConfig:
    """
    Comprehensive database configuration for all database types.

    Supports PostgreSQL, Neo4j, and Redis with environment-specific
    settings for development, staging, and production.
    """

    # Environment
    environment: str = "local"

    # PostgreSQL configuration (primary database)
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_database: str = "antifragile"
    postgres_ssl_mode: str = "prefer"

    # Application PostgreSQL (separate from Temporal)
    app_postgres_host: str = "localhost"
    app_postgres_port: int = 5433
    app_postgres_user: str = "app_user"
    app_postgres_password: str = "app_password"
    app_postgres_database: str = "antifragile"

    # Neo4j configuration (knowledge graph)
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "neo4j_password"
    neo4j_database: str = "neo4j"

    # Redis configuration (caching and sessions)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str | None = None
    redis_database: int = 0
    redis_ssl: bool = False

    # Connection pooling settings
    postgres_pool_min_size: int = 5
    postgres_pool_max_size: int = 20
    postgres_pool_timeout_seconds: int = 30

    neo4j_pool_max_size: int = 10
    neo4j_connection_timeout_seconds: int = 30

    redis_pool_max_connections: int = 10
    redis_socket_timeout_seconds: int = 30

    # SSL and security settings
    postgres_ssl_cert_path: str | None = None
    postgres_ssl_key_path: str | None = None
    postgres_ssl_ca_path: str | None = None

    neo4j_encrypted: bool = False
    neo4j_trust_all_certificates: bool = False

    def __post_init__(self):
        """Load configuration from environment variables."""
        self._load_postgres_config()
        self._load_neo4j_config()
        self._load_redis_config()

    def _load_postgres_config(self) -> None:
        """Load PostgreSQL configuration from environment."""
        # Temporal PostgreSQL (main database)
        self.postgres_host = os.getenv("POSTGRES_HOST", self.postgres_host)
        self.postgres_port = int(os.getenv("POSTGRES_PORT", str(self.postgres_port)))
        self.postgres_user = os.getenv("POSTGRES_USER", self.postgres_user)
        self.postgres_password = os.getenv("POSTGRES_PASSWORD", self.postgres_password)
        self.postgres_database = os.getenv("POSTGRES_DB", self.postgres_database)
        self.postgres_ssl_mode = os.getenv("POSTGRES_SSL_MODE", self.postgres_ssl_mode)

        # Application PostgreSQL
        self.app_postgres_host = os.getenv("APP_POSTGRES_HOST", self.app_postgres_host)
        self.app_postgres_port = int(os.getenv("APP_POSTGRES_PORT", str(self.app_postgres_port)))
        self.app_postgres_user = os.getenv("APP_POSTGRES_USER", self.app_postgres_user)
        self.app_postgres_password = os.getenv("APP_POSTGRES_PASSWORD", self.app_postgres_password)
        self.app_postgres_database = os.getenv("APP_POSTGRES_DB", self.app_postgres_database)

        # SSL configuration
        self.postgres_ssl_cert_path = os.getenv("POSTGRES_SSL_CERT_PATH")
        self.postgres_ssl_key_path = os.getenv("POSTGRES_SSL_KEY_PATH")
        self.postgres_ssl_ca_path = os.getenv("POSTGRES_SSL_CA_PATH")

    def _load_neo4j_config(self) -> None:
        """Load Neo4j configuration from environment."""
        self.neo4j_uri = os.getenv("NEO4J_URI", self.neo4j_uri)
        self.neo4j_user = os.getenv("NEO4J_USER", self.neo4j_user)
        self.neo4j_password = os.getenv("NEO4J_PASSWORD", self.neo4j_password)
        self.neo4j_database = os.getenv("NEO4J_DATABASE", self.neo4j_database)

        # SSL/encryption settings
        if os.getenv("NEO4J_ENCRYPTED"):
            self.neo4j_encrypted = os.getenv("NEO4J_ENCRYPTED").lower() in ("true", "1", "yes")

        if os.getenv("NEO4J_TRUST_ALL_CERTIFICATES"):
            self.neo4j_trust_all_certificates = os.getenv(
                "NEO4J_TRUST_ALL_CERTIFICATES"
            ).lower() in ("true", "1", "yes")

    def _load_redis_config(self) -> None:
        """Load Redis configuration from environment."""
        self.redis_host = os.getenv("REDIS_HOST", self.redis_host)
        self.redis_port = int(os.getenv("REDIS_PORT", str(self.redis_port)))
        self.redis_password = os.getenv("REDIS_PASSWORD")
        self.redis_database = int(os.getenv("REDIS_DATABASE", str(self.redis_database)))

        if os.getenv("REDIS_SSL"):
            self.redis_ssl = os.getenv("REDIS_SSL").lower() in ("true", "1", "yes")

    def get_connection_url(self, database_type: str) -> str:
        """Get connection URL for the specified database type."""
        if database_type == "postgres":
            return self._get_postgres_url()
        elif database_type == "app_postgres":
            return self._get_app_postgres_url()
        elif database_type == "neo4j":
            return self._get_neo4j_url()
        elif database_type == "redis":
            return self._get_redis_url()
        else:
            raise ValueError(f"Unknown database type: {database_type}")

    def _get_postgres_url(self) -> str:
        """Get PostgreSQL connection URL."""
        url = f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_database}"

        # Add SSL parameters
        params = []
        if self.postgres_ssl_mode != "prefer":
            params.append(f"sslmode={self.postgres_ssl_mode}")

        if self.postgres_ssl_cert_path:
            params.append(f"sslcert={self.postgres_ssl_cert_path}")

        if self.postgres_ssl_key_path:
            params.append(f"sslkey={self.postgres_ssl_key_path}")

        if self.postgres_ssl_ca_path:
            params.append(f"sslrootcert={self.postgres_ssl_ca_path}")

        if params:
            url += "?" + "&".join(params)

        return url

    def _get_app_postgres_url(self) -> str:
        """Get application PostgreSQL connection URL."""
        return f"postgresql://{self.app_postgres_user}:{self.app_postgres_password}@{self.app_postgres_host}:{self.app_postgres_port}/{self.app_postgres_database}"

    def _get_neo4j_url(self) -> str:
        """Get Neo4j connection URL."""
        return self.neo4j_uri

    def _get_redis_url(self) -> str:
        """Get Redis connection URL."""
        protocol = "rediss" if self.redis_ssl else "redis"
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"{protocol}://{auth}{self.redis_host}:{self.redis_port}/{self.redis_database}"

    def get_postgres_connection_params(self, app_db: bool = False) -> dict:
        """Get PostgreSQL connection parameters as a dictionary."""
        if app_db:
            return {
                "host": self.app_postgres_host,
                "port": self.app_postgres_port,
                "user": self.app_postgres_user,
                "password": self.app_postgres_password,
                "database": self.app_postgres_database,
                "minconn": self.postgres_pool_min_size,
                "maxconn": self.postgres_pool_max_size,
                "timeout": self.postgres_pool_timeout_seconds,
            }
        else:
            params = {
                "host": self.postgres_host,
                "port": self.postgres_port,
                "user": self.postgres_user,
                "password": self.postgres_password,
                "database": self.postgres_database,
                "sslmode": self.postgres_ssl_mode,
                "minconn": self.postgres_pool_min_size,
                "maxconn": self.postgres_pool_max_size,
                "timeout": self.postgres_pool_timeout_seconds,
            }

            # Add SSL certificate parameters
            if self.postgres_ssl_cert_path:
                params["sslcert"] = self.postgres_ssl_cert_path

            if self.postgres_ssl_key_path:
                params["sslkey"] = self.postgres_ssl_key_path

            if self.postgres_ssl_ca_path:
                params["sslrootcert"] = self.postgres_ssl_ca_path

            return params

    def get_neo4j_connection_params(self) -> dict:
        """Get Neo4j connection parameters as a dictionary."""
        return {
            "uri": self.neo4j_uri,
            "auth": (self.neo4j_user, self.neo4j_password),
            "database": self.neo4j_database,
            "max_connection_pool_size": self.neo4j_pool_max_size,
            "connection_timeout": self.neo4j_connection_timeout_seconds,
            "encrypted": self.neo4j_encrypted,
            "trust": "TRUST_ALL_CERTIFICATES"
            if self.neo4j_trust_all_certificates
            else "TRUST_SYSTEM_CA_SIGNED_CERTIFICATES",
        }

    def get_redis_connection_params(self) -> dict:
        """Get Redis connection parameters as a dictionary."""
        params = {
            "host": self.redis_host,
            "port": self.redis_port,
            "db": self.redis_database,
            "max_connections": self.redis_pool_max_connections,
            "socket_timeout": self.redis_socket_timeout_seconds,
            "ssl": self.redis_ssl,
        }

        if self.redis_password:
            params["password"] = self.redis_password

        return params

    def validate(self) -> None:
        """Validate the database configuration."""
        # Validate PostgreSQL settings
        if not self.postgres_host:
            raise ValueError("postgres_host is required")

        if self.postgres_port <= 0 or self.postgres_port > 65535:
            raise ValueError("postgres_port must be between 1 and 65535")

        if not self.postgres_user:
            raise ValueError("postgres_user is required")

        if not self.postgres_database:
            raise ValueError("postgres_database is required")

        # Validate Neo4j settings
        if not self.neo4j_uri:
            raise ValueError("neo4j_uri is required")

        if not self.neo4j_user:
            raise ValueError("neo4j_user is required")

        # Validate Redis settings
        if not self.redis_host:
            raise ValueError("redis_host is required")

        if self.redis_port <= 0 or self.redis_port > 65535:
            raise ValueError("redis_port must be between 1 and 65535")

        if self.redis_database < 0:
            raise ValueError("redis_database must be non-negative")

        # Validate pool settings
        if self.postgres_pool_min_size < 0:
            raise ValueError("postgres_pool_min_size must be non-negative")

        if self.postgres_pool_max_size <= self.postgres_pool_min_size:
            raise ValueError("postgres_pool_max_size must be greater than postgres_pool_min_size")

        if self.neo4j_pool_max_size <= 0:
            raise ValueError("neo4j_pool_max_size must be positive")

        if self.redis_pool_max_connections <= 0:
            raise ValueError("redis_pool_max_connections must be positive")

        # Validate SSL mode
        valid_ssl_modes = ["disable", "allow", "prefer", "require", "verify-ca", "verify-full"]
        if self.postgres_ssl_mode not in valid_ssl_modes:
            raise ValueError(f"postgres_ssl_mode must be one of: {', '.join(valid_ssl_modes)}")

        # Validate production settings
        if self.environment == "production":
            if self.postgres_ssl_mode in ("disable", "allow"):
                raise ValueError(
                    "Production environment requires secure SSL mode (prefer, require, verify-ca, or verify-full)"
                )

            if self.postgres_password == "postgres":
                raise ValueError("Production environment requires secure PostgreSQL password")

            if self.neo4j_password == "neo4j_password":
                raise ValueError("Production environment requires secure Neo4j password")

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization (excluding sensitive data)."""
        return {
            "environment": self.environment,
            "postgres": {
                "host": self.postgres_host,
                "port": self.postgres_port,
                "database": self.postgres_database,
                "ssl_mode": self.postgres_ssl_mode,
                "pool_settings": {
                    "min_size": self.postgres_pool_min_size,
                    "max_size": self.postgres_pool_max_size,
                    "timeout": self.postgres_pool_timeout_seconds,
                },
            },
            "neo4j": {
                "uri": self.neo4j_uri,
                "database": self.neo4j_database,
                "encrypted": self.neo4j_encrypted,
                "pool_max_size": self.neo4j_pool_max_size,
            },
            "redis": {
                "host": self.redis_host,
                "port": self.redis_port,
                "database": self.redis_database,
                "ssl": self.redis_ssl,
                "pool_max_connections": self.redis_pool_max_connections,
            },
        }
