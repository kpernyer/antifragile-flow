# Pub/Sub Event System Architecture

This document describes the comprehensive, tenant-safe event-driven architecture implemented in the Living Twin monorepo.

## 🏗️ Architecture Overview

The event system provides:

- **Tenant-safe event distribution** with filtering
- **Idempotency** to prevent duplicate processing
- **Dead Letter Queues (DLQ)** for failed messages
- **Retry policies** with exponential backoff
- **Cloud Run job workers** for scalable processing
- **Event correlation** and tracing

## 📋 Event Types

### Document Events

- `document.ingested` - Document successfully ingested
- `document.updated` - Document content updated
- `document.deleted` - Document removed

### Query Events

- `query.executed` - Query successfully processed
- `query.failed` - Query processing failed

### User Events

- `user.registered` - New user registration
- `user.login` - User authentication

### Organization Events

- `organization.created` - New organization setup
- `organization.updated` - Organization settings changed

### System Events

- `system.error` - System-level errors
- `system.health_check` - Health monitoring

## 🔧 Infrastructure Components

### Topics Structure

```bash
living-twin-events              # Main events topic
living-twin-document-events     # Document-specific events
living-twin-query-events        # Query-specific events
living-twin-user-events         # User-specific events
living-twin-system-events       # System-specific events
```

### Dead Letter Queue Topics

```bash
living-twin-events-dlq
living-twin-document-events-dlq
living-twin-query-events-dlq
living-twin-user-events-dlq
living-twin-system-events-dlq
```

### Tenant-Specific Subscriptions

```bash
{topic-name}-{tenant-id}-worker
{topic-name}-{tenant-id}-dlq
```

## 🛡️ Tenant Safety

### Message Filtering

- All messages include `tenant_id` attribute
- Subscriptions use filter expressions: `attributes.tenant_id = "tenant-123"`
- Workers verify tenant isolation before processing

### Idempotency

- Each event has unique `idempotency_key`
- Generated from: `{event_type}:{tenant_id}:{event_id}`
- Prevents duplicate processing across retries

### Security Best Practices

- Service accounts with minimal required permissions
- Tenant-specific worker instances
- Message encryption in transit

## 📊 Event Flow

### 1. Event Publishing

```python
from app.domain.events import EventFactory
from app.adapters.pubsub_bus import PubSubBusAdapter

# Create event
event = EventFactory.create_document_ingested(
    tenant_id="tenant-123",
    document_id="doc-456",
    document_title="Important Document",
    document_type="pdf",
    user_id="user-789"
)

# Publish event
pubsub = PubSubBusAdapter(project_id="your-project")
message_id = await pubsub.publish_domain_event(event)
```

### 2. Event Processing

```python
# Worker processes events with idempotency
async def process_event(event: DomainEvent) -> bool:
    try:
        # Business logic here
        logger.info(f"Processing {event.event_type} for tenant {event.tenant_id}")

        # Return True for successful processing
        return True
    except Exception as e:
        logger.error(f"Error processing event: {e}")
        # Return False to trigger retry
        return False
```

### 3. Retry and DLQ Handling

- **Initial retry**: Exponential backoff (10s to 600s)
- **Max delivery attempts**: 5
- **DLQ routing**: Failed messages after max attempts
- **Manual recovery**: DLQ messages can be reprocessed

## 🚀 Deployment

### Infrastructure Setup

```bash
# Deploy Pub/Sub infrastructure
make tf-apply-staging

# Build and push worker container
make build-worker
make push-worker
```

### Worker Deployment

```bash
# Deploy Cloud Run job for tenant
gcloud run jobs execute twin-event-worker \
  --region europe-west1 \
  --set-env-vars TENANT_ID=tenant-123
```

### Monitoring

```bash
# View worker logs
gcloud logs tail --follow \
  --filter="resource.type=cloud_run_job"

# Monitor Pub/Sub metrics
gcloud monitoring dashboards list
```

## 📈 Scaling and Performance

### Horizontal Scaling

- **Per-tenant workers**: Isolated processing
- **Concurrent messages**: Configurable flow control
- **Auto-scaling**: Cloud Run jobs scale to zero

### Performance Tuning

- **Batch processing**: Process multiple events together
- **Ack deadline**: 10 minutes for complex processing
- **Flow control**: Max 5-10 concurrent messages per worker

### Cost Optimization

- **Message retention**: 7 days
- **Idle scaling**: Workers scale to zero when idle
- **Resource limits**: 1 CPU, 2GB RAM per worker

## 🔍 Monitoring and Observability

### Metrics

- Message publish rate per tenant
- Processing latency per event type
- Error rates and DLQ message counts
- Worker resource utilization

### Logging

- Structured JSON logs with correlation IDs
- Event processing traces
- Error details with stack traces
- Performance metrics

### Alerting

- DLQ message accumulation
- Worker processing failures
- High latency events
- Resource exhaustion

## 🛠️ Development and Testing

### Local Development

```bash
# Start local development with Pub/Sub emulator
make dev-full

# Test event publishing
curl -X POST http://localhost:8000/test/publish-event \
  -H "Content-Type: application/json" \
  -d '{"event_type": "document.ingested", "tenant_id": "test-tenant"}'
```

### Testing Events

```python
# Unit test event creation
def test_document_ingested_event():
    event = EventFactory.create_document_ingested(
        tenant_id="test-tenant",
        document_id="test-doc",
        document_title="Test Document",
        document_type="txt"
    )

    assert event.tenant_id == "test-tenant"
    assert event.event_type == EventType.DOCUMENT_INGESTED
    assert event.idempotency_key is not None
```

### Integration Testing

```bash
# Test full event flow
python -m pytest tests/integration/test_event_flow.py -v
```

## 🔧 Configuration

### Environment Variables

```bash
# Pub/Sub Configuration
GCP_PROJECT_ID=your-project-id
PUBSUB_ENABLE_DLQ=true

# Worker Configuration
TENANT_ID=tenant-123
MAX_CONCURRENT_MESSAGES=5
WORKER_TIMEOUT=3600

# Monitoring
LOG_LEVEL=INFO
ENABLE_METRICS=true
```

### Terraform Variables

```hcl
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "europe-west1"
}

variable "enable_dlq" {
  description = "Enable Dead Letter Queues"
  type        = bool
  default     = true
}
```

## 🚨 Error Handling

### Common Issues

1. **Tenant mismatch**: Worker receives wrong tenant's events
2. **Idempotency failures**: Duplicate processing detection
3. **DLQ accumulation**: Messages failing repeatedly
4. **Worker timeouts**: Long-running processing

### Resolution Strategies

1. **Verify filters**: Check subscription filter expressions
2. **Check idempotency**: Review key generation and storage
3. **Analyze DLQ**: Investigate failed message patterns
4. **Optimize processing**: Reduce worker processing time

## 📚 Best Practices

### Event Design

- **Immutable events**: Never modify published events
- **Rich context**: Include all necessary data in event
- **Versioning**: Plan for event schema evolution
- **Correlation**: Use correlation IDs for tracing

### Processing

- **Idempotent handlers**: Safe to process multiple times
- **Fast processing**: Keep handlers lightweight
- **Error handling**: Distinguish retryable vs. permanent errors
- **Monitoring**: Log all processing attempts

### Security

- **Least privilege**: Minimal IAM permissions
- **Tenant isolation**: Strict tenant boundary enforcement
- **Audit logging**: Track all event processing
- **Encryption**: Encrypt sensitive event data

## 🔄 Migration and Rollback

### Schema Evolution

```python
# Handle event version compatibility
def process_event(event: DomainEvent) -> bool:
    if event.data.get('version', '1.0') == '1.0':
        return process_v1_event(event)
    elif event.data.get('version') == '2.0':
        return process_v2_event(event)
    else:
        logger.warning(f"Unknown event version: {event.data.get('version')}")
        return True  # Ack unknown versions
```

### Rollback Strategy

1. **Stop new deployments**
2. **Drain existing messages**
3. **Deploy previous version**
4. **Resume processing**

This event system provides a robust, scalable foundation for the Living Twin platform's event-driven architecture with strong tenant isolation and reliability guarantees.
