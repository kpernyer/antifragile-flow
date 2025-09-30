import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { Card, CardContent, Typography, Box } from '@mui/material';

interface KPIChartProps {
  title: string;
  value: number;
  color: string;
  description: string;
}

const KPIChart: React.FC<KPIChartProps> = ({ title, value, color, description }) => {
  const data = [
    { name: 'Learned', value: value },
    { name: 'Remaining', value: 100 - value }
  ];

  const COLORS = [color, '#f0f0f0'];

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Typography variant="h6" gutterBottom align="center">
          {title}
        </Typography>
        <Box height={200}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={40}
                outerRadius={80}
                startAngle={90}
                endAngle={450}
                dataKey="value"
              >
                {data.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => [`${value}%`, '']} />
            </PieChart>
          </ResponsiveContainer>
        </Box>
        <Box textAlign="center" mt={2}>
          <Typography variant="h4" color={color} fontWeight="bold">
            {value}%
          </Typography>
          <Typography variant="body2" color="textSecondary">
            {description}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default KPIChart;