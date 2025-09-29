# ⚡ Pure Technical Activities

Pure technical activities that handle non-AI operations in the system. These are the "leaves" of the workflow tree - deterministic technical implementations that workflows orchestrate.

## 🏗️ Architecture Philosophy

**Clean Separation**: Technical activities are separated from AI activities to create clear dependency boundaries.

- **`activity/`** = Pure technical activities (file I/O, storage, scheduling)
- **`agent_activity/`** = AI-powered activities (OpenAI agents framework)
- **Workflows** coordinate business processes by calling multiple activities
- **Single responsibility** - each activity does one specific technical task
- **Deterministic workflows** - all non-deterministic work happens in activities

## 📋 Current Technical Activities

### 📄 **Document Activities** (`document_activities.py`)

**Purpose**: Pure technical document processing without AI dependencies

#### Technical Functions
- **`process_document_upload(file_path: str) -> DocumentInfo`**
  - Extracts text from uploaded documents
  - Handles PDF, DOCX, TXT, Excel file types
  - Returns structured document metadata
  - No AI dependencies - pure file I/O operations

#### Shared Data Classes
**All document-related dataclasses are defined here for shared use:**
- `DocumentInfo` - Basic document metadata and extracted text
- `DocumentSummaryResult` - Result structure for AI analysis
- `DocumentSummaryWorkflowResult` - Quick summary for admin UI
- `SimpleResearchResult` - Research findings structure

**Usage in Workflows**:
```python
# Pure technical document processing
document_info = await workflow.execute_activity(
    process_document_upload,
    file_path,
    start_to_close_timeout=timedelta(minutes=5)
)

# AI analysis happens in agent_activity
from agent_activity.ai_activities import analyze_document_content
analysis = await workflow.execute_activity(
    analyze_document_content,
    document_info,
    start_to_close_timeout=timedelta(minutes=10)
)
```

### 📁 **Storage Activities** (`storage_activities.py`)

**Purpose**: MinIO document storage and retrieval operations

#### Class-Based Activities (Stateful)
- **`StorageActivities.store_document_in_minio(document_data, filename, document_type)`**
  - Stores documents in MinIO object storage
  - Maintains persistent MinIO client connection
  - Handles bucket creation and error fallbacks

- **`StorageActivities.retrieve_document_from_minio(storage_path)`**
  - Retrieves documents from MinIO storage
  - Returns raw document bytes

**Pattern Justification**: Uses class pattern because it needs to maintain MinIO client connection state.

**Usage in Worker**:
```python
# Initialize once in worker
storage_activities = StorageActivities()

# Register instance methods
all_activities = [
    storage_activities.store_document_in_minio,
    storage_activities.retrieve_document_from_minio,
    # ...
]
```

### ⏰ **Scheduler Activities** (`scheduler_activities.py`)

**Purpose**: Automated operations and maintenance tasks

#### Function-Based Activities
- **`schedule_competitor_scan(request: CompetitorScanRequest) -> CompetitorScanResult`**
  - Executes competitor intelligence scanning
  - Simulates research workflow calls (TODO: integrate with research activities)
  - Returns scan results with metadata

- **`send_scheduled_notification(recipient, subject, message, notification_type)`**
  - Sends email/slack notifications
  - Logs notifications for debugging
  - TODO: Implement actual email/slack integration

- **`cleanup_old_data(data_type: str, retention_days: int)`**
  - Cleans up old documents, reports, cache data
  - Configurable retention policies
  - TODO: Implement actual cleanup logic

- **`health_check_external_services() -> ScheduledTaskResult`**
  - Monitors external service health (OpenAI, MinIO, Temporal)
  - Returns service status and response times
  - TODO: Implement actual health checks

**Usage in Scheduler Workflows**:
```python
# Weekly competitor monitoring
scan_result = await workflow.execute_activity(
    schedule_competitor_scan,
    request,
    start_to_close_timeout=timedelta(minutes=10),
    retry_policy=workflow.RetryPolicy(maximum_attempts=3)
)
```

## 🎯 Activity Design Patterns

### ✅ **Function-Based Activities (Preferred)**
Use for stateless technical tasks:
```python
@activity.defn
async def process_document(file_path: str) -> DocumentResult:
    """Pure function - no state needed"""
    # Process document
    return result
```

### ✅ **Class-Based Activities (When Needed)**
Use for stateful activities that need persistent connections:
```python
class StorageActivities:
    def __init__(self):
        self.client = create_persistent_connection()

    @activity.defn
    async def store_data(self, data: bytes) -> str:
        """Uses persistent connection"""
        return self.client.store(data)
```

## 🏗️ Activity Principles

### 1. **Single Responsibility**
```python
# ✅ Good - single technical task
async def extract_text_from_pdf(file_path: str) -> str:
    # Only handles PDF text extraction

# ❌ Bad - multiple responsibilities
async def process_and_analyze_document(file_path: str) -> AnalysisResult:
    # Handles extraction AND analysis AND summarization
```

### 2. **No Business Logic**
```python
# ✅ Good - pure technical implementation
async def read_file_content(file_path: str) -> str:
    with open(file_path, 'r') as f:
        return f.read()

# ❌ Bad - business logic in activity
async def decide_document_priority(doc: Document) -> Priority:
    if doc.sender == "CEO":  # Business rule!
        return Priority.HIGH
```

### 3. **No AI Dependencies**
```python
# ✅ Good - pure technical operation
async def extract_text_from_file(file_path: str) -> str:
    # File I/O operations only

# ❌ Bad - AI dependency (belongs in agent_activity/)
async def analyze_with_openai(text: str) -> Analysis:
    # OpenAI API calls belong in agent_activity/
```

### 4. **Deterministic Operations**
```python
# ✅ Good - deterministic file operation
content = await read_file(file_path)

# ❌ Bad - non-deterministic in activity
now = datetime.now()  # Breaks workflow replay!
```

### 5. **Proper Error Handling**
```python
@activity.defn
async def risky_operation(data: str) -> Result:
    try:
        # Risky operation
        return success_result
    except SpecificError as e:
        logger.error(f"Operation failed: {e}")
        return error_result
    # Let unexpected errors bubble up for Temporal retry
```

## 🚀 Testing Technical Activities

### Unit Testing
```bash
# Test individual activities
uv run python -c "
from activity.document_activities import process_document_upload
print('✅ Technical activity imports successfully')
"
```

### Integration Testing
```bash
# Test with real dependencies
uv run python -c "
import asyncio
from activity.storage_activities import StorageActivities

async def test():
    storage = StorageActivities()
    # Test storage operations

asyncio.run(test())
"
```

## 📊 Activity Registration

Technical activities are registered in the unified worker (`worker/onboarding_worker.py`):

```python
# Pure technical activities
from activity.document_activities import process_document_upload
from activity.scheduler_activities import (
    schedule_competitor_scan,
    send_scheduled_notification,
    cleanup_old_data,
    health_check_external_services,
)
from activity.storage_activities import StorageActivities

# Class-based activities
storage_activities = StorageActivities()

# Function-based activities
all_activities = [
    # Document processing (technical only)
    process_document_upload,

    # Scheduler operations
    schedule_competitor_scan,
    send_scheduled_notification,
    cleanup_old_data,
    health_check_external_services,

    # Class-based activities (instance methods)
    storage_activities.store_document_in_minio,
    storage_activities.retrieve_document_from_minio,
]
```

## 📋 Naming Conventions

**All activity files follow `*_activities.py` pattern:**
- ✅ `document_activities.py`
- ✅ `scheduler_activities.py`
- ✅ `storage_activities.py`

**Activity functions use `verb_noun` pattern:**
- ✅ `process_document_upload`
- ✅ `schedule_competitor_scan`
- ✅ `cleanup_old_data`

## 🔄 Best Practices

- **Technical tasks only** - No business logic or AI operations
- **Single responsibility** - Each activity does one specific thing
- **Pure functions** - Stateless operations preferred
- **Proper error handling** - Let Temporal handle retries for transient errors
- **Structured returns** - Use dataclasses for complex return types
- **Async/await** - All activities should be async for proper Temporal integration
- **Logging** - Log important operations for debugging
- **Type hints** - Full type annotations for better IDE support and documentation

## 🚀 Next Steps

1. **Implement TODO items** - Actual email sending, health checks, cleanup logic
2. **Add metrics activities** - Business KPI tracking and operational monitoring
3. **Enhance error handling** - More sophisticated retry policies per activity type
4. **Performance optimization** - Caching and batching for high-volume operations

## 🔗 Related Components

- **AI Activities**: See `agent_activity/README.md` for AI-powered activities
- **Workflows**: See `workflow/README.md` for business process orchestration
- **Worker**: See `worker/README.md` for activity registration and execution
