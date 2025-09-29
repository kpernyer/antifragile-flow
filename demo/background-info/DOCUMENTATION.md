# Living Twin Documentation

Welcome to the Living Twin documentation! This guide will help you navigate our comprehensive documentation structure and find the information you need.

## 📚 Documentation Structure

Our documentation is organized into logical sections to help you find what you need quickly:

```
docs/
├── getting-started/     # New user onboarding and setup
├── architecture/        # System design and technical architecture
├── ai-ml/              # AI/ML implementation and guides
├── development/        # Development workflows and tools
├── deployment/         # Production deployment and operations
├── guides/             # Feature guides and best practices
├── api/                # API documentation and integration
└── presentations/      # Business presentations and pitches
```

**📱 Mobile Development:**
Mobile development has been moved to a separate repository: [living-twin-mobile](../living-twin-mobile/)
The mobile app consumes the same REST and GraphQL APIs documented in this repository.

## 🚀 Getting Started

**Start here if you're new to Living Twin or setting up your development environment.**

### Essential Reading Order:
1. **[Local Development](docs/getting-started/local-development.md)** - Quick start with mock data
2. **[Environment Setup](docs/getting-started/environment-setup.md)** - Complete development environment
3. **[Git Setup](docs/getting-started/git-setup.md)** - Version control configuration
4. **[GitHub Setup](docs/getting-started/github-setup.md)** - Repository and CI/CD setup

### Quick Start Commands:
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

## 🏗️ Architecture

**Understanding the system design and technical architecture.**

### Core Architecture:
- **[System Architecture](docs/architecture/system-architecture.md)** - Overall system design
- **[System Overview](docs/architecture/system-overview.md)** - High-level system components
- **[AI Agent Architecture](docs/architecture/ai-agent-architecture.md)** - AI agent system design
- **[AI Agent Diagrams](docs/architecture/ai-agent-diagrams.md)** - Visual architecture diagrams
- **[Tenant Isolation](docs/architecture/tenant-isolation.md)** - Multi-tenant security and isolation

### Key Concepts:
- Multi-tenant organizational twins
- RAG-enabled knowledge management
- AI agent orchestration
- Graph-based data relationships

## 🤖 AI/ML Implementation

**AI and machine learning implementation guides and best practices.**

### RAG and Fine-tuning:
- **[RAG Stack](docs/ai-ml/rag-stack.md)** - Complete RAG architecture explanation
- **[RAG vs Fine-tuning](docs/ai-ml/rag-vs-finetuning.md)** - When to use each approach
- **[Strategic Alignment](docs/ai-ml/strategic-alignment.md)** - Multi-tenant strategic AI architecture
- **[Ollama Setup](docs/ai-ml/ollama-setup.md)** - Local LLM setup and configuration
- **[Verifiable Rewards](docs/guides/verifiable-rewards.md)** - Organizational learning and evolution

### Conversational AI:
- **[Conversational AI](docs/ai-ml/conversational-ai.md)** - Conversational AI evolution guide
- **[Conversational Implementation](docs/ai-ml/conversational-implementation.md)** - Implementation details

### Key AI Features:
- Hybrid RAG + Fine-tuning architecture
- Multi-tenant DNA models
- Strategic alignment AI
- Local LLM support

## 💻 Development

**Development workflows, tools, and technical implementation.**

### Development Tools:
- **[External Dependencies](docs/development/external-dependencies.md)** - Third-party integrations
- **[Configuration Sync](docs/development/configuration-sync.md)** - Environment configuration
- **[Flutter vs React Native](docs/development/flutter-react-comparison.md)** - Mobile framework comparison
- **[PDF Ingestion](docs/development/pdf-ingestion.md)** - Document processing implementation

### Development Workflows:
- **[README Patch](docs/development/readme-patch.md)** - Documentation updates
- **[Python Backend Assessment](docs/development/python-backend-assessment.md)** - Backend architecture assessment

## 🚀 Deployment

**Production deployment, security, and operations.**

### Deployment Guides:
- **[Deployment Setup](docs/deployment/deployment-setup.md)** - Production deployment configuration
- **[Deployment Sprint](docs/deployment/deployment-sprint.md)** - Sprint-based deployment process
- **[Security Testing](docs/deployment/security-testing.md)** - Security and performance testing
- **[Scaling & Cost](docs/deployment/scaling-cost.md)** - Performance optimization and cost management
- **[Sentry Setup](docs/deployment/sentry-setup.md)** - Error monitoring and alerting

### Production Considerations:
- Multi-tenant deployment
- Security and compliance
- Performance optimization
- Cost management

## 📖 Guides

**Feature guides, best practices, and implementation examples.**

### Strategic Features:
- **[Strategic Testing](docs/guides/strategic-testing.md)** - Strategic test implementation
- **[SWOT Detection](docs/guides/swot-detection.md)** - SWOT analysis implementation
- **[SWOT Examples](docs/guides/swot-examples.md)** - SWOT analysis examples
- **[Source Selection](docs/guides/source-selection.md)** - Document source selection strategy

### Core Features:
- **[Core Concepts](docs/guides/core-concepts.md)** - Living Twin core concepts
- **[Intelligence Hub](docs/guides/intelligence-hub.md)** - Intelligence hub implementation
- **[Schema Consistency](docs/guides/schema-consistency.md)** - Data schema consistency

### Management:
- **[API Budget Management](docs/guides/api-budget-management.md)** - API cost management
- **[Terminology Fixes](docs/guides/terminology-fixes.md)** - Terminology alignment
- **[Terminology Updates](docs/guides/terminology-updates.md)** - Terminology updates

### Tools and Analysis:
- **[ASCII Art Guide](docs/guides/ascii-art.md)** - Documentation illustrations
- **[Cline vs Cursor](docs/guides/cline-cursor-analysis.md)** - IDE comparison

## 🔌 API

**API documentation and integration guides.**

### API Documentation:
- **[PubSub Events](docs/api/pubsub-events.md)** - Event-driven architecture
- **[OpenAPI Documentation](docs/api/readme-openapi.md)** - REST API documentation
- **[GraphQL Integration](docs/api/readme-graphql.md)** - GraphQL API documentation

## 📊 Presentations

**Business presentations, pitches, and strategic documents.**

### Business Presentations:
- **[CEO Pitch](docs/presentations/ceo-pitch.md)** - Executive pitch deck
- **[Investor Presentation](docs/presentations/investor-preso.md)** - Investor-focused presentation
- **[Company Presentation](docs/presentations/company-preso.md)** - General company overview
- **[Strategic Alignment](docs/presentations/living_twin_strategic_alignment_presentation.md)** - Strategic alignment presentation
- **[PMF & GTM Strategy](docs/presentations/living_twin_pmf_gtm_strategy.md)** - Product-market fit and go-to-market strategy

### Technical Presentations:
- **[System Overview](docs/presentations/system-overview.md)** - Technical system overview
- **[System Management](docs/presentations/system-management.md)** - System management presentation
- **[User Experience](docs/presentations/user-experience.md)** - UX design and user experience
- **[5-Slide CEO Pitch](docs/presentations/5-slide-ceo-pitch.md)** - Concise executive summary

## 📱 Mobile

**Mobile app development guides and Flutter implementation.**

### Flutter Development:
- **[Dart Language Optimization](docs/mobile/dart_language_optimization_guide.md)** - Dart performance optimization
- **[Dart Migration Guide](docs/mobile/dart_migration_guide.md)** - Migration strategies and best practices
- **[Dart Optimization Status](docs/mobile/dart_optimization_status.md)** - Current optimization status
- **[Dart Security Audit](docs/mobile/dart_security_performance_audit.md)** - Security and performance audit
- **[Crash Reporting Setup](docs/mobile/crash_reporting_setup.md)** - Error monitoring and crash reporting
- **[Dependency Injection](docs/mobile/dependency_injection_example.md)** - DI patterns and examples

## 🎯 Reading Paths

### **For New Developers:**
1. [Local Development](docs/getting-started/local-development.md)
2. [System Overview](docs/architecture/system-overview.md)
3. [Core Concepts](docs/guides/core-concepts.md)
4. [RAG Stack](docs/ai-ml/rag-stack.md)

### **For AI/ML Engineers:**
1. [Strategic Alignment](docs/ai-ml/strategic-alignment.md)
2. [RAG vs Fine-tuning](docs/ai-ml/rag-vs-finetuning.md)
3. [Ollama Setup](docs/ai-ml/ollama-setup.md)
4. [Conversational AI](docs/ai-ml/conversational-ai.md)

### **For DevOps Engineers:**
1. [Deployment Setup](docs/deployment/deployment-setup.md)
2. [Security Testing](docs/deployment/security-testing.md)
3. [Scaling & Cost](docs/deployment/scaling-cost.md)
4. [Tenant Isolation](docs/architecture/tenant-isolation.md)

### **For Product Managers:**
1. [Core Concepts](docs/guides/core-concepts.md)
2. [System Overview](docs/architecture/system-overview.md)
3. [Strategic Alignment](docs/ai-ml/strategic-alignment.md)
4. [API Budget Management](docs/guides/api-budget-management.md)

### **For Business Stakeholders:**
1. [Core Concepts](docs/guides/core-concepts.md)
2. [Strategic Alignment](docs/ai-ml/strategic-alignment.md)
3. [SWOT Detection](docs/guides/swot-detection.md)
4. [Scaling & Cost](docs/deployment/scaling-cost.md)

### **For Mobile Developers:**
1. [Dart Language Optimization](docs/mobile/dart_language_optimization_guide.md)
2. [Dart Migration Guide](docs/mobile/dart_migration_guide.md)
3. [Crash Reporting Setup](docs/mobile/crash_reporting_setup.md)
4. [Dependency Injection](docs/mobile/dependency_injection_example.md)

### **For Business Development:**
1. [CEO Pitch](docs/presentations/ceo-pitch.md)
2. [Investor Presentation](docs/presentations/investor-preso.md)
3. [Strategic Alignment](docs/presentations/living_twin_strategic_alignment_presentation.md)
4. [PMF & GTM Strategy](docs/presentations/living_twin_pmf_gtm_strategy.md)

## 🔍 Search and Navigation

### **Quick Find by Topic:**

**AI/ML:**
- RAG implementation: [RAG Stack](docs/ai-ml/rag-stack.md)
- Fine-tuning: [RAG vs Fine-tuning](docs/ai-ml/rag-vs-finetuning.md)
- Strategic AI: [Strategic Alignment](docs/ai-ml/strategic-alignment.md)
- Local LLMs: [Ollama Setup](docs/ai-ml/ollama-setup.md)

**Architecture:**
- System design: [System Architecture](docs/architecture/system-architecture.md)
- AI agents: [AI Agent Architecture](docs/architecture/ai-agent-architecture.md)
- Multi-tenancy: [Tenant Isolation](docs/architecture/tenant-isolation.md)

**Development:**
- Quick start: [Local Development](docs/getting-started/local-development.md)
- Environment: [Environment Setup](docs/getting-started/environment-setup.md)
- Deployment: [Deployment Setup](docs/deployment/deployment-setup.md)

**Features:**
- Strategic testing: [Strategic Testing](docs/guides/strategic-testing.md)
- SWOT analysis: [SWOT Detection](docs/guides/swot-detection.md)
- Conversational AI: [Conversational AI](docs/ai-ml/conversational-ai.md)

**Presentations:**
- Business pitches: [Presentations](docs/presentations/)
- Mobile development: [Mobile guides](docs/mobile/)

## 📝 Contributing to Documentation

### **Documentation Standards:**
- Use clear, concise language
- Include code examples where relevant
- Provide step-by-step instructions
- Include troubleshooting sections
- Keep information up-to-date

### **Adding New Documentation:**
1. Choose the appropriate directory based on content type
2. Use kebab-case for filenames (e.g., `my-new-guide.md`)
3. Include a brief description in this index
4. Update relevant reading paths

### **Documentation Maintenance:**
- Regular reviews for accuracy
- Update links when files are moved
- Ensure code examples work
- Validate technical accuracy

## 🆘 Getting Help

### **Common Issues:**
- **Setup problems**: Check [Local Development](docs/getting-started/local-development.md)
- **AI/ML questions**: See [AI/ML guides](docs/ai-ml/)
- **Deployment issues**: Review [Deployment guides](docs/deployment/)
- **Architecture questions**: Check [Architecture docs](docs/architecture/)

### **Support Channels:**
- GitHub Issues: For bugs and feature requests
- Documentation Issues: For documentation improvements
- Team Chat: For quick questions and discussions

---

## 📊 Documentation Statistics

- **Total Documents**: 40+
- **Categories**: 9 main sections
- **Last Updated**: $(date)
- **Maintained By**: Living Twin Development Team

---

*This documentation is continuously updated. If you find any issues or have suggestions for improvements, please contribute through our GitHub repository.*
