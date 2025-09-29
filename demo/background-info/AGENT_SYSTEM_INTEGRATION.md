# 🔧 Agent System Integration Guide

## 📋 Complete Agent Portfolio Setup

This document shows how to integrate the complete agent portfolio system with concrete examples of all agents working together.

## 🚀 Quick Start Integration

```typescript
import { AgentRegistry, MessageBus } from '@aprio/agent-core';
import { PriorityManagementAgent } from '@aprio/agent-workflow';
import { DocumentIntelligenceAgent } from '@aprio/agent-intelligence';
import { VoiceInterfaceAgent } from '@aprio/voice-sdk';
import { setupDailyBriefingWorkflow } from '@aprio/agent-workflow';

// Initialize the complete system
async function initializeAgentSystem() {
  // Core infrastructure
  const registry = new AgentRegistry();
  const messageBus = new MessageBus();

  // Initialize agents
  const agents = await initializeAllAgents();

  // Register agents with registry
  for (const agent of agents) {
    registry.register(agent);

    // Connect agents to message bus
    messageBus.subscribe(agent.id, async (message) => {
      try {
        const result = await agent.process({
          type: message.payload.action,
          data: message.payload.data,
          context: message.context,
          metadata: {
            requestId: message.id,
            timestamp: message.timestamp,
            priority: message.context?.priority || 'medium',
          },
        });

        if (message.type === 'REQUEST') {
          await messageBus.respond(message, result, agent.id);
        }
      } catch (error) {
        await messageBus.respond(message, { error: String(error) }, agent.id);
      }
    });
  }

  // Setup workflows
  await setupWorkflows(registry, messageBus);

  return { registry, messageBus };
}
```

## 🤖 Agent Initialization

```typescript
async function initializeAllAgents() {
  const agents = [];

  // 1. Voice Interface Agent (Core)
  const voiceAgent = new VoiceInterfaceAgent();
  await voiceAgent.initialize({
    id: 'voice-interface',
    configuration: {
      providers: ['openai-realtime', 'browser-speech'],
      defaultProvider: 'browser-speech',
      fallbackProvider: 'openai-realtime',
    },
  });
  agents.push(voiceAgent);

  // 2. Priority Management Agent (Workflow)
  const priorityAgent = new PriorityManagementAgent();
  await priorityAgent.initialize({
    id: 'priority-management',
    configuration: {
      analysisDepth: 'comprehensive',
      recommendationEngine: 'ml-enhanced',
    },
  });
  agents.push(priorityAgent);

  // 3. Document Intelligence Agent (AlphaSense-inspired)
  const documentAgent = new DocumentIntelligenceAgent();
  await documentAgent.initialize({
    id: 'document-intelligence',
    configuration: {
      aiModels: {
        entityExtraction: 'bert-large-ner',
        sentiment: 'roberta-sentiment',
        summarization: 'bart-large-cnn',
        embedding: 'sentence-transformers',
      },
      alphasenseIntegration: {
        enabled: true,
        apiKey: process.env.ALPHASENSE_API_KEY,
      },
    },
  });
  agents.push(documentAgent);

  // 4. Context Manager Agent (Core)
  const contextAgent = new ContextManagerAgent();
  await contextAgent.initialize({
    id: 'context-manager',
    configuration: {
      organizationDataSource: 'internal-api',
      cacheStrategy: 'redis',
      updateFrequency: '1h',
    },
  });
  agents.push(contextAgent);

  // 5. Sentiment Analysis Agent (Communication)
  const sentimentAgent = new SentimentAnalysisAgent();
  await sentimentAgent.initialize({
    id: 'sentiment-analysis',
    configuration: {
      realTimeAnalysis: true,
      stressDetection: true,
      emotionalIntelligence: 'advanced',
    },
  });
  agents.push(sentimentAgent);

  // 6. Crisis Response Agent (Workflow)
  const crisisAgent = new CrisisResponseAgent();
  await crisisAgent.initialize({
    id: 'crisis-response',
    configuration: {
      escalationRules: 'enterprise',
      notificationChannels: ['email', 'slack', 'voice'],
      responseTemplates: 'comprehensive',
    },
  });
  agents.push(crisisAgent);

  return agents;
}
```

## 🔄 Workflow Registration

```typescript
async function setupWorkflows(registry: AgentRegistry, messageBus: MessageBus) {
  // 1. Daily Briefing Workflow
  await setupDailyBriefingWorkflow(registry, messageBus);

  // 2. Document Analysis Workflow
  const documentAnalysisWorkflow = {
    id: 'document-analysis-v1',
    name: 'Intelligent Document Processing',
    description: 'AlphaSense-style document intelligence workflow',
    version: '1.0.0',
    agents: [
      { id: 'document-intelligence', role: 'analyzer', required: true },
      { id: 'context-manager', role: 'context-provider', required: true },
      { id: 'priority-management', role: 'action-prioritizer', required: false },
      { id: 'voice-interface', role: 'results-presenter', required: false },
    ],
    flow: [
      {
        step: 1,
        agent: 'context-manager',
        action: 'load-organizational-context',
        timeout: 5000,
      },
      {
        step: 2,
        agent: 'document-intelligence',
        action: 'analyze-document',
        timeout: 30000,
      },
      {
        step: 3,
        agent: 'document-intelligence',
        action: 'extract-insights',
        timeout: 15000,
      },
      {
        step: 4,
        agent: 'priority-management',
        action: 'prioritize-insights',
        condition: 'insights.length > 0',
        timeout: 10000,
        onError: 'continue',
      },
      {
        step: 5,
        agent: 'voice-interface',
        action: 'present-analysis',
        condition: 'context.presentationMode === "voice"',
        timeout: 60000,
        onError: 'continue',
      },
    ],
    input: {
      type: 'DocumentAnalysisRequest',
      schema: {
        type: 'object',
        required: ['document'],
        properties: {
          document: { type: 'object' },
          analysisType: { type: 'string', enum: ['comprehensive', 'financial', 'competitive'] },
          presentationMode: { type: 'string', enum: ['text', 'voice', 'both'] },
          organizationContext: { type: 'object' },
        },
      },
    },
  };

  registry.registerWorkflow(documentAnalysisWorkflow);

  // 3. Crisis Response Workflow
  const crisisResponseWorkflow = {
    id: 'crisis-response-v1',
    name: 'Emergency Crisis Management',
    description: 'Automated crisis detection and response coordination',
    version: '1.0.0',
    agents: [
      { id: 'crisis-response', role: 'coordinator', required: true },
      { id: 'sentiment-analysis', role: 'stress-monitor', required: true },
      { id: 'priority-management', role: 'priority-rebalancer', required: true },
      { id: 'voice-interface', role: 'communication-hub', required: true },
      { id: 'document-intelligence', role: 'plan-generator', required: false },
    ],
    flow: [
      {
        step: 1,
        agent: 'crisis-response',
        action: 'assess-severity',
        timeout: 5000,
      },
      {
        step: 2,
        agent: 'sentiment-analysis',
        action: 'monitor-stress-levels',
        timeout: 3000,
      },
      {
        step: 3,
        agent: 'priority-management',
        action: 'emergency-rebalancing',
        timeout: 10000,
      },
      {
        step: 4,
        agent: 'crisis-response',
        action: 'coordinate-response',
        timeout: 30000,
      },
      {
        step: 5,
        agent: 'voice-interface',
        action: 'stakeholder-notifications',
        timeout: 60000,
      },
    ],
    trigger: {
      type: 'keyword',
      patterns: ['crisis', 'emergency', 'urgent', 'critical situation', 'outage', 'security breach'],
    },
  };

  registry.registerWorkflow(crisisResponseWorkflow);
}
```

## 🎯 Real-World Usage Examples

### Example 1: Daily Executive Briefing

```typescript
async function runDailyBriefing(registry: AgentRegistry) {
  try {
    // Create workflow execution
    const execution = registry.createWorkflow('daily-briefing-v1', {
      organizationId: 'wellnessroberts_care',
      userId: 'ceo-001',
      timeframe: 'today',
      includeMarketUpdates: true,
      includePriorityAnalysis: true,
      includeHealthMetrics: true,
    });

    // Execute workflow
    const result = await registry.executeWorkflow(execution);

    console.log('Daily briefing completed:', {
      status: result.status,
      duration: result.metrics.totalTime,
      insights: result.output.summary.keyInsights,
      healthScore: result.output.priorities.healthScore,
    });

    return result;
  } catch (error) {
    console.error('Daily briefing failed:', error);
    throw error;
  }
}
```

### Example 2: Document Analysis (AlphaSense-style)

```typescript
async function analyzeDocument(registry: AgentRegistry, documentPath: string) {
  try {
    // Prepare document for analysis
    const document = {
      id: `doc-${Date.now()}`,
      title: 'Q4 2024 Earnings Report',
      content: await fs.readFile(documentPath, 'utf-8'),
      metadata: {
        type: 'financial-report' as const,
        company: 'TechCorp Inc.',
        industry: 'Technology',
        date: '2024-12-15',
        language: 'en',
        wordCount: 15000,
        tags: ['earnings', 'quarterly', 'financial'],
      },
      source: {
        file: documentPath,
        provider: 'upload' as const,
        confidence: 1.0,
      },
    };

    // Execute document analysis workflow
    const execution = registry.createWorkflow('document-analysis-v1', {
      document,
      analysisType: 'comprehensive',
      presentationMode: 'voice',
      organizationContext: {
        company: 'WellnessRoberts Care',
        industry: 'Healthcare',
        priorities: ['growth', 'innovation', 'market-expansion'],
      },
    });

    const result = await registry.executeWorkflow(execution);

    console.log('Document analysis completed:', {
      insights: result.output.insights?.length || 0,
      sentiment: result.output.analysis?.sentiment,
      recommendations: result.output.recommendations?.length || 0,
    });

    return result;
  } catch (error) {
    console.error('Document analysis failed:', error);
    throw error;
  }
}
```

### Example 3: Crisis Response

```typescript
async function handleCrisisScenario(registry: AgentRegistry, messageBus: MessageBus) {
  // Simulate crisis trigger
  await messageBus.broadcast(
    'system',
    'EVENT' as any,
    {
      event: 'crisis-detected',
      severity: 'high',
      type: 'system-outage',
      description: 'Primary database cluster is down',
      affectedSystems: ['patient-records', 'appointment-scheduling'],
      estimatedImpact: 'high',
    }
  );

  // The crisis response workflow will automatically trigger
  // and coordinate the response across all relevant agents

  // Monitor the response
  messageBus.subscribe('crisis-monitor', async (message) => {
    if (message.payload.event === 'crisis-response-completed') {
      console.log('Crisis response completed:', {
        responseTime: message.payload.metrics.totalTime,
        actionsPerformed: message.payload.actions.length,
        stakeholdersNotified: message.payload.notifications.length,
      });
    }
  });
}
```

## 🔗 AlphaSense Integration

```typescript
// Integration with AlphaSense API for enhanced document intelligence
class AlphaSenseConnector {
  constructor(private documentAgent: DocumentIntelligenceAgent, private apiKey: string) {}

  async searchAlphaSenseDocuments(query: string, filters: any = {}) {
    const response = await fetch('https://api.alphasense.com/v1/search', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        filters,
        limit: 50,
      }),
    });

    const results = await response.json();

    // Process each document through our Document Intelligence Agent
    const processedResults = [];

    for (const doc of results.documents) {
      const analysis = await this.documentAgent.process({
        type: 'analyze-document',
        data: {
          document: this.transformAlphaSenseDoc(doc),
          analysisType: 'comprehensive',
        },
        metadata: {
          requestId: `alphasense-${doc.id}`,
          timestamp: new Date().toISOString(),
          priority: 'medium',
        },
      });

      processedResults.push(analysis);
    }

    return processedResults;
  }

  private transformAlphaSenseDoc(alphaDoc: any): any {
    return {
      id: alphaDoc.id,
      title: alphaDoc.title,
      content: alphaDoc.content,
      metadata: {
        type: alphaDoc.document_type,
        company: alphaDoc.company,
        industry: alphaDoc.industry,
        date: alphaDoc.published_date,
        language: alphaDoc.language,
        wordCount: alphaDoc.content?.length || 0,
        tags: alphaDoc.tags || [],
      },
      source: {
        provider: 'alphasense',
        url: alphaDoc.url,
        confidence: alphaDoc.relevance_score || 0.8,
      },
    };
  }
}
```

## 📊 System Monitoring

```typescript
// Comprehensive monitoring for the agent system
class AgentSystemMonitor {
  constructor(private registry: AgentRegistry, private messageBus: MessageBus) {
    this.setupMonitoring();
  }

  private setupMonitoring() {
    // Monitor agent health
    setInterval(async () => {
      const agents = await this.registry.listAgents();
      const unhealthyAgents = agents.filter(agent => agent.healthStatus.status !== 'healthy');

      if (unhealthyAgents.length > 0) {
        console.warn('Unhealthy agents detected:', unhealthyAgents.map(a => a.id));
        // Trigger alerts or auto-recovery
      }
    }, 30000); // Check every 30 seconds

    // Monitor workflow performance
    this.registry.on('workflowCompleted', (event) => {
      const { execution, result } = event;
      const metrics = {
        workflowId: execution.flow.id,
        duration: result.metrics.totalTime,
        success: result.status === 'success',
        stepCount: result.metrics.stepCount,
        failedSteps: result.metrics.failedSteps,
      };

      console.log('Workflow metrics:', metrics);

      // Store metrics for analysis
      this.storeWorkflowMetrics(metrics);
    });

    // Monitor message bus performance
    this.messageBus.on('messageSent', (message) => {
      // Track message patterns, response times, etc.
    });
  }

  async getSystemStatus() {
    const agents = await this.registry.listAgents();
    const runningWorkflows = this.registry.getRunningWorkflows();

    return {
      agents: {
        total: agents.length,
        healthy: agents.filter(a => a.healthStatus.status === 'healthy').length,
        degraded: agents.filter(a => a.healthStatus.status === 'degraded').length,
        unhealthy: agents.filter(a => a.healthStatus.status === 'unhealthy').length,
      },
      workflows: {
        running: runningWorkflows.length,
        pending: runningWorkflows.filter(w => w.state.status === 'pending').length,
        active: runningWorkflows.filter(w => w.state.status === 'running').length,
      },
      performance: await this.getPerformanceMetrics(),
    };
  }

  private async getPerformanceMetrics() {
    const agents = await this.registry.listAgents();
    const avgResponseTime = agents.reduce((sum, agent) => sum + agent.metrics.averageProcessingTime, 0) / agents.length;

    return {
      averageResponseTime: avgResponseTime,
      totalRequests: agents.reduce((sum, agent) => sum + agent.metrics.requestCount, 0),
      errorRate: agents.reduce((sum, agent) => sum + agent.metrics.errorCount, 0) / agents.reduce((sum, agent) => sum + agent.metrics.requestCount, 1),
    };
  }

  private storeWorkflowMetrics(metrics: any) {
    // Store in database/monitoring system
    console.log('Storing workflow metrics:', metrics);
  }
}
```

## 🚀 Deployment Configuration

```typescript
// Production deployment configuration
export const productionConfig = {
  agents: {
    'voice-interface': {
      replicas: 2,
      resources: { memory: '2Gi', cpu: '1000m' },
      providers: ['openai-realtime', 'browser-speech'],
      fallbackChain: ['browser-speech', 'openai-realtime'],
    },
    'priority-management': {
      replicas: 3,
      resources: { memory: '1Gi', cpu: '500m' },
      analysisDepth: 'comprehensive',
      caching: { enabled: true, ttl: '1h' },
    },
    'document-intelligence': {
      replicas: 4,
      resources: { memory: '4Gi', cpu: '2000m' },
      aiModels: {
        gpu: true,
        modelCache: '8Gi',
      },
      alphasense: {
        enabled: true,
        apiKey: process.env.ALPHASENSE_API_KEY,
        rateLimit: { requests: 1000, per: 'hour' },
      },
    },
  },
  workflows: {
    'daily-briefing-v1': {
      schedule: '0 8 * * 1-5', // 8 AM weekdays
      timeout: '5m',
      retries: 2,
    },
    'document-analysis-v1': {
      maxConcurrent: 10,
      timeout: '10m',
      priority: 'high',
    },
    'crisis-response-v1': {
      priority: 'critical',
      timeout: '2m',
      notifications: ['slack', 'email', 'sms'],
    },
  },
  monitoring: {
    healthChecks: { interval: '30s' },
    metrics: { enabled: true, endpoint: '/metrics' },
    logging: { level: 'info', structured: true },
  },
};
```

This integration guide demonstrates a complete, production-ready agent system that combines the best of AlphaSense's specialized intelligence with your organizational voice assistant platform. The system is modular, scalable, and designed for enterprise-grade reliability.
