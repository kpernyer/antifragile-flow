import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  CircularProgress,
  Chip,
  Divider,
  LinearProgress,
  Button
} from '@mui/material';
// import { Business } from '@mui/icons-material';
import { getOrganizationData, OrganizationData } from '../../api/organization';
import { resetOrganizationState } from '../../utils/organizationState';
import KPIChart from '../../components/common/KPIChart';
import './Organization.css';

const Organization: React.FC = () => {
  const [orgData, setOrgData] = useState<OrganizationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchOrganizationData = async () => {
    try {
      setLoading(true);
      const data = await getOrganizationData();
      setOrgData(data);
    } catch (err) {
      setError('Failed to fetch organization data');
    }
    setLoading(false);
  };

  const handleResetDemo = () => {
    resetOrganizationState();
    fetchOrganizationData();
  };

  useEffect(() => {
    fetchOrganizationData();
  }, []);

  if (loading) {
    return <CircularProgress />;
  }

  if (error) {
    return <Typography color="error">{error}</Typography>;
  }

  if (!orgData) {
    return <Typography>No organization data available</Typography>;
  }

  const overallProgress = Math.round(
    (orgData.kpis.dna + orgData.kpis.products + orgData.kpis.market + orgData.kpis.aspiration) / 4
  );

  return (
    <div className="organization-container">
      <Box mb={4}>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <div>
            <Typography variant="h4" gutterBottom>
              {orgData.name}
            </Typography>
            <Box display="flex" alignItems="center" gap={2}>
              <Chip
                label={orgData.industry}
                color="primary"
                // icon={<Business />}
              />
              <Typography variant="body2" color="textSecondary">
                Last updated: {new Date(orgData.lastUpdated).toLocaleDateString()}
              </Typography>
            </Box>
          </div>
          <Button
            variant="outlined"
            color="secondary"
            size="small"
            onClick={handleResetDemo}
          >
            Reset Demo
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3} mb={4}>
        <Grid size={{ xs: 12, md: 8 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Organizational Learning Progress
              </Typography>
              <Box mb={2}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="body2">Overall Understanding</Typography>
                  <Typography variant="body2" fontWeight="bold">{overallProgress}%</Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={overallProgress}
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>
              <Typography variant="body2" color="textSecondary">
                Based on {orgData.documentsProcessed} processed documents, we're building a comprehensive understanding of your organization across four key dimensions.
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Learning Metrics
              </Typography>
              <Box mb={2}>
                <Typography variant="body2" color="textSecondary">
                  Documents Processed
                </Typography>
                <Typography variant="h4">
                  {orgData.documentsProcessed}
                </Typography>
              </Box>
              <Divider sx={{ my: 2 }} />
              <Box>
                <Typography variant="body2" color="textSecondary">
                  Knowledge Areas
                </Typography>
                <Typography variant="h4">
                  4
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  DNA • Products • Market • Aspiration
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Typography variant="h5" gutterBottom>
        Knowledge Dimensions
      </Typography>
      <Typography variant="body2" color="textSecondary" mb={3}>
        Our AI analyzes your documents to understand these core aspects of your organization
      </Typography>

      <Grid container spacing={3}>
        <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
          <KPIChart
            title="DNA"
            value={orgData.kpis.dna}
            color="#1976d2"
            description="Core values, culture, and organizational identity"
          />
        </Grid>

        <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
          <KPIChart
            title="Products"
            value={orgData.kpis.products}
            color="#2e7d32"
            description="Product portfolio, features, and capabilities"
          />
        </Grid>

        <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
          <KPIChart
            title="Market"
            value={orgData.kpis.market}
            color="#ed6c02"
            description="Market position, competitors, and opportunities"
          />
        </Grid>

        <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
          <KPIChart
            title="Aspiration"
            value={orgData.kpis.aspiration}
            color="#9c27b0"
            description="Vision, goals, and strategic direction"
          />
        </Grid>
      </Grid>

      <Box mt={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Next Steps
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Continue uploading documents to improve our understanding in all dimensions. The more context we have, the better we can assist with strategic decisions and organizational alignment.
            </Typography>
          </CardContent>
        </Card>
      </Box>
    </div>
  );
};

export default Organization;