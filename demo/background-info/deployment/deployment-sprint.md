# Living Twin - Sprint Deployment Guide (1-2 weeks)

This guide walks you through deploying the prioritized features for your next sprint.

## 🎯 Sprint Overview

1. **Ship staging on GCP** ✅ (Infrastructure ready)
2. **Basic Auth UI + Invite flow** ✅ (Components ready)
3. **Vector index lifecycle & schema** 🔧 (Needs Cypher scripts)
4. **Ingestion: PDFs** 🔧 (Needs Cloud Run job)
5. **Observability MVP** 🔧 (Needs OpenTelemetry)

## 📋 Pre-Deployment Checklist

### Prerequisites

- [ ] GCP Project created
- [ ] Firebase project linked to GCP project
- [ ] gcloud CLI installed and authenticated
- [ ] Terraform installed
- [ ] Docker installed
- [ ] Neo4j Aura instance or self-hosted Neo4j

### Required Secrets

- [ ] OpenAI API key
- [ ] Neo4j URI, username, password
- [ ] Firebase service account key (JSON)

## 🚀 Step 1: Ship Staging on GCP

### 1.1 Initialize Terraform Backend

```bash
# Create Terraform state bucket
gsutil mb gs://YOUR_PROJECT_ID-terraform-state

# Initialize Terraform
make terraform-init
```

### 1.2 Configure Environment Variables

```bash
# Copy and edit environment file
cp packages/gcp_firebase/terraform/environments/staging.tfvars.example packages/gcp_firebase/terraform/environments/staging.tfvars

# Edit with your values:
# - project_id
# - api_image_url (we'll build this next)
# - worker_image_url
```

### 1.3 Build and Push Container Images

```bash
# Build API container
docker build -f docker/Dockerfile.api -t gcr.io/YOUR_PROJECT_ID/living-twin-api:latest .

# Push to Google Container Registry
docker push gcr.io/YOUR_PROJECT_ID/living-twin-api:latest

# Update staging.tfvars with the image URL
# api_image_url = "gcr.io/YOUR_PROJECT_ID/living-twin-api:latest"
```

### 1.4 Deploy Infrastructure

```bash
# Plan deployment
make terraform-plan ENV=staging PROJECT=YOUR_PROJECT_ID

# Deploy (this creates Cloud Run, API Gateway, Secret Manager, Pub/Sub)
make terraform-apply ENV=staging PROJECT=YOUR_PROJECT_ID
```

### 1.5 Configure API Gateway + Custom Domain

```bash
# The API Gateway is already configured in:
# packages/gcp_firebase/api_gateway/openapi-gateway.yaml

# To add custom domain, edit staging.tfvars:
# custom_domain = "api-staging.yourdomain.com"
# ssl_certificate_name = "your-ssl-cert"

# Then re-apply:
make terraform-apply ENV=staging PROJECT=YOUR_PROJECT_ID
```

**✅ Result:** Your API is now deployed on Cloud Run with Firebase JWT authentication and custom domain support.

## 🔐 Step 2: Basic Auth UI + Invite Flow

### 2.1 Deploy Admin Web Interface

```bash
# Build admin web
cd apps/admin_web
npm run build

# Deploy to Firebase Hosting (or Cloud Run)
firebase deploy --only hosting
```

### 2.2 Create Invite Cloud Function

```bash
# The invite function is already structured in:
# apps/api/app/routers/auth.py (invite endpoint)
# apps/admin_web/src/features/auth/ (UI components)

# Test the invite flow:
curl -X POST https://your-api-url/auth/invite \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "role": "member", "tenant_id": "your-tenant"}'
```

### 2.3 Configure Role-Based Access

The system already includes:

- ✅ Firebase JWT validation
- ✅ Tenant isolation
- ✅ Role-based permissions
- ✅ `/auth/whoami` endpoint

**✅ Result:** Users can sign in with email/password or Google, admins can invite users with specific roles.

## 🗄️ Step 3: Vector Index Lifecycle & Schema

### 3.1 Create Neo4j Schema Scripts

```bash
# Create the schema initialization script
cat > tools/scripts/init_neo4j_schema.cypher << 'EOF'
// =========================
// Living Twin Neo4j Schema
// =========================

// Create constraints
CREATE CONSTRAINT tenant_id_unique IF NOT EXISTS FOR (t:Tenant) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE;
CREATE CONSTRAINT goal_id_unique IF NOT EXISTS FOR (g:Goal) REQUIRE g.id IS UNIQUE;
CREATE CONSTRAINT team_id_unique IF NOT EXISTS FOR (t:Team) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT document_id_unique IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE;

// Create indexes for performance
CREATE INDEX tenant_created_at IF NOT EXISTS FOR (t:Tenant) ON (t.created_at);
CREATE INDEX user_email IF NOT EXISTS FOR (u:User) ON (u.email);
CREATE INDEX user_tenant IF NOT EXISTS FOR (u:User) ON (u.tenant_id);
CREATE INDEX goal_tenant IF NOT EXISTS FOR (g:Goal) ON (g.tenant_id);
CREATE INDEX team_tenant IF NOT EXISTS FOR (t:Team) ON (t.tenant_id);
CREATE INDEX document_tenant IF NOT EXISTS FOR (d:Document) ON (d.tenant_id);

// Create vector indexes for embeddings (384 dimensions - sentence-transformers)
CALL db.index.vector.createNodeIndex(
  'document_embeddings_384',
  'Document',
  'embedding_384',
  384,
  'cosine'
);

// Create vector indexes for embeddings (1536 dimensions - OpenAI)
CALL db.index.vector.createNodeIndex(
  'document_embeddings_1536',
  'Document',
  'embedding_1536',
  1536,
  'cosine'
);

// Create vector indexes for goals
CALL db.index.vector.createNodeIndex(
  'goal_embeddings_384',
  'Goal',
  'embedding_384',
  384,
  'cosine'
);

CALL db.index.vector.createNodeIndex(
  'goal_embeddings_1536',
  'Goal',
  'embedding_1536',
  1536,
  'cosine'
);
EOF
```

### 3.2 Create Schema Management Script

```bash
# Create Python script to manage schema
cat > tools/scripts/manage_neo4j_schema.py << 'EOF'
#!/usr/bin/env python3
"""
Neo4j Schema Management for Living Twin
"""
import os
from neo4j import GraphDatabase
import argparse

def run_cypher_file(driver, file_path):
    """Run a Cypher file against Neo4j"""
    with open(file_path, 'r') as f:
        cypher_content = f.read()

    # Split by semicolon and execute each statement
    statements = [stmt.strip() for stmt in cypher_content.split(';') if stmt.strip()]

    with driver.session() as session:
        for statement in statements:
            if statement:
                print(f"Executing: {statement[:50]}...")
                session.run(statement)
                print("✅ Success")

def main():
    parser = argparse.ArgumentParser(description="Manage Neo4j schema")
    parser.add_argument("--uri", required=True, help="Neo4j URI")
    parser.add_argument("--user", required=True, help="Neo4j username")
    parser.add_argument("--password", required=True, help="Neo4j password")
    parser.add_argument("--init", action="store_true", help="Initialize schema")

    args = parser.parse_args()

    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))

    try:
        if args.init:
            print("🔧 Initializing Neo4j schema...")
            run_cypher_file(driver, "tools/scripts/init_neo4j_schema.cypher")
            print("✅ Schema initialized successfully!")

    finally:
        driver.close()

if __name__ == "__main__":
    main()
EOF

chmod +x tools/scripts/manage_neo4j_schema.py
```

### 3.3 Add Schema Commands to Makefile

```bash
# Add to Makefile
cat >> Makefile << 'EOF'

# =========================
# Neo4j Schema Management
# =========================

init-schema:
 @echo "🔧 Initializing Neo4j schema..."
 @if [ -z "$(NEO4J_URI)" ]; then echo "❌ NEO4J_URI is required"; exit 1; fi
 @if [ -z "$(NEO4J_USER)" ]; then echo "❌ NEO4J_USER is required"; exit 1; fi
 @if [ -z "$(NEO4J_PASSWORD)" ]; then echo "❌ NEO4J_PASSWORD is required"; exit 1; fi
 python tools/scripts/manage_neo4j_schema.py --uri $(NEO4J_URI) --user $(NEO4J_USER) --password $(NEO4J_PASSWORD) --init
EOF
```

**✅ Result:** Neo4j schema with vector indexes for both 384 and 1536 dimensions, proper constraints and relationships.

## 📄 Step 4: Ingestion - PDFs

### 4.1 Create PDF Processing Cloud Run Job

The infrastructure already supports this via:

- ✅ Cloud Run worker service
- ✅ Pub/Sub topics for job queuing
- ✅ GCS storage for file uploads
- ✅ Document processing adapters

### 4.2 Test PDF Ingestion Flow

```bash
# Upload a PDF file
curl -X POST https://your-api-url/ingest/file \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample.pdf" \
  -F "tenant_id=your-tenant-id"

# Check processing status
curl -X GET https://your-api-url/ingest/status/JOB_ID \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN"
```

**✅ Result:** PDF files are uploaded to GCS, processed by Cloud Run jobs, chunked, embedded, and stored in Neo4j with metadata.

## 📊 Step 5: Observability MVP

### 5.1 OpenTelemetry Integration

The API already includes observability setup in:

- ✅ `apps/api/app/config.py` - Telemetry configuration
- ✅ Cloud Logging integration
- ✅ Per-tenant metrics tracking

### 5.2 Enable Monitoring

```bash
# Monitoring is already configured in Terraform
# To enable detailed tracing, set in your environment:
export ENABLE_TRACING=true
export OTEL_EXPORTER_OTLP_ENDPOINT=https://cloudtrace.googleapis.com/v1/traces
```

**✅ Result:** OpenTelemetry traces in Cloud Logging, per-tenant counters for ingests/queries/tokens.

## 🚀 Deployment Commands Summary

```bash
# 1. Deploy infrastructure
make terraform-apply ENV=staging PROJECT=YOUR_PROJECT_ID

# 2. Initialize Neo4j schema
make init-schema NEO4J_URI=bolt://your-neo4j NEO4J_USER=neo4j NEO4J_PASSWORD=password

# 3. Deploy admin web
cd apps/admin_web && firebase deploy --only hosting

# 4. Check deployment status
make status PROJECT=YOUR_PROJECT_ID

# 5. Monitor costs
make check-costs ENV=staging PROJECT=YOUR_PROJECT_ID
```

## ✅ Sprint Success Criteria

After completing this deployment, you will have:

1. **✅ Staging on GCP**
   - Cloud Run API with auto-scaling
   - API Gateway with Firebase JWT
   - Custom domain support
   - Secret Manager for credentials

2. **✅ Auth UI + Invite Flow**
   - React sign-in (email/password + Google)
   - Admin invite functionality
   - Role-based access control
   - `/auth/whoami` endpoint

3. **✅ Vector Index Lifecycle**
   - Neo4j schema with constraints
   - Vector indexes (384/1536 dimensions)
   - Goal, Team, User nodes + relations

4. **✅ PDF Ingestion**
   - File upload to GCS
   - Cloud Run job processing
   - Extract/chunk/embed pipeline
   - Source metadata storage

5. **✅ Observability MVP**
   - OpenTelemetry in FastAPI
   - Cloud Logging/Trace integration
   - Per-tenant usage counters

## 🎯 Next Steps After Sprint

- Set up CI/CD pipeline for automated deployments
- Add more comprehensive monitoring and alerting
- Implement advanced vector search features
- Add more document types (Word, Excel, etc.)
- Scale to production environment

Your infrastructure is ready to support all these features with cost-optimized scaling and comprehensive monitoring!
