# Living Twin RAG Stack Explanation

A comprehensive guide to the RAG (Retrieval-Augmented Generation) architecture powering the Living Twin organizational intelligence platform.

## 🏗️ Architecture Overview

Living Twin uses a **hybrid, multi-tenant RAG architecture** that combines the best of cloud and local AI capabilities with enterprise-grade data management.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   Neo4j         │
│   (React/Flutter)│◄──►│   RAG Engine    │◄──►│   Vector DB     │
│                 │    │                 │    │   + Graph       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   LLM Layer     │
                       │   (Hybrid)      │
                       └─────────────────┘
```

## 🔧 Core RAG Components

### 1. **Embeddings Layer** - Multi-Provider Support

**Primary Options:**
- **OpenAI Embeddings** (Production): `text-embedding-3-small` (1536 dimensions)
- **Local SBERT** (Development/Privacy): `all-MiniLM-L6-v2` (384 dimensions)
- **Stub Embeddings** (Testing): Zero vectors for development

**Configuration:**
```bash
# Production (OpenAI)
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_EMBEDDING_DIMENSIONS=1536

# Local Development
LOCAL_EMBEDDINGS=true
SBERT_MODEL=all-MiniLM-L6-v2
SBERT_EMBEDDING_DIMENSIONS=384
```

**Why This Choice:**
- **OpenAI**: Best quality, production-ready, handles complex queries
- **SBERT**: Privacy-first, no API costs, good for development
- **Automatic Fallback**: System switches based on configuration

### 2. **Vector Database** - Neo4j with Native Vector Support

**Technology:** Neo4j 5.20+ with native vector indexes

**Key Features:**
- **Native Vector Indexes**: Built-in cosine similarity search
- **Graph Relationships**: Document → Chunk → Source relationships
- **Multi-tenant Isolation**: Tenant-based data segregation
- **Hybrid Search**: Vector + graph traversal capabilities

**Schema:**
```cypher
// Document chunks with embeddings
CREATE (d:Doc {
  id: string,
  text: string,
  embedding: vector,
  tenantId: string,
  source: string
})

// Vector index for similarity search
CALL db.index.vector.createNodeIndex(
  'docEmbeddings',
  'Doc',
  'embedding',
  1536,  // or 384 for local
  'cosine'
)
```

**Why Neo4j:**
- **Unified Storage**: Graph + vectors in one database
- **Enterprise Ready**: ACID compliance, backup, clustering
- **Rich Queries**: Combine vector search with graph traversal
- **Scalability**: Handles millions of documents efficiently

### 3. **LLM Layer** - Hybrid Generation

**Available Providers:**
- **OpenAI** (Production): `gpt-4o-mini`, `gpt-4-turbo`
- **Ollama** (Local): `llama3`, `mistral-7b`, `gpt-oss-20b`
- **Stub** (Testing): Returns top snippets without generation

**Configuration:**
```bash
# OpenAI (Production)
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4o-mini

# Local LLM
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3

# RAG-only mode (no LLM generation)
RAG_ONLY=true
```

**Why Hybrid:**
- **Cost Control**: Local models for development/testing
- **Privacy**: Sensitive data stays on-premises
- **Flexibility**: Choose best model for each use case
- **Reliability**: Fallback options if one provider fails

### 4. **Orchestration** - Custom Domain-Driven Design (No LangChain/LlamaIndex)

**Architecture Pattern:** Clean Architecture with dependency injection

**Why Custom Orchestration:**
- **Full Control**: Complete ownership of the RAG pipeline
- **Multi-tenant Focus**: Built specifically for organizational data isolation
- **Performance**: Optimized for enterprise-scale document processing
- **Flexibility**: Easy to extend and customize for specific business needs

**Core Services:**
- **RagService**: Pure business logic for RAG operations
- **ConversationalRagService**: RAG with conversation memory
- **DocumentService**: Document management and ingestion

**Key Features:**
- **Tenant Isolation**: Multi-tenant data segregation
- **Conversation Memory**: Context-aware multi-turn conversations
- **Chunking Strategy**: 800-token chunks with 120-token overlap
- **Confidence Scoring**: Relevance-based confidence metrics
- **Custom Prompting**: Tailored prompts for organizational intelligence

## 🔄 Orchestration Comparison

### **Custom Orchestration vs. LangChain/LlamaIndex**

| Aspect | Living Twin (Custom) | LangChain/LlamaIndex |
|--------|---------------------|---------------------|
| **Architecture** | Domain-driven, clean architecture | Framework-based, opinionated |
| **Multi-tenancy** | Built-in tenant isolation | Requires custom implementation |
| **Performance** | Optimized for enterprise scale | General-purpose, may have overhead |
| **Flexibility** | Full control over every component | Constrained by framework patterns |
| **Learning Curve** | Steeper initial learning | Faster to get started |
| **Customization** | Unlimited customization | Limited by framework capabilities |
| **Dependencies** | Minimal external dependencies | Heavy framework dependencies |

### **Why Custom Orchestration?**

**Advantages:**
- **Enterprise Focus**: Built specifically for organizational intelligence
- **Multi-tenant Native**: Tenant isolation at the core architecture level
- **Performance Optimized**: No framework overhead, direct control
- **Security**: Complete control over data flow and processing
- **Scalability**: Can optimize for specific use cases and scale patterns

**Trade-offs:**
- **Development Time**: More initial development effort required
- **Maintenance**: Need to maintain custom orchestration logic
- **Community**: Less community support compared to popular frameworks

## 🚀 Deployment Options

### Development Stack
```bash
# Local development with mock data
LOCAL_EMBEDDINGS=true
LLM_PROVIDER=stub
RAG_ONLY=true
USE_LOCAL_MOCK=true
```

### Production Stack
```bash
# Production with OpenAI
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

### Hybrid Stack
```bash
# Local embeddings + cloud LLM
LOCAL_EMBEDDINGS=true
LLM_PROVIDER=openai
```

### Privacy-First Stack
```bash
# Everything local
LOCAL_EMBEDDINGS=true
LLM_PROVIDER=ollama
OLLAMA_MODEL=mistral-7b
```

## 📊 Performance Characteristics

### Embedding Performance
| Provider | Model | Dimensions | Speed | Quality | Cost |
|----------|-------|------------|-------|---------|------|
| OpenAI | text-embedding-3-small | 1536 | Fast | Excellent | $0.02/1M tokens |
| SBERT | all-MiniLM-L6-v2 | 384 | Very Fast | Good | Free |
| Stub | Zero vectors | 384 | Instant | None | Free |

### Vector Search Performance
- **Neo4j Vector Index**: Sub-100ms for 1M+ documents
- **Cosine Similarity**: Industry-standard relevance scoring
- **Multi-tenant**: Isolated search per tenant
- **Hybrid Queries**: Vector + graph traversal

### LLM Generation Performance
| Provider | Model | Speed | Quality | Cost | Privacy |
|----------|-------|-------|---------|------|---------|
| OpenAI | gpt-4o-mini | Fast | Excellent | $0.15/1M tokens | Cloud |
| Ollama | llama3 | Medium | Good | Free | Local |
| Stub | None | Instant | None | Free | Local |

## 🔒 Security & Privacy Features

### Data Isolation
- **Tenant-based Segregation**: Complete data isolation per organization
- **User-level Permissions**: Role-based access control
- **Audit Logging**: Track all data access and modifications

### Privacy Options
- **Local Processing**: All AI processing on-premises
- **No Data Leakage**: Embeddings and vectors stay in your infrastructure
- **Compliance Ready**: GDPR, HIPAA, SOC2 compatible

### Authentication
- **Firebase Auth**: Enterprise-grade authentication
- **JWT Tokens**: Secure API access
- **Multi-factor Support**: Enhanced security

## 🛠️ Integration Capabilities

### API Endpoints
```bash
# Document ingestion
POST /api/v1/ingest/text
POST /api/v1/ingest/file

# RAG queries
POST /api/v1/query
POST /api/v1/conversational/query

# Debug and monitoring
GET /api/v1/debug/rag
GET /api/v1/health
```

### SDK Support
- **Python**: Native FastAPI client
- **JavaScript/TypeScript**: REST API client
- **Flutter**: Mobile app integration
- **React**: Admin web interface

### Event-Driven Architecture
- **Pub/Sub Events**: Asynchronous processing
- **Job Queues**: Background document processing
- **Webhooks**: Real-time notifications

## 📈 Scaling Considerations

### Horizontal Scaling
- **Neo4j Clustering**: Multi-node database setup
- **API Load Balancing**: Multiple FastAPI instances
- **Redis Caching**: Session and query caching

### Vertical Scaling
- **GPU Acceleration**: For local LLM inference
- **Memory Optimization**: Efficient embedding storage
- **Index Optimization**: Tuned vector search performance

### Cost Optimization
- **Hybrid Deployment**: Mix of local and cloud resources
- **Caching Strategy**: Reduce redundant API calls
- **Batch Processing**: Efficient bulk operations

## 🎯 Use Cases & Applications

### Organizational Intelligence
- **Document Q&A**: Ask questions about company documents
- **Policy Compliance**: Automated policy interpretation
- **Knowledge Discovery**: Find relevant information across documents

### Conversational AI
- **Multi-turn Conversations**: Context-aware chat
- **Conversation Memory**: Remember previous interactions
- **Personalized Responses**: User-specific recommendations

### Analytics & Insights
- **Document Analysis**: Extract key insights from documents
- **Trend Detection**: Identify patterns across documents
- **Recommendation Engine**: Suggest relevant content

## 🔧 Development & Testing

### Local Development
```bash
# Quick start with mock data
make dev-mock

# Full stack with Firebase emulators
make dev-full

# Local LLM testing
ollama serve
make dev-ollama
```

### Testing Strategy
- **Unit Tests**: Domain logic testing
- **Integration Tests**: API endpoint testing
- **End-to-End Tests**: Full RAG pipeline testing
- **Performance Tests**: Load and stress testing

### Monitoring & Observability
- **Health Checks**: Service availability monitoring
- **Metrics Collection**: Performance and usage metrics
- **Logging**: Comprehensive audit trails
- **Alerting**: Proactive issue detection

## 🚀 Getting Started

### Quick Setup
```bash
# Clone and setup
git clone <repo>
cd living_twin_monorepo
make dev-setup

# Start services
make quick-start

# Access interfaces
# Neo4j: http://localhost:7474
# API: http://localhost:8000
# Admin: http://localhost:5173
```

### Configuration
```bash
# Copy environment template
cp .env.example .env

# Configure your stack
OPENAI_API_KEY=your_key_here
LLM_PROVIDER=openai  # or ollama, stub
LOCAL_EMBEDDINGS=false  # or true for local
```

### First Query
```bash
# Test the RAG pipeline
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are our company policies?",
    "tenant_id": "demo"
  }'
```

---

## 📚 Additional Resources

- **Architecture Diagrams**: [AI_AGENT_ARCHITECTURE_DIAGRAMS.md](AI_AGENT_ARCHITECTURE_DIAGRAMS.md)
- **Development Guide**: [DEVELOPMENT_ENVIRONMENT_SETUP.md](DEVELOPMENT_ENVIRONMENT_SETUP.md)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Neo4j Browser**: [http://localhost:7474](http://localhost:7474)

---

*This RAG stack provides enterprise-grade capabilities while maintaining flexibility for different deployment scenarios and privacy requirements.*
