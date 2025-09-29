# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Structure

This is a Living Twin monorepo with the following structure:
- `apps/admin_web/` - React admin interface (Vite + TypeScript)
- `apps/api/` - FastAPI backend with GraphQL and vector search
- `packages/gcp_firebase/` - Infrastructure code (Terraform)
- `docs/` - Comprehensive documentation
- `docker/` - Container configurations

## Essential Commands

**Development (Containerized - Recommended)**:
```bash
make quick-start        # Complete setup and start all services
make dev-full          # Start full containerized environment
make api-dev           # API with hot reload
make web-dev           # React admin interface
make docker-up         # Start all services (Neo4j, Redis, API, Web)
```

**Local Development (OS-level)**:
```bash
make api-dev-local     # Run API with uv locally (requires Neo4j/Redis running)
make web-dev-local     # Run React app with pnpm
```

**Code Quality**:
```bash
make lint              # All linters (Python + JS/TS)
make format            # Auto-format all code
make test              # All tests
make test-api          # API tests only
make test-web          # Web tests only
```

**Dependencies**:
```bash
make install-deps      # Install all dependencies
make fix-deps          # Fix Python dependency conflicts
```

**Database**:
```bash
make neo4j-init        # Initialize Neo4j schema and constraints
make seed-db           # Populate with sample data
```

## Architecture Overview

**Technology Stack**:
- **Backend**: FastAPI + Strawberry GraphQL, Python 3.11+
- **Frontend**: React 18 + TypeScript + Vite
- **Database**: Neo4j (graph + vector search) + Redis (cache/queue)
- **AI/ML**: OpenAI GPT-4o-mini, LangChain, sentence-transformers
- **Auth**: Firebase Auth + Google Cloud services
- **Infrastructure**: Docker + GCP Cloud Run + Firebase Hosting

**Key Architectural Patterns**:
- Clean Architecture with domain-driven design
- Custom dependency injection system (`apps/api/app/di.py`)
- Multi-tenant architecture with tenant isolation
- RAG (Retrieval-Augmented Generation) system with vector embeddings
- Dual GraphQL + REST API approach

**Package Management**:
- **Python**: `uv` (primary) + pip fallback
- **Node.js**: `pnpm` (workspace configuration)

## Development Workflow

**Environment Setup**:
- Containerized development is recommended via `make quick-start`
- Requires Docker and Docker Compose
- Environment variables: copy `.env.development.example` to `.env`

**Code Style**:
- **Python**: Black (line length 100), isort, flake8, mypy with strict typing
- **TypeScript**: ESLint with TypeScript rules, Prettier integration

**Testing**:
- API tests: pytest with comprehensive fixtures
- Web tests: Standard React testing setup

**Database Development**:
- Neo4j runs on port 7687 (bolt) / 7474 (browser)
- Redis runs on port 6379
- Use `make seed-db` for sample data
- Vector embeddings stored alongside graph data

## Important Notes

**AI/ML Components**:
- Supports multiple AI providers (OpenAI, Ollama, local embeddings)
- Document ingestion pipeline for PDF/DOCX processing
- Semantic search with vector similarity
- LangChain integration for RAG workflows

**Firebase Integration**:
- Authentication handled by Firebase Auth
- Cloud Functions in `packages/gcp_firebase/`
- Terraform infrastructure-as-code

**Monitoring & Observability**:
- Sentry integration for error tracking
- Structured logging with structlog
- Health check endpoints available

## Documentation

Comprehensive documentation available in `docs/`:
- `docs/getting-started/` - Setup guides
- `docs/architecture/` - System design
- `docs/ai-ml/` - AI/ML implementation details
- `docs/development/` - Development workflows
- `docs/deployment/` - Production deployment
- `docs/api/` - API documentation

Refer to `DOCUMENTATION.md` for complete navigation of available docs.
