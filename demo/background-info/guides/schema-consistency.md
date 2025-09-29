# Living Twin - Schema Consistency Guide

This document ensures consistent naming conventions and data structures across all data stores in the Living Twin system.

## 🎯 **Schema Consistency Overview**

All data stores follow the same naming conventions and entity relationships:

- **Neo4j** (Graph database) - Primary data store
- **Firestore** (Document database) - Configuration and metadata
- **Local Storage** (Flutter/React) - Offline caching
- **Pub/Sub Topics** - Event messaging

## 📋 **Core Entities & Naming Conventions**

### **1. Entity Names (PascalCase for types, snake_case for properties)**

| Entity | Neo4j Label | Firestore Collection | Local Storage Key | Pub/Sub Topic |
|--------|-------------|---------------------|-------------------|---------------|
| Tenant | `:Tenant` | `tenants` | `tenant_data` | `tenant-events` |
| User | `:User` | `users` | `user_data` | `user-events` |
| Team | `:Team` | `teams` | `team_data` | `team-events` |
| Goal | `:Goal` | `goals` | `goal_data` | `goal-events` |
| Document | `:Document` | `documents` | `document_data` | `document-events` |
| Chunk | `:Chunk` | `chunks` | `chunk_data` | `chunk-events` |
| Source | `:Source` | `sources` | `source_data` | `source-events` |

### **2. Property Naming (snake_case everywhere)**

| Property | Type | Description | Example |
|----------|------|-------------|---------|
| `id` | string | Unique identifier | `tenant-abc123` |
| `tenant_id` | string | Tenant reference | `tenant-abc123` |
| `created_at` | datetime/timestamp | Creation time | `2024-01-15T10:30:00Z` |
| `updated_at` | datetime/timestamp | Last update | `2024-01-15T10:30:00Z` |
| `created_by` | string | Creator user ID | `user-xyz789` |
| `display_name` | string | Human-readable name | `Engineering Team` |
| `description` | string | Detailed description | `Software development team` |
| `status` | string | Current state | `active`, `inactive`, `archived` |
| `metadata` | object | Additional data | `{"source": "api", "version": 1}` |

## 🗄️ **Detailed Schema Definitions**

### **Tenant Entity**

```yaml
# Neo4j
(:Tenant {
  id: string,                    # "tenant-abc123"
  display_name: string,          # "Acme Corporation"
  domain: string,                # "acme.com"
  settings: object,              # Configuration object
  created_at: datetime,
  updated_at: datetime,
  status: string                 # "active" | "suspended" | "trial"
})

# Firestore: /tenants/{tenant_id}
{
  "id": "tenant-abc123",
  "display_name": "Acme Corporation",
  "domain": "acme.com",
  "settings": {
    "embedding_model": "sentence-transformers",
    "max_chunk_size": 1000,
    "chunk_overlap": 200,
    "allowed_file_types": ["pdf", "docx", "txt"]
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "status": "active"
}

# Flutter Local Storage
Map<String, dynamic> tenantData = {
  "id": "tenant-abc123",
  "display_name": "Acme Corporation",
  "domain": "acme.com",
  "settings": {...},
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "status": "active"
};

# React Local Storage
interface TenantData {
  id: string;
  display_name: string;
  domain: string;
  settings: TenantSettings;
  created_at: string;
  updated_at: string;
  status: 'active' | 'suspended' | 'trial';
}

# Pub/Sub Message
{
  "event_type": "tenant.created",
  "tenant_id": "tenant-abc123",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "id": "tenant-abc123",
    "display_name": "Acme Corporation",
    "status": "active"
  }
}
```

### **User Entity**

```yaml
# Neo4j
(:User {
  id: string,                    # "user-xyz789"
  tenant_id: string,             # "tenant-abc123"
  email: string,                 # "john@acme.com"
  display_name: string,          # "John Doe"
  role: string,                  # "admin" | "member" | "viewer"
  firebase_uid: string,          # Firebase Auth UID
  created_at: datetime,
  updated_at: datetime,
  last_login: datetime,
  status: string                 # "active" | "inactive" | "invited"
})

# Firestore: /tenants/{tenant_id}/users/{user_id}
{
  "id": "user-xyz789",
  "tenant_id": "tenant-abc123",
  "email": "john@acme.com",
  "display_name": "John Doe",
  "role": "admin",
  "firebase_uid": "firebase-uid-123",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "last_login": "2024-01-15T10:30:00Z",
  "status": "active"
}

# Flutter/React Local Storage (same structure)
{
  "id": "user-xyz789",
  "tenant_id": "tenant-abc123",
  "email": "john@acme.com",
  "display_name": "John Doe",
  "role": "admin",
  "status": "active"
}

# Pub/Sub Message
{
  "event_type": "user.login",
  "tenant_id": "tenant-abc123",
  "user_id": "user-xyz789",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "email": "john@acme.com",
    "role": "admin"
  }
}
```

### **Goal Entity**

```yaml
# Neo4j
(:Goal {
  id: string,                    # "goal-launch-mvp"
  tenant_id: string,             # "tenant-abc123"
  title: string,                 # "Launch MVP Product"
  description: string,           # "Complete and launch..."
  status: string,                # "draft" | "active" | "completed" | "archived"
  priority: string,              # "low" | "medium" | "high" | "critical"
  due_date: datetime,
  created_at: datetime,
  updated_at: datetime,
  created_by: string,            # "user-xyz789"
  embedding_384: array,          # Vector embedding (384 dims)
  embedding_1536: array          # Vector embedding (1536 dims)
})

# Firestore: /tenants/{tenant_id}/goals/{goal_id}
{
  "id": "goal-launch-mvp",
  "tenant_id": "tenant-abc123",
  "title": "Launch MVP Product",
  "description": "Complete and launch the minimum viable product",
  "status": "active",
  "priority": "high",
  "due_date": "2024-02-15T00:00:00Z",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "created_by": "user-xyz789"
}

# Flutter/React Local Storage (same structure, no embeddings)
{
  "id": "goal-launch-mvp",
  "tenant_id": "tenant-abc123",
  "title": "Launch MVP Product",
  "description": "Complete and launch the minimum viable product",
  "status": "active",
  "priority": "high",
  "due_date": "2024-02-15T00:00:00Z"
}

# Pub/Sub Message
{
  "event_type": "goal.status_changed",
  "tenant_id": "tenant-abc123",
  "goal_id": "goal-launch-mvp",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "old_status": "draft",
    "new_status": "active",
    "changed_by": "user-xyz789"
  }
}
```

### **Document Entity**

```yaml
# Neo4j
(:Document {
  id: string,                    # "doc-product-spec"
  tenant_id: string,             # "tenant-abc123"
  title: string,                 # "Product Specification"
  file_name: string,             # "product-spec.pdf"
  file_type: string,             # "pdf"
  file_size: integer,            # 1024000 (bytes)
  gcs_path: string,              # "gs://bucket/tenant-abc123/docs/product-spec.pdf"
  page_count: integer,           # 25
  chunk_count: integer,          # 50
  processing_status: string,     # "pending" | "processing" | "completed" | "failed"
  created_at: datetime,
  updated_at: datetime,
  created_by: string,            # "user-xyz789"
  embedding_384: array,          # Document-level embedding
  embedding_1536: array
})

# Firestore: /tenants/{tenant_id}/documents/{document_id}
{
  "id": "doc-product-spec",
  "tenant_id": "tenant-abc123",
  "title": "Product Specification",
  "file_name": "product-spec.pdf",
  "file_type": "pdf",
  "file_size": 1024000,
  "gcs_path": "gs://bucket/tenant-abc123/docs/product-spec.pdf",
  "page_count": 25,
  "chunk_count": 50,
  "processing_status": "completed",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "created_by": "user-xyz789"
}

# Pub/Sub Message
{
  "event_type": "document.processing_completed",
  "tenant_id": "tenant-abc123",
  "document_id": "doc-product-spec",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "file_name": "product-spec.pdf",
    "chunk_count": 50,
    "processing_duration_ms": 45000
  }
}
```

### **Chunk Entity**

```yaml
# Neo4j
(:Chunk {
  id: string,                    # "chunk-doc-product-spec-001"
  tenant_id: string,             # "tenant-abc123"
  document_id: string,           # "doc-product-spec"
  content: string,               # "The product specification defines..."
  position: integer,             # 1 (chunk order in document)
  page_number: integer,          # 1
  start_char: integer,           # 0
  end_char: integer,             # 1000
  token_count: integer,          # 250
  created_at: datetime,
  embedding_384: array,          # Chunk embedding
  embedding_1536: array
})

# Firestore: /tenants/{tenant_id}/chunks/{chunk_id}
{
  "id": "chunk-doc-product-spec-001",
  "tenant_id": "tenant-abc123",
  "document_id": "doc-product-spec",
  "content": "The product specification defines...",
  "position": 1,
  "page_number": 1,
  "start_char": 0,
  "end_char": 1000,
  "token_count": 250,
  "created_at": "2024-01-15T10:30:00Z"
}
```

## 🔗 **Relationship Naming Conventions**

### **Neo4j Relationships**

```cypher
# User belongs to Tenant
(:User)-[:BELONGS_TO]->(:Tenant)

# User is member of Team
(:User)-[:MEMBER_OF]->(:Team)

# Team belongs to Tenant
(:Team)-[:BELONGS_TO]->(:Tenant)

# Team owns Goal
(:Team)-[:OWNS]->(:Goal)

# Goal belongs to Tenant
(:Goal)-[:BELONGS_TO]->(:Tenant)

# Document belongs to Tenant
(:Document)-[:BELONGS_TO]->(:Tenant)

# Chunk belongs to Document
(:Chunk)-[:BELONGS_TO]->(:Document)

# Document relates to Goal
(:Document)-[:RELATES_TO]->(:Goal)

# User created Document
(:User)-[:CREATED]->(:Document)
```

## 📨 **Pub/Sub Topic & Message Conventions**

### **Topic Naming Pattern**

```bash
{entity}-{action}
```

### **Topics List**

```yaml
# Entity lifecycle events
- tenant-events          # tenant.created, tenant.updated, tenant.deleted
- user-events            # user.created, user.login, user.role_changed
- team-events            # team.created, team.member_added, team.member_removed
- goal-events            # goal.created, goal.status_changed, goal.completed
- document-events        # document.uploaded, document.processing_completed
- chunk-events           # chunk.created, chunk.embedded

# Processing events
- ingestion-jobs         # ingestion.started, ingestion.completed, ingestion.failed
- embedding-jobs         # embedding.started, embedding.completed, embedding.failed
- search-events          # search.query, search.results

# System events
- audit-events           # audit.login, audit.permission_change, audit.data_access
- billing-events         # billing.usage_updated, billing.limit_exceeded
```

### **Message Structure**

```json
{
  "event_type": "entity.action",
  "tenant_id": "tenant-abc123",
  "entity_id": "entity-specific-id",
  "timestamp": "2024-01-15T10:30:00Z",
  "correlation_id": "uuid-for-tracing",
  "data": {
    // Event-specific payload
  },
  "metadata": {
    "source": "api|worker|scheduler",
    "version": "1.0",
    "user_id": "user-xyz789"
  }
}
```

## 💾 **Local Storage Conventions**

### **Flutter (Dart)**

```dart
// Storage keys
class StorageKeys {
  static const String tenantData = 'tenant_data';
  static const String userData = 'user_data';
  static const String goalData = 'goal_data';
  static const String documentData = 'document_data';
  static const String offlineQueue = 'offline_queue';
}

// Data models
class TenantModel {
  final String id;
  final String displayName;
  final String domain;
  final Map<String, dynamic> settings;
  final DateTime createdAt;
  final DateTime updatedAt;
  final String status;
}
```

### **React (TypeScript)**

```typescript
// Storage keys
export const STORAGE_KEYS = {
  TENANT_DATA: 'tenant_data',
  USER_DATA: 'user_data',
  GOAL_DATA: 'goal_data',
  DOCUMENT_DATA: 'document_data',
  OFFLINE_QUEUE: 'offline_queue'
} as const;

// Data interfaces
interface TenantData {
  id: string;
  display_name: string;
  domain: string;
  settings: TenantSettings;
  created_at: string;
  updated_at: string;
  status: 'active' | 'suspended' | 'trial';
}
```

## 🔄 **Data Synchronization Patterns**

### **Write Pattern (API → All Stores)**

1. **API receives request** → Validates data
2. **Write to Neo4j** → Primary source of truth
3. **Write to Firestore** → For fast queries and offline support
4. **Publish to Pub/Sub** → Notify other services
5. **Update local storage** → Via real-time sync

### **Read Pattern (Optimized for each use case)**

- **Complex queries** → Neo4j (graph relationships)
- **Simple lookups** → Firestore (fast document access)
- **Offline access** → Local storage (cached data)
- **Real-time updates** → Pub/Sub subscriptions

## ✅ **Validation Rules**

### **ID Format Validation**

```bash
# Entity ID patterns
tenant_id: ^tenant-[a-z0-9]{6,12}$
user_id: ^user-[a-z0-9]{6,12}$
goal_id: ^goal-[a-z0-9-]{6,50}$
document_id: ^doc-[a-z0-9-]{6,50}$
chunk_id: ^chunk-[a-z0-9-]{6,50}$
```

### **Property Validation**

```yaml
# Required fields for all entities
- id: string (required, unique)
- tenant_id: string (required, valid tenant reference)
- created_at: datetime (required, ISO 8601)
- updated_at: datetime (required, ISO 8601)

# Optional but recommended
- created_by: string (user reference)
- status: string (enum values)
- metadata: object (additional context)
```

This schema consistency ensures that your data flows seamlessly between Neo4j, Firestore, local storage, and Pub/Sub messaging, maintaining the same structure and naming conventions throughout your entire system.
