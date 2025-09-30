import { getApiUrl } from '../config/defaults';

export interface User {
  id: string;
  name: string;
  email: string;
  department?: string;
  role?: string;
  status: 'active' | 'inactive';
}

export const getUsers = async (): Promise<{ users: User[] }> => {
  // Mock data for demo - replace with actual API call
  const { mockUsers } = await import('./mockData');
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ users: mockUsers });
    }, 500);
  });

  // Uncomment below for actual API integration:
  // const apiUrl = getApiUrl();
  // const response = await fetch(`${apiUrl}/users`);
  // if (!response.ok) {
  //   throw new Error('Failed to fetch users');
  // }
  // return response.json();
};