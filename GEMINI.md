# GEMINI.md

This file provides guidance to Gemini when working with code in this repository.

## Project Overview

This is an **Organizational Twin System** - an intelligent human-AI collaborative platform that creates digital twins of organizations, enabling sophisticated decision-making through AI agents, human-in-the-loop workflows, and adaptive communication patterns built on Temporal orchestration.

The system creates an AI-powered digital representation that learns your team's communication patterns, personalities, and cultural dynamics, orchestrating complex workflows where AI agents and humans collaborate seamlessly.

## Repository Structure

The repository contains a sophisticated multi-language implementation focused on Python and TypeScript:

- `shared/` - Shared components and libraries
  - `models/` - Pydantic data models and base classes
  - `config/` - Configuration management system
  - `prompts/` - AI prompt template system with Jinja2 templating
  - `temporal_client/` - Temporal connection utilities
- `python/` - Primary backend implementation with Temporal SDK
  - `src/workflows.py` - Temporal workflow definitions
  - `src/activities.py` - Temporal activity implementations
  - `src/worker.py` - Temporal worker process
  - `src/organizational_twin.py` - Core intelligence system
  - `src/agents/` - AI agent implementations
  - `pyproject.toml` - Python dependencies and poe scripts
- `typescript/` - Frontend and Node.js services
  - `src/workflows.ts` - Workflow definitions
  - `src/activities.ts` - Activity implementations
  - `src/worker.ts` - Worker process
  - `package.json` - Node.js dependencies with pnpm
- `Makefile` - Development automation and quality gates
- `compose.yaml` - Docker services for PostgreSQL, Neo4j, MinIO, Temporal

## Development Commands

### Root Level Commands (Quality & Infrastructure)
- `make check` - Check all dependencies and servers are properly installed
- `make install` - Install dependencies for Python and TypeScript modules
- `make build` - Build all modules
- `make test` - Run comprehensive tests
- `make lint` - Lint all modules with ruff and ESLint
- `make typecheck` - Type check with mypy and TypeScript compiler
- `make format` - Format code with ruff and Prettier
- `make quality` - Run all quality gates including prompt validation
- `make pre-commit-run` - Run pre-commit hooks
- `make docker-up` - Start all services (PostgreSQL, Neo4j, MinIO, Temporal)
- `make docker-down` - Stop all Docker services

### Temporal Server
- `make temporal` - Start local Temporal server (WebUI at localhost:8233)
- `make temporal-stop` - Stop running Temporal server
- `docker compose up temporal` - Run Temporal via Docker

### Prompt Management
- `make prompts-validate` - Validate all AI prompt templates
- `make prompts-list` - List available prompts
- `make prompts-stats` - Show prompt usage statistics
- `make prompts-show PROMPT_ID=<id>` - Show specific prompt details
- `make prompts-test PROMPT_ID=<id> VARS='key=value'` - Test prompt rendering

### Python Development (from python/ directory)
- `uv sync` - Install dependencies
- `uv run poe dev` - Run worker with file watcher (recommended for development)
- `uv run poe worker` - Run worker without file watcher
- `uv run poe starter` - Run workflow starter
- `uv run poe test` - Run tests
- `uv run poe lint` - Run ruff linting
- `uv run poe format` - Format code with ruff
- `uv run poe typecheck` - Type check with mypy

### TypeScript Development (from typescript/ directory)
- `pnpm install` - Install dependencies
- `pnpm run build` - Compile TypeScript
- `pnpm run build.watch` - Compile with watch mode
- `pnpm run worker:watch` - Run worker with auto-reload (recommended for development)
- `pnpm run worker` - Run worker
- `pnpm run starter` - Run workflow starter
- `pnpm test` - Run tests with Mocha
- `pnpm run lint` - Run ESLint
- `pnpm run format` - Format code with Prettier

## Core Architecture

### Organizational Twin Intelligence

The heart of the system is the **Organizational Twin** - an AI system that builds comprehensive understanding of your organization:

- **🧠 Behavioral Modeling**: Learns individual and team decision-making patterns
- **🗣️ Communication Intelligence**: Adapts to personal and cultural communication styles
- **📋 Process Optimization**: Continuously improves workflow efficiency based on outcomes
- **🔗 Relationship Mapping**: Understands organizational structure and stakeholder relationships

### AI Agent System

Intelligent agent architecture where AI agents understand organizational roles and can seamlessly collaborate with or substitute for human team members:

- **Strategic Decision Agents**: Handle high-level planning and strategic choices
- **Communication Agents**: Manage personalized messaging and stakeholder engagement
- **Document Processing Agents**: Analyze, summarize, and extract insights from documents
- **Consensus Building Agents**: Facilitate agreement across diverse stakeholders
- **Cultural Intelligence Agents**: Adapt communication style to organizational culture

### Temporal Workflow Components

Each implementation follows sophisticated Temporal patterns optimized for human-AI collaboration:

- **Workflows** (`workflows.py/ts`) - Orchestrate complex decision-making processes with human-in-the-loop
- **Activities** (`activities.py/ts`) - Handle AI processing, external service calls, and document operations
- **Worker** (`worker.py/ts`) - Long-running processes that execute workflows and activities
- **Starter** (`starter.py/ts`) - Clients that trigger workflow execution with organizational context

### Storage Architecture

- **PostgreSQL**: Structured organizational data, user profiles, decision history
- **Neo4j**: Knowledge graph for relationships, organizational intelligence, and pattern recognition
- **MinIO**: S3-compatible document storage for media files and large data objects
- **Redis**: Caching and session management

### Key Files and Components

- **Organizational Twin** (`organizational_twin.py`) - Core intelligence system
- **Prompt System** (`shared/prompts/`) - AI prompt templates with Jinja2 templating
- **Base Models** (`shared/models/`) - Strongly-typed Pydantic data models
- **Configuration** (`shared/config/`) - Environment and service configuration
- **Docker Compose** (`compose.yaml`) - Complete infrastructure stack

## Temporal Best Practices for Organizational Intelligence

Following these patterns ensures your organizational workflows are:
- **Deterministic workflows** - Can replay without side effects
- **Fault tolerant** - Automatic retries and recovery from failures
- **Observable** - Complete visibility into decision-making processes
- **Scalable** - Add more workers and agents as needed
- **Maintainable** - Clear separation between orchestration and business logic

### 1. Workflow as Intelligent Orchestrator
- Workflow orchestrates human-AI collaboration patterns
- Manages decision escalation and consensus building
- Handles timeout and backup scenarios for absent humans
- Tracks organizational context and learning

### 2. Activities Handle Specialized Operations
- AI agent interactions and prompt processing
- Document analysis and storage operations
- External service integrations (email, calendar, etc.)
- Database operations and knowledge graph updates
- Human interaction management

### 3. Human-in-the-Loop Patterns
- **Collaborative Decision Making**: Humans provide strategic input while AI handles analysis
- **Intelligent Escalation**: AI manages routine decisions but escalates complex issues
- **Backup and Coverage**: AI agents step in when humans are unavailable
- **Continuous Learning**: System learns from human decisions to improve recommendations

### 4. Proper Data Transfer Objects (DTOs)
- Strong typing with Pydantic models for Python
- Comprehensive interfaces for TypeScript
- Organizational context embedded in all data structures
- Serializable models compatible with Temporal

### 5. AI-Assisted Communication Patterns
- Personality-aware message generation using prompt templates
- Cultural intelligence for organizational communication
- Context-aware escalation and routing
- Adaptive messaging based on recipient preferences

## Development Workflow

1. Install dependencies: `make install`
2. Start infrastructure: `make docker-up` (PostgreSQL, Neo4j, MinIO, Temporal)
3. Validate prompts: `make prompts-validate`
4. Run quality checks: `make quality`
5. Navigate to language directory for development
6. Run worker with watch mode for real-time development
7. Run starter to trigger organizational workflows
8. Monitor workflows in Temporal WebUI at localhost:8233
9. Access MinIO console at localhost:9001 for document management

## Code Style and Standards

### Python
- Use **idiomatic Python** with comprehensive type hints
- **Pydantic v2** for all data validation and organizational models
- **Strong typing** with mypy strict mode
- Use `ruff` for linting and formatting
- Async/await patterns for all I/O operations
- Context managers for resource handling

### TypeScript
- Use **strict TypeScript** with comprehensive type annotations
- **pnpm** as package manager
- Follow idiomatic TypeScript patterns with proper generics
- Use interfaces for organizational data structures
- Implement proper error handling patterns

### Prompt Management
- **YAML-based definitions** for all AI prompts
- **Jinja2 templating** with organizational context
- Comprehensive validation and testing
- Version control and usage analytics
- Role-based prompt organization

## Testing and Quality

- **Comprehensive test coverage** for organizational logic
- **Prompt validation** integrated into quality pipeline
- **Type checking** with mypy and TypeScript compiler
- **Linting** with ruff and ESLint
- **Integration tests** for human-AI collaboration patterns
- **End-to-end testing** of organizational workflows

## Deployment and Infrastructure

### Docker and Container Orchestration
- Multi-stage Dockerfiles optimized for production
- Docker Compose for complete development stack
- Health checks for all services
- Proper signal handling for graceful shutdowns

### Google Cloud Platform with Terraform
- Infrastructure as Code using Terraform modules
- Cloud Run for serverless container deployment
- Cloud SQL for PostgreSQL and managed Redis
- Google Cloud Storage integration with MinIO compatibility
- Secrets management with Google Secret Manager

## Important Instructions

### Code Quality Requirements
- All code must pass `make quality` checks before deployment
- Prompt templates must be validated with `make prompts-validate`
- Comprehensive type hints required for all Python functions
- Strong typing required for all TypeScript interfaces

### System Architecture Guidelines
- **Prefer editing existing files** over creating new ones
- Follow established patterns for human-AI collaboration
- Use organizational context in all decision-making logic
- Implement proper backup and escalation patterns
- Ensure all AI interactions use validated prompt templates

### Development Priorities
1. **Human-AI Collaboration**: Focus on seamless integration patterns
2. **Organizational Intelligence**: Build systems that learn and adapt
3. **Communication Excellence**: Ensure culturally-aware messaging
4. **Reliability**: Robust error handling and backup systems
5. **Observability**: Complete visibility into organizational processes

This system represents the cutting edge of organizational intelligence, combining the reliability of Temporal workflows with sophisticated AI agents that truly understand and enhance human collaboration patterns.
