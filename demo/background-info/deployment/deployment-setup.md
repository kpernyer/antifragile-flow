# Living Twin - Cloud Run Deployment Setup Guide

This guide provides step-by-step instructions to set up automated deployment to Google Cloud Run using GitHub Actions.

## 🚀 **Ready-to-Use Files**

### **1. Cloud Run Dockerfile** (`docker/Dockerfile.cloudrun`)

✅ **Multi-stage build** for optimized image size
✅ **Production-ready** with gunicorn + uvicorn workers
✅ **Security hardened** with non-root user
✅ **Health checks** for Cloud Run
✅ **Environment variable** support for PORT

### **2. GitHub Actions Workflow** (`.github/workflows/deploy-cloud-run.yml`)

✅ **Automated testing** (linting, type checking, unit tests)
✅ **Multi-environment** deployment (staging/production)
✅ **Security scanning** with Trivy
✅ **Performance testing** with k6 load tests
✅ **Notifications** for deployment status
✅ **Workload Identity** for secure GCP authentication

## 🔧 **Setup Instructions**

### **Step 1: Google Cloud Setup**

1. **Create or select a GCP project:**

   ```bash
   gcloud projects create living-twin-prod --name="Living Twin Production"
   gcloud config set project living-twin-prod
   ```

2. **Enable required APIs:**

   ```bash
   gcloud services enable \
     cloudbuild.googleapis.com \
     run.googleapis.com \
     artifactregistry.googleapis.com \
     secretmanager.googleapis.com \
     apigateway.googleapis.com
   ```

3. **Create Artifact Registry repository:**

   ```bash
   gcloud artifacts repositories create living-twin \
     --repository-format=docker \
     --location=us-central1 \
     --description="Living Twin Docker images"
   ```

### **Step 2: Service Account Setup**

1. **Create service account for Cloud Run:**

   ```bash
   gcloud iam service-accounts create living-twin-cloudrun \
     --display-name="Living Twin Cloud Run Service Account"
   ```

2. **Grant necessary permissions:**

   ```bash
   # Cloud Run service account permissions
   gcloud projects add-iam-policy-binding living-twin-prod \
     --member="serviceAccount:living-twin-cloudrun@living-twin-prod.iam.gserviceaccount.com" \
     --role="roles/secretmanager.secretAccessor"

   gcloud projects add-iam-policy-binding living-twin-prod \
     --member="serviceAccount:living-twin-cloudrun@living-twin-prod.iam.gserviceaccount.com" \
     --role="roles/cloudsql.client"
   ```

### **Step 3: Workload Identity Setup**

1. **Create service account for GitHub Actions:**

   ```bash
   gcloud iam service-accounts create github-actions \
     --display-name="GitHub Actions Service Account"
   ```

2. **Grant deployment permissions:**

   ```bash
   gcloud projects add-iam-policy-binding living-twin-prod \
     --member="serviceAccount:github-actions@living-twin-prod.iam.gserviceaccount.com" \
     --role="roles/run.admin"

   gcloud projects add-iam-policy-binding living-twin-prod \
     --member="serviceAccount:github-actions@living-twin-prod.iam.gserviceaccount.com" \
     --role="roles/artifactregistry.admin"

   gcloud projects add-iam-policy-binding living-twin-prod \
     --member="serviceAccount:github-actions@living-twin-prod.iam.gserviceaccount.com" \
     --role="roles/iam.serviceAccountUser"
   ```

3. **Create Workload Identity Pool:**

   ```bash
   gcloud iam workload-identity-pools create "github-pool" \
     --location="global" \
     --display-name="GitHub Actions Pool"

   gcloud iam workload-identity-pools providers create-oidc "github-provider" \
     --location="global" \
     --workload-identity-pool="github-pool" \
     --display-name="GitHub Actions Provider" \
     --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
     --issuer-uri="https://token.actions.githubusercontent.com"
   ```

4. **Bind service account to Workload Identity:**

   ```bash
   gcloud iam service-accounts add-iam-policy-binding \
     --role roles/iam.workloadIdentityUser \
     --member "principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/YOUR_GITHUB_USERNAME/living_twin_monorepo" \
     github-actions@living-twin-prod.iam.gserviceaccount.com
   ```

### **Step 4: Secret Manager Setup**

Create secrets for your application:

```bash
# Neo4j connection
echo -n "neo4j+s://your-neo4j-instance.databases.neo4j.io" | \
  gcloud secrets create neo4j-uri --data-file=-

echo -n "neo4j" | \
  gcloud secrets create neo4j-user --data-file=-

echo -n "your-neo4j-password" | \
  gcloud secrets create neo4j-password --data-file=-

# OpenAI API Key
echo -n "sk-your-openai-api-key" | \
  gcloud secrets create openai-api-key --data-file=-

# Firebase Project ID
echo -n "your-firebase-project-id" | \
  gcloud secrets create firebase-project-id --data-file=-
```

### **Step 5: GitHub Repository Secrets**

Add these secrets to your GitHub repository (`Settings > Secrets and variables > Actions`):

#### **Required Secrets:**

```bash
GCP_PROJECT_ID=living-twin-prod
WIF_PROVIDER=projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/providers/github-provider
WIF_SERVICE_ACCOUNT=github-actions@living-twin-prod.iam.gserviceaccount.com
CLOUD_RUN_SERVICE_ACCOUNT=living-twin-cloudrun@living-twin-prod.iam.gserviceaccount.com
```

#### **Optional Secrets (for notifications):**

```bash
NOTIFICATION_WEBHOOK_URL=https://hooks.example.com/services/YOUR/WEBHOOK
```

### **Step 6: Get Project Number**

```bash
gcloud projects describe living-twin-prod --format="value(projectNumber)"
```

Replace `PROJECT_NUMBER` in the WIF_PROVIDER secret with this value.

## 🎯 **Deployment Workflow**

### **Automatic Deployments:**

- **Staging:** Push to `staging` branch → deploys to `living-twin-api-staging`
- **Production:** Push to `main` branch → deploys to `living-twin-api`

### **Manual Deployment:**

```bash
# Build and push manually
docker build -f docker/Dockerfile.cloudrun -t gcr.io/living-twin-prod/living-twin-api:latest .
docker push gcr.io/living-twin-prod/living-twin-api:latest

# Deploy manually
gcloud run deploy living-twin-api \
  --image gcr.io/living-twin-prod/living-twin-api:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated
```

## 🔍 **Monitoring & Debugging**

### **View Logs:**

```bash
# Cloud Run logs
gcloud logs read --service=living-twin-api --limit=50

# Build logs
gcloud builds list --limit=10
gcloud builds log BUILD_ID
```

### **Health Check:**

```bash
curl https://your-service-url.a.run.app/healthz
```

### **Performance Testing:**

```bash
# Run load tests locally
k6 run tools/scripts/load-test.js
```

## 🚨 **Security Considerations**

### **✅ Implemented Security Features:**

- **Workload Identity** - No service account keys stored in GitHub
- **Secret Manager** - Sensitive data encrypted at rest
- **Non-root containers** - Reduced attack surface
- **Vulnerability scanning** - Trivy scans on every build
- **Least privilege** - Minimal IAM permissions
- **HTTPS only** - Cloud Run enforces TLS

### **🔒 Additional Security Recommendations:**

1. **Enable VPC Connector** for private network access
2. **Set up Cloud Armor** for DDoS protection
3. **Configure Binary Authorization** for image verification
4. **Enable Audit Logs** for compliance
5. **Set up Monitoring Alerts** for anomalies

## 📊 **Cost Optimization**

### **Current Configuration:**

- **CPU:** 2 vCPU (scales to zero when idle)
- **Memory:** 2GB
- **Min instances:** 0 (saves costs during low traffic)
- **Max instances:** 10 (prevents runaway costs)
- **Concurrency:** 80 requests per instance

### **Cost Estimates (US-Central1):**

- **Idle:** $0/month (scales to zero)
- **Light usage:** ~$10-30/month
- **Production load:** ~$50-200/month

## 🎉 **Ready to Deploy!**

Your deployment pipeline is now configured with:

✅ **Production-ready Dockerfile** with multi-stage builds
✅ **Automated CI/CD** with testing and security scanning
✅ **Multi-environment** support (staging/production)
✅ **Performance monitoring** with load tests
✅ **Security hardening** with Workload Identity
✅ **Cost optimization** with auto-scaling
✅ **Monitoring & alerting** with notifications

**Next Steps:**

1. Push your code to the `staging` branch to test deployment
2. Verify the staging environment works correctly
3. Merge to `main` branch for production deployment
4. Monitor logs and metrics in Google Cloud Console

🚀 **Your Living Twin API is ready for production deployment!**
