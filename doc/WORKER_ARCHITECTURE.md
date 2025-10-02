# Three-Worker Temporal Architecture

## Overview

The Antifragile Flow application has been restructured to use a **three-worker architecture** to optimize resource usage, enable independent scaling, and improve cost management.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Temporal Server                          │
│                      (Workflow Orchestration)                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Task Routing
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        v                     v                     v
┌───────────────┐     ┌───────────────┐    ┌──────────────┐
│ Default Worker│     │   ML Worker   │    │OpenAI Worker │
│ (default-queue)│    │  (ml-queue)   │    │(openai-queue)│
└───────────────┘     └───────────────┘    └──────────────┘
        │                     │                     │
        v                     v                     v
┌───────────────┐     ┌───────────────┐    ┌──────────────┐
│   General     │     │  ML Training  │    │  OpenAI API  │
│  Activities   │     │  Activities   │    │  Activities  │
└───────────────┘     └───────────────┘    └──────────────┘
        │                     │                     │
        v                     v                     v
┌───────────────┐     ┌───────────────┐    ┌──────────────┐
│   Services    │     │     PyTorch   │    │   GPT-4 API  │
│   (DB, S3)    │     │Transformers   │    │  (Remote)    │
└───────────────┘     └───────────────┘    └──────────────┘
```

## Worker Specifications

### 1. Default Worker
**File:** `worker/default_worker.py`
**Queue:** `default-queue`
**Purpose:** Handles general-purpose activities

#### Responsibilities
- Document processing (extraction, parsing)
- System activities (health checks, cleanup)
- Scheduler activities
- Storage operations
- Training job management (delegation)

#### Activities
- `process_document_upload`
- `cleanup_old_data`
- `health_check_external_services`
- `schedule_competitor_scan`
- `send_scheduled_notification`
- `submit_model_training_job`
- `check_training_job_status`
- `get_organization_training_history`
- `cancel_training_job`
- `collect_model_feedback`
- `start_model_improvement`
- `validate_training_readiness`

#### Resource Requirements
- Lightweight
- Standard CPU/Memory
- Database connections
- S3 access

### 2. ML Worker
**File:** `worker/ml_worker.py`
**Queue:** `ml-queue`
**Purpose:** Handles machine learning training activities

#### Responsibilities
- LoRA fine-tuning of local models
- Model training on Mistral-7B and Qwen-3B
- ML model testing and evaluation

#### Activities
- `train_organizational_model`
- `test_qwen_model`

#### Resource Requirements
- **High Memory:** 16GB+ RAM
- **GPU:** NVIDIA GPU with CUDA (optional but recommended)
- **MPS:** Apple Silicon with MPS support (optional)
- **Dependencies:** PyTorch, Transformers, PEFT, TRL
- **Storage:** Large disk space for model checkpoints

#### Performance
- CPU Training: ~2-4 hours per model
- GPU Training: ~10-30 minutes per model (10-100x faster)
- MPS Training: ~30-60 minutes per model

### 3. OpenAI Worker
**File:** `worker/openai_worker.py`
**Queue:** `openai-queue`
**Purpose:** Handles remote OpenAI API calls

#### Responsibilities
- Document analysis using GPT models
- Research and synthesis activities
- Interactive refinement (catchball)
- Crowd wisdom synthesis

#### Activities
- `analyze_document_content`
- `generate_document_summary`
- `perform_simple_research`
- `run_catchball`
- `synthesize_wisdom`

#### Resource Requirements
- **API Key:** Valid OpenAI API key
- **Network:** Reliable internet connection
- **Dependencies:** Agents framework
- **Rate Limiting:** Consider API rate limits

#### Cost Considerations
- GPT-4: ~$0.03 per 1K tokens input, $0.06 per 1K tokens output
- Typical document analysis: $0.10-$0.50 per document
- Monitor usage via OpenAI dashboard

## Configuration

### Task Queue Configuration
All task queues are defined in `shared/config/defaults.py`:

```python
from shared.config.defaults import (
    DEFAULT_QUEUE,  # "default-queue"
    ML_QUEUE,       # "ml-queue"
    OPENAI_QUEUE,   # "openai-queue"
)
```

### Workflow Task Routing
Workflows automatically route activities to appropriate workers:

```python
# In workflow code
from shared.config.defaults import DEFAULT_QUEUE, ML_QUEUE, OPENAI_QUEUE

# Route to default worker
await workflow.execute_activity(
    process_document_upload,
    file_path,
    task_queue=DEFAULT_QUEUE
)

# Route to ML worker
await workflow.execute_activity(
    train_organizational_model,
    training_request,
    task_queue=ML_QUEUE,
    start_to_close_timeout=timedelta(hours=4)  # ML takes time
)

# Route to OpenAI worker
await workflow.execute_activity(
    analyze_document_content,
    document_info,
    task_queue=OPENAI_QUEUE,
    start_to_close_timeout=timedelta(minutes=5)
)
```

## Deployment

### Development
Start all workers on your local machine:

```bash
# Using the helper script
./worker/start_workers.sh all

# Or manually
python worker/default_worker.py &
python worker/ml_worker.py &
python worker/openai_worker.py &
```

### Production - Docker Compose

```yaml
version: '3.8'
services:
  worker-default:
    build: .
    command: python worker/default_worker.py
    environment:
      - TEMPORAL_ADDRESS=temporal:7233
      - POSTGRES_HOST=postgres
      - REDIS_HOST=redis
    restart: always
    deploy:
      replicas: 3  # Scale for throughput

  worker-ml:
    build: .
    command: python worker/ml_worker.py
    environment:
      - TEMPORAL_ADDRESS=temporal:7233
    restart: always
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
      replicas: 1  # Typically one per GPU

  worker-openai:
    build: .
    command: python worker/openai_worker.py
    environment:
      - TEMPORAL_ADDRESS=temporal:7233
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    restart: always
    deploy:
      replicas: 2  # Scale based on API usage
```

### Production - Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: worker-default
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: worker
        image: antifragile-flow:latest
        command: ["python", "worker/default_worker.py"]
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: worker-ml
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: worker
        image: antifragile-flow:latest
        command: ["python", "worker/ml_worker.py"]
        resources:
          requests:
            memory: "16Gi"
            cpu: "4000m"
          limits:
            nvidia.com/gpu: 1
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: worker-openai
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: worker
        image: antifragile-flow:latest
        command: ["python", "worker/openai_worker.py"]
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: openai-secret
              key: api-key
```

## Benefits

### Resource Optimization
- **Default Worker**: Lightweight, handles 80% of workload
- **ML Worker**: Heavy compute only when needed
- **OpenAI Worker**: Isolated cost monitoring

### Independent Scaling
- Scale default workers for general throughput
- Add ML workers during training campaigns
- Increase OpenAI workers during peak API usage

### Cost Management
- Monitor OpenAI API costs separately
- Control ML compute resource allocation
- Optimize default worker for efficiency

### Fault Isolation
- ML failures don't affect general operations
- API rate limits isolated to OpenAI worker
- Each worker can restart independently

### Development Flexibility
- Developers can run only needed workers locally
- Test ML features without OpenAI API key
- Test OpenAI features without GPU

## Monitoring

### Temporal UI
Monitor each queue separately:
- **Default Queue**: http://localhost:8233 - Check default-queue
- **ML Queue**: http://localhost:8233 - Check ml-queue
- **OpenAI Queue**: http://localhost:8233 - Check openai-queue

### Metrics to Track
- Queue depth per worker type
- Activity execution times
- Failure rates per worker
- Resource utilization (CPU, Memory, GPU)
- API costs (OpenAI worker)

### Alerts
Set up alerts for:
- Queue backlog exceeding threshold
- Worker disconnections
- ML training failures
- OpenAI API rate limit errors
- High API costs

## Migration from Single Worker

### Before (Legacy)
```python
# worker/main_worker.py
worker = Worker(
    client,
    task_queue="hackathon",  # Single queue
    workflows=[...],
    activities=[...]  # All activities
)
```

### After (Three-Worker Architecture)
```python
# worker/default_worker.py
worker = Worker(
    client,
    task_queue="default-queue",
    workflows=[...],
    activities=[general_activities]
)

# worker/ml_worker.py
worker = Worker(
    client,
    task_queue="ml-queue",
    workflows=[],
    activities=[ml_activities]
)

# worker/openai_worker.py
worker = Worker(
    client,
    task_queue="openai-queue",
    workflows=[],
    activities=[openai_activities]
)
```

## Troubleshooting

### Default Worker Issues
- Check database connectivity
- Verify S3 credentials
- Check system resource availability

### ML Worker Issues
- Verify ML dependencies installed: `pip install torch transformers peft trl`
- Check GPU availability: `nvidia-smi` or check MPS support
- Ensure sufficient memory (16GB+)
- Check disk space for model checkpoints

### OpenAI Worker Issues
- Verify `OPENAI_API_KEY` environment variable set
- Check internet connectivity
- Monitor API rate limits
- Check OpenAI account balance

## Future Enhancements

1. **Auto-scaling**: Scale workers based on queue depth
2. **Worker Pools**: Multiple instances of each worker type
3. **Health Checks**: Dedicated health check endpoints
4. **Metrics Export**: Prometheus metrics for monitoring
5. **Distributed Tracing**: OpenTelemetry integration
6. **Priority Queues**: High/low priority task routing
7. **Cost Optimization**: Automatic model switching based on budget

## References

- [Temporal Workers Documentation](https://docs.temporal.io/workers)
- [Task Queue Documentation](https://docs.temporal.io/concepts/what-is-a-task-queue)
- [Worker README](../worker/README.md)
- [Shared Configuration](../shared/config/defaults.py)
