import { getApiUrl } from '../config/defaults';

// Mock workflows data for demo
const mockWorkflowsData = {
  workflows: [
    {
      id: 'wf-001',
      name: 'Document Analysis Pipeline',
      status: 'Running'
    },
    {
      id: 'wf-002',
      name: 'Market Intelligence Gathering',
      status: 'Completed'
    },
    {
      id: 'wf-003',
      name: 'Competitive Analysis',
      status: 'Running'
    },
    {
      id: 'wf-004',
      name: 'Customer Sentiment Analysis',
      status: 'Completed'
    },
    {
      id: 'wf-005',
      name: 'Strategic Planning Workflow',
      status: 'Failed'
    }
  ]
};

export const getWorkflows = async (): Promise<{ workflows: any[] }> => {
  // Mock data for demo - replace with actual API call when backend is ready
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(mockWorkflowsData);
    }, 500);
  });

  // Uncomment below for actual API integration:
  // const apiUrl = getApiUrl();
  // const response = await fetch(`${apiUrl}/workflows`);
  // if (!response.ok) {
  //   throw new Error('Failed to fetch workflows');
  // }
  // return response.json();
};

export const startDemoWorkflows = async () => {
  // Mock response for demo
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ message: 'Demo workflows started successfully' });
    }, 1000);
  });

  // Uncomment below for actual API integration:
  // const apiUrl = getApiUrl();
  // const response = await fetch(`${apiUrl}/workflows/start-demo`, {
  //   method: 'POST',
  // });
  // if (!response.ok) {
  //   throw new Error('Failed to start demo workflows');
  // }
  // return response.json();
};
