# Development environment configuration
gcp_project  = "antifragile-flow-dev"
region       = "us-central1"
environment  = "dev"
project_name = "antifragile-flow"

# Container images (update with actual registry)
container_images = {
  typescript = "gcr.io/antifragile-flow-dev/temporal-typescript:latest"
  python     = "gcr.io/antifragile-flow-dev/temporal-python:latest"
  golang     = "gcr.io/antifragile-flow-dev/temporal-golang:latest"
}

# Database configuration for development
database_config = {
  tier               = "db-f1-micro"
  disk_size          = 20
  backup_enabled     = true
  point_in_time_recovery_enabled = false
  deletion_protection = false
}

# Environment variables
environment_variables = {
  typescript = {
    NODE_ENV = "development"
    LOG_LEVEL = "debug"
  }
  python = {
    PYTHONPATH = "/app"
    LOG_LEVEL = "DEBUG"
  }
  golang = {
    CGO_ENABLED = "0"
    LOG_LEVEL = "debug"
  }
}

# SSL certificate domains (empty for dev)
ssl_certificate_domains = []

# Notification channels (empty for dev)
notification_channels = []
