/**
 * Centralized default values for the Antifragile Flow frontend.
 *
 * This module provides all default ports, URLs, and configuration values
 * that correspond to the Python backend configuration.
 *
 * These values should stay in sync with shared/config/defaults.py
 */

/**
 * Standard port assignments for all services.
 * Must match Python DefaultPorts class.
 */
export const DEFAULT_PORTS = {
  // Temporal
  TEMPORAL_SERVER: 7233,
  TEMPORAL_UI: 8233,

  // Web services
  FRONTEND: 3000,
  API_SERVER: 8080,
  GRAPHQL_SERVER: 4000,  // Knowledge Base GraphQL server

  // Databases
  POSTGRES: 5432,
  REDIS: 6379,
  MONGODB: 27017,

  // Development services
  DEV_PROXY: 9000,
  METRICS: 9464,
} as const;

/**
 * Standard hostnames for all services.
 * Must match Python DefaultHosts class.
 */
export const DEFAULT_HOSTS = {
  LOCAL: 'localhost',
  TEMPORAL_CLOUD_SUFFIX: '.tmprl.cloud',
  PRODUCTION_CLUSTER: 'temporal.production.svc.cluster.local',
} as const;

/**
 * Standard URL patterns.
 * Must match Python DefaultURLs class.
 */
export const DEFAULT_URLS = {
  // Local development
  FRONTEND_LOCAL: `http://${DEFAULT_HOSTS.LOCAL}:${DEFAULT_PORTS.FRONTEND}`,
  API_LOCAL: `http://${DEFAULT_HOSTS.LOCAL}:${DEFAULT_PORTS.API_SERVER}`,
  GRAPHQL_LOCAL: `http://${DEFAULT_HOSTS.LOCAL}:${DEFAULT_PORTS.GRAPHQL_SERVER}`,
  TEMPORAL_LOCAL: `${DEFAULT_HOSTS.LOCAL}:${DEFAULT_PORTS.TEMPORAL_SERVER}`,
  TEMPORAL_UI_LOCAL: `http://${DEFAULT_HOSTS.LOCAL}:${DEFAULT_PORTS.TEMPORAL_UI}`,

  // Knowledge Base GraphQL endpoints
  GRAPHQL_ENDPOINT: `http://${DEFAULT_HOSTS.LOCAL}:${DEFAULT_PORTS.GRAPHQL_SERVER}/graphql`,
  GRAPHQL_PLAYGROUND: `http://${DEFAULT_HOSTS.LOCAL}:${DEFAULT_PORTS.GRAPHQL_SERVER}/playground`,
  GRAPHQL_SUBSCRIPTIONS: `ws://${DEFAULT_HOSTS.LOCAL}:${DEFAULT_PORTS.GRAPHQL_SERVER}/graphql`,

  // Database connection strings (without credentials)
  POSTGRES_LOCAL: `postgresql://${DEFAULT_HOSTS.LOCAL}:${DEFAULT_PORTS.POSTGRES}`,
  REDIS_LOCAL: `redis://${DEFAULT_HOSTS.LOCAL}:${DEFAULT_PORTS.REDIS}`,
  MONGODB_LOCAL: `mongodb://${DEFAULT_HOSTS.LOCAL}:${DEFAULT_PORTS.MONGODB}`,
} as const;

/**
 * Temporal task queue names.
 * Must match Python TaskQueues class.
 */
export const TASK_QUEUES = {
  // Current simplified queue name
  DEFAULT: 'hackathon',

  // Future organized queues
  ONBOARDING: 'onboarding-queue',
  DOCUMENT_PROCESSING: 'document-processing-queue',
  RESEARCH: 'research-queue',
  CONSENSUS: 'consensus-queue',
  DAILY_INTERACTION: 'daily-interaction-queue',
  KNOWLEDGE_BUILDING: 'knowledge-building-queue',
} as const;

/**
 * Environment-aware configuration getters.
 */
export const getTemporalAddress = (): string => {
  return process.env.REACT_APP_TEMPORAL_ADDRESS || DEFAULT_URLS.TEMPORAL_LOCAL;
};

export const getTemporalUIUrl = (workflowId: string, namespace: string = 'default'): string => {
  const baseUrl = process.env.REACT_APP_TEMPORAL_UI_ADDRESS || DEFAULT_URLS.TEMPORAL_UI_LOCAL;
  return `${baseUrl}/namespaces/${namespace}/workflows/${workflowId}`;
};

export const getApiUrl = (): string => {
  return process.env.REACT_APP_API_URL || DEFAULT_URLS.API_LOCAL;
};

export const getGraphQLUrl = (): string => {
  return process.env.REACT_APP_GRAPHQL_URL || DEFAULT_URLS.GRAPHQL_LOCAL;
};

export const getGraphQLEndpoint = (): string => {
  return process.env.REACT_APP_GRAPHQL_ENDPOINT || DEFAULT_URLS.GRAPHQL_ENDPOINT;
};

export const getGraphQLPlaygroundUrl = (): string => {
  return process.env.REACT_APP_GRAPHQL_PLAYGROUND || DEFAULT_URLS.GRAPHQL_PLAYGROUND;
};

export const getGraphQLSubscriptionsUrl = (): string => {
  return process.env.REACT_APP_GRAPHQL_SUBSCRIPTIONS || DEFAULT_URLS.GRAPHQL_SUBSCRIPTIONS;
};

export const getFrontendUrl = (): string => {
  return process.env.REACT_APP_FRONTEND_URL || DEFAULT_URLS.FRONTEND_LOCAL;
};

// Backward compatibility
export const TASK_QUEUE_NAME = TASK_QUEUES.DEFAULT;

/**
 * Type definitions for better TypeScript support.
 */
export type PortName = keyof typeof DEFAULT_PORTS;
export type HostName = keyof typeof DEFAULT_HOSTS;
export type URLName = keyof typeof DEFAULT_URLS;
export type QueueName = keyof typeof TASK_QUEUES;
