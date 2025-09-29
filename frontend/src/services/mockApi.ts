
import { getApiUrl, getGraphQLEndpoint } from '../config/defaults';

/**
 * Mock API service for document processing.
 *
 * In production, this will connect to:
 * - REST API: ${getApiUrl()}
 * - GraphQL API: ${getGraphQLEndpoint()}
 */

// Mock Temporal workflow for quick scan
export const quickScan = async (file: File): Promise<{ summary: string; format: string; title: string; length: number; topic: string; sentiment: string; }> => {
  const apiUrl = getApiUrl();
  const graphqlEndpoint = getGraphQLEndpoint();

  console.log(`Starting quick scan for: ${file.name}`);
  console.log(`API endpoint (future): ${apiUrl}`);
  console.log(`GraphQL endpoint (future): ${graphqlEndpoint}`);

  // Simulate network request and analysis
  await new Promise(resolve => setTimeout(resolve, 2000));
  console.log(`Quick scan completed for: ${file.name}`);

  return {
    summary: 'This is a mock summary.',
    format: file.type || 'unknown',
    title: file.name,
    length: file.size,
    topic: 'mock topic',
    sentiment: 'neutral',
  };
};
