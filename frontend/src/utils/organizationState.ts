// Shared state for organization learning progress
// This simulates a global state that persists across page refreshes
// In a real app, this would be stored in a backend database

interface ProcessedDocument {
  name: string;
  size: number;
  processedAt: string;
  type: string;
}

interface OrganizationState {
  documentsProcessed: number;
  processedFiles: ProcessedDocument[];
  kpis: {
    dna: number;
    products: number;
    market: number;
    aspiration: number;
  };
  lastUpdated: string;
}

const STORAGE_KEY = 'organizationState';

// Default starting state
const defaultState: OrganizationState = {
  documentsProcessed: 0,
  processedFiles: [],
  kpis: {
    dna: 15,
    products: 12,
    market: 8,
    aspiration: 10
  },
  lastUpdated: new Date().toISOString()
};

// Get current state from localStorage
export const getOrganizationState = (): OrganizationState => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (error) {
    console.warn('Failed to parse organization state from localStorage');
  }
  return defaultState;
};

// Save state to localStorage
export const saveOrganizationState = (state: OrganizationState): void => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch (error) {
    console.warn('Failed to save organization state to localStorage');
  }
};

// Document type recognition based on filename
const detectDocumentType = (filename: string): string => {
  const name = filename.toLowerCase();

  if (name.includes('annual') || name.includes('yearly') || name.includes('year') || name.includes('report')) {
    return 'yearly_report';
  }
  if (name.includes('product') && (name.includes('catalog') || name.includes('catalogue'))) {
    return 'product_catalog';
  }
  if (name.includes('sustainability') || name.includes('esg') || name.includes('environmental')) {
    return 'sustainability_report';
  }
  if (name.includes('company') && name.includes('profile')) {
    return 'company_profile';
  }

  return 'general_document';
};

// KPI impact profiles for different document types
const getKPIImpact = (documentType: string): { dna: number; products: number; market: number; aspiration: number } => {
  switch (documentType) {
    case 'yearly_report':
      // Yearly report: moves all numbers significantly
      return { dna: 20, products: 25, market: 30, aspiration: 28 };

    case 'product_catalog':
      // Product catalog: slight DNA/Market, medium Aspiration, major Products
      return { dna: 5, products: 35, market: 8, aspiration: 15 };

    case 'sustainability_report':
      // Sustainability: major DNA, some Products/Aspiration
      return { dna: 30, products: 12, market: 6, aspiration: 18 };

    case 'company_profile':
      // Company profile: major Aspiration, medium Market/Products, some DNA
      return { dna: 10, products: 15, market: 20, aspiration: 35 };

    default:
      // General document: modest increases
      return { dna: 8, products: 10, market: 12, aspiration: 9 };
  }
};

// Apply variability to KPI impact (±20% randomness)
const applyVariability = (baseValue: number): number => {
  const variation = baseValue * 0.2; // 20% variation
  return Math.floor(baseValue + (Math.random() * variation * 2 - variation));
};

// Calculate KPI increment with content awareness and current value consideration
const calculateKPIIncrement = (currentValue: number, baseIncrement: number): number => {
  let increment = applyVariability(baseIncrement);

  // Slow down as values get higher (diminishing returns)
  if (currentValue >= 90) {
    increment = Math.floor(increment * 0.1); // 10% of normal increment
  } else if (currentValue >= 80) {
    increment = Math.floor(increment * 0.3); // 30% of normal increment
  } else if (currentValue >= 70) {
    increment = Math.floor(increment * 0.6); // 60% of normal increment
  }

  return Math.max(1, increment); // Minimum 1 point increase
};

// Add documents with smart content-aware KPI updates and duplicate detection
export const addDocuments = (files: File[]): { state: OrganizationState; newFiles: number; duplicateFiles: string[] } => {
  const currentState = getOrganizationState();
  const newFiles: ProcessedDocument[] = [];
  const duplicateFiles: string[] = [];

  // Check each file for duplicates and process new ones
  files.forEach(file => {
    const isDuplicate = currentState.processedFiles.some(
      processedFile => processedFile.name === file.name && processedFile.size === file.size
    );

    if (isDuplicate) {
      duplicateFiles.push(file.name);
    } else {
      const documentType = detectDocumentType(file.name);
      newFiles.push({
        name: file.name,
        size: file.size,
        processedAt: new Date().toISOString(),
        type: documentType
      });
    }
  });

  // If no new files, return current state
  if (newFiles.length === 0) {
    return {
      state: currentState,
      newFiles: 0,
      duplicateFiles
    };
  }

  // Calculate KPI updates based on document types
  let kpiUpdates = { dna: 0, products: 0, market: 0, aspiration: 0 };

  newFiles.forEach(file => {
    const impact = getKPIImpact(file.type);
    kpiUpdates.dna += calculateKPIIncrement(currentState.kpis.dna, impact.dna);
    kpiUpdates.products += calculateKPIIncrement(currentState.kpis.products, impact.products);
    kpiUpdates.market += calculateKPIIncrement(currentState.kpis.market, impact.market);
    kpiUpdates.aspiration += calculateKPIIncrement(currentState.kpis.aspiration, impact.aspiration);
  });

  // Apply updates with caps at 100%
  const newKpis = {
    dna: Math.min(100, currentState.kpis.dna + kpiUpdates.dna),
    products: Math.min(100, currentState.kpis.products + kpiUpdates.products),
    market: Math.min(100, currentState.kpis.market + kpiUpdates.market),
    aspiration: Math.min(100, currentState.kpis.aspiration + kpiUpdates.aspiration)
  };

  const newState: OrganizationState = {
    documentsProcessed: currentState.documentsProcessed + newFiles.length,
    processedFiles: [...currentState.processedFiles, ...newFiles],
    kpis: newKpis,
    lastUpdated: new Date().toISOString()
  };

  saveOrganizationState(newState);
  return {
    state: newState,
    newFiles: newFiles.length,
    duplicateFiles
  };
};

// Reset state (for demo purposes)
export const resetOrganizationState = (): OrganizationState => {
  saveOrganizationState(defaultState);
  return defaultState;
};

// Get user-friendly document type name
export const getDocumentTypeName = (documentType: string): string => {
  switch (documentType) {
    case 'yearly_report':
      return 'Annual/Yearly Report';
    case 'product_catalog':
      return 'Product Catalog';
    case 'sustainability_report':
      return 'Sustainability Report';
    case 'company_profile':
      return 'Company Profile';
    default:
      return 'General Document';
  }
};

// Export the detection function for use in components
export { detectDocumentType };