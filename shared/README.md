# 🔧 Shared Utilities and Configuration

Centralized shared utilities, configurations, and constants used across the Antifragile Flow application.

## 📁 Directory Structure

### 🚀 **Currently Active**

#### `shared.py` - Core Constants
**Status**: ✅ **ACTIVE** - Used throughout the application
```python
from shared import shared
task_queue = shared.TASK_QUEUE_NAME  # "hackathon"
```
**Contains**: Essential Temporal task queue configuration used by all workflows and workers.

#### `prompts/` - AI Prompt Management
**Status**: ✅ **ACTIVE** - Used by testing infrastructure
```python
from shared.prompts import load_prompt
prompt = load_prompt("document_processor.analyze_document", **variables)
```
**Contains**: Comprehensive prompt template system with YAML definitions, Jinja2 templating, and type-safe validation.

### 🏗️ **Infrastructure Ready (Not Yet Integrated)**

#### `config/` - Application Configuration
**Status**: ⏳ **READY** - Complete implementation, not yet integrated
**Contains**:
- `settings.py` - Comprehensive application settings with environment support
- `ai_config.py` - AI service configuration (OpenAI, model settings)
- `database_config.py` - Database connection configuration

**Future Integration**: Replace hardcoded values with centralized configuration management.

#### `models/` - Base Data Models
**Status**: ⏳ **READY** - Complete implementation, not yet integrated
**Contains**: Pydantic base models for data validation and serialization.

**Future Integration**: Standardize data models across workflows and activities.

#### `temporal_client/` - Temporal Client Wrapper
**Status**: ⏳ **READY** - Complete implementation, not yet integrated
**Contains**:
- `client.py` - Enhanced Temporal client with connection pooling and retry logic
- `config.py` - Comprehensive Temporal configuration with task queue management

**Future Integration**: Replace direct `Client.connect()` calls with managed client wrapper.

## 🎯 Current Usage Patterns

### Temporal Configuration
```python
# Current pattern (simplified)
from shared import shared
client = await Client.connect("localhost:7233")
handle = await client.start_workflow(..., task_queue=shared.TASK_QUEUE_NAME)
```

### Prompt Management
```python
# Template-based AI prompts
from shared.prompts import load_prompt
prompt = load_prompt(
    "document_processor.analyze_document",
    document_type="financial_report",
    document_content=content
)
```

## 🚀 Future Integration Opportunities

### 1. **Configuration Management**
Replace hardcoded values with centralized settings:
```python
# Future pattern
from shared.config import get_settings
settings = get_settings()
client = await Client.connect(settings.temporal.target_host)
```

### 2. **Enhanced Temporal Client**
Use managed client with automatic retry and connection pooling:
```python
# Future pattern
from shared.temporal_client import get_temporal_client
client = await get_temporal_client()
```

### 3. **Standardized Data Models**
Use validated Pydantic models for all data transfer:
```python
# Future pattern
from shared.models import WorkflowRequest, WorkflowResult
```

## 📋 Integration Checklist

To integrate the ready infrastructure:

- [ ] **Config Integration**: Replace hardcoded settings with `shared.config.get_settings()`
- [ ] **Temporal Client**: Replace direct `Client.connect()` with `shared.temporal_client.get_temporal_client()`
- [ ] **Data Models**: Standardize request/response models using `shared.models`
- [ ] **Environment Support**: Add `.env` files and environment-specific configurations

## 🔧 Development Notes

- **Backward Compatibility**: All changes maintain existing import patterns
- **Professional Implementation**: Ready modules follow enterprise patterns with validation, type safety, and comprehensive configuration
- **Gradual Migration**: Infrastructure can be integrated incrementally without breaking existing functionality
- **Documentation**: Each ready module includes comprehensive documentation and examples

The shared directory provides both immediate functionality (constants, prompts) and professional infrastructure ready for future integration as the application scales.
