import { User } from './users';
import { OrganizationData } from './organization';

export const mockUsers: User[] = [
  {
    id: '1',
    name: 'Mary O\'Keefe',
    email: 'mary.okeefe@globex-industrial-group.com',
    department: 'Engineering',
    role: 'Senior Developer',
    status: 'active'
  },
  {
    id: '2',
    name: 'John Smith',
    email: 'john.smith@globex-industrial-group.com',
    department: 'Product',
    role: 'Product Manager',
    status: 'active'
  },
  {
    id: '3',
    name: 'Sarah Johnson',
    email: 'sarah.johnson@globex-industrial-group.com',
    department: 'Engineering',
    role: 'Team Lead',
    status: 'active'
  },
  {
    id: '4',
    name: 'Mike Davis',
    email: 'mike.davis@globex-industrial-group.com',
    department: 'Sales',
    role: 'Sales Representative',
    status: 'inactive'
  },
  {
    id: '5',
    name: 'Lisa Wilson',
    email: 'lisa.wilson@globex-industrial-group.com',
    department: 'Marketing',
    role: 'Marketing Manager',
    status: 'active'
  }
];

export const mockOrganizationData: OrganizationData = {
  name: 'Globex Industrial Group',
  industry: 'Manufacturing & Technology',
  documentsProcessed: 247,
  lastUpdated: new Date().toISOString(),
  kpis: {
    dna: 72,
    products: 85,
    market: 64,
    aspiration: 58
  }
};