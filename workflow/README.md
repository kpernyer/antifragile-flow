# 🔄 Temporal Workflows

Workflows orchestrate business processes and coordinate multiple activities. They are deterministic, long-running processes that can survive failures and restarts.

## 🏗️ Architecture Philosophy

**Workflows = Business Orchestration, Activities = Technical Implementation**

- **Workflows** coordinate business processes (onboarding, research, monitoring)
- **Activities** handle technical tasks (AI calls, document processing, API requests)
- **One unified worker** handles all workflows for simplicity and shared infrastructure

## 📋 Current Workflows

### 🏢 **Business Workflows**

#### `organization_onboarding_workflow.py` - Main Business Process
**Purpose**: Complete organization onboarding orchestration
**Coordinates**:
- Document processing pipeline
- Interactive research sessions
- Competitor monitoring setup
- Admin notifications throughout process

**Usage**:
```python
result = await client.execute_workflow(
    OrganizationOnboardingWorkflow.run,
    OnboardingRequest(
        organization_name="Acme Corp",
        documents=["contract.pdf", "financials.xlsx"],
        research_queries=["What is Acme Corp's market position?"],
        competitors=["Competitor A", "Competitor B"]
    )
)
```

#### `document_processing_workflow.py` - Document Pipeline
**Purpose**: Handle multiple document uploads with dual output
**Features**:
- Quick summaries for immediate admin UI display
- Full analysis for business intelligence
- Batch processing of multiple documents
- Called by organization onboarding workflow

#### `interactive_research_workflow.py` - Human-AI Research
**Purpose**: Guided research with human clarifications
**Features**:
- Back-and-forth clarification process
- Generates comprehensive research reports
- **Status**: Import issues with openai_agents module (temporarily disabled)

#### `research_bot_workflow.py` - Automated Research
**Purpose**: Fully automated research without human interaction
**Features**:
- Plan → Search → Write report pipeline
- **Status**: Import issues (temporarily disabled)

### ⚙️ **Operational Workflows**

#### `scheduler_workflow.py` - Automated Operations
**Contains three specialized workflows**:

1. **CompetitorMonitoringWorkflow** - Weekly Monday 9 AM competitor intelligence
2. **MaintenanceWorkflow** - Daily 2 AM system cleanup and health checks
3. **AdHocSchedulerWorkflow** - Custom one-time scheduled tasks

**Cron Examples**:
```python
# Weekly competitor monitoring
await client.start_workflow(
    CompetitorMonitoringWorkflow.run,
    request,
    id="weekly-competitor-monitoring",
    cron_schedule="0 9 * * 1",  # Every Monday 9 AM
)

# Daily maintenance
await client.start_workflow(
    MaintenanceWorkflow.run,
    id="daily-maintenance",
    cron_schedule="0 2 * * *",  # Every day 2 AM
)
```

## 🎯 Workflow Hierarchy in Practice

```
🏢 OrganizationOnboardingWorkflow (USER ENTRY POINT)
├── 📄 DocumentProcessingWorkflow (child workflow)
├── 💬 InteractiveResearchWorkflow (child workflow)
└── 🗓️ CompetitorMonitoringWorkflow (setup for future)

⚙️ SCHEDULED OPERATIONS (automatic)
├── 🗓️ CompetitorMonitoringWorkflow (every Monday)
├── 🔧 MaintenanceWorkflow (every day 2 AM)
└── ⚡ AdHocSchedulerWorkflow (custom timing)
```

## 🚀 Running Workflows

### Start the Unified Worker
```bash
# Single worker handles all workflows
uv run python worker/onboarding_worker.py
```

### Trigger Business Workflows
```python
from temporalio.client import Client

client = await Client.connect("localhost:7233")

# Complete organization onboarding
handle = await client.start_workflow(
    OrganizationOnboardingWorkflow.run,
    onboarding_request,
    id=f"onboarding-{org_name}",
    task_queue=shared.TASK_QUEUE_NAME
)

# Query progress
progress = await handle.query("get_progress")
```

## 🏗️ Workflow Design Principles

### 1. **Business Process Alignment**
```python
# ✅ Good - matches business process
class OrganizationOnboardingWorkflow:
    async def run(self, request):
        # Orchestrate business sub-processes
        docs = await workflow.execute_child_workflow(DocumentProcessingWorkflow.run, ...)
        research = await workflow.execute_child_workflow(InteractiveResearchWorkflow.run, ...)

# ❌ Bad - technical task as workflow
class DocumentSummaryWorkflow:  # Should be an activity!
```

### 2. **Orchestration Only**
```python
# ✅ Good - orchestration
result = await workflow.execute_activity(simple_research, query)

# ❌ Bad - business logic in workflow
analysis = openai.chat.completions.create(...)  # Breaks determinism!
```

### 3. **Child Workflow Coordination**
```python
# Parallel execution of major sub-processes
doc_task = workflow.execute_child_workflow(DocumentProcessingWorkflow.run, docs)
research_task = workflow.execute_child_workflow(InteractiveResearchWorkflow.run, queries)

# Wait for both to complete
doc_results = await doc_task
research_results = await research_task
```

## 📊 Activities vs Workflows

### ✅ **When to Use Workflows**
- Complete business processes (organization onboarding)
- Multi-step pipelines (document processing)
- Human-AI interaction coordination
- Scheduled business operations

### ✅ **When to Use Activities**
- Technical tasks (OpenAI API calls)
- Document text extraction
- Database operations
- Quick summaries for UI

## 🎯 Current Activity Integration

Workflows coordinate these key activities:
- `summarize_document` - Quick admin UI summaries
- `simple_research` - One-shot research using prompt templates
- `process_document_upload` - File processing and storage
- `analyze_document_content` - AI-powered document analysis
- Scheduler activities - Health checks, cleanup, notifications

## 🧪 Testing Workflows

### Unit Testing
```bash
# Test individual workflows
uv run python -c "
from workflow.organization_onboarding_workflow import OrganizationOnboardingWorkflow
print('✅ Imports successful')
"
```

### Integration Testing
```bash
# Start worker
uv run python worker/onboarding_worker.py &

# Test complete onboarding process
uv run python test/onboarding_integration_test.py
```

## 📋 Naming Conventions

**All workflow files follow `*_workflow.py` pattern:**
- ✅ `organization_onboarding_workflow.py`
- ✅ `document_processing_workflow.py`
- ✅ `scheduler_workflow.py`

**All workflows use `@workflow.defn` decorator:**
```python
@workflow.defn
class SomethingWorkflow:
    @workflow.run
    async def run(self, request: SomeRequest) -> SomeResult:
        # Orchestration logic
```

## 🔄 Best Practices

- **Align with business processes** - Workflows should match how users think about the work
- **Use child workflows** - Break complex processes into manageable sub-processes
- **Activities for technical tasks** - Keep AI calls, API requests, database ops in activities
- **Proper error handling** - Graceful degradation when sub-processes fail
- **Progress tracking** - Use queries to expose workflow status to users
- **Unified worker** - Single worker simplifies development and operations
- **Clear naming** - Business intent should be obvious from workflow names

## 🚀 Next Steps

1. **Fix research workflow imports** - Resolve openai_agents module dependencies
2. **Add prompt template integration** - All research should use shared prompt system
3. **Enhance progress tracking** - More detailed status queries for admin UI
4. **Add workflow metrics** - Business KPIs and operational monitoring
