# Docker & Google Cloud Commands Guide

## Core Docker Commands

### Building Images
```bash
# Build for current platform
docker build -t image-name:tag .

# Build for Linux AMD64 (required for Cloud Run)
docker buildx build --platform linux/amd64 -t image-name:tag .

# Build with specific Dockerfile
docker build -f Dockerfile.simple -t image-name:tag .

# Build from specific directory
docker build -t image-name:tag apps/api
```

### Managing Images
```bash
# List local images
docker images

# Remove image
docker rmi image-name:tag

# Tag image for registry
docker tag local-image:tag gcr.io/project-id/image-name:tag

# Push to Google Container Registry
docker push gcr.io/project-id/image-name:tag

# Pull from registry
docker pull gcr.io/project-id/image-name:tag
```

### Running Containers Locally
```bash
# Run container
docker run -p 8080:8000 image-name:tag

# Run in background
docker run -d -p 8080:8000 image-name:tag

# Run with environment variables
docker run -e ENV_VAR=value -p 8080:8000 image-name:tag

# Run with volume mount
docker run -v $(pwd):/app -p 8080:8000 image-name:tag
```

## Google Cloud Run Commands

### Service Management
```bash
# List services
gcloud run services list --region=europe-north1

# Deploy service
gcloud run deploy service-name \
  --image gcr.io/project-id/image-name:tag \
  --region=europe-north1 \
  --allow-unauthenticated \
  --port=8000

# Deploy with environment variables
gcloud run deploy service-name \
  --image gcr.io/project-id/image-name:tag \
  --region=europe-north1 \
  --set-env-vars="ENV=production,REDIS_HOST=10.1.1.1"

# Deploy with memory and CPU limits
gcloud run deploy service-name \
  --image gcr.io/project-id/image-name:tag \
  --region=europe-north1 \
  --memory=1Gi \
  --cpu=1000m \
  --max-instances=10

# Update service
gcloud run services update service-name \
  --region=europe-north1 \
  --image gcr.io/project-id/new-image:tag
```

### Service Information
```bash
# Describe service
gcloud run services describe service-name --region=europe-north1

# Get service URL
gcloud run services describe service-name \
  --region=europe-north1 \
  --format="value(status.url)"

# Get current image
gcloud run services describe service-name \
  --region=europe-north1 \
  --format="value(spec.template.spec.containers[0].image)"

# View logs
gcloud logs read --project=project-id --resource-name=service-name
```

### Traffic Management
```bash
# Split traffic between revisions
gcloud run services update-traffic service-name \
  --region=europe-north1 \
  --to-revisions=revision1=50,revision2=50

# Route all traffic to latest
gcloud run services update-traffic service-name \
  --region=europe-north1 \
  --to-latest
```

## Container Registry Commands

### Registry Management
```bash
# List images in registry
gcloud container images list --repository=gcr.io/project-id

# List tags for specific image
gcloud container images list-tags gcr.io/project-id/image-name

# Delete image
gcloud container images delete gcr.io/project-id/image-name:tag

# Authenticate Docker with GCR
gcloud auth configure-docker
```

## Terraform Commands (Infrastructure)

### Basic Operations
```bash
# Initialize Terraform
terraform init

# Plan changes
terraform plan

# Apply changes
terraform apply

# Apply without prompt
terraform apply -auto-approve

# Destroy resources
terraform destroy

# Import existing resource
terraform import resource_name resource_id
```

### State Management
```bash
# Show current state
terraform show

# List resources in state
terraform state list

# Remove resource from state
terraform state rm resource_name

# Refresh state
terraform refresh
```

## Docker Compose (Local Development)

### Basic Commands
```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Build and start
docker-compose up --build

# Stop services
docker-compose down

# View logs
docker-compose logs service-name

# Execute command in running container
docker-compose exec service-name bash
```

## Makefile Integration

Our project uses Makefile for simplified commands:

```bash
# Development
make quick-start        # Complete setup and start all services
make dev-full          # Start full containerized environment
make api-dev           # API with hot reload
make web-dev           # React admin interface

# Code Quality
make lint              # All linters
make format            # Auto-format all code
make test              # All tests

# Database
make neo4j-init        # Initialize Neo4j schema
make seed-db           # Populate with sample data
```

## Common Workflows

### 1. Deploy New Version
```bash
# Build image
docker buildx build --platform linux/amd64 -t gcr.io/living-twin-aprio/app:latest apps/app

# Push to registry
docker push gcr.io/living-twin-aprio/app:latest

# Deploy to Cloud Run
gcloud run deploy app-service \
  --image gcr.io/living-twin-aprio/app:latest \
  --region=europe-north1
```

### 2. Debug Deployment Issues
```bash
# Check service status
gcloud run services describe service-name --region=europe-north1

# View recent logs
gcloud logs read --project=living-twin-aprio --limit=50

# Test locally first
docker run -p 8080:8000 gcr.io/living-twin-aprio/app:latest
```

### 3. Rollback Deployment
```bash
# List revisions
gcloud run revisions list --service=service-name --region=europe-north1

# Route traffic to previous revision
gcloud run services update-traffic service-name \
  --region=europe-north1 \
  --to-revisions=previous-revision=100
```

## Environment Variables

### Common Environment Variables
```bash
# Production settings
ENVIRONMENT=production
PORT=8000

# Database connections
NEO4J_URI=bolt://neo4j:7687
REDIS_HOST=10.142.223.195
REDIS_PORT=6379

# Google Cloud
PROJECT_ID=living-twin-aprio
REGION=europe-north1
```

### Set Environment Variables in Cloud Run
```bash
gcloud run services update service-name \
  --region=europe-north1 \
  --set-env-vars="ENV=production,DEBUG=false"

# Or during deployment
gcloud run deploy service-name \
  --image gcr.io/project-id/image:tag \
  --region=europe-north1 \
  --set-env-vars="KEY1=value1,KEY2=value2"
```

## Troubleshooting

### Common Issues
1. **Architecture mismatch**: Always use `--platform linux/amd64` for Cloud Run
2. **Port binding**: Ensure container listens on `0.0.0.0:$PORT`
3. **Health checks**: Implement `/health` endpoint for monitoring
4. **Permissions**: Use `--allow-unauthenticated` for public services

### Debug Commands
```bash
# Test container locally
docker run -p 8080:8000 -e PORT=8000 image:tag

# Check container logs
docker logs container-id

# Enter running container
docker exec -it container-id bash

# Check Cloud Run logs
gcloud logs tail --resource-name=service-name
```
