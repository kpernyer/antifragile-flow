# AI Agent Architecture

## Overview

The Living Twin AI Agent system provides a plug-and-play architecture for running multiple AI agents that can monitor news, track trends, and gather intelligence for each tenant. The system supports both tenant-specific and shared agents with full isolation capabilities.

## Architecture Components

### 1. Domain Models (`agent_models.py`)

**Core Models:**

- `Agent`: Main agent entity with configuration and status
- `AgentConfig`: Configuration for agent behavior and sources
- `AgentResult`: Results from agent executions
- `AgentExecution`: Execution records for monitoring and debugging

**Enums:**

- `AgentType`: `TENANT_SPECIFIC` or `SHARED`
- `AgentStatus`: `ACTIVE`, `INACTIVE`, `ERROR`, `RUNNING`
- `AgentCapability`: Various capabilities like news monitoring, trend analysis, etc.

### 2. Agent Implementations (`agents.py`)

**Base Classes:**

- `BaseAgent`: Abstract base class for all agents
- `AgentFactory`: Factory for creating agent instances

**Concrete Implementations:**

- `NewsMonitoringAgent`: Monitors news using free APIs and RSS feeds
- `TechnologyTrendsAgent`: Shared agent for global technology trends

### 3. Agent Service (`agent_service.py`)

**Key Features:**

- Agent lifecycle management (create, update, delete, activate/deactivate)
- Scheduled execution with configurable frequencies
- Health monitoring and metrics
- Result caching and querying
- Isolation mode support

### 4. API Layer (`routers/agents.py`)

**Endpoints:**

- `POST /agents/` - Create new agent
- `GET /agents/` - List agents (tenant-specific + shared)
- `PUT /agents/{id}` - Update agent
- `DELETE /agents/{id}` - Delete agent
- `POST /agents/{id}/execute` - Manual execution
- `GET /agents/{id}/results` - Get agent results
- `GET /agents/{id}/health` - Health status
- `POST /agents/setup-demo` - Setup demo agents

### 5. Worker System (`workers/agent_worker.py`)

**Isolation Mode:**

- Runs agents in separate Cloud Run jobs
- Environment-based configuration
- Graceful shutdown handling
- Error isolation and recovery

## Configuration

### Environment Variables

```bash
# Agent System
AGENT_SCHEDULER_ENABLED=true
AGENT_SCHEDULER_INTERVAL_SECONDS=60
AGENT_MAX_CONCURRENT_EXECUTIONS=10
AGENT_EXECUTION_TIMEOUT_SECONDS=300

# Isolation Mode
AGENT_ISOLATION_ENABLED=true
AGENT_ISOLATION_WORKER_TIMEOUT=600

# News API (optional)
NEWSAPI_API_KEY=your_api_key_here
NEWSAPI_BASE_URL=https://newsapi.org/v2

# Worker Configuration
AGENT_WORKER_MEMORY_MB=512
AGENT_WORKER_CPU_CORES=0.5
AGENT_WORKER_TIMEOUT_SECONDS=600

# Health Monitoring
AGENT_HEALTH_CHECK_INTERVAL_MINUTES=15
AGENT_HEALTH_SUCCESS_RATE_THRESHOLD=0.8
AGENT_HEALTH_MAX_ERROR_COUNT=3
```

## Usage Examples

### 1. Create a Tenant-Specific News Monitor

```python
from app.domain.agent_models import AgentRequest, AgentConfig, AgentType, AgentCapability

# Create agent request
request = AgentRequest(
    name="Competitor News Monitor",
    description="Monitors news about competitors and industry keywords",
    agent_type=AgentType.TENANT_SPECIFIC,
    capabilities=[AgentCapability.NEWS_MONITORING, AgentCapability.CUSTOM_KEYWORD_MONITORING],
    config=AgentConfig(
        keywords=["competitor", "industry", "market trends"],
        update_frequency_minutes=30,
        max_results_per_update=10,
        isolation_mode=False
    ),
    tenant_id="tenant-123"
)

# Create agent via API
agent = await agent_service.create_agent(request)
```

### 2. Create a Shared Technology Trends Agent

```python
request = AgentRequest(
    name="Global Tech Trends",
    description="Monitors global technology trends and innovations",
    agent_type=AgentType.SHARED,
    capabilities=[AgentCapability.TECHNOLOGY_TRENDS, AgentCapability.TREND_ANALYSIS],
    config=AgentConfig(
        keywords=["artificial intelligence", "machine learning", "cloud computing"],
        update_frequency_minutes=60,
        max_results_per_update=20,
        isolation_mode=True
    ),
    tenant_id=None  # Shared agent
)
```

### 3. Execute Agent Manually

```python
from app.domain.agent_models import AgentExecutionRequest

request = AgentExecutionRequest(
    agent_id="agent-123",
    tenant_id="tenant-123",
    force_run=True,
    isolation_mode=True
)

execution = await agent_service.execute_agent(request)
```

### 4. Query Agent Results

```python
from app.domain.agent_models import AgentResultQuery

query = AgentResultQuery(
    agent_id="agent-123",
    tenant_id="tenant-123",
    date_from=datetime.now() - timedelta(days=7),
    keywords=["competitor", "industry"],
    limit=50,
    offset=0
)

results = await agent_service.get_agent_results(query)
```

## Isolation Mode

### Why Isolation?

- **Security**: Prevents agent interference
- **Resource Management**: Isolated memory and CPU
- **Error Containment**: Failures don't affect other agents
- **Scalability**: Independent scaling per agent

### How It Works

1. **API Mode**: Agents run in the same process as the API
2. **Worker Mode**: Agents run in separate Cloud Run jobs

```bash
# Run agent in isolation
AGENT_ID=agent-123 TENANT_ID=tenant-123 python -m app.workers.agent_worker
```

## Free News Sources

The system includes built-in free news sources:

### General News

- BBC News RSS
- CNN RSS
- Reuters RSS
- The Guardian RSS
- NPR RSS

### Technology News

- TechCrunch RSS
- Wired RSS
- Ars Technica RSS
- The Verge RSS
- VentureBeat RSS

## Health Monitoring

### Metrics Tracked

- Success rate (last 7 days)
- Average execution time
- Error count
- Last run time
- Next scheduled run

### Health Status

- **Healthy**: Active + success rate ≥ 80% + error count < 3
- **Unhealthy**: Any issues detected

### Health Check Endpoint

```bash

GET /agents/{agent_id}/health
```

Response:

```json
{
  "agent_id": "agent-123",
  "status": "active",
  "last_run": "2024-12-01T10:00:00Z",
  "next_run": "2024-12-01T11:00:00Z",
  "error_count": 0,
  "success_rate": 0.95,
  "average_execution_time": 45.2,
  "is_healthy": true,
  "issues": []
}
```

## Extending the System

### Adding New Agent Types

1. **Create Agent Implementation**:

```python
class CustomAgent(BaseAgent):
    def get_capabilities(self) -> List[AgentCapability]:
        return [AgentCapability.CUSTOM_CAPABILITY]

    def validate_config(self, config: AgentConfig) -> bool:
        # Validate configuration
        return True

    async def execute(self, isolation_mode: bool = False) -> List[AgentResult]:
        # Implement execution logic
        return results
```

1. **Add to Factory**:

```python
@staticmethod
def create_agent(agent: Agent) -> BaseAgent:
    capabilities = set(agent.capabilities)

    if AgentCapability.CUSTOM_CAPABILITY in capabilities:
        return CustomAgent(agent)
    # ... existing logic
```

1. **Add Capability Enum**:

```python
class AgentCapability(str, Enum):
    CUSTOM_CAPABILITY = "custom_capability"
```

### Adding New Data Sources

1. **Extend Agent Implementation**:

```python
async def _fetch_custom_source(self) -> List[AgentResult]:
    # Implement custom source fetching
    return results
```

1. **Add to Configuration**:

```python
custom_sources: List[str] = [
    "https://custom-source.com/feed",
    "https://another-source.com/api"
]
```

## Deployment

### Docker Configuration

```dockerfile
# Agent Worker Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "-m", "app.workers.agent_worker"]
```

### Cloud Run Deployment

```bash
# Deploy agent worker
gcloud run deploy living-twin-agent-worker \
  --source . \
  --platform managed \
  --region europe-west1 \
  --memory 512Mi \
  --cpu 0.5 \
  --timeout 600 \
  --set-env-vars AGENT_ID=$AGENT_ID,TENANT_ID=$TENANT_ID
```

## Monitoring and Observability

### Logging

- Structured logging with correlation IDs
- Agent execution logs
- Error tracking and alerting

### Metrics

- Execution success/failure rates
- Response times
- Resource utilization
- Result counts

### Alerts

- Agent health degradation
- High error rates
- Execution timeouts
- Resource exhaustion

## Security Considerations

### Tenant Isolation

- Agents can only access their tenant's data
- Shared agents have no tenant context
- API-level tenant validation

### API Key Management

- Secure storage of external API keys
- Rotation capabilities
- Usage monitoring

### Data Privacy

- Result filtering by tenant
- Data retention policies
- Audit logging

## Performance Optimization

### Caching

- Agent results cached in memory
- Configurable retention periods
- Query result caching

### Concurrency

- Configurable concurrent executions
- Resource limits per agent
- Queue management

### Scaling

- Horizontal scaling via Cloud Run
- Auto-scaling based on demand
- Resource allocation optimization
