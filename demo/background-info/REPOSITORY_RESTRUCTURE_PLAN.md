# 🏗️ Repository Restructure Plan

## 📋 Executive Summary

Clean separation of the monorepo into focused, domain-specific repositories to improve maintainability, development velocity, and deployment independence.

## 🎯 Repository Architecture

### **Repository 1: `living-twin-data` (Current Repo - Refined)**
**Purpose**: Data infrastructure, ETL, and Clojure-based data processing
**Domain**: Data engineering and organizational intelligence backend

```
living-twin-data/
├── apps/
│   ├── admin_web/                 # Admin interface (kept)
│   └── api/                       # Backend API (kept)
├── packages/
│   └── gcp_firebase/              # Infrastructure (kept)
├── data/
│   ├── etl/                       # Data transformation pipelines
│   ├── clojure/                   # Clojure data processing
│   ├── neo4j/                     # Graph database schemas
│   └── vector/                    # Vector database configs
├── scripts/
│   ├── data-migration/            # Data migration tools
│   ├── analytics/                 # Data analytics scripts
│   └── reporting/                 # Business intelligence reports
└── docs/
    ├── data-architecture/         # Data system docs
    └── api-documentation/         # API specs
```

### **Repository 2: `living-twin-agentic` (NEW)**
**Purpose**: AI Agent portfolio framework with 15 core use cases
**Domain**: Business intelligence agents and workflows

```
living-twin-agentic/
├── packages/
│   ├── agent-core/                # 🆕 Base agent infrastructure
│   ├── agent-intelligence/        # 🆕 AlphaSense-style agents
│   ├── agent-workflow/            # 🆕 Business workflow agents
│   ├── agent-communication/       # 🆕 Communication agents
│   ├── agent-temporal/            # 🆕 Temporal workflow integration
│   ├── voice-sdk/                 # 🔄 Enhanced voice capabilities
│   └── ui-components/             # 🆕 Shared UI components
├── examples/
│   ├── daily-briefing/            # Example implementation
│   ├── document-analysis/         # AlphaSense-style example
│   ├── crisis-response/           # Emergency management
│   ├── priority-management/       # Executive priority optimization
│   └── market-intelligence/       # Business intelligence
├── apps/
│   ├── agentic-web/               # 🆕 Agent portfolio dashboard
│   ├── agentic-mobile/            # 🔄 Mobile app (moved from current)
│   └── agentic-cli/               # 🆕 CLI for agent management
├── workflows/
│   ├── 01-daily-briefing/         # Core workflow implementations
│   ├── 02-document-analysis/      # Document intelligence
│   ├── 03-crisis-response/        # Emergency management
│   ├── 04-priority-optimization/  # Priority management
│   ├── 05-market-research/        # Market intelligence
│   ├── 06-competitive-analysis/   # Competitive intelligence
│   ├── 07-financial-analysis/     # Financial document analysis
│   ├── 08-sentiment-monitoring/   # Real-time sentiment
│   ├── 09-stakeholder-comms/      # Stakeholder communication
│   ├── 10-decision-support/       # Decision frameworks
│   ├── 11-risk-assessment/        # Risk analysis
│   ├── 12-performance-review/     # Performance analytics
│   ├── 13-strategic-planning/     # Strategic workflow
│   ├── 14-compliance-monitoring/  # Compliance automation
│   └── 15-knowledge-synthesis/    # Knowledge management
├── integrations/
│   ├── alphasense/                # AlphaSense connector
│   ├── openai/                    # OpenAI integration
│   ├── temporal/                  # Temporal.io integration
│   ├── mcp/                       # Model Context Protocol
│   └── enterprise/                # Enterprise system connectors
├── deployments/
│   ├── docker/                    # Container configurations
│   ├── kubernetes/                # K8s manifests
│   ├── terraform/                 # Infrastructure as code
│   └── helm/                      # Helm charts
└── docs/
    ├── architecture/              # System architecture
    ├── agent-development/         # Agent development guides
    ├── workflow-creation/         # Workflow authoring
    └── integration-guides/        # Integration documentation
```

### **Repository 3: `living-twin-swarm` (NEW)**
**Purpose**: High-performance Rust worker system for distributed processing
**Domain**: Performance-critical distributed computing and real-time processing

```
living-twin-swarm/
├── crates/
│   ├── swarm-core/                # Core swarm coordination
│   ├── swarm-worker/              # Individual worker implementation
│   ├── swarm-scheduler/           # Task scheduling and distribution
│   ├── swarm-comms/               # Inter-worker communication
│   ├── swarm-storage/             # Distributed storage layer
│   └── swarm-metrics/             # Performance monitoring
├── workers/
│   ├── document-processor/        # High-speed document processing
│   ├── vector-indexer/            # Vector database indexing
│   ├── real-time-analyzer/        # Stream processing
│   ├── ml-inference/              # Machine learning inference
│   ├── data-transformer/          # ETL processing
│   └── cache-warmer/              # Cache optimization
├── examples/
│   ├── basic-swarm/               # Simple swarm setup
│   ├── document-analysis/         # Document processing swarm
│   ├── real-time-pipeline/        # Streaming data pipeline
│   └── ml-inference-cluster/      # ML model serving
├── deployments/
│   ├── docker/                    # Rust container configs
│   ├── kubernetes/                # K8s for Rust services
│   └── ansible/                   # Deployment automation
├── benchmarks/                    # Performance benchmarks
├── monitoring/                    # Swarm monitoring tools
└── docs/
    ├── architecture/              # Swarm system design
    ├── performance/               # Performance guides
    └── operations/                # Operational procedures
```

## 🔄 Migration Strategy

### **Phase 1: Repository Creation & Setup (Week 1)**

#### **Step 1: Create New Repositories**
```bash
# Create new repositories
mkdir -p /Users/kenper/src/aprio-one/living-twin-agentic
mkdir -p /Users/kenper/src/aprio-one/living-twin-swarm

# Initialize git repositories
cd /Users/kenper/src/aprio-one/living-twin-agentic
git init
git remote add origin git@github.com:aprio-one/living-twin-agentic.git

cd /Users/kenper/src/aprio-one/living-twin-swarm
git init
git remote add origin git@github.com:aprio-one/living-twin-swarm.git
```

#### **Step 2: Setup Base Structure**
```bash
# Create agentic framework structure
cd /Users/kenper/src/aprio-one/living-twin-agentic
mkdir -p packages/{agent-core,agent-intelligence,agent-workflow,agent-communication,agent-temporal,voice-sdk,ui-components}
mkdir -p examples/{daily-briefing,document-analysis,crisis-response}
mkdir -p apps/{agentic-web,agentic-mobile,agentic-cli}
mkdir -p workflows/{01-daily-briefing,02-document-analysis,03-crisis-response}
mkdir -p integrations/{alphasense,openai,temporal,mcp,enterprise}
mkdir -p deployments/{docker,kubernetes,terraform,helm}

# Create swarm system structure
cd /Users/kenper/src/aprio-one/living-twin-swarm
mkdir -p crates/{swarm-core,swarm-worker,swarm-scheduler,swarm-comms,swarm-storage,swarm-metrics}
mkdir -p workers/{document-processor,vector-indexer,real-time-analyzer,ml-inference}
mkdir -p examples/{basic-swarm,document-analysis,real-time-pipeline}
mkdir -p deployments/{docker,kubernetes,ansible}
```

### **Phase 2: Code Migration (Week 2-3)**

#### **Agentic Framework Migration**
```bash
# Move agent packages
cp -r /Users/kenper/src/aprio-one/living-twin-monorepo/packages/agent_* \
      /Users/kenper/src/aprio-one/living-twin-agentic/packages/

# Move voice SDK
cp -r /Users/kenper/src/aprio-one/living-twin-monorepo/packages/voice_sdk \
      /Users/kenper/src/aprio-one/living-twin-agentic/packages/voice-sdk

# Move mobile app
cp -r /Users/kenper/src/aprio-one/living-twin-monorepo/apps/end_user_app/mobile \
      /Users/kenper/src/aprio-one/living-twin-agentic/apps/agentic-mobile

# Move web components
cp -r /Users/kenper/src/aprio-one/living-twin-monorepo/apps/end_user_app/web \
      /Users/kenper/src/aprio-one/living-twin-agentic/apps/agentic-web
```

#### **Data Repository Cleanup**
```bash
# Keep only data-related components in original repo
cd /Users/kenper/src/aprio-one/living-twin-monorepo

# Remove agent packages (moved to agentic repo)
rm -rf packages/agent_*
rm -rf packages/voice_sdk
rm -rf apps/end_user_app

# Rename repo to living-twin-data
# Update documentation and references
```

### **Phase 3: Rust Swarm System (Week 3-4)**

#### **Create Rust Workspace**
```toml
# living-twin-swarm/Cargo.toml
[workspace]
members = [
    "crates/swarm-core",
    "crates/swarm-worker",
    "crates/swarm-scheduler",
    "crates/swarm-comms",
    "crates/swarm-storage",
    "crates/swarm-metrics",
    "workers/document-processor",
    "workers/vector-indexer",
    "workers/real-time-analyzer",
    "workers/ml-inference",
    "examples/basic-swarm"
]

[workspace.dependencies]
tokio = { version = "1.0", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }
anyhow = "1.0"
clap = { version = "4.0", features = ["derive"] }
tracing = "0.1"
```

## 📊 **15 Core Use Cases Implementation**

### **Immediate Priority (Weeks 1-4)**
1. **Daily Executive Briefing** ✅ (Already implemented)
2. **Document Intelligence Analysis** ✅ (Already implemented)
3. **Crisis Response Management** ✅ (Already implemented)
4. **Priority Optimization** ✅ (Already implemented)
5. **Market Intelligence** (AlphaSense integration)

### **High Impact (Weeks 5-8)**
6. **Competitive Analysis** (Market research + competitor tracking)
7. **Financial Document Analysis** (Earnings, reports, forecasts)
8. **Real-time Sentiment Monitoring** (Communication optimization)
9. **Stakeholder Communication** (Multi-channel notifications)
10. **Decision Support Framework** (Structured decision processes)

### **Strategic Value (Weeks 9-12)**
11. **Risk Assessment & Monitoring** (Proactive risk management)
12. **Performance Review Automation** (KPI tracking and analysis)
13. **Strategic Planning Support** (Long-term planning workflows)
14. **Compliance Monitoring** (Regulatory and policy compliance)
15. **Knowledge Synthesis** (Multi-source information aggregation)

## 🔧 **Cross-Repository Integration**

### **Shared Dependencies**
```yaml
# living-twin-agentic/package.json
{
  "name": "@aprio/living-twin-agentic",
  "dependencies": {
    "@aprio/living-twin-data-client": "^1.0.0"  # Data API client
  }
}

# living-twin-data/package.json
{
  "name": "@aprio/living-twin-data",
  "main": "dist/client.js",  # Exports data API client
  "peerDependencies": {
    "@aprio/living-twin-agentic": "^1.0.0"  # Optional agent integration
  }
}
```

### **Inter-Repository Communication**
```typescript
// Data Repository API Client
export class LivingTwinDataClient {
  async getOrganizationalContext(orgId: string): Promise<OrgContext> {
    return await this.api.get(`/organizations/${orgId}/context`);
  }

  async getPriorities(orgId: string): Promise<Priority[]> {
    return await this.api.get(`/organizations/${orgId}/priorities`);
  }

  async storeAnalysisResult(result: AnalysisResult): Promise<void> {
    await this.api.post('/analysis-results', result);
  }
}

// Agentic Framework Integration
import { LivingTwinDataClient } from '@aprio/living-twin-data-client';

export class ContextManagerAgent extends BaseAgent {
  constructor(private dataClient: LivingTwinDataClient) {
    super('context-manager', 'Context Manager', '1.0.0');
  }

  async loadOrganizationalContext(orgId: string): Promise<OrgContext> {
    return await this.dataClient.getOrganizationalContext(orgId);
  }
}
```

### **Rust Swarm Integration**
```rust
// Swarm system provides high-performance processing
// Called from agentic framework for heavy workloads

use reqwest::Client;
use serde_json::Value;

pub struct SwarmClient {
    client: Client,
    swarm_endpoint: String,
}

impl SwarmClient {
    pub async fn process_document(&self, document: &Document) -> Result<ProcessingResult> {
        let response = self.client
            .post(&format!("{}/workers/document-processor", self.swarm_endpoint))
            .json(document)
            .send()
            .await?;

        Ok(response.json().await?)
    }

    pub async fn index_vectors(&self, vectors: &[Vector]) -> Result<IndexResult> {
        // High-performance vector indexing
    }
}
```

## 🚀 **Development Workflow**

### **Independent Development**
- **Data Team**: Focus on ETL, analytics, and data infrastructure
- **Agent Team**: Focus on business intelligence and workflow automation
- **Performance Team**: Focus on high-speed processing and optimization

### **Integration Points**
- **Standardized APIs** between repositories
- **Shared TypeScript types** via published packages
- **Common deployment patterns** using shared infrastructure

### **Release Coordination**
- **Semantic versioning** for cross-repository dependencies
- **Integration testing** across repository boundaries
- **Coordinated releases** for major feature launches

## 📋 **Migration Checklist**

### **Week 1: Setup**
- [ ] Create new repositories with proper structure
- [ ] Setup CI/CD pipelines for each repository
- [ ] Establish inter-repository dependency management
- [ ] Create migration scripts for code movement

### **Week 2: Agentic Framework**
- [ ] Migrate agent packages with updated imports
- [ ] Implement 15 core use case scaffolding
- [ ] Setup Temporal integration in new repository
- [ ] Create agentic framework documentation

### **Week 3: Data Repository Cleanup**
- [ ] Remove migrated packages from data repository
- [ ] Update API endpoints for cross-repository communication
- [ ] Implement data client library for agentic framework
- [ ] Update existing applications to use new structure

### **Week 4: Rust Swarm Foundation**
- [ ] Create Rust workspace with core crates
- [ ] Implement basic swarm coordination
- [ ] Create example workers for common tasks
- [ ] Setup performance benchmarking

## 🏆 **Expected Benefits**

### **Development Velocity**
- **Parallel development** across specialized teams
- **Reduced cognitive load** with focused repositories
- **Independent deployment** and release cycles

### **Technical Benefits**
- **Clear separation of concerns** between data, agents, and performance
- **Optimized technology choices** per domain (TypeScript for agents, Rust for performance)
- **Modular architecture** enabling easy integration and testing

### **Business Benefits**
- **Faster feature delivery** with specialized teams
- **Better code quality** with domain-focused expertise
- **Easier onboarding** for new developers with clear boundaries

This restructure transforms your monorepo into a **clean, maintainable, multi-repository architecture** while preserving all the innovative work on AI agents and maintaining clean integration patterns! 🏗️✨
