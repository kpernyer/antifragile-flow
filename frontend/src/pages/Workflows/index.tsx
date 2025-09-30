import React, { useState, useEffect } from 'react';
import { Box, Card, CardContent, Chip, Grid, Typography, Button, CircularProgress } from '@mui/material';
import { getWorkflows, startDemoWorkflows } from '../../api/workflows';
import './Workflows.css';

interface Workflow {
  id: string;
  name: string;
  status: 'Running' | 'Completed' | 'Failed';
}

const getStatusColor = (status: Workflow['status']) => {
  switch (status) {
    case 'Running':
      return 'primary';
    case 'Completed':
      return 'success';
    case 'Failed':
      return 'error';
    default:
      return 'default';
  }
};

const Workflows: React.FC = () => {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchWorkflows = async () => {
    try {
      const data = await getWorkflows();
      setWorkflows(data.workflows);
    } catch (err) {
      setError('Failed to fetch workflows');
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const handleStartDemoWorkflows = async () => {
    try {
      await startDemoWorkflows();
      // Refresh the list of workflows after starting the demo workflows
      fetchWorkflows();
    } catch (err) {
      setError('Failed to start demo workflows');
    }
  };

  if (loading) {
    return <CircularProgress />;
  }

  if (error) {
    return <Typography color="error">{error}</Typography>;
  }

  return (
    <div className="workflows-container">
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h4" gutterBottom>
          Workflows
        </Typography>
        <Button variant="contained" color="primary" onClick={handleStartDemoWorkflows}>
          Start Demo Workflows
        </Button>
      </Box>
      <Grid container spacing={3}>
        {workflows.map((workflow) => (
          <Grid size={{ xs: 12, sm: 6, md: 4 }} key={workflow.id}>
            <Card>
              <CardContent>
                <Typography variant="h6">{workflow.name}</Typography>
                <Box mt={2}>
                  <Chip label={workflow.status} color={getStatusColor(workflow.status)} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </div>
  );
};

export default Workflows;
