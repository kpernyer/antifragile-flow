# Kolomolo Hackathon - Organizational Twin System

An intelligent human-AI collaborative platform that creates digital twins of organizations, enabling sophisticated decision-making through AI agents, human-in-the-loop workflows, and adaptive communication patterns built on Temporal orchestration.

## 🎯 Overview

Kolomolo Hackathon transforms how organizations make decisions by creating an **Organizational Twin** - an AI-powered digital representation that learns your team's communication patterns, personalities, and cultural dynamics. The system orchestrates complex workflows where AI agents and humans collaborate seamlessly, with intelligent backup when team members are unavailable.

### Key Capabilities

- **🤖 Intelligent Agent System**: AI agents that understand roles, responsibilities, and decision-making patterns
- **🔄 Human-in-the-Loop Workflows**: Sophisticated orchestration where humans and AI collaborate on strategic decisions
- **💬 AI-Assisted Communication**: The Organizational Twin learns individual personalities, communication styles, and cultural nuances
- **🔧 Adaptive Backup**: AI agents seamlessly assist or take over when humans are late, on leave, or unavailable
- **📊 Document Intelligence**: Automated processing and analysis using MinIO document storage
- **🎨 Prompt Management**: Sophisticated AI prompt templates with Jinja2 templating for consistent, context-aware responses

## 🏗️ Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    Organizational Twin System                    │
├─────────────────────────────────────────────────────────────────┤
│  🤖 AI Agents        │  👥 Human Users    │  🔄 Temporal Engine  │
│  - Decision Makers   │  - Strategic Input │  - Workflow Orchestration │
│  - Communicators     │  - Approvals       │  - State Management │
│  - Document Processors│ - Oversight       │  - Retry Logic      │
├─────────────────────────────────────────────────────────────────┤
│               📡 Organizational Twin Intelligence                │
│  - Personality Learning  │  - Culture Adaptation  │  - Pattern Recognition │
├─────────────────────────────────────────────────────────────────┤
│  💾 Data Layer                      │  📄 Document Storage      │
│  - PostgreSQL (Relational)          │  - MinIO (Object Storage) │
│  - Neo4j (Knowledge Graph)          │  - Document Intelligence  │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **🐍 Python**: Primary backend language with Temporal SDK, AI integration, and data processing
- **⚡ TypeScript**: Frontend interfaces and Node.js services for real-time interaction
- **⏱️ Temporal**: Workflow orchestration engine ensuring reliable, long-running processes
- **🗄️ PostgreSQL**: Primary database for structured organizational data
- **🕸️ Neo4j**: Knowledge graph for relationships and organizational intelligence
- **📦 MinIO**: S3-compatible object storage for documents and media
- **🎨 Jinja2**: Advanced prompt templating with organizational context

## 🤖 Agent System

The heart of Antifragile Flow is its intelligent agent architecture where AI agents understand organizational roles and can seamlessly collaborate with or substitute for human team members.

### Agent Types

- **Strategic Decision Agents**: Handle high-level planning and strategic choices
- **Communication Agents**: Manage personalized messaging and stakeholder engagement
- **Document Processing Agents**: Analyze, summarize, and extract insights from documents
- **Consensus Building Agents**: Facilitate agreement across diverse stakeholders
- **Cultural Intelligence Agents**: Adapt communication style to organizational culture

### Human-AI Collaboration Patterns

1. **🔄 Collaborative Decision Making**: Humans provide strategic input while AI handles analysis and coordination
2. **⚡ Intelligent Escalation**: AI manages routine decisions but escalates complex issues to humans
3. **🛡️ Backup and Coverage**: AI agents step in when humans are unavailable, maintaining business continuity
4. **📈 Continuous Learning**: The system learns from human decisions to improve future recommendations

## 💬 AI-Assisted Communication

The Organizational Twin continuously learns and adapts to your team's unique communication patterns:

### Personality Learning
- **Individual Styles**: Learns how each team member prefers to communicate
- **Decision Patterns**: Understands individual decision-making approaches
- **Response Preferences**: Adapts message timing, length, and formality

### Cultural Intelligence
- **Team Dynamics**: Recognizes formal vs informal communication contexts
- **Organizational Values**: Aligns messaging with company culture and values
- **Stakeholder Relationships**: Understands power dynamics and relationship nuances

### Adaptive Messaging
- **Context-Aware Prompts**: Uses organizational knowledge to craft appropriate messages
- **Personalized Content**: Tailors communication style to recipient preferences
- **Cultural Sensitivity**: Ensures messages align with organizational culture

## 🔄 Human-in-the-Loop Workflows

Sophisticated workflow orchestration that seamlessly blends human insight with AI efficiency:

### Strategic Decision Workflow Example
```
1. 🎯 Strategic Proposal (CEO/AI Agent)
   ↓
2. 🤖 Organizational Twin Analysis
   ↓
3. 👥 Multi-Stakeholder Input (VPs)
   ↓ (AI agents backup absent VPs)
4. 📊 Consensus Building (AI-facilitated)
   ↓
5. ✅ Final Decision (Human oversight)
```

### Intelligent Backup System
- **Absence Detection**: Monitors human availability and response times
- **Gradual Escalation**: AI provides increasing assistance based on urgency
- **Seamless Handoff**: Smooth transitions between AI and human control
- **Context Preservation**: Maintains full context when humans return

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+** with uv package manager
- **Node.js 18+** with pnpm
- **Docker** and Docker Compose
- **PostgreSQL** database
- **MinIO** object storage
- **Temporal** server (local or cloud)

### Installation

1. **Clone and install dependencies**:
```bash
git clone <repository-url>
cd antifragile-flow
make install
```

2. **Start infrastructure services**:
```bash
# Start PostgreSQL, MinIO, and Temporal
make docker-up

# Or start individually
make temporal
docker compose up postgres minio
```

3. **Run the system**:
```bash
# Terminal 1: Start Temporal worker
uv run workers/worker.py

# Terminal 2: Trigger workflows
uv run workflows/starter.py

# Terminal 3: Start frontend (optional)
cd frontend
pnpm start
```

### Accessing Services

- **Temporal WebUI**: http://localhost:8233 (workflow monitoring)
- **MinIO Console**: http://localhost:9001 (document storage)
- **System Logs**: Real-time workflow and agent activity

## 📁 Project Structure

```
antifragile-flow/
├── workflows/                 # Temporal workflows and starters
│   ├── workflows.py          # Workflow definitions
│   ├── starter.py            # Workflow starter
│   └── ceo_starter.py        # CEO-specific workflows
├── activities/               # Temporal activities
│   ├── activities.py         # Core activity implementations
│   └── workflow_activities.py # Specialized workflow activities
├── workers/                  # Temporal worker processes
│   └── worker.py            # Main worker process
├── inbox/                    # Organizational Twin & messaging system
│   ├── organizational_twin.py # Core intelligence system
│   ├── inbox_service.py      # Message handling
│   ├── inbox_models.py       # Data models
│   └── user_profiles.py      # User management
├── services/                 # Database & external services
│   ├── neo4j_service.py      # Knowledge graph operations
│   ├── postgres_models.py    # PostgreSQL models
│   └── db_models.py         # Database schemas
├── agents/                   # AI agent implementations
│   ├── document_analysis/    # Document processing agents
│   ├── consensus_facilitator/ # Decision-making agents
│   └── knowledge_builder/    # Knowledge management agents
├── frontend/                 # React TypeScript UI
│   └── src/                 # Frontend source code
├── shared/                   # Shared components and libraries
│   ├── models/              # Pydantic data models and base classes
│   ├── config/              # Configuration management
│   ├── prompts/             # AI prompt template system
│   └── temporal_client/     # Temporal connection utilities
├── Makefile                 # Development automation
└── compose.yaml             # Docker services
```

## 🛠️ Development

### Core Commands

```bash
# Development workflow
make install              # Install all dependencies
make build               # Build all components
make test                # Run comprehensive tests
make lint                # Code quality checks
make format              # Auto-format code

# Quality assurance
make quality             # Run all quality gates
make pre-commit-run      # Run pre-commit hooks

# Prompt management
make prompts-validate    # Validate AI prompt templates
make prompts-list        # List available prompts
make prompts-stats       # Show prompt usage statistics
```

### Language-Specific Development

**Python Development**:
```bash
# From root directory
uv run workers/worker.py        # Run worker
uv run workflows/starter.py     # Trigger workflows

# Development commands
uv run poe dev                  # Development with file watching
uv run poe test                 # Run tests
uv run poe lint                 # Lint code
uv run poe format               # Format code
```

**Frontend Development** (from `frontend/` directory):
```bash
pnpm install                    # Install dependencies
pnpm start                      # Start development server
pnpm build                      # Build for production
pnpm test                       # Run tests
```

## 🎨 Prompt Management

Sophisticated AI prompt template system with organizational intelligence:

### Features
- **📝 YAML-based definitions**: Structured, version-controlled prompt templates
- **🎭 Jinja2 templating**: Dynamic content with organizational context
- **🔍 Validation system**: Comprehensive template and variable validation
- **📊 Usage analytics**: Track prompt performance and usage patterns
- **🎯 Role-based prompts**: Templates for agents, workflows, personas, and common use cases

### Example Usage
```bash
# Validate all prompts
make prompts-validate

# Test a specific prompt
make prompts-test PROMPT_ID=strategic_decision.analyze_proposal \
  VARS="proposal_type=market_expansion urgency=high"

# Show prompt details
make prompts-show PROMPT_ID=consensus_builder.facilitate_decision
```

## 🤝 Contributing

1. **Code Quality**: All code must pass `make quality` checks
2. **Testing**: Comprehensive test coverage for new features
3. **Documentation**: Update prompts and README for new capabilities
4. **Type Safety**: Strong typing in both Python and TypeScript

## 📚 Architecture Deep Dive

### Organizational Twin Intelligence

The core of the system is the **Organizational Twin** - an AI system that builds a comprehensive understanding of your organization:

- **🧠 Behavioral Modeling**: Learns individual and team decision-making patterns
- **🗣️ Communication Intelligence**: Adapts to personal and cultural communication styles
- **📋 Process Optimization**: Continuously improves workflow efficiency based on outcomes
- **🔗 Relationship Mapping**: Understands organizational structure and stakeholder relationships

### Temporal Workflow Orchestration

Built on Temporal's robust workflow engine for reliable, long-running processes:

- **🔄 Deterministic Execution**: Workflows can be replayed without side effects
- **🛡️ Fault Tolerance**: Automatic retries and recovery from failures
- **📊 Observability**: Complete visibility into workflow state and progress
- **⚡ Scalability**: Horizontal scaling with additional worker processes

### Storage Architecture

**PostgreSQL**: Structured organizational data, user profiles, decision history
**Neo4j**: Knowledge graph for relationships, organizational intelligence, and pattern recognition
**MinIO**: Document storage, media files, and large data objects with S3 compatibility

This architecture enables the Organizational Twin to maintain rich context while ensuring data consistency and performance.

## 🔗 Resources

- **[Temporal Documentation](https://docs.temporal.io)**: Workflow orchestration platform
- **[Prompt Management Guide](./shared/prompts/README.md)**: Comprehensive prompt system documentation
- **[Agent Development](./python/src/agents/)**: Building intelligent organizational agents
- **[Workflow Patterns](./python/src/workflows.py)**: Human-in-the-loop workflow examples

## 🚀 Getting Started with Development

### 1. Environment Setup

Choose your preferred development environment:

#### Docker Compose (Recommended)
```bash
# Start all services including Temporal, PostgreSQL, and MinIO
make docker-up
```

#### Local Development
```bash
# Install dependencies
make install

# Start Temporal server
make temporal

# Start individual services
docker compose up postgres minio -d
```

### 2. Language-Specific Setup

**Python Development**:
```bash
cd python
uv sync                  # Install dependencies
uv run poe dev          # Start with file watching
```

**TypeScript Development**:
```bash
cd typescript
pnpm install            # Install dependencies
pnpm run worker:watch   # Start with auto-reload
```

### 3. Verify Installation

```bash
# Run all quality checks
make quality

# Test prompt system
make prompts-validate

# Run comprehensive tests
make test
```

### 4. Explore the System

- **Temporal WebUI**: http://localhost:8233 - Monitor workflow execution
- **MinIO Console**: http://localhost:9001 - Manage document storage
- **System Logs**: Watch real-time agent and workflow activity

Start building your organizational twin by exploring the example workflows and extending the agent system to match your organization's unique needs.
