import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  CircularProgress,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText
} from '@mui/material';
// import { Person } from '@mui/icons-material';
import { getUsers, User } from '../../api/users';
import './Users.css';

const getStatusColor = (status: User['status']) => {
  return status === 'active' ? 'success' : 'default';
};

const Users: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const data = await getUsers();
        setUsers(data.users);
      } catch (err) {
        setError('Failed to fetch users');
      }
      setLoading(false);
    };

    fetchUsers();
  }, []);

  if (loading) {
    return <CircularProgress />;
  }

  if (error) {
    return <Typography color="error">{error}</Typography>;
  }

  return (
    <div className="users-container">
      <Typography variant="h4" gutterBottom>
        Team Members
      </Typography>
      <Typography variant="subtitle1" color="textSecondary" gutterBottom>
        Organizational knowledge graph from Neo4j
      </Typography>

      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 8 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Active Users ({users.filter(u => u.status === 'active').length})
              </Typography>
              <List>
                {users.map((user) => (
                  <ListItem key={user.id}>
                    <ListItemAvatar>
                      <Avatar>
                        {user.name.charAt(0)}
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={user.name}
                      secondary={
                        <Box display="flex" alignItems="center" gap={1}>
                          <Typography variant="body2" color="textSecondary">
                            {user.email}
                          </Typography>
                          {user.department && (
                            <Chip
                              label={user.department}
                              size="small"
                              variant="outlined"
                            />
                          )}
                          {user.role && (
                            <Chip
                              label={user.role}
                              size="small"
                              color="primary"
                              variant="outlined"
                            />
                          )}
                          <Chip
                            label={user.status}
                            size="small"
                            color={getStatusColor(user.status)}
                          />
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Team Overview
              </Typography>
              <Box mb={2}>
                <Typography variant="body2" color="textSecondary">
                  Total Members
                </Typography>
                <Typography variant="h4">
                  {users.length}
                </Typography>
              </Box>
              <Box mb={2}>
                <Typography variant="body2" color="textSecondary">
                  Active Members
                </Typography>
                <Typography variant="h4" color="success.main">
                  {users.filter(u => u.status === 'active').length}
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="textSecondary">
                  Departments
                </Typography>
                <Typography variant="h4">
                  {new Set(users.map(u => u.department).filter(Boolean)).size}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </div>
  );
};

export default Users;