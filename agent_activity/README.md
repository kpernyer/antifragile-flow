# 🤖 AI-Powered Activities

AI-powered activities using the OpenAI agents framework. These activities handle all operations that require OpenAI API calls and AI intelligence.

## 🏗️ Architecture Philosophy

**Clean Separation**: AI activities are isolated from pure technical activities to create clear dependency boundaries and easier testing.

- **`activity/`** = Pure technical activities (file I/O, storage, scheduling)
- **`agent_activity/`** = AI-powered activities (OpenAI agents framework)

## 📋 Current AI Activities

### 🤖 **`ai_activities.py`** - Core AI Operations

All AI-powered document and research activities using OpenAI agents framework:

#### Document Analysis Activities
- **`analyze_document_content(document_info: DocumentInfo) -> DocumentSummaryResult`**
  - Deep AI analysis of document content
  - Generates summaries, key takeaways, topics
  - Uses OpenAI agents with proper tracing

- **`generate_document_summary(file_path: str) -> DocumentSummaryWorkflowResult`**
  - Quick document summary for immediate admin UI display
  - Combines file processing + AI analysis in one call
  - Optimized for fast user feedback

#### Research Activities
- **`perform_simple_research(query: str, context: str) -> SimpleResearchResult`**
  - One-shot research using OpenAI agents with prompt templates
  - Structured research findings with confidence scoring
  - Fallback to basic OpenAI API if prompt system fails

## 🎯 Supporting Agent Framework

### **`core/`** - Agent Implementations
- **`writer_agent.py`** - Research and writing agent for document analysis
- **`research_manager.py`** - Advanced research coordination
- **`instruction_agent.py`** - Task instruction processing
- **`clarifying_agent.py`** - Question clarification handling
- **`triage_agent.py`** - Query routing and triage

### **Legacy Implementations** (retained for reference)
- **`openai-agents-demos/`** - Original OpenAI agents examples
- **`website-ai-agent-starter/`** - Web-based agent starter
- Various specialized directories for specific use cases

## 🚀 Usage in Workflows

### Import Pattern
```python
# Pure technical activities
from activity.document_activities import process_document_upload

# AI-powered activities
from agent_activity.ai_activities import (
    analyze_document_content,
    generate_document_summary,
    perform_simple_research
)
```

### Workflow Usage
```python
# In DocumentProcessingWorkflow
@workflow.defn
class DocumentProcessingWorkflow:
    async def run(self, request: DocumentProcessingRequest):
        # Step 1: Pure technical processing
        document_info = await workflow.execute_activity(
            process_document_upload,
            file_path,
            start_to_close_timeout=timedelta(minutes=5)
        )

        # Step 2: AI-powered analysis
        analysis_result = await workflow.execute_activity(
            analyze_document_content,
            document_info,
            start_to_close_timeout=timedelta(minutes=10)
        )
```

## 🔧 Worker Registration

Activities are registered in the unified worker (`worker/onboarding_worker.py`):

```python
# Pure technical activities
from activity.document_activities import process_document_upload

# AI-powered activities
from agent_activity.ai_activities import (
    analyze_document_content,
    generate_document_summary,
    perform_simple_research,
)

all_activities = [
    # Technical activities
    process_document_upload,

    # AI activities
    analyze_document_content,
    generate_document_summary,
    perform_simple_research,

    # Storage activities
    storage_activities.store_document_in_minio,
    # ...
]
```

## 🧪 Testing AI Activities

### Import Testing
```bash
# Test AI activities import correctly
uv run python -c "
from agent_activity.ai_activities import (
    analyze_document_content,
    generate_document_summary,
    perform_simple_research
)
print('✅ AI activities import successfully')
"
```

### Integration Testing
```bash
# Test with real OpenAI API (requires valid API key)
uv run python -c "
import asyncio
from agent_activity.ai_activities import perform_simple_research

async def test():
    result = await perform_simple_research(
        'What is the capital of France?',
        'Testing simple research'
    )
    print(f'Research result: {result.findings}')

asyncio.run(test())
"
```

## 📊 Data Flow

```
📄 Document Upload
   ↓
🔧 process_document_upload (technical)
   ↓
🤖 analyze_document_content (AI)
   ↓
📋 DocumentSummaryResult
   ↓
🎯 Business Workflow
```

## 🎯 AI Framework Integration

### OpenAI Agents Framework
- **Tracing**: All AI activities use proper trace IDs for monitoring
- **Error Handling**: Graceful fallbacks for API failures
- **Structured Output**: Uses `ReportData` and structured agent responses
- **Configuration**: Centralized AI configuration in `shared/config/ai_config.py`

### Prompt Templates
- **Template System**: Uses Jinja2 templates from `shared/prompts/`
- **Research Prompts**: Specialized prompts for different research types
- **Document Analysis**: Templates for structured document analysis

## 🔄 Best Practices

### Activity Design
- **Single Responsibility**: Each activity handles one specific AI task
- **Async/Await**: All activities are async for proper Temporal integration
- **Error Handling**: Comprehensive error handling with fallbacks
- **Structured Returns**: Use dataclasses for complex return types

### AI Integration
- **Tracing**: Always use `trace()` context for OpenAI agent calls
- **Retry Logic**: Built-in retry logic for transient API failures
- **Confidence Scoring**: Include confidence metrics in results
- **Resource Management**: Proper cleanup of AI resources

### Testing
- **Mock AI Calls**: Use mocks for unit testing
- **Integration Tests**: Test with real API for end-to-end validation
- **Error Scenarios**: Test API failures and fallback behavior

## 🚀 Adding New AI Activities

1. **Create Activity Function**
   ```python
   @activity.defn
   async def my_ai_activity(input_data: MyInputType) -> MyOutputType:
       run_config = RunConfig(trace_id=gen_trace_id("my_activity"))
       agent = create_specialized_agent()

       with trace("my_activity", run_config.trace_id):
           result = await Runner.run(agent, prompt, run_config)
           return process_result(result)
   ```

2. **Register in Worker**
   ```python
   # Add to agent_activity/ai_activities.py imports
   from agent_activity.ai_activities import my_ai_activity

   # Add to all_activities list in worker
   all_activities = [
       # ...existing activities
       my_ai_activity,
   ]
   ```

3. **Use in Workflows**
   ```python
   result = await workflow.execute_activity(
       my_ai_activity,
       input_data,
       start_to_close_timeout=timedelta(minutes=15),
       retry_policy=workflow.RetryPolicy(maximum_attempts=3)
   )
   ```

## 📋 Current Limitations

- **OpenAI API Key**: Requires valid OpenAI API key for functionality
- **Rate Limits**: Subject to OpenAI API rate limiting
- **Network Dependency**: Requires internet connection for AI operations
- **Cost**: AI operations incur OpenAI API costs

## 🔧 Future Enhancements

1. **Advanced Research Activities** - Multi-step research with web scraping
2. **Document Comparison** - AI-powered document similarity analysis
3. **Intelligent Routing** - Smart activity routing based on content type
4. **Cost Optimization** - Request batching and caching strategies
5. **Local Models** - Support for local LLM alternatives
