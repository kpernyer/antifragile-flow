# Living Twin — Web Platform Development Guide

This is the development stack for **Living Twin** — a RAG-enabled, Neo4j-backed, multi-tenant "organizational twin" web platform.

## 📜 System Architecture

![System Architecture](https://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/kpernyer/living-twin-monorep/main/docs/v0.1/system/system_architecture.puml)

### Microservices Architecture

- **API Services**: FastAPI + Strawberry GraphQL backend with strategic intelligence
- **Web Applications**: React + TypeScript admin interface with real-time updates
- **Infrastructure**: GCP Cloud Run, Firebase, Neo4j graph database + vector search
- **External Services**: OpenAI GPT-4o-mini, Firebase Auth, Sentry monitoring

📋 [**View Detailed Documentation**](docs/v0.1/README.md) | 🔍 [**System Analysis**](docs/v0.1/system/SYSTEM.md) | 📚 [**Complete Docs Index**](DOCUMENTATION.md)

## 📚 Documentation & Guides

> 🚀 **Start Here:** [**Complete Documentation Index**](DOCUMENTATION.md) - Your gateway to 61+ organized guides, tutorials, and references

### **Quick Navigation:**
- **[Getting Started](docs/getting-started/)** - New user onboarding and setup guides
- **[API Documentation](docs/api/)** - REST API, GraphQL, and PubSub event guides
- **[AI/ML Implementation](docs/ai-ml/)** - RAG, fine-tuning, and strategic AI guides
- **[Architecture](docs/architecture/)** - System design and technical architecture
- **[Development](docs/development/)** - Development workflows and tools
- **[Deployment](docs/deployment/)** - Production deployment and operations

### **Key Features:**
- **Strategic AI** - Multi-tenant organizational intelligence with SWOT/Porter's analysis
- **Hybrid RAG** - Fine-tuned DNA models + dynamic strategy RAG
- **GraphQL API** - Modern API with real-time strategic insights (Strawberry)
- **Containerized Stack** - Docker-based development with hot reload
- **Web-First Development** - Fast iteration with React/TypeScript
- **Business Presentations** - Complete pitch deck collection

### **📱 Mobile Development:**
Mobile development has been moved to a separate repository to enable faster web iteration. The mobile app will consume the same REST and GraphQL APIs when ready, ensuring consistency across platforms.

### **🚀 Quick API Access:**
- **REST API**: <http://localhost:8000/docs> (Swagger UI)
- **GraphQL**: <http://localhost:8000/graphql> (GraphQL Playground)
- **API Documentation**: [Complete API Guides](docs/api/)

## 1️⃣ Prerequisites

- **Docker + Docker Compose**
- **Python 3.11+** (3.13 not recommended — pydantic-core build issues)
- **Node.js 20+** + npm
- (Optional) **Ollama** for local LLM testing:

  ```bash
  brew install ollama
  ollama pull llama3
  ```

- OpenAI account with API key (if using OpenAI models)

> 📋 **New to the project?** Start with our [**Complete Documentation Index**](DOCUMENTATION.md) for comprehensive guides and [**Getting Started**](docs/getting-started/) for automated installation scripts and containerization strategies for macOS and Linux.

## 2️⃣ One-time setup

```bash
# Clone repo
git clone <your-repo-url> living_twin_monorepo
cd living_twin_monorepo

# Quick setup (recommended)
make dev-setup

# Or manual setup:
# Env
cp .env.example .env
# Fill in:
# OPENAI_API_KEY=sk-...
# Adjust Neo4j creds if needed (dev default: neo4j/password)

# Install all dependencies
make install-deps

# Start services and initialize
make docker-up
make seed-db
```

## 3️⃣ Verify setup

- **Neo4j** — <http://localhost:7474> → login `neo4j` / `password`

  ```cypher
  SHOW INDEXES WHERE name='docEmbeddings';
  ```

- **Python deps**

  ```bash
  .venv/bin/python -c "import fastapi, neo4j, sentence_transformers; print('✅ Python OK')"
  ```

- **React admin**

  ```bash
  make dev-react
  # Visit http://localhost:5173
  ```

- **OpenAI key check**

  ```bash
  make check-billing-py
  ```

## 4️⃣ Run modes

### Quick Start (Recommended)

```bash
make quick-start
```

- Sets up everything and starts all services
- Includes sample data and Neo4j initialization

### Development Mode

```bash
make docker-up    # Start all services
make api-dev      # Run API in development mode
make web-dev      # Run admin web interface
make mobile-dev   # Run Flutter mobile app
```

### Local (no OpenAI cost)

```bash
# Set in .env: LOCAL_EMBEDDINGS=1, RAG_ONLY=1
make docker-up
```

- Local embeddings: `all-MiniLM-L6-v2` (384-dim)
- Stub LLM: RAG_ONLY=1 (just returns top snippets)

### OpenAI (cheap dev)

```bash
# Set in .env: LLM_PROVIDER=openai
make docker-up
```

- LLM: `gpt-4o-mini`
- Embeddings: `text-embedding-3-small` (1536-dim)

### Ollama (local LLM)

```bash
ollama serve &
# Set in .env: LLM_PROVIDER=ollama
make docker-up
```

## 5️⃣ Demo flow

1. **Quick Start**:

   ```bash
   make quick-start
   ```

2. **Access the interfaces**:
   - **Admin Web**: <http://localhost:5173>
   - **API Docs**: <http://localhost:8000/docs>
   - **Neo4j Browser**: <http://localhost:7474>

3. **Test the system**:
   - **Ingest a snippet**
     - Paste: "Fix bug X and raise NPS by 5 points in Q3"
     - Title: "Retention Strategy Q3"
     - Click **Ingest**
   - **Ask a question**
     - "How do we improve retention according to the latest plan?"
     - Answer should cite `[1] Retention Strategy Q3`
   - **Debug RAG**
     - Show retrieved chunks + scores, grouped by source

4. **Test authentication**:
   - Sign in with `john@acme.com` (auto-binds to Acme Corporation)
   - Try invitation code: `APRIO-ACME-INV123456789`

## 6️⃣ CLI ingestion/query

```bash
# Ingest
curl -s -X POST http://localhost:8000/ingest/text \
  -H 'Content-Type: application/json' \
  -d '{"title":"Retention Strategy Q3","text":"Fix bug X and raise NPS by 5 points.","tenantId":"demo"}' | jq

# Recent
curl -s http://localhost:8000/ingest/recent | jq

# Query
curl -s -X POST http://localhost:8000/query \
  -H 'Content-Type: application/json' \
  -d '{"question":"How do we improve retention?", "k":5, "tenantId":"demo"}' | jq

# Health check
curl -s http://localhost:8000/healthz | jq
```

## 7️⃣ Common gotchas

| Issue | Fix |
|-------|-----|
| **`No such vector schema index: docEmbeddings`** | Run `make neo4j-init` |
| **Quota exceeded** from OpenAI | Enable Pay-as-you-go in OpenAI billing, or switch to LOCAL_EMBEDDINGS=1 |
| **pydantic-core build error** | Use Python 3.11 or 3.12 |
| **Auth error to Neo4j** | Reset volume: `docker compose down -v && make neo4j-up && make neo4j-init` |
| **Vectors dim mismatch** | Re-ingest docs after changing embedding model |

## 8️⃣ Environment toggles

In `.env`:

```bash
LLM_PROVIDER=openai       # openai | ollama | stub
LLM_MODEL=gpt-4o-mini
EMBEDDINGS_MODEL=text-embedding-3-small
LOCAL_EMBEDDINGS=0        # 1 = use sentence-transformers locally
LOCAL_EMBEDDINGS_MODEL=sentence-transformers/all-MiniLM-L6-v2
RAG_ONLY=0                # 1 = skip LLM, just return top snippets

# Ollama settings
OLLAMA_BASE=http://localhost:11434
OLLAMA_MODEL=llama3
```

## 9️⃣ Development Tools

### **Testing**

```bash
make test              # Run all tests
make test-unit         # Unit tests only
make test-integration  # Integration tests only
make lint              # Run linters
make format            # Format code
```

### **Database Management**

```bash
make seed-db           # Populate with sample data
make init-schema       # Initialize Neo4j schema
make validate-schema   # Validate Neo4j constraints
```

### **Monitoring & Debugging**

```bash
make docker-logs       # View container logs
make status            # Check service status
make logs-api          # API logs (production)
make logs-worker       # Worker logs (production)
```

### **Cost Management**

```bash
make check-costs ENV=dev PROJECT=your-project
make cost-optimize-dev PROJECT=your-project
make scale-down-staging PROJECT=your-project
```

## 🔟 Testing & CI/CD

### **Automated Testing**

The project includes comprehensive test suites:

- **Unit Tests**: `apps/api/tests/test_services.py`, `test_routes.py`
- **Integration Tests**: `apps/api/tests/test_integration.py`
- **Load Testing**: `tools/scripts/load-test.js` (k6)

### **GitHub Actions**

- **Continuous Integration**: `.github/workflows/deploy-cloud-run.yml`
- **Automated Testing**: Runs on every PR and push
- **Security Scanning**: Trivy vulnerability scanner
- **Performance Testing**: k6 load tests on staging
- **Deployment**: Automated deployment to Cloud Run

### **Quality Assurance**

```bash
make lint              # Code linting (flake8, mypy)
make test              # Full test suite
make format            # Code formatting (black, isort)
```

## 1️⃣1️⃣ Next steps

- Add PDF/DOCX ingestion (`unstructured` lib)
- Wire API Gateway + Firebase Auth in staging
- Add multi-tenant plugin marketplace
- Extend graph schema for goals/teams/projects links
- Introduce agents with **Ping / Act / Aggregate** modes

## 📚 Documentation

For detailed documentation on specific topics, see the [`docs/`](docs/) directory:

### Architecture & Design

- [**Architecture Overview**](docs/ARCHITECTURE.md) - System architecture and design patterns
- [**Schema Consistency Guide**](docs/SCHEMA_CONSISTENCY_GUIDE.md) - Data models and schema management
- [**Configuration Sync**](docs/CONFIGURATION_SYNC.md) - Environment and configuration management

### Development & Deployment

- [**Development Environment Setup**](docs/DEVELOPMENT_ENVIRONMENT_SETUP.md) - External tools, containerization strategies, and automated setup scripts
- [**Local Development Setup**](docs/README_LOCAL_DEV.md) - Detailed local development guide
- [**Deployment Setup**](docs/DEPLOYMENT_SETUP.md) - Production deployment instructions
- [**Deployment Sprint Guide**](docs/DEPLOYMENT_SPRINT_GUIDE.md) - Step-by-step deployment process
- [**Scaling & Cost Guide**](docs/SCALING_AND_COST_GUIDE.md) - Performance optimization and cost management

### Features & Implementation

- [**Conversational Evolution Guide**](docs/CONVERSATIONAL_EVOLUTION_GUIDE.md) - Chat and conversation features
- [**Conversational Implementation Guide**](docs/CONVERSATIONAL_IMPLEMENTATION_GUIDE.md) - Technical implementation details
- [**PubSub Event System**](docs/PUBSUB_EVENT_SYSTEM.md) - Event-driven architecture
- [**PDF/DOCX Ingestion**](docs/pdf-docx-ingestion.md) - Document processing capabilities

### Security & Operations

- [**Security & Performance Testing**](docs/SECURITY_AND_PERFORMANCE_TESTING.md) - Testing strategies and security
- [**Tenant Isolation & Authorization**](docs/TENANT_ISOLATION_AND_AUTHORIZATION.md) - Multi-tenant security

### Release Notes

- [**README Patch Notes**](docs/README_PATCH.md) - Recent changes and updates

### Development Workflow

- [**Git Setup Guide**](docs/GIT_SETUP_GUIDE.md) - Repository initialization and Git best practices
- [**GitHub Setup Guide**](docs/GITHUB_SETUP_GUIDE.md) - GitHub integration and CI/CD configuration

Each document provides in-depth coverage of its respective topic with implementation details, best practices, and troubleshooting guides.
