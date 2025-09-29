# S3 Storage Configuration Guide

This guide explains how to configure S3 storage for both local development (MinIO) and production (AWS S3).

## 🏠 Local Development (MinIO)

### Quick Start

1. **Start infrastructure:**
   ```bash
   make infra-up
   ```

2. **MinIO will be available at:**
   - API: http://localhost:9000
   - Console: http://localhost:9001
   - Credentials: `minio` / `minio12345`

3. **Bucket is automatically created:** `documents`

### Configuration

The API automatically uses MinIO when you start with `make dev`. No additional configuration needed.

## ☁️ Production (AWS S3)

### 1. Create S3 Bucket

```bash
# Create bucket
aws s3 mb s3://your-kolomolo-documents --region us-west-2

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket your-kolomolo-documents \
  --versioning-configuration Status=Enabled

# Enable server-side encryption
aws s3api put-bucket-encryption \
  --bucket your-kolomolo-documents \
  --server-side-encryption-configuration '{
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "AES256"
        }
      }
    ]
  }'
```

### 2. Create IAM User/Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:GetObjectVersion"
      ],
      "Resource": "arn:aws:s3:::your-kolomolo-documents/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": "arn:aws:s3:::your-kolomolo-documents"
    }
  ]
}
```

### 3. Environment Configuration

Create `.env` file in the `api/` directory:

```env
# Production S3 Configuration
S3_ENDPOINT_URL=https://s3.amazonaws.com
S3_ACCESS_KEY_ID=your-aws-access-key
S3_SECRET_ACCESS_KEY=your-aws-secret-key
S3_BUCKET_NAME=your-kolomolo-documents
S3_REGION=us-west-2

# Other production settings
TEMPORAL_HOST=your-temporal-host
TEMPORAL_PORT=7233
DATABASE_URL=postgresql://user:pass@your-db-host:5432/kolomolo
```

### 4. Terraform S3 Configuration

The Terraform configuration automatically creates S3 resources:

```hcl
# In terraform/main.tf
module "s3" {
  source = "./modules/s3"

  bucket_name = var.s3_bucket_name
  environment = var.environment

  # Enable versioning and encryption
  versioning_enabled = true
  encryption_enabled = true

  # CORS configuration for web uploads
  cors_rules = [
    {
      allowed_headers = ["*"]
      allowed_methods = ["GET", "PUT", "POST", "DELETE"]
      allowed_origins = ["*"]
      expose_headers  = ["ETag"]
      max_age_seconds = 3000
    }
  ]
}
```

## 🔄 Switching Between Local and Production

### Local Development
```bash
# Uses MinIO automatically
make dev
```

### Production Deployment
```bash
# Set production environment variables
export S3_ENDPOINT_URL=https://s3.amazonaws.com
export S3_ACCESS_KEY_ID=your-production-key
export S3_SECRET_ACCESS_KEY=your-production-secret
export S3_BUCKET_NAME=your-production-bucket

# Deploy with Terraform
cd terraform
terraform apply
```

## 📁 File Organization

Documents are organized in S3 with this structure:

```
your-bucket/
├── tenant-1/
│   ├── 2024/01/15/
│   │   ├── document-1.pdf
│   │   └── document-2.jpg
│   └── 2024/01/16/
│       └── document-3.pdf
└── tenant-2/
    └── 2024/01/15/
        └── document-4.pdf
```

## 🔒 Security Best Practices

### 1. Access Control
- Use IAM roles instead of access keys when possible
- Implement least privilege access
- Rotate access keys regularly

### 2. Encryption
- Enable server-side encryption (SSE-S3 or SSE-KMS)
- Use HTTPS for all API calls
- Consider client-side encryption for sensitive documents

### 3. Monitoring
- Enable CloudTrail for S3 API calls
- Set up CloudWatch alarms for unusual activity
- Monitor access patterns and costs

## 🚨 Troubleshooting

### Common Issues

1. **Access Denied**
   - Check IAM permissions
   - Verify bucket policy
   - Ensure correct region

2. **CORS Errors**
   - Configure CORS policy on bucket
   - Check allowed origins in API

3. **Presigned URL Issues**
   - Verify credentials
   - Check bucket exists
   - Ensure proper permissions

### Debug Commands

```bash
# Test S3 connection
aws s3 ls s3://your-bucket

# Test presigned URL generation
curl -X POST http://localhost:7000/api/v1/upload/presign \
  -H "Content-Type: application/json" \
  -d '{"filename": "test.pdf", "content_type": "application/pdf", "tenant_id": "test"}'
```

## 📊 Monitoring

### Metrics to Track
- Upload/download rates
- Error rates
- Storage usage
- API response times

### Alerts to Set Up
- High error rates
- Unusual access patterns
- Storage quota approaching limits
- Failed uploads
