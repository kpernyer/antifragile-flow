# Living Twin - Scaling and Cost Management Guide

This guide explains how scaling is configured, where costs come from, and how to optimize them.

## 🎯 Quick Cost Check

Run this command to see your current resource utilization and costs:

```bash
python tools/scripts/check_resource_utilization.py --project-id YOUR_PROJECT_ID --environment dev --show-config
```

## 📊 Scaling Configuration Overview

### Environment-Specific Scaling (Main Configuration)

**File:** `packages/gcp_firebase/terraform/main.tf`

```hcl
# Environment-specific configuration
env_config = {
  dev = {
    min_instances = 0        # 💚 Scales to zero = NO COST when idle
    max_instances = 5        # Limits max cost
    cpu_limit     = "1000m"  # 1 CPU core
    memory_limit  = "2Gi"    # 2GB RAM
    enable_dlq    = true
    enable_backup = false    # 💰 Saves storage costs
  }
  staging = {
    min_instances = 1        # 💛 Always 1 instance running
    max_instances = 10
    cpu_limit     = "1000m"
    memory_limit  = "2Gi"
    enable_dlq    = true
    enable_backup = true
  }
  prod = {
    min_instances = 2        # 🔴 Always 2 instances running
    max_instances = 50
    cpu_limit     = "2000m"  # 2 CPU cores
    memory_limit  = "4Gi"    # 4GB RAM
    enable_dlq    = true
    enable_backup = true
  }
}
```

### 💰 Cost Impact by Environment

| Environment | Min Cost/Month | When Idle | When Busy |
|-------------|----------------|-----------|-----------|
| **dev** | ~$0 | Scales to 0 | Scales up as needed |
| **staging** | ~$15-25 | 1 instance always running | Scales 1-10 |
| **prod** | ~$60-100 | 2 instances always running | Scales 2-50 |

## 🚀 Cloud Run Scaling Behavior

### How Auto-Scaling Works

1. **Scale to Zero** (min_instances = 0)
   - Service shuts down when no requests
   - Cold start delay (~1-3 seconds) on first request
   - **Cost: $0 when idle** 💚

2. **Always On** (min_instances > 0)
   - Always keeps minimum instances running
   - No cold start delay
   - **Cost: Continuous billing** 💰

3. **Scale Up Triggers**
   - CPU utilization > 60%
   - Request concurrency > 80 per instance
   - Custom metrics (if configured)

### Scaling Configuration Locations

#### 1. Main Terraform Configuration

```bash
# File: packages/gcp_firebase/terraform/main.tf
# Section: locals.env_config

# To modify:
vim packages/gcp_firebase/terraform/main.tf
# Edit the env_config section
```

#### 2. Override Variables

```bash
# File: packages/gcp_firebase/terraform/variables.tf
# Variables: api_min_instances, api_max_instances, etc.

# To override via command line:
terraform apply -var="api_min_instances=0" -var="api_max_instances=3"
```

#### 3. Environment Files (Recommended)

```bash
# Create environment-specific variable files:
# packages/gcp_firebase/terraform/environments/dev.tfvars
# packages/gcp_firebase/terraform/environments/staging.tfvars
# packages/gcp_firebase/terraform/environments/prod.tfvars
```

## 💡 Cost Optimization Strategies

### 1. Development Environment (Minimize Costs)

```hcl
# Recommended dev settings
dev = {
  min_instances = 0        # Scale to zero
  max_instances = 3        # Limit max scale
  cpu_limit     = "1000m"  # 1 CPU core
  memory_limit  = "1Gi"    # 1GB RAM (reduced)
  enable_backup = false    # No backups needed
}
```

### 2. Staging Environment (Balance Cost/Performance)

```hcl
# Recommended staging settings
staging = {
  min_instances = 0        # Can scale to zero for cost savings
  max_instances = 5        # Moderate scaling
  cpu_limit     = "1000m"
  memory_limit  = "2Gi"
  enable_backup = true     # Test backup functionality
}
```

### 3. Production Environment (Performance First)

```hcl
# Recommended prod settings
prod = {
  min_instances = 1        # Always ready (or 2 for HA)
  max_instances = 20       # Scale for traffic
  cpu_limit     = "2000m"  # More CPU for performance
  memory_limit  = "4Gi"    # More memory for caching
  enable_backup = true     # Full backups
}
```

## 🔧 How to Change Scaling Configuration

### Method 1: Edit Terraform Configuration

```bash
# 1. Edit the main configuration
vim packages/gcp_firebase/terraform/main.tf

# 2. Find locals.env_config section
# 3. Modify the values for your environment
# 4. Apply changes
cd packages/gcp_firebase/terraform
terraform workspace select dev  # or staging/prod
terraform plan
terraform apply
```

### Method 2: Use Environment Variables

```bash
# Create environment-specific tfvars file
cat > packages/gcp_firebase/terraform/environments/dev.tfvars << EOF
api_min_instances = 0
api_max_instances = 3
worker_min_instances = 0
worker_max_instances = 2
enable_backup = false
EOF

# Apply with environment file
terraform apply -var-file=environments/dev.tfvars
```

### Method 3: Command Line Override

```bash
# Quick one-time changes
terraform apply \
  -var="api_min_instances=0" \
  -var="api_max_instances=5" \
  -var="worker_min_instances=0"
```

## 📈 Monitoring and Alerts

### Built-in Cost Monitoring

The infrastructure includes monitoring for:

- Service scaling events
- Resource utilization
- Cost anomalies
- Unused resources

### Manual Monitoring Commands

```bash
# Check current service status
gcloud run services list --region=europe-west1

# Check current instances
gcloud run services describe SERVICE_NAME --region=europe-west1

# Monitor costs
gcloud billing budgets list
```

## 🚨 Cost Alerts and Budgets

### Setting Up Budget Alerts

```bash
# Create a budget alert (run once)
gcloud billing budgets create \
  --billing-account=YOUR_BILLING_ACCOUNT \
  --display-name="Living Twin Monthly Budget" \
  --budget-amount=100 \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90
```

### Automated Cost Monitoring

The resource utilization script runs checks and provides recommendations:

```bash
# Daily cost check (add to cron)
python tools/scripts/check_resource_utilization.py \
  --project-id YOUR_PROJECT_ID \
  --environment dev
```

## 🎛️ Advanced Scaling Configuration

### Custom Scaling Metrics

```hcl
# In Cloud Run module
resource "google_cloud_run_service" "service" {
  # ... other config

  metadata {
    annotations = {
      "autoscaling.knative.dev/minScale" = var.min_instances
      "autoscaling.knative.dev/maxScale" = var.max_instances
      "run.googleapis.com/cpu-throttling" = "false"  # No CPU throttling
      "run.googleapis.com/execution-environment" = "gen2"  # Better performance
    }
  }
}
```

### Traffic-Based Scaling

```hcl
# Configure concurrency limits
spec {
  container_concurrency = 80  # Max requests per instance
  timeout_seconds = 300       # Request timeout
}
```

## 📋 Cost Optimization Checklist

### ✅ Development Environment

- [ ] `min_instances = 0` (scale to zero)
- [ ] `max_instances ≤ 5` (limit max cost)
- [ ] `enable_backup = false` (no backups needed)
- [ ] Use smaller CPU/memory limits
- [ ] Monitor with resource utilization script

### ✅ Staging Environment

- [ ] Consider `min_instances = 0` for cost savings
- [ ] `max_instances ≤ 10` (reasonable limit)
- [ ] `enable_backup = true` (test backups)
- [ ] Monitor scaling behavior

### ✅ Production Environment

- [ ] `min_instances ≥ 1` (always ready)
- [ ] `max_instances` based on expected traffic
- [ ] `enable_backup = true` (full backups)
- [ ] Set up budget alerts
- [ ] Monitor costs regularly

## 🔍 Troubleshooting Scaling Issues

### Service Not Scaling Down

```bash
# Check if there are active requests
gcloud run services describe SERVICE_NAME --region=europe-west1

# Check logs for errors preventing shutdown
gcloud logs read "resource.type=cloud_run_revision" --limit=50
```

### Unexpected Costs

```bash
# Run cost analysis
python tools/scripts/check_resource_utilization.py \
  --project-id YOUR_PROJECT_ID \
  --environment ENVIRONMENT

# Check billing details
gcloud billing accounts list
gcloud billing projects describe YOUR_PROJECT_ID
```

### Cold Start Issues

If cold starts are problematic:

1. Increase `min_instances` to 1
2. Optimize application startup time
3. Consider using Cloud Run always-on CPU allocation

## 📞 Quick Commands Reference

```bash
# Check resource utilization and costs
python tools/scripts/check_resource_utilization.py --project-id PROJECT_ID --environment dev --show-config

# List all Cloud Run services
gcloud run services list --region=europe-west1

# Scale a service manually (temporary)
gcloud run services update SERVICE_NAME --min-instances=0 --max-instances=5 --region=europe-west1

# Check current Terraform workspace
terraform workspace show

# Switch environment
terraform workspace select dev

# Apply scaling changes
terraform apply -var-file=environments/dev.tfvars
```

Remember: **The key to cost optimization is setting `min_instances = 0` for non-production environments!** This allows services to scale to zero when not in use, eliminating idle costs.
