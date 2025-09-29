# Shared Configuration

This project uses a centralized configuration system to ensure all components (API, frontend, workflows) agree on the same settings.

## Configuration File

The main configuration is stored in `shared-config.json` at the project root:

```json
{
  "tenant": {
    "id": "globex-industrial-group",
    "name": "Globex Industrial Group",
    "tagline": "Innovating Tomorrow's Infrastructure",
    "description": "A leading multinational manufacturer of advanced equipment and solutions for heavy industry and infrastructure"
  },
  "storage": {
    "bucket_name": "documents",
    "structure": "tenant-id/filename",
    "endpoint": "http://localhost:9000"
  },
  "api": {
    "port": 7001,
    "base_url": "http://localhost:7001"
  },
  "frontend": {
    "port": 3000,
    "base_url": "http://localhost:3000"
  },
  "temporal": {
    "host": "localhost",
    "port": 7233,
    "task_queue": "doc-ingest-q",
    "workflow_name": "DocIngestWorkflow"
  },
  "minio": {
    "endpoint": "http://localhost:9000",
    "console_endpoint": "http://localhost:9001",
    "access_key": "minio",
    "secret_key": "minio12345",
    "bucket": "documents"
  }
}
```

## Component Usage

### API (`api/config.py`)
- Loads `shared-config.json`
- Provides fallback to environment variables
- Exports commonly used values like `TENANT_ID`, `BUCKET_NAME`, etc.

### Frontend (`frontend/src/config/shared.ts`)
- TypeScript interface matching the JSON structure
- Exports `TENANT_ID`, `API_BASE_URL`, `MINIO_CONSOLE_URL`
- Used by API service and upload hooks

### Workflows (`workflows/config.py`)
- Loads `shared-config.json`
- Provides fallback to environment variables
- Used by worker and workflow definitions

## File Storage Structure

Files are stored in MinIO with the following structure:
```
documents/
├── globex-industrial-group/
│   ├── uuid1-filename1.pdf
│   ├── uuid2-filename2.pdf
│   └── ...
└── other-tenant/
    ├── uuid3-filename3.pdf
    └── ...
```

## Environment Variables (Fallback)

If `shared-config.json` is not found, components fall back to environment variables:

- `TENANT_ID` → tenant.id
- `S3_BUCKET` → storage.bucket_name
- `S3_ENDPOINT` → minio.endpoint
- `S3_ACCESS_KEY` → minio.access_key
- `S3_SECRET_KEY` → minio.secret_key
- `TEMPORAL_HOST` → temporal.host
- `TEMPORAL_PORT` → temporal.port
- `TASK_QUEUE` → temporal.task_queue
- `WORKFLOW_NAME` → temporal.workflow_name

## Benefits

1. **Single Source of Truth**: All configuration in one place
2. **Type Safety**: TypeScript interfaces ensure consistency
3. **Environment Flexibility**: Can override with environment variables
4. **Easy Updates**: Change tenant ID or endpoints in one place
5. **Documentation**: Clear structure and purpose of each setting
