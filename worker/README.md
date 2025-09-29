# Worker Directory

This directory contains Temporal workers that execute workflows and activities for the Organizational Twin system.

## Architecture Decision: Single Worker Design

We use **one unified worker** (`onboarding_worker.py`) instead of multiple specialized workers. This design choice optimizes for simplicity, resource efficiency, and maintainability during the demo phase.

### Why One Worker?

#### ✅ **Shared Infrastructure**
- All workflows use the same AI infrastructure (OpenAI agents)
- Common storage system (MinIO for documents, PostgreSQL/Neo4j for data)
- Shared authentication and configuration
- Same dependency stack (Python, temporalio, openai-agents)

#### ✅ **Operational Simplicity**
- Single deployment unit
- Unified monitoring and logging
- Easier debugging and development
- Reduced operational overhead

#### ✅ **Resource Efficiency**
- No duplicate infrastructure
- Efficient resource sharing
- Better cost optimization for demo environments
- Simpler scaling decisions

#### ✅ **Development Velocity**
- Faster iteration cycles
- Easier testing and validation
- Single point of configuration
- Reduced complexity for demos

## Current Worker Capabilities

### `onboarding_worker.py`

**Supported Workflows:**
- `DocumentSummaryWorkflow` - Document processing and AI analysis
- `CompetitorResearchWorkflow` - Scheduled competitor monitoring *(coming soon)*
- `InteractiveResearchWorkflow` - Human-in-the-loop research *(coming soon)*
- `OnboardingWorkflow` - Combined document + research onboarding *(planned)*

**Available Activities:**
- **Document Processing**: Upload, text extraction, AI analysis
- **Storage Operations**: MinIO document storage and retrieval
- **Research Activities**: Web scraping, content analysis *(coming soon)*
- **Scheduler Activities**: Cron-like scheduling, notifications *(planned)*

## When to Split Workers

Consider multiple workers when you encounter:

### **Different Infrastructure Requirements**
```python
# High-memory AI worker
onboarding_worker.py     # 16GB RAM, GPU access for AI processing

# Lightweight scheduler worker
scheduler_worker.py      # 1GB RAM, always-on for cron jobs
```

### **Different Scaling Patterns**
```python
# Elastic scaling (0→100 instances)
document_worker.py       # Scales with document uploads

# Fixed scaling (always 1-3 instances)
monitoring_worker.py     # Constant monitoring workflows
```

### **Different Security Boundaries**
```python
# Customer data access
internal_worker.py       # Access to sensitive customer documents

# External API access only
research_worker.py       # Web scraping, public data only
```

### **Performance Bottlenecks**
```python
# CPU-intensive work
analysis_worker.py       # Heavy document processing

# I/O-intensive work
integration_worker.py    # API calls, database operations
```

## Scheduler Activities Architecture

### Temporal Cron Workflows
For scheduled tasks like Monday morning competitor monitoring:

```python
# Start cron workflow
await client.start_workflow(
    CompetitorResearchWorkflow.run,
    competitors=["competitor1", "competitor2"],
    id="weekly-competitor-scan",
    cron_schedule="0 9 * * 1",  # Every Monday 9 AM
    task_queue=shared.TASK_QUEUE_NAME,
)
```

### Scheduler Activity Pattern
```python
@activity.defn
async def schedule_competitor_scan(competitors: List[str]) -> ScanResult:
    \"\"\"Scheduled activity for competitor monitoring\"\"\"
    results = []
    for competitor in competitors:
        # Trigger research workflow for each competitor
        scan_result = await workflow.execute_child_workflow(
            CompetitorResearchWorkflow.run,
            competitor
        )
        results.append(scan_result)

    return ScanResult(
        scan_date=datetime.now(),
        competitors_scanned=len(competitors),
        results=results
    )
```

## Future Expansion

### Phase 1: Enhanced Document Processing ✅
- Document upload and analysis
- AI-powered summarization
- Storage integration

### Phase 2: Research Capabilities ⏳
- Web scraping activities
- Competitor monitoring
- Research report generation

### Phase 3: Scheduler Integration 📋
- Cron-based workflows
- Automated monitoring
- Alert notifications

### Phase 4: Advanced Onboarding 🎯
- Combined document + research workflows
- Multi-step onboarding processes
- Human-in-the-loop interactions

## Development Guidelines

### Adding New Workflows
1. Create workflow in `/workflow/` directory
2. Add workflow import to `onboarding_worker.py`
3. Register in `all_workflows` list
4. Test end-to-end functionality

### Adding New Activities
1. Create activity in `/activity/` directory
2. Add activity import to `onboarding_worker.py`
3. Register in `all_activities` list
4. Ensure proper error handling and retries

### Testing
```bash
# Start the worker
uv run python worker/onboarding_worker.py

# Test with sample workflow
uv run python workflow/simple_test_starter.py
```

## Monitoring and Operations

### Health Checks
- Worker reports status on startup
- Temporal UI shows workflow/activity metrics
- Application logs include structured events

### Scaling
- Single worker instance for demo
- Can scale horizontally by running multiple instances
- Temporal handles load balancing automatically

### Error Handling
- Activities have built-in retry policies
- Workflow state persisted in Temporal
- Graceful degradation for external service failures

## Configuration

### Environment Variables
- `TEMPORAL_ADDRESS` - Temporal server address (default: localhost:7233)
- `TASK_QUEUE_NAME` - Worker task queue (from shared.shared)
- `OPENAI_API_KEY` - OpenAI API key for AI activities
- `MINIO_*` - MinIO configuration for document storage

### Dependencies
- `temporalio` - Temporal Python SDK
- `openai-agents` - AI agent framework
- `pydantic` - Data validation and serialization
- Project-specific modules (activity, workflow, shared)

---

*This README reflects the current architecture decision optimized for demo simplicity and development velocity. The design supports future expansion to multiple workers as requirements evolve.*
