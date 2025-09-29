variable "gcp_project" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "antifragile-flow"
}

variable "container_images" {
  description = "Container images for each service"
  type = object({
    typescript = string
    python     = string
    golang     = string
  })
  default = {
    typescript = "gcr.io/PROJECT_ID/temporal-typescript:latest"
    python     = "gcr.io/PROJECT_ID/temporal-python:latest"
    golang     = "gcr.io/PROJECT_ID/temporal-golang:latest"
  }
}

variable "temporal_address" {
  description = "Temporal server address"
  type        = string
  default     = "temporal.temporal.svc.cluster.local:7233"
}

variable "environment_variables" {
  description = "Environment variables for Cloud Run services"
  type        = map(map(string))
  default = {
    typescript = {
      NODE_ENV = "production"
    }
    python = {
      PYTHONPATH = "/app"
    }
    golang = {
      CGO_ENABLED = "0"
    }
  }
}

variable "database_config" {
  description = "Database configuration"
  type = object({
    tier               = string
    disk_size          = number
    backup_enabled     = bool
    point_in_time_recovery_enabled = bool
    deletion_protection = bool
  })
  default = {
    tier               = "db-f1-micro"
    disk_size          = 20
    backup_enabled     = true
    point_in_time_recovery_enabled = true
    deletion_protection = true
  }
}

variable "secrets" {
  description = "Secrets to create in Secret Manager"
  type        = map(string)
  default = {
    "database-password" = "PLACEHOLDER"
    "temporal-tls-cert" = "PLACEHOLDER"
    "temporal-tls-key"  = "PLACEHOLDER"
  }
}

variable "ssl_certificate_domains" {
  description = "Domains for SSL certificate"
  type        = list(string)
  default     = []
}

variable "notification_channels" {
  description = "Notification channels for monitoring alerts"
  type        = list(string)
  default     = []
}
