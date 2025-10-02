# Temporal Workers

This directory contains three specialized Temporal workers for the Antifragile Flow application.

## Three-Worker Architecture

The application uses a three-worker architecture to separate concerns and optimize resource usage:

### 1. Default Worker (`default_worker.py`)
**Queue:** `default-queue`

Handles general-purpose activities that don't require specialized resources:
- Document processing (extraction, parsing)
- System activities (health checks, cleanup)
- Scheduler activities
- Storage operations
- Training service delegation

**Start command:**
```bash
python worker/default_worker.py
```

### 2. ML Worker (`ml_worker.py`)
**Queue:** `ml-queue`

Handles machine learning training activities requiring compute resources:
- LoRA fine-tuning of local models (Mistral-7B, Qwen-3B)
- Model training job management
- ML model testing and evaluation

**Requirements:**
- PyTorch
- Transformers
- PEFT (Parameter-Efficient Fine-Tuning)
- TRL (Transformer Reinforcement Learning)
- GPU/MPS/CPU compute resources

**Start command:**
```bash
python worker/ml_worker.py
```

### 3. OpenAI Worker (`openai_worker.py`)
**Queue:** `openai-queue`

Handles activities that make remote OpenAI API calls:
- Document analysis using GPT models
- Research and synthesis activities
- Catchball interactions
- Wisdom synthesis

**Requirements:**
- OpenAI API key (set `OPENAI_API_KEY` environment variable)
- Agents framework dependencies

**Start command:**
```bash
python worker/openai_worker.py
```

## Starting All Workers

You can start all three workers simultaneously using the provided script:

```bash
# Start all workers in separate terminal windows
make workers

# Or start them individually
python worker/default_worker.py &
python worker/ml_worker.py &
python worker/openai_worker.py &
```

## Architecture Benefits

### Resource Optimization
- **Default Worker**: Lightweight, handles most traffic
- **ML Worker**: Can run on GPU-enabled machines for training
- **OpenAI Worker**: Isolated API rate limiting and cost control

### Scalability
- Scale each worker independently based on load
- Add more ML workers for parallel training jobs
- Add more OpenAI workers during high API usage periods

### Cost Management
- Monitor OpenAI API costs separately
- Control ML compute resource allocation
- Optimize default worker for general throughput

## Task Queue Routing

Workflows automatically route activities to the appropriate worker:

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
    request,
    task_queue=ML_QUEUE
)

# Route to OpenAI worker
await workflow.execute_activity(
    analyze_document_content,
    document_info,
    task_queue=OPENAI_QUEUE
)
```

## Legacy Workers

### `main_worker.py`
The original monolithic worker that registered all activities on a single queue. This has been replaced by the three-worker architecture but is kept for backward compatibility.

**Note:** Use the specialized workers for production deployments.

### `onboarding_worker.py`
Specialized worker for onboarding workflows. May be integrated into the default worker in future updates.

## Configuration

Worker configuration is centralized in `shared/config/defaults.py`:

```python
from shared.config.defaults import (
    DEFAULT_QUEUE,  # "default-queue"
    ML_QUEUE,       # "ml-queue"
    OPENAI_QUEUE,   # "openai-queue"
)
```

## Monitoring

Monitor worker health via Temporal UI:
- **Local:** http://localhost:8233
- Check worker status per task queue
- Monitor activity execution times
- Track failure rates

## Development Tips

1. **Start with Default Worker**: For basic development, start only the default worker
2. **Add ML Worker**: Only needed when testing model training
3. **Add OpenAI Worker**: Only needed when testing AI-powered features
4. **Use Docker Compose**: For production-like environments

## Docker Deployment

Each worker can be containerized separately:

```yaml
# docker-compose.yml
services:
  worker-default:
    build: .
    command: python worker/default_worker.py

  worker-ml:
    build: .
    command: python worker/ml_worker.py
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  worker-openai:
    build: .
    command: python worker/openai_worker.py
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
```

## Troubleshooting

### Worker Not Receiving Tasks
1. Verify worker is connected to correct Temporal server
2. Check task queue name matches workflow configuration
3. Ensure worker has registered required activities

### ML Worker Fails to Start
1. Install ML dependencies: `pip install torch transformers peft trl`
2. Verify CUDA/MPS availability if using GPU
3. Check available system memory

### OpenAI Worker Fails
1. Set `OPENAI_API_KEY` environment variable
2. Install agents dependencies: `pip install agents`
3. Check API rate limits and quotas

## Performance Tuning

### Default Worker
- Increase `max_concurrent_activities` for higher throughput
- Optimize database connection pooling
- Consider horizontal scaling

### ML Worker
- Allocate sufficient memory for model loading
- Use GPU for faster training (10-100x speedup)
- Adjust batch sizes based on available VRAM

### OpenAI Worker
- Implement rate limiting to avoid API throttling
- Use request batching where possible
- Consider caching responses for repeated queries

## Future Enhancements

- Auto-scaling based on queue depth
- Worker pools for each queue type
- Health check endpoints
- Prometheus metrics export
- Distributed tracing integration
