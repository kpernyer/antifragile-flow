terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.84"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 4.84"
    }
  }
}

provider "google" {
  project = var.gcp_project
  region  = var.region
}

provider "google-beta" {
  project = var.gcp_project
  region  = var.region
}

# Local values
locals {
  name_prefix = "${var.project_name}-${var.environment}"
  common_labels = {
    project     = var.project_name
    environment = var.environment
    managed_by  = "terraform"
  }
}

# Enable required APIs
module "project_services" {
  source = "./modules/project-services"

  gcp_project = var.gcp_project
}

# VPC Network
module "network" {
  source = "./modules/network"

  project_id   = var.gcp_project
  name_prefix  = local.name_prefix
  region       = var.region
  labels       = local.common_labels
}

# Cloud Run services
module "cloud_run" {
  source = "./modules/cloud-run"

  project_id           = var.gcp_project
  region               = var.region
  name_prefix          = local.name_prefix
  labels               = local.common_labels
  vpc_connector_name   = module.network.vpc_connector_name
  container_images     = var.container_images
  temporal_address     = var.temporal_address
  environment_variables = var.environment_variables
}

# Load Balancer
module "load_balancer" {
  source = "./modules/load-balancer"

  project_id    = var.gcp_project
  name_prefix   = local.name_prefix
  labels        = local.common_labels
  cloud_run_services = module.cloud_run.services
  ssl_certificate_domains = var.ssl_certificate_domains
}

# Cloud SQL (PostgreSQL)
module "database" {
  source = "./modules/database"

  project_id      = var.gcp_project
  region          = var.region
  name_prefix     = local.name_prefix
  labels          = local.common_labels
  network_id      = module.network.vpc_network_id
  database_config = var.database_config
}

# Secret Manager
module "secrets" {
  source = "./modules/secrets"

  project_id  = var.gcp_project
  name_prefix = local.name_prefix
  labels      = local.common_labels
  secrets     = var.secrets
}

# Monitoring and Logging
module "monitoring" {
  source = "./modules/monitoring"

  project_id       = var.gcp_project
  name_prefix      = local.name_prefix
  labels           = local.common_labels
  notification_channels = var.notification_channels
}
