# 🕰️ Temporal.io Integration for Agent Workflows

## 📋 Why Temporal for Agent Orchestration

Temporal.io is perfect for your AI agent portfolio because it provides:

- **Durable Workflows**: Long-running agent interactions that survive system restarts
- **Reliable Execution**: Automatic retries, timeouts, and error handling
- **Observability**: Built-in monitoring and debugging for complex agent workflows
- **Scalability**: Distributed execution across multiple workers
- **Versioning**: Safe workflow updates without breaking running instances

## 🏗️ Architecture Integration

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Voice SDK     │    │  Temporal       │    │  Agent Portfolio│
│                 │    │  Workflows      │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │Voice Input  │ │───▶│ │ Daily       │ │───▶│ │Priority     │ │
│ │Recognition  │ │    │ │ Briefing    │ │    │ │Management   │ │
│ └─────────────┘ │    │ │ Workflow    │ │    │ │Agent        │ │
│                 │    │ └─────────────┘ │    │ └─────────────┘ │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │Text-to-     │ │◀───│ │ Document    │ │◀───│ │Document     │ │
│ │Speech       │ │    │ │ Analysis    │ │    │ │Intelligence │ │
│ │Output       │ │    │ │ Workflow    │ │    │ │Agent        │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Implementation Strategy

### 1. Core Temporal Workflow Classes

```typescript
// packages/agent_temporal/src/workflows/BaseAgentWorkflow.ts
import {
  defineSignal,
  defineQuery,
  setHandler,
  condition,
  workflowInfo,
  sleep
} from '@temporalio/workflow';
import { AgentInput, AgentOutput } from '@aprio/agent-core';

export interface AgentWorkflowInput {
  workflowId: string;
  organizationId: string;
  userId: string;
  agentChain: string[];
  initialData: any;
  configuration: WorkflowConfiguration;
}

export interface WorkflowConfiguration {
  timeout: number;
  retryPolicy: {
    maximumAttempts: number;
    backoffCoefficient: number;
    maximumInterval: string;
  };
  scheduleConfig?: {
    cron: string;
    timezone: string;
  };
}

// Signals for workflow control
export const pauseWorkflowSignal = defineSignal<[]>('pauseWorkflow');
export const resumeWorkflowSignal = defineSignal<[]>('resumeWorkflow');
export const cancelWorkflowSignal = defineSignal<[]>('cancelWorkflow');
export const updateConfigSignal = defineSignal<[Partial<WorkflowConfiguration>]>('updateConfig');

// Queries for workflow state
export const getWorkflowStatusQuery = defineQuery<WorkflowStatus>('getWorkflowStatus');
export const getAgentProgressQuery = defineQuery<AgentProgress[]>('getAgentProgress');

export interface WorkflowStatus {
  status: 'running' | 'paused' | 'completed' | 'failed' | 'cancelled';
  currentAgent: string;
  currentStep: number;
  totalSteps: number;
  startTime: Date;
  lastActivityTime: Date;
  errors: string[];
}

export interface AgentProgress {
  agentId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  startTime?: Date;
  endTime?: Date;
  output?: any;
  error?: string;
}

export abstract class BaseAgentWorkflow {
  protected status: WorkflowStatus = {
    status: 'running',
    currentAgent: '',
    currentStep: 0,
    totalSteps: 0,
    startTime: new Date(),
    lastActivityTime: new Date(),
    errors: [],
  };

  protected agentProgress: AgentProgress[] = [];
  protected isPaused = false;
  protected configuration: WorkflowConfiguration;

  constructor(input: AgentWorkflowInput) {
    this.configuration = input.configuration;
    this.status.totalSteps = input.agentChain.length;

    // Set up signal handlers
    setHandler(pauseWorkflowSignal, () => {
      this.isPaused = true;
      this.status.status = 'paused';
    });

    setHandler(resumeWorkflowSignal, () => {
      this.isPaused = false;
      this.status.status = 'running';
    });

    setHandler(cancelWorkflowSignal, () => {
      this.status.status = 'cancelled';
      throw new Error('Workflow cancelled by user');
    });

    setHandler(updateConfigSignal, (newConfig) => {
      this.configuration = { ...this.configuration, ...newConfig };
    });

    // Set up query handlers
    setHandler(getWorkflowStatusQuery, () => this.status);
    setHandler(getAgentProgressQuery, () => this.agentProgress);
  }

  protected async waitIfPaused(): Promise<void> {
    await condition(() => !this.isPaused);
  }

  protected updateStatus(currentAgent: string, step: number): void {
    this.status.currentAgent = currentAgent;
    this.status.currentStep = step;
    this.status.lastActivityTime = new Date();
  }

  protected recordAgentStart(agentId: string): void {
    const progress: AgentProgress = {
      agentId,
      status: 'running',
      startTime: new Date(),
    };
    this.agentProgress.push(progress);
  }

  protected recordAgentComplete(agentId: string, output: any): void {
    const progress = this.agentProgress.find(p => p.agentId === agentId);
    if (progress) {
      progress.status = 'completed';
      progress.endTime = new Date();
      progress.output = output;
    }
  }

  protected recordAgentError(agentId: string, error: string): void {
    const progress = this.agentProgress.find(p => p.agentId === agentId);
    if (progress) {
      progress.status = 'failed';
      progress.endTime = new Date();
      progress.error = error;
    }
    this.status.errors.push(`${agentId}: ${error}`);
  }

  abstract execute(input: AgentWorkflowInput): Promise<any>;
}
```

### 2. Daily Briefing Temporal Workflow

```typescript
// packages/agent_temporal/src/workflows/DailyBriefingWorkflow.ts
import { BaseAgentWorkflow, AgentWorkflowInput } from './BaseAgentWorkflow';
import { executeAgentActivity, notifyStakeholdersActivity } from '../activities';

export interface DailyBriefingInput extends AgentWorkflowInput {
  includeMarketUpdates: boolean;
  includePriorityAnalysis: boolean;
  includeHealthMetrics: boolean;
  deliveryPreferences: {
    voice: boolean;
    email: boolean;
    slack: boolean;
  };
}

export interface DailyBriefingOutput {
  briefingId: string;
  summary: {
    greeting: string;
    keyInsights: string[];
    healthScore: number;
  };
  priorities: {
    critical: any[];
    recommendations: any[];
  };
  marketUpdates?: any;
  deliveryResults: {
    voice: boolean;
    email: boolean;
    slack: boolean;
  };
  metrics: {
    totalDuration: number;
    agentExecutionTimes: Record<string, number>;
    userEngagement?: number;
  };
}

export class DailyBriefingWorkflow extends BaseAgentWorkflow {
  async execute(input: DailyBriefingInput): Promise<DailyBriefingOutput> {
    const briefingId = `briefing-${workflowInfo().workflowId}-${Date.now()}`;
    const startTime = Date.now();

    try {
      // Step 1: Load organizational context
      await this.waitIfPaused();
      this.updateStatus('context-manager', 1);
      this.recordAgentStart('context-manager');

      const contextResult = await executeAgentActivity({
        agentId: 'context-manager',
        action: 'load-organizational-context',
        data: {
          organizationId: input.organizationId,
          userId: input.userId,
        },
        timeout: 10000,
      });

      this.recordAgentComplete('context-manager', contextResult);

      // Step 2: Analyze priorities
      await this.waitIfPaused();
      this.updateStatus('priority-management', 2);
      this.recordAgentStart('priority-management');

      const priorityResult = await executeAgentActivity({
        agentId: 'priority-management',
        action: 'analyze-priorities',
        data: {
          priorities: contextResult.priorities,
          timeframe: 'today',
        },
        timeout: 15000,
      });

      this.recordAgentComplete('priority-management', priorityResult);

      // Step 3: Market updates (conditional)
      let marketResult = null;
      if (input.includeMarketUpdates) {
        await this.waitIfPaused();
        this.updateStatus('market-research', 3);
        this.recordAgentStart('market-research');

        try {
          marketResult = await executeAgentActivity({
            agentId: 'market-research',
            action: 'get-market-updates',
            data: {
              industry: contextResult.organization.industry,
              companies: contextResult.organization.competitors,
            },
            timeout: 20000,
          });

          this.recordAgentComplete('market-research', marketResult);
        } catch (error) {
          this.recordAgentError('market-research', String(error));
          // Continue without market updates
        }
      }

      // Step 4: Sentiment analysis for communication style
      await this.waitIfPaused();
      this.updateStatus('sentiment-analysis', 4);
      this.recordAgentStart('sentiment-analysis');

      const sentimentResult = await executeAgentActivity({
        agentId: 'sentiment-analysis',
        action: 'assess-communication-style',
        data: {
          userId: input.userId,
          timeOfDay: new Date().getHours(),
          recentInteractions: contextResult.recentInteractions,
        },
        timeout: 5000,
      });

      this.recordAgentComplete('sentiment-analysis', sentimentResult);

      // Step 5: Prepare briefing content
      await this.waitIfPaused();
      this.updateStatus('briefing-generator', 5);
      this.recordAgentStart('briefing-generator');

      const briefingContent = {
        summary: {
          greeting: this.generateGreeting(sentimentResult.preferredStyle),
          keyInsights: this.extractKeyInsights(priorityResult, marketResult),
          healthScore: priorityResult.healthScore,
        },
        priorities: {
          critical: priorityResult.criticalItems,
          recommendations: priorityResult.recommendations,
        },
        marketUpdates: marketResult,
      };

      this.recordAgentComplete('briefing-generator', briefingContent);

      // Step 6: Deliver briefing through multiple channels
      const deliveryResults = await this.deliverBriefing(
        briefingContent,
        input.deliveryPreferences,
        sentimentResult.preferredStyle
      );

      // Final metrics
      const totalDuration = Date.now() - startTime;
      const agentExecutionTimes = this.calculateAgentTimes();

      this.status.status = 'completed';

      return {
        briefingId,
        ...briefingContent,
        deliveryResults,
        metrics: {
          totalDuration,
          agentExecutionTimes,
        },
      };

    } catch (error) {
      this.status.status = 'failed';
      throw error;
    }
  }

  private async deliverBriefing(
    content: any,
    preferences: DailyBriefingInput['deliveryPreferences'],
    communicationStyle: string
  ): Promise<Record<string, boolean>> {
    const results: Record<string, boolean> = {};

    // Voice delivery
    if (preferences.voice) {
      await this.waitIfPaused();
      this.updateStatus('voice-interface', 6);
      this.recordAgentStart('voice-interface');

      try {
        await executeAgentActivity({
          agentId: 'voice-interface',
          action: 'deliver-briefing',
          data: {
            content,
            style: communicationStyle,
            interactionMode: 'briefing',
          },
          timeout: 120000, // 2 minutes for voice delivery
        });

        this.recordAgentComplete('voice-interface', { delivered: true });
        results.voice = true;
      } catch (error) {
        this.recordAgentError('voice-interface', String(error));
        results.voice = false;
      }
    }

    // Email delivery
    if (preferences.email) {
      try {
        await notifyStakeholdersActivity({
          type: 'email',
          recipients: [input.userId],
          content: this.formatEmailBriefing(content),
          subject: `Daily Briefing - ${new Date().toLocaleDateString()}`,
        });
        results.email = true;
      } catch (error) {
        results.email = false;
      }
    }

    // Slack delivery
    if (preferences.slack) {
      try {
        await notifyStakeholdersActivity({
          type: 'slack',
          recipients: [input.userId],
          content: this.formatSlackBriefing(content),
        });
        results.slack = true;
      } catch (error) {
        results.slack = false;
      }
    }

    return results;
  }

  private generateGreeting(style: string): string {
    const timeOfDay = new Date().getHours() < 12 ? 'morning' : 'afternoon';

    if (style === 'formal') {
      return `Good ${timeOfDay}. Here's your executive briefing.`;
    } else {
      return `Good ${timeOfDay}! Ready for your daily update?`;
    }
  }

  private extractKeyInsights(priorityResult: any, marketResult?: any): string[] {
    const insights: string[] = [];

    if (priorityResult.criticalItems > 0) {
      insights.push(`${priorityResult.criticalItems} critical priorities need attention`);
    }

    if (priorityResult.overdueTasks > 0) {
      insights.push(`${priorityResult.overdueTasks} tasks are overdue`);
    }

    if (marketResult?.significantNews?.length > 0) {
      insights.push(`${marketResult.significantNews.length} significant market developments`);
    }

    if (insights.length === 0) {
      insights.push('All systems running smoothly');
    }

    return insights;
  }

  private calculateAgentTimes(): Record<string, number> {
    const times: Record<string, number> = {};

    this.agentProgress.forEach(progress => {
      if (progress.startTime && progress.endTime) {
        times[progress.agentId] = progress.endTime.getTime() - progress.startTime.getTime();
      }
    });

    return times;
  }

  private formatEmailBriefing(content: any): string {
    return `
      <h2>Daily Executive Briefing</h2>
      <p>${content.summary.greeting}</p>

      <h3>Key Insights</h3>
      <ul>
        ${content.summary.keyInsights.map((insight: string) => `<li>${insight}</li>`).join('')}
      </ul>

      <h3>Priority Summary</h3>
      <p>Health Score: ${Math.round(content.summary.healthScore * 100)}%</p>
      <p>Critical Items: ${content.priorities.critical.length}</p>

      ${content.marketUpdates ? `
        <h3>Market Updates</h3>
        <p>Industry developments and competitor activity tracked.</p>
      ` : ''}
    `;
  }

  private formatSlackBriefing(content: any): string {
    return `
🌅 *Daily Briefing* - ${new Date().toLocaleDateString()}

${content.summary.greeting}

📊 *Key Insights:*
${content.summary.keyInsights.map((insight: string) => `• ${insight}`).join('\n')}

🎯 *Priorities:* Health Score ${Math.round(content.summary.healthScore * 100)}%
• ${content.priorities.critical.length} critical items
• ${content.priorities.recommendations.length} recommendations

${content.marketUpdates ? '📈 *Market Updates:* Industry intelligence updated' : ''}
    `;
  }
}
```

### 3. Temporal Activities for Agent Execution

```typescript
// packages/agent_temporal/src/activities/index.ts
import { AgentRegistry, MessageBus } from '@aprio/agent-core';

let agentRegistry: AgentRegistry;
let messageBus: MessageBus;

export function initializeActivities(registry: AgentRegistry, bus: MessageBus) {
  agentRegistry = registry;
  messageBus = bus;
}

export interface AgentActivityInput {
  agentId: string;
  action: string;
  data: any;
  timeout: number;
}

export async function executeAgentActivity(input: AgentActivityInput): Promise<any> {
  const { agentId, action, data, timeout } = input;

  // Get agent from registry
  const agent = agentRegistry.getAgent(agentId);
  if (!agent) {
    throw new Error(`Agent ${agentId} not found in registry`);
  }

  if (!agent.isInitialized) {
    throw new Error(`Agent ${agentId} is not initialized`);
  }

  // Execute agent with timeout
  const timeoutPromise = new Promise((_, reject) =>
    setTimeout(() => reject(new Error(`Agent ${agentId} timeout after ${timeout}ms`)), timeout)
  );

  const executionPromise = agent.process({
    type: action,
    data,
    metadata: {
      requestId: `temporal-${Date.now()}`,
      timestamp: new Date().toISOString(),
      priority: 'high',
    },
  });

  const result = await Promise.race([executionPromise, timeoutPromise]);

  if (result.metadata?.status === 'error') {
    throw new Error(`Agent ${agentId} failed: ${result.data.error}`);
  }

  return result.data;
}

export interface NotificationInput {
  type: 'email' | 'slack' | 'sms';
  recipients: string[];
  content: string;
  subject?: string;
}

export async function notifyStakeholdersActivity(input: NotificationInput): Promise<void> {
  const { type, recipients, content, subject } = input;

  // Mock notification implementation
  // In production, integrate with actual notification services
  console.log(`Sending ${type} notification to ${recipients.join(', ')}`);
  console.log(`Subject: ${subject || 'N/A'}`);
  console.log(`Content: ${content}`);

  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 1000));

  // For email integration
  if (type === 'email') {
    // await emailService.send({ to: recipients, subject, html: content });
  }

  // For Slack integration
  if (type === 'slack') {
    // await slackService.postMessage({ channels: recipients, text: content });
  }

  // For SMS integration
  if (type === 'sms') {
    // await smsService.send({ to: recipients, message: content });
  }
}

export async function scheduleFollowUpActivity(input: {
  workflowId: string;
  delay: number;
  followUpType: string;
  data: any;
}): Promise<void> {
  const { workflowId, delay, followUpType, data } = input;

  // Schedule a follow-up workflow
  // This could trigger another workflow after a delay
  console.log(`Scheduling follow-up for workflow ${workflowId} in ${delay}ms`);
  console.log(`Follow-up type: ${followUpType}`);
  console.log(`Data:`, data);

  // In production, this might start a new Temporal workflow
  // await workflowClient.start(FollowUpWorkflow, { args: [{ ...data, originalWorkflowId: workflowId }] });
}
```

### 4. Document Analysis Temporal Workflow

```typescript
// packages/agent_temporal/src/workflows/DocumentAnalysisWorkflow.ts
import { BaseAgentWorkflow, AgentWorkflowInput } from './BaseAgentWorkflow';
import { executeAgentActivity, scheduleFollowUpActivity } from '../activities';

export interface DocumentAnalysisInput extends AgentWorkflowInput {
  documentId: string;
  analysisType: 'comprehensive' | 'financial' | 'competitive' | 'legal';
  urgency: 'low' | 'medium' | 'high' | 'critical';
  stakeholders: string[];
  followUpRequired: boolean;
}

export interface DocumentAnalysisOutput {
  analysisId: string;
  document: any;
  insights: any[];
  recommendations: any[];
  riskFactors: any[];
  actionItems: any[];
  confidence: number;
  processingMetrics: {
    totalTime: number;
    agentBreakdown: Record<string, number>;
  };
}

export class DocumentAnalysisWorkflow extends BaseAgentWorkflow {
  async execute(input: DocumentAnalysisInput): Promise<DocumentAnalysisOutput> {
    const analysisId = `analysis-${workflowInfo().workflowId}-${Date.now()}`;
    const startTime = Date.now();

    try {
      // Step 1: Load document and organizational context
      await this.waitIfPaused();
      this.updateStatus('context-manager', 1);
      this.recordAgentStart('context-manager');

      const [documentData, contextData] = await Promise.all([
        executeAgentActivity({
          agentId: 'document-intelligence',
          action: 'load-document',
          data: { documentId: input.documentId },
          timeout: 15000,
        }),
        executeAgentActivity({
          agentId: 'context-manager',
          action: 'load-organizational-context',
          data: { organizationId: input.organizationId },
          timeout: 10000,
        }),
      ]);

      this.recordAgentComplete('context-manager', { documentData, contextData });

      // Step 2: Deep document analysis
      await this.waitIfPaused();
      this.updateStatus('document-intelligence', 2);
      this.recordAgentStart('document-intelligence');

      const analysisResult = await executeAgentActivity({
        agentId: 'document-intelligence',
        action: 'analyze-document',
        data: {
          document: documentData,
          analysisType: input.analysisType,
          organizationContext: contextData,
        },
        timeout: 60000, // 1 minute for deep analysis
      });

      this.recordAgentComplete('document-intelligence', analysisResult);

      // Step 3: Extract business insights
      await this.waitIfPaused();
      this.updateStatus('document-intelligence', 3);
      this.recordAgentStart('research-synthesis');

      const insightsResult = await executeAgentActivity({
        agentId: 'document-intelligence',
        action: 'extract-insights',
        data: {
          documents: [documentData],
          focus: input.analysisType,
          organizationPriorities: contextData.priorities,
        },
        timeout: 30000,
      });

      this.recordAgentComplete('research-synthesis', insightsResult);

      // Step 4: Market context (for competitive/financial analysis)
      let marketContext = null;
      if (['competitive', 'financial'].includes(input.analysisType)) {
        await this.waitIfPaused();
        this.updateStatus('market-research', 4);
        this.recordAgentStart('market-research');

        try {
          marketContext = await executeAgentActivity({
            agentId: 'market-research',
            action: 'provide-market-context',
            data: {
              industry: contextData.organization.industry,
              analysisType: input.analysisType,
              documentInsights: insightsResult.insights,
            },
            timeout: 25000,
          });

          this.recordAgentComplete('market-research', marketContext);
        } catch (error) {
          this.recordAgentError('market-research', String(error));
          // Continue without market context
        }
      }

      // Step 5: Priority analysis and action item generation
      await this.waitIfPaused();
      this.updateStatus('priority-management', 5);
      this.recordAgentStart('priority-management');

      const actionItemsResult = await executeAgentActivity({
        agentId: 'priority-management',
        action: 'generate-action-items',
        data: {
          insights: insightsResult.insights,
          marketContext,
          urgency: input.urgency,
          currentPriorities: contextData.priorities,
        },
        timeout: 20000,
      });

      this.recordAgentComplete('priority-management', actionItemsResult);

      // Step 6: Risk assessment
      await this.waitIfPaused();
      this.updateStatus('risk-analysis', 6);

      const riskFactors = await this.assessRisks(
        analysisResult,
        insightsResult,
        marketContext,
        input.urgency
      );

      // Step 7: Generate recommendations
      const recommendations = await this.generateRecommendations(
        analysisResult,
        insightsResult,
        actionItemsResult,
        riskFactors,
        contextData
      );

      // Step 8: Notify stakeholders if urgent
      if (['high', 'critical'].includes(input.urgency)) {
        await this.notifyStakeholders(input.stakeholders, {
          analysisId,
          urgency: input.urgency,
          keyInsights: insightsResult.insights.slice(0, 3),
          criticalActions: actionItemsResult.actionItems.filter((item: any) => item.priority === 'critical'),
        });
      }

      // Step 9: Schedule follow-up if required
      if (input.followUpRequired) {
        await scheduleFollowUpActivity({
          workflowId: workflowInfo().workflowId,
          delay: this.calculateFollowUpDelay(input.urgency),
          followUpType: 'document-analysis-review',
          data: {
            originalAnalysisId: analysisId,
            stakeholders: input.stakeholders,
          },
        });
      }

      const totalTime = Date.now() - startTime;
      this.status.status = 'completed';

      return {
        analysisId,
        document: documentData,
        insights: insightsResult.insights,
        recommendations,
        riskFactors,
        actionItems: actionItemsResult.actionItems,
        confidence: this.calculateOverallConfidence(analysisResult, insightsResult),
        processingMetrics: {
          totalTime,
          agentBreakdown: this.calculateAgentTimes(),
        },
      };

    } catch (error) {
      this.status.status = 'failed';
      throw error;
    }
  }

  private async assessRisks(
    analysisResult: any,
    insightsResult: any,
    marketContext: any,
    urgency: string
  ): Promise<any[]> {
    const risks: any[] = [];

    // Extract risks from document analysis
    if (analysisResult.intelligence?.riskFactors) {
      risks.push(...analysisResult.intelligence.riskFactors);
    }

    // Add market-based risks
    if (marketContext?.risks) {
      risks.push(...marketContext.risks);
    }

    // Add urgency-based risk assessment
    if (urgency === 'critical') {
      risks.push({
        type: 'time-sensitive',
        severity: 'high',
        description: 'Critical urgency requires immediate action',
        mitigation: 'Expedite decision-making process',
      });
    }

    return risks;
  }

  private async generateRecommendations(
    analysisResult: any,
    insightsResult: any,
    actionItemsResult: any,
    riskFactors: any[],
    contextData: any
  ): Promise<any[]> {
    const recommendations: any[] = [];

    // Add analysis-based recommendations
    if (analysisResult.recommendations) {
      recommendations.push(...analysisResult.recommendations);
    }

    // Add insight-based recommendations
    insightsResult.insights.forEach((insight: any) => {
      if (insight.implications?.length > 0) {
        recommendations.push({
          type: 'strategic',
          priority: insight.importance > 0.8 ? 'high' : 'medium',
          title: `Act on ${insight.title}`,
          description: insight.implications[0],
          source: 'document-insights',
        });
      }
    });

    // Add risk mitigation recommendations
    riskFactors.forEach(risk => {
      if (risk.mitigation) {
        recommendations.push({
          type: 'risk-mitigation',
          priority: risk.severity === 'high' ? 'critical' : 'medium',
          title: `Mitigate ${risk.type} risk`,
          description: risk.mitigation,
          source: 'risk-assessment',
        });
      }
    });

    return recommendations;
  }

  private async notifyStakeholders(stakeholders: string[], summary: any): Promise<void> {
    // Send urgent notifications to stakeholders
    const content = `
🚨 *Urgent Document Analysis Complete*

Analysis ID: ${summary.analysisId}
Urgency Level: ${summary.urgency.toUpperCase()}

*Key Insights:*
${summary.keyInsights.map((insight: any) => `• ${insight.title}`).join('\n')}

*Critical Actions Required:*
${summary.criticalActions.map((action: any) => `• ${action.title}`).join('\n')}

Please review the full analysis for detailed recommendations.
    `;

    await notifyStakeholdersActivity({
      type: 'slack',
      recipients: stakeholders,
      content,
    });
  }

  private calculateFollowUpDelay(urgency: string): number {
    switch (urgency) {
      case 'critical':
        return 2 * 60 * 60 * 1000; // 2 hours
      case 'high':
        return 24 * 60 * 60 * 1000; // 1 day
      case 'medium':
        return 3 * 24 * 60 * 60 * 1000; // 3 days
      case 'low':
        return 7 * 24 * 60 * 60 * 1000; // 1 week
      default:
        return 24 * 60 * 60 * 1000; // 1 day
    }
  }

  private calculateOverallConfidence(analysisResult: any, insightsResult: any): number {
    const analysisConfidence = analysisResult.confidence || 0.8;
    const insightsConfidence = insightsResult.insights.reduce(
      (sum: number, insight: any) => sum + (insight.confidence || 0.8),
      0
    ) / (insightsResult.insights.length || 1);

    return (analysisConfidence + insightsConfidence) / 2;
  }
}
```

### 5. Temporal Worker Setup

```typescript
// packages/agent_temporal/src/worker.ts
import { Worker } from '@temporalio/worker';
import { AgentRegistry, MessageBus } from '@aprio/agent-core';
import { initializeActivities } from './activities';
import * as workflows from './workflows';

export async function createTemporalWorker(
  agentRegistry: AgentRegistry,
  messageBus: MessageBus,
  options: {
    taskQueue: string;
    workflowsPath?: string;
    activitiesPath?: string;
  }
): Promise<Worker> {
  // Initialize activities with agent registry and message bus
  initializeActivities(agentRegistry, messageBus);

  const worker = await Worker.create({
    workflowsPath: options.workflowsPath || require.resolve('./workflows'),
    activitiesPath: options.activitiesPath || require.resolve('./activities'),
    taskQueue: options.taskQueue,
    // Workflow options
    maxConcurrentWorkflowExecutions: 100,
    maxConcurrentActivityExecutions: 200,
    // Activity options
    maxConcurrentLocalActivityExecutions: 50,
    // Enable logging
    dataConverter: {
      // Custom data converter for agent inputs/outputs if needed
    },
    interceptors: {
      // Add monitoring and logging interceptors
      workflowModules: [workflows],
    },
  });

  return worker;
}

// packages/agent_temporal/src/client.ts
import { Client, WorkflowHandle } from '@temporalio/client';
import { DailyBriefingWorkflow, DailyBriefingInput, DailyBriefingOutput } from './workflows/DailyBriefingWorkflow';
import { DocumentAnalysisWorkflow, DocumentAnalysisInput, DocumentAnalysisOutput } from './workflows/DocumentAnalysisWorkflow';

export class TemporalAgentClient {
  private client: Client;
  private taskQueue: string;

  constructor(client: Client, taskQueue: string = 'agent-workflows') {
    this.client = client;
    this.taskQueue = taskQueue;
  }

  // Daily Briefing Operations
  async startDailyBriefing(input: DailyBriefingInput): Promise<WorkflowHandle<DailyBriefingWorkflow, DailyBriefingOutput>> {
    const workflowId = `daily-briefing-${input.organizationId}-${input.userId}-${Date.now()}`;

    return await this.client.workflow.start(DailyBriefingWorkflow, {
      workflowId,
      taskQueue: this.taskQueue,
      args: [input],
      workflowExecutionTimeout: '10m',
      workflowTaskTimeout: '1m',
    });
  }

  async scheduleDailyBriefing(
    input: DailyBriefingInput,
    cronSchedule: string = '0 8 * * 1-5' // 8 AM weekdays
  ): Promise<WorkflowHandle> {
    const scheduleId = `daily-briefing-schedule-${input.organizationId}-${input.userId}`;

    return await this.client.workflow.start(DailyBriefingWorkflow, {
      workflowId: scheduleId,
      taskQueue: this.taskQueue,
      args: [input],
      cronSchedule,
    });
  }

  // Document Analysis Operations
  async startDocumentAnalysis(input: DocumentAnalysisInput): Promise<WorkflowHandle<DocumentAnalysisWorkflow, DocumentAnalysisOutput>> {
    const workflowId = `document-analysis-${input.documentId}-${Date.now()}`;

    return await this.client.workflow.start(DocumentAnalysisWorkflow, {
      workflowId,
      taskQueue: this.taskQueue,
      args: [input],
      workflowExecutionTimeout: '30m',
      workflowTaskTimeout: '2m',
    });
  }

  // Workflow Control Operations
  async pauseWorkflow(workflowId: string): Promise<void> {
    const handle = this.client.workflow.getHandle(workflowId);
    await handle.signal('pauseWorkflow');
  }

  async resumeWorkflow(workflowId: string): Promise<void> {
    const handle = this.client.workflow.getHandle(workflowId);
    await handle.signal('resumeWorkflow');
  }

  async cancelWorkflow(workflowId: string): Promise<void> {
    const handle = this.client.workflow.getHandle(workflowId);
    await handle.cancel();
  }

  async getWorkflowStatus(workflowId: string): Promise<any> {
    const handle = this.client.workflow.getHandle(workflowId);
    return await handle.query('getWorkflowStatus');
  }

  async getAgentProgress(workflowId: string): Promise<any[]> {
    const handle = this.client.workflow.getHandle(workflowId);
    return await handle.query('getAgentProgress');
  }

  // Monitoring Operations
  async listActiveWorkflows(): Promise<any[]> {
    // Use Temporal's list workflows API
    const workflows = [];

    for await (const workflow of this.client.workflow.list()) {
      if (workflow.status.name === 'RUNNING') {
        workflows.push({
          workflowId: workflow.workflowId,
          workflowType: workflow.workflowType,
          startTime: workflow.startTime,
          runId: workflow.runId,
        });
      }
    }

    return workflows;
  }
}
```

### 6. Integration with Voice SDK

```typescript
// packages/voice_sdk/src/temporal/VoiceWorkflowIntegration.ts
import { TemporalAgentClient } from '@aprio/agent-temporal';
import { useVoiceAssistant } from '../contexts/VoiceAssistantContext';

export class VoiceTemporalIntegration {
  constructor(private temporalClient: TemporalAgentClient) {}

  async handleVoiceCommand(command: string, context: any): Promise<void> {
    const commandType = this.classifyCommand(command);

    switch (commandType) {
      case 'daily-briefing':
        await this.startDailyBriefingWorkflow(context);
        break;

      case 'document-analysis':
        await this.startDocumentAnalysisWorkflow(command, context);
        break;

      case 'workflow-status':
        await this.getWorkflowStatus(command, context);
        break;

      case 'pause-workflow':
        await this.pauseActiveWorkflow(context);
        break;

      default:
        // Handle as regular voice command
        break;
    }
  }

  private async startDailyBriefingWorkflow(context: any): Promise<void> {
    const input = {
      workflowId: `briefing-${Date.now()}`,
      organizationId: context.organizationId,
      userId: context.userId,
      agentChain: ['context-manager', 'priority-management', 'market-research', 'voice-interface'],
      initialData: {},
      configuration: {
        timeout: 300000, // 5 minutes
        retryPolicy: {
          maximumAttempts: 3,
          backoffCoefficient: 2,
          maximumInterval: '60s',
        },
      },
      includeMarketUpdates: true,
      includePriorityAnalysis: true,
      includeHealthMetrics: true,
      deliveryPreferences: {
        voice: true,
        email: false,
        slack: false,
      },
    };

    const handle = await this.temporalClient.startDailyBriefing(input);

    // Notify user that briefing is starting
    context.speak("Starting your daily briefing. I'll analyze your priorities and market updates.");

    // Monitor workflow progress
    this.monitorWorkflowProgress(handle.workflowId, context);
  }

  private async monitorWorkflowProgress(workflowId: string, context: any): Promise<void> {
    const interval = setInterval(async () => {
      try {
        const status = await this.temporalClient.getWorkflowStatus(workflowId);
        const progress = await this.temporalClient.getAgentProgress(workflowId);

        // Update voice interface with progress
        if (status.status === 'running') {
          context.updateStatus(`Processing with ${status.currentAgent}...`);
        } else if (status.status === 'completed') {
          context.speak("Your briefing is ready!");
          clearInterval(interval);
        } else if (status.status === 'failed') {
          context.speak("I encountered an issue with your briefing. Let me try a different approach.");
          clearInterval(interval);
        }
      } catch (error) {
        console.error('Error monitoring workflow:', error);
        clearInterval(interval);
      }
    }, 5000); // Check every 5 seconds
  }

  private classifyCommand(command: string): string {
    const lowerCommand = command.toLowerCase();

    if (lowerCommand.includes('briefing') || lowerCommand.includes('daily update')) {
      return 'daily-briefing';
    }

    if (lowerCommand.includes('analyze') && (lowerCommand.includes('document') || lowerCommand.includes('file'))) {
      return 'document-analysis';
    }

    if (lowerCommand.includes('status') || lowerCommand.includes('progress')) {
      return 'workflow-status';
    }

    if (lowerCommand.includes('pause') || lowerCommand.includes('stop')) {
      return 'pause-workflow';
    }

    return 'unknown';
  }
}
```

## 🚀 Benefits of Temporal Integration

### 1. **Reliability & Durability**
- Workflows survive system restarts and failures
- Automatic retries with exponential backoff
- Guaranteed execution even with temporary agent failures

### 2. **Observability**
- Real-time workflow monitoring and debugging
- Complete execution history and audit trails
- Performance metrics and agent execution times

### 3. **Scalability**
- Distributed workflow execution across multiple workers
- Load balancing of agent operations
- Horizontal scaling based on workflow demand

### 4. **Flexibility**
- Dynamic workflow modification with versioning
- Conditional agent execution based on results
- Pause/resume capabilities for long-running processes

### 5. **Voice Integration**
- Seamless voice command triggering of complex workflows
- Real-time progress updates through voice interface
- Conversational workflow control (pause, resume, status)

This Temporal integration transforms your agent portfolio into a production-grade, enterprise-ready system with the reliability and observability needed for business-critical AI workflows! 🕰️✨
