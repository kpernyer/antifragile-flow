import React, { useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button, List, ListItem, ListItemText, Paper, Typography, Alert, Chip, Box, LinearProgress, Card, CardContent, Divider } from '@mui/material';
import { addDocuments, detectDocumentType, getDocumentTypeName, getOrganizationState } from '../../utils/organizationState';
import './Onboarding.css';

interface ProcessedDocumentDisplay {
  name: string;
  size: number;
  type: string;
  typeName: string;
  analysisProgress: number;
  status: 'analyzing' | 'completed' | 'duplicate';
  labels: string[];
}

const Onboarding: React.FC = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [processing, setProcessing] = useState(false);
  const [processedMessage, setProcessedMessage] = useState<string>('');
  const [documentTypes, setDocumentTypes] = useState<string[]>([]);
  const [processedDocuments, setProcessedDocuments] = useState<ProcessedDocumentDisplay[]>([]);
  const [analysingDocuments, setAnalysingDocuments] = useState<ProcessedDocumentDisplay[]>([]);

  // Generate labels based on document type
  const generateLabels = (documentType: string): string[] => {
    switch (documentType) {
      case 'yearly_report':
        return ['Financial Data', 'Performance Metrics', 'Strategic Overview', 'Market Analysis'];
      case 'product_catalog':
        return ['Product Features', 'Specifications', 'Pricing Info', 'Market Positioning'];
      case 'sustainability_report':
        return ['ESG Metrics', 'Environmental Goals', 'Social Impact', 'Governance'];
      case 'company_profile':
        return ['Vision & Mission', 'Company History', 'Leadership Team', 'Market Position'];
      default:
        return ['Content Analysis', 'Key Insights', 'Data Extraction'];
    }
  };

  // Load existing processed documents on component mount
  useEffect(() => {
    const orgState = getOrganizationState();
    const displayDocs: ProcessedDocumentDisplay[] = orgState.processedFiles.map(doc => ({
      name: doc.name,
      size: doc.size,
      type: doc.type,
      typeName: getDocumentTypeName(doc.type),
      analysisProgress: 100,
      status: 'completed' as const,
      labels: generateLabels(doc.type)
    }));
    setProcessedDocuments(displayDocs);
  }, []);

  const onDrop = (acceptedFiles: File[]) => {
    setFiles(acceptedFiles);
    // Detect document types for preview
    const types = acceptedFiles.map(file => getDocumentTypeName(detectDocumentType(file.name)));
    setDocumentTypes(types);
  };

  const { getRootProps, getInputProps } = useDropzone({ onDrop });

  const handleProcessDocuments = () => {
    setProcessing(true);
    setProcessedMessage('');

    // Create analyzing documents with 0% progress
    const newAnalysingDocs: ProcessedDocumentDisplay[] = files.map(file => {
      const docType = detectDocumentType(file.name);
      return {
        name: file.name,
        size: file.size,
        type: docType,
        typeName: getDocumentTypeName(docType),
        analysisProgress: 0,
        status: 'analyzing' as const,
        labels: generateLabels(docType)
      };
    });

    setAnalysingDocuments(newAnalysingDocs);

    // Simulate analysis progress
    const progressInterval = setInterval(() => {
      setAnalysingDocuments(prev =>
        prev.map(doc => ({
          ...doc,
          analysisProgress: Math.min(100, doc.analysisProgress + Math.random() * 25 + 10)
        }))
      );
    }, 300);

    // Complete processing after 2 seconds
    setTimeout(() => {
      clearInterval(progressInterval);

      // Add documents to organization learning system
      const result = addDocuments(files);

      // Move completed documents to processed list
      const completedDocs = newAnalysingDocs.map(doc => ({
        ...doc,
        analysisProgress: 100,
        status: result.duplicateFiles.includes(doc.name) ? 'duplicate' as const : 'completed' as const
      }));

      setProcessedDocuments(prev => [...completedDocs, ...prev]);
      setAnalysingDocuments([]);

      setSuggestions([
        'Found potential competitor: Competitor A',
        'Market trend: Increased demand for AI solutions',
        'Industry report: The future of Organizational Twins',
      ]);

      // Create detailed processing message
      let message = '';
      if (result.newFiles > 0) {
        message = `Successfully processed ${result.newFiles} new document${result.newFiles !== 1 ? 's' : ''}! `;
        if (result.duplicateFiles.length > 0) {
          message += `Skipped ${result.duplicateFiles.length} duplicate${result.duplicateFiles.length !== 1 ? 's' : ''}: ${result.duplicateFiles.join(', ')}. `;
        }
        message += `Organization knowledge updated. Total documents: ${result.state.documentsProcessed}`;
      } else if (result.duplicateFiles.length > 0) {
        message = `All ${result.duplicateFiles.length} document${result.duplicateFiles.length !== 1 ? 's have' : ' has'} already been processed: ${result.duplicateFiles.join(', ')}. No KPI updates needed.`;
      }

      setProcessedMessage(message);
      setProcessing(false);

      // Clear files after processing
      setTimeout(() => {
        setFiles([]);
      }, 1000);
    }, 2500);
  };

  const handleSuggestionConfirm = (suggestion: string) => {
    console.log(`Confirmed: ${suggestion}`);
  };

  const handleSuggestionReject = (suggestion: string) => {
    console.log(`Rejected: ${suggestion}`);
  };

  return (
    <div className="onboarding-container">
      <Typography variant="h4" gutterBottom>
        Onboarding
      </Typography>
      <Paper elevation={3} className="dropzone">
        <div {...getRootProps({ className: 'dropzone-area' })}>
          <input {...getInputProps()} />
          <p>Drag 'n' drop some files here, or click to select files</p>
        </div>
      </Paper>
      {files.length > 0 && (
        <Paper elevation={2} sx={{ p: 2, mt: 2 }}>
          <Typography variant="h6" gutterBottom>
            Files Ready for Processing
          </Typography>
          <List>
            {files.map((file, index) => (
              <ListItem key={file.name} sx={{ px: 0 }}>
                <ListItemText
                  primary={file.name}
                />
                <Box ml={2}>
                  <Chip
                    label={documentTypes[index] || 'General Document'}
                    size="small"
                    color="primary"
                    variant="outlined"
                  />
                </Box>
              </ListItem>
            ))}
          </List>
        </Paper>
      )}
      <Button
        variant="contained"
        color="primary"
        onClick={handleProcessDocuments}
        disabled={files.length === 0 || processing}
      >
        {processing ? 'Processing...' : 'Process Documents'}
      </Button>

      {processedMessage && (
        <Alert severity="success" sx={{ mt: 2 }}>
          {processedMessage}
        </Alert>
      )}

      {/* Analysing Documents */}
      {analysingDocuments.length > 0 && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Analyzing Documents...
            </Typography>
            {analysingDocuments.map((doc, index) => (
              <Box key={index} mb={2}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="subtitle1">{doc.name}</Typography>
                  <Chip label={doc.typeName} size="small" color="primary" />
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={doc.analysisProgress}
                  sx={{ height: 8, borderRadius: 4 }}
                />
                <Typography variant="body2" color="textSecondary" mt={1}>
                  {Math.round(doc.analysisProgress)}% complete
                </Typography>
              </Box>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Processed Documents List */}
      {processedDocuments.length > 0 && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Processed Documents ({processedDocuments.length})
            </Typography>
            {processedDocuments.map((doc, index) => (
              <Box key={index}>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start" py={2}>
                  <Box flex={1}>
                    <Box display="flex" alignItems="center" gap={2} mb={1}>
                      <Typography variant="subtitle1">{doc.name}</Typography>
                      <Chip
                        label={doc.typeName}
                        size="small"
                        color={doc.status === 'duplicate' ? 'default' : 'primary'}
                      />
                      {doc.status === 'duplicate' && (
                        <Chip label="Duplicate" size="small" color="warning" />
                      )}
                    </Box>
                    <Box display="flex" gap={1} flexWrap="wrap" mb={1}>
                      {doc.labels.map((label, labelIndex) => (
                        <Chip
                          key={labelIndex}
                          label={label}
                          size="small"
                          variant="outlined"
                          color="secondary"
                        />
                      ))}
                    </Box>
                    <Typography variant="body2" color="textSecondary">
                      Analysis: {doc.analysisProgress}% complete
                    </Typography>
                  </Box>
                </Box>
                {index < processedDocuments.length - 1 && <Divider />}
              </Box>
            ))}
          </CardContent>
        </Card>
      )}

      {suggestions.length > 0 && (
        <div className="suggestions-container">
          <Typography variant="h5" gutterBottom>
            Suggestions
          </Typography>
          <List>
            {suggestions.map((suggestion, index) => (
              <ListItem key={index}>
                <ListItemText primary={suggestion} />
                <Button onClick={() => handleSuggestionConfirm(suggestion)}>Confirm</Button>
                <Button onClick={() => handleSuggestionReject(suggestion)}>Reject</Button>
              </ListItem>
            ))}
          </List>
        </div>
      )}
    </div>
  );
};

export default Onboarding;
