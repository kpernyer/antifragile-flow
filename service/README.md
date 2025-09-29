# Services Architecture

Services are foundational infrastructure components that provide specific capabilities to the Organizational Twin system. Each service encapsulates a particular domain of functionality and provides clean APIs for agents, workflows, and other components.

## 🏗️ Service Design Principles

**Services are:**
- ✅ **Infrastructure components** (databases, storage, messaging, etc.)
- ✅ **Stateful** (maintain data and state)
- ✅ **Shared** by multiple agents and workflows
- ✅ **Domain-focused** with their own data models and business logic
- ✅ **API-driven** with clean interfaces for other components

**Services are NOT:**
- ❌ **Agents** (AI components with single responsibilities)
- ❌ **Activities** (Temporal task executors)
- ❌ **Workflows** (orchestration logic)

## 📋 Available Services

### 📬 Inbox Service (`/services/inbox/`)
**Purpose**: Communication and messaging hub for human-AI collaboration

**Components:**
- `inbox_service.py` - Core messaging functionality
- `db_inbox_service.py` - Database persistence layer
- `inbox_models.py` - Data models for messages, workflows, users
- `organizational_twin.py` - AI decision-making logic
- `user_client.py` - User interaction interface
- `user_profiles.py` - User management
- `human_input_handler.py` - Human-in-the-loop processing

**Used by:** Communication agents, workflow orchestration, human interaction flows

### 📁 Document Store Service (`/services/document_store/`)
**Purpose**: Document storage and retrieval using MinIO

**Used by:** Document processing agents, file management workflows

### 🧠 Knowledge Graph Service (`/services/knowledge_graph/`)
**Purpose**: Graph-based knowledge representation using Neo4j

**Used by:** Knowledge reasoning agents, relationship mapping, organizational memory

### ⏰ Scheduler Service (`/services/scheduler/`)
**Purpose**: Task scheduling and cron-like functionality

**Used by:** Workflow automation, periodic tasks, reminder systems

### 🗄️ Database Services
**Purpose**: Core data persistence
- `postgres_models.py` - PostgreSQL data models
- `neo4j_service.py` - Neo4j graph database service
- `db_models.py` - General database models

## 🔌 Service Usage Pattern

```python
# Agents use services through clean interfaces
from service.inbox import InboxService
from service.document_store import DocumentStoreService

class MyAgent:
    def __init__(self):
        self.inbox = InboxService()
        self.docs = DocumentStoreService()

    def process_message(self, message):
        # Agent focuses on AI logic
        # Service handles infrastructure
        response = self.inbox.send_message(message)
        return response
```

## 🎯 Benefits

1. **Separation of Concerns**: Agents focus on AI logic, services handle infrastructure
2. **Reusability**: Multiple agents can use the same service
3. **Testability**: Services can be mocked/stubbed for testing
4. **Maintainability**: Infrastructure changes isolated to service layer
5. **Scalability**: Services can be independently scaled or replaced
