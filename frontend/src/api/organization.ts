import { getApiUrl } from '../config/defaults';

export interface OrganizationKPI {
  dna: number;
  products: number;
  market: number;
  aspiration: number;
}

export interface OrganizationData {
  name: string;
  industry: string;
  documentsProcessed: number;
  lastUpdated: string;
  kpis: OrganizationKPI;
}

export const getOrganizationData = async (): Promise<OrganizationData> => {
  // Use shared state for dynamic KPIs that sync with onboarding
  const { getOrganizationState } = await import('../utils/organizationState');
  const state = getOrganizationState();

  const data: OrganizationData = {
    name: 'Globex Industrial Group',
    industry: 'Manufacturing & Technology',
    documentsProcessed: state.documentsProcessed,
    lastUpdated: state.lastUpdated,
    kpis: state.kpis
  };

  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(data);
    }, 500);
  });

  // Uncomment below for actual API integration:
  // const apiUrl = getApiUrl();
  // const response = await fetch(`${apiUrl}/organization`);
  // if (!response.ok) {
  //   throw new Error('Failed to fetch organization data');
  // }
  // return response.json();
};