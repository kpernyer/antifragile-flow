# Production environment configuration
gcp_project  = "antifragile-flow-prod"
region       = "us-central1"
environment  = "prod"
project_name = "antifragile-flow"

# Container images (update with actual registry)
container_images = {
  typescript = "gcr.io/antifragile-flow-prod/temporal-typescript:latest"
  python     = "gcr.io/antifragile-flow-prod/temporal-python:latest"
  golang     = "gcr.io/antifragile-flow-prod/temporal-golang:latest"
}

# Database configuration for production
database_config = {
  tier               = "db-n1-standard-2"
  disk_size          = 100
  backup_enabled     = true
  point_in_time_recovery_enabled = true
  deletion_protection = true
}

# Environment variables
environment_variables = {
  typescript = {
    NODE_ENV = "production"
    LOG_LEVEL = "info"
  }
  python = {
    PYTHONPATH = "/app"
    LOG_LEVEL = "INFO"
  }
  golang = {
    CGO_ENABLED = "0"
    LOG_LEVEL = "info"
  }
}

# SSL certificate domains (configure for production)
ssl_certificate_domains = [
  "api.antifragile-flow.com",
  "www.antifragile-flow.com"
]

# Notification channels for production alerts
notification_channels = [
  # Add email/Slack notification channels
]
