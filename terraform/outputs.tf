output "load_balancer_ip" {
  description = "The external IP address of the load balancer"
  value       = module.load_balancer.external_ip
}

output "cloud_run_urls" {
  description = "URLs of the Cloud Run services"
  value       = module.cloud_run.service_urls
}

output "database_connection_name" {
  description = "The connection name of the Cloud SQL instance"
  value       = module.database.connection_name
}

output "database_private_ip" {
  description = "The private IP address of the Cloud SQL instance"
  value       = module.database.private_ip_address
}

output "vpc_network_name" {
  description = "The name of the VPC network"
  value       = module.network.vpc_network_name
}

output "vpc_connector_name" {
  description = "The name of the VPC connector"
  value       = module.network.vpc_connector_name
}

output "secret_ids" {
  description = "The IDs of created secrets"
  value       = module.secrets.secret_ids
}

output "monitoring_dashboard_url" {
  description = "URL of the monitoring dashboard"
  value       = module.monitoring.dashboard_url
}
